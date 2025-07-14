import json
import re

def is_private(name: str) -> bool:
    """Return True if any part of the dotted name starts with an underscore."""
    return any(part.startswith("_") for part in name.split("."))

def find_non_private_classes_with_private_unknown_base(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pattern = re.compile(r'Type of base class "([^"]+)" is partially unknown')

    symbols = data.get("typeCompleteness", {}).get("symbols", [])
    affected = []

    for symbol in symbols:
        if symbol.get("category") != "class":
            continue

        class_name = symbol.get("name", "")
        if is_private(class_name):
            continue  # skip private classes

        for diagnostic in symbol.get("diagnostics", []):
            message = diagnostic.get("message", "")
            match = pattern.search(message)
            if match:
                base_class_name = match.group(1)
                if is_private(base_class_name):
                    affected.append((class_name, base_class_name))

    return affected

if __name__ == "__main__":
    input_json = 'pyright_public_api_coverage/results/torch_type_completeness.json'
    output_file = 'pyright_public_api_coverage/results/public_classes_with_private_unknown_base.txt'

    results = find_non_private_classes_with_private_unknown_base(input_json)

    print(f"Found {len(results)} non-private classes inheriting from private base classes with unknown types.")
    print("-" * 30)

    if results:
        with open(output_file, 'w', encoding='utf-8') as f:
            for class_name, base_class in results:
                f.write(f'Class: "{class_name}", Private Base Class: "{base_class}"\n')

        print(f"Successfully saved list to '{output_file}'")
    else:
        print("No such classes found.")
