"""把 模板/ 下所有 .docx 跑一遍，输出一张 Markdown 对照表。

输出可以直接贴进 README —— 那张「我在 N 份模板上跑过」的证据表就是它。
"""

import glob
import os

from scan import RULES, check_item, extract_salary, read_blocks, 是中文文档

符号 = {"已检索到": "✔ 已检索到", "待确认": "？待确认", "未检索到": "— 未检索到",
        "有金额": "✔ 有金额", "金额留空": "！金额未填"}

files = sorted(glob.glob("模板/*.docx"))
项名列表 = list(RULES.keys())

print("> 「未检索到」＝本工具的中文词表没匹配上，**不等于合同里没有这一条**。需法务复核。\n")
print("| 文件 | 块数 | 劳动报酬 | " + " | ".join(项名列表) + " |")
print("|---|---|---|" + "---|" * len(项名列表))

跳过的 = []
for path in files:
    name = os.path.basename(path).replace(".docx", "")
    blocks = read_blocks(path)

    # 英文文档不进表 —— 中文词表在它上面全落空，混进去会被读成「这份合同啥都缺」
    if not 是中文文档(blocks):
        跳过的.append(name)
        continue

    行 = [name, str(len(blocks))]
    状态, _ = extract_salary(blocks)
    行.append(符号[状态])
    for rule in RULES.values():
        状态, _ = check_item(blocks, rule)
        行.append(符号[状态])
    print("| " + " | ".join(行) + " |")

if 跳过的:
    print(f"\n⛔ 跳过 {len(跳过的)} 份非中文文档（中文词表不适用，不是合同缺条款）：")
    for n in 跳过的:
        print(f"   - {n}")
