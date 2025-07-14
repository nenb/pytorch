import json
import re
from collections import Counter

"""
 Schema: Pyright Type Completeness Report for a Python Package
{
  version: string,         // Version of the type completeness report tool
  time: timestamp,         // Time the report was generated (Unix epoch in ms)
  generalDiagnostics: [],  // List of general diagnostics (empty if no issues)
  summary: {               // Summary of the type checking process
    filesAnalyzed: int,        // Number of Python files checked
    errorCount: int,           // Total number of type errors found
    warningCount: int,         // Total number of warnings found
    informationCount: int,     // Informational messages count
    timeInSec: float           // Total time taken for analysis
  },
  typeCompleteness: {
    packageName: string,       // Name of the Python package (e.g. "torch")
    packageRootDirectory: str, // Path to the package installation
    moduleName: string,        // Top-level module name (same as packageName)
    moduleRootDirectory: str,  // Directory containing the top-level module
    ignoreUnknownTypesFromImports: bool, // Whether unknown types from imports are ignored
    pyTypedPath: string,       // Path to the PEP 561 `py.typed` marker file
    exportedSymbolCounts: {    // Type information for exported (public) symbols
      withKnownType: int,
      withAmbiguousType: int,
      withUnknownType: int
    },
    otherSymbolCounts: {       // Type information for internal/private symbols
      withKnownType: int,
      withAmbiguousType: int,
      withUnknownType: int
    },
    missingFunctionDocStringCount: int,  // Number of functions lacking docstrings
    missingClassDocStringCount: int,     // Number of classes lacking docstrings
    missingDefaultParamCount: int,       // Number of parameters missing default values
    completenessScore: float,  // Normalized score (0-1) indicating type coverage completeness
    modules: [                 // List of all modules within the package
      { name: string }         // Module name, fully qualified (e.g. "torch.nn.functional")
    ],
    symbols: [                 // Detailed symbol-level report
      {
        category: string,         // Type of symbol ("function", "class", etc.)
        name: string,             // Fully qualified symbol name
        referenceCount: int,      // Number of times the symbol is referenced
        isExported: bool,         // Whether the symbol is part of the public API
        isTypeKnown: bool,        // Whether the symbol has a known type
        isTypeAmbiguous: bool,    // Whether the symbol’s type is ambiguous
        diagnostics: []           // List of diagnostic issues for the symbol
      }
    ]
  }
}

"""

def find_and_group_unknown_types(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    grouped_counts = Counter()

    pattern = re.compile(r'Type of parameter "([^"]+)" is partially unknown\n\s+Parameter type is "([^"]+)"')

    symbols = data.get("typeCompleteness", {}).get("symbols", [])

    for symbol in symbols:
        for diagnostic in symbol.get('diagnostics', []):
            message = diagnostic.get('message', '')
            match = pattern.search(message)
            if match:
                # group(1) is X (parameter name), group(2) is Y (parameter type)
                param_name = match.group(1)
                param_type = match.group(2)

                grouped_counts[(param_name, param_type)] += 1

    total_count = sum(grouped_counts.values())
    return total_count, grouped_counts

if __name__ == "__main__":
    input_json = 'results/torch_type_completeness.json'
    output_file = 'results/partially_unknown_grouped_by_type.txt'

    total_count, counts = find_and_group_unknown_types(input_json)

    print(f"Total count of parameters with partially unknown types: {total_count}")
    print("-" * 30)

    if counts:
        sorted_items = counts.most_common()

        # Aggregate by type only (ignore param name)
        type_totals = Counter()
        for (_, param_type), count in sorted_items:
            type_totals[param_type] += count

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Grouped by Parameter and Type:\n")
            for (param_name, param_type), count in sorted_items:
                line = f'Parameter: "{param_name}", Type: "{param_type}", Count: {count}\n'
                f.write(line)

            f.write("\nTotal occurrences per Type:\n")
            for param_type, count in type_totals.most_common():
                line = f'Type: "{param_type}", Count: {count}\n'
                f.write(line)

        print(f"\nSuccessfully saved sorted and grouped results to '{output_file}'")
    else:
        print("No parameters with partially unknown types were found.")