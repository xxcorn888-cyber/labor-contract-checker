"""合同自检 · 统一入口。

用法：python check.py 合同.docx

报告分三段，顺序是有意的 —— 法务最该先看「确定违法」那一段：
  一、数字规则   法律写死了上限，比大小就能定，结论是确定的
  二、劳动报酬   提取金额；分得清「没写条款」和「写了但没填数字」
  三、条款有无   关键词匹配，业界实测 F1 约 0.6，所以只给「未检索到」不给「缺失」
"""

import sys

from rules_number import 跑全部
from scan import (RULES, check_item, extract_salary, read_blocks, 是中文文档)

结论标记 = {"违法": "🔴 违法", "合规": "✅ 合规", "信息不足": "◻ 信息不足",
            "已检索到": "✅ 已检索到", "待确认": "❓ 待确认", "未检索到": "— 未检索到",
            "有金额": "✅ 已填写", "金额留空": "⚠ 条款在，金额未填"}


def main(path):
    blocks = read_blocks(path)
    全文 = "\n".join(t for _, t in blocks if t)

    print("=" * 66)
    print(f"合同自检报告　{path}")
    print(f"读到 {len(blocks)} 块（正文段落 + 表格行）")
    print("=" * 66)
    print("⚠ 本工具只做初筛，全部结论需法务复核。")
    print("　「未检索到」不等于合同里没有 —— 可能只是换了说法，本工具认不出。\n")

    if not 是中文文档(blocks):
        print("⛔ 这不是中文文档，而本工具词表是中文的。下面的结果不成立。\n")
        return

    # ---------- 一、数字规则 ----------
    print("─" * 66)
    print("一、数字规则（法定上限，结论确定）")
    print("─" * 66)
    for 名, 结论, 说明, 法条 in 跑全部(全文):
        print(f"{结论标记[结论]}　{名}")
        print(f"        {说明}")
        print(f"        依据：{法条}\n")

    # ---------- 二、劳动报酬 ----------
    print("─" * 66)
    print("二、劳动报酬")
    print("─" * 66)
    状态, 证据 = extract_salary(blocks)
    print(f"{结论标记.get(状态, 状态)}")
    for pos, 值, 原文 in 证据[:3]:
        print(f"        {pos}　{值}　| {原文[:46]}")
    print()

    # ---------- 三、条款有无 ----------
    print("─" * 66)
    print("三、条款有无（关键词匹配，仅供定位）")
    print("─" * 66)
    for 项名, rule in RULES.items():
        状态, 证据 = check_item(blocks, rule)
        print(f"{结论标记[状态]}　{项名}")
        for pos, 原文, 主词, 弱化 in 证据[:1]:
            尾 = f"　⚠ 弱化词：{'/'.join(弱化)}" if 弱化 else ""
            print(f"        {pos} [{主词}]{尾}")
            print(f"        {原文[:56]}")
    print()


if __name__ == "__main__":
    main(sys.argv[1])
