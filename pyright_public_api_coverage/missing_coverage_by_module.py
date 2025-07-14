import json
from collections import defaultdict

input_json_path = "results/torch_type_completeness.json"
output_report_path = "results/missing_type_hints_by_submodule.txt"

with open(input_json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

symbols = data.get("typeCompleteness", {}).get("symbols", [])

missing_by_submodule = defaultdict(int)
total_missing = 0

for sym in symbols:
    if sym.get("isTypeKnown") is False:
        total_missing += 1

        name_parts = sym.get("name", "").split(".")
        if len(name_parts) > 2 and name_parts[0] == "torch":
            # e.g., "torch.fx.symbolic_trace" -> "torch.fx"
            group = ".".join(name_parts[:2])
        elif len(name_parts) == 2:
            group = name_parts[0]
        else:
            group = "other"

        missing_by_submodule[group] += 1

with open(output_report_path, 'w', encoding='utf-8') as f_out:
    f_out.write(f"{'Submodule':<20} {'Missing Count':>15} {'Percentage':>12}\n")
    f_out.write(f"{'-'*20} {'-'*15} {'-'*12}\n")

    if total_missing > 0:
        sorted_items = sorted(missing_by_submodule.items(), key=lambda item: -item[1])
        for group, count in sorted_items:
            percentage = f"({count / total_missing:.1%})"
            f_out.write(f"{group:<20} {count:>15} {percentage:>12}\n")

    f_out.write("\n" + "-"*49 + "\n")
    f_out.write(f"Total missing type hints: {total_missing}\n")






