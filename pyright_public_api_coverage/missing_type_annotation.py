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

def find_and_count_inferred_types(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    type_counts = Counter()
    namespace_counts = Counter()

    pattern = re.compile(
        r'Type is missing type annotation and could be inferred differently by type checkers\n\s+Inferred type is "([^"]+)"'
    )

    symbols = data.get("typeCompleteness", {}).get("symbols", [])

    for symbol in symbols:
        symbol_name = symbol.get("name", "")
        parts = symbol_name.split(".")
        # Extract top-level torch namespace, e.g. torch.nn
        namespace = ".".join(parts[:2]) if len(parts) >= 2 else "<unknown>"

        for diagnostic in symbol.get("diagnostics", []):
            message = diagnostic.get("message", "")
            match = pattern.search(message)
            if match:
                inferred_type = match.group(1)
                type_counts[inferred_type] += 1
                namespace_counts[namespace] += 1

    total_count = sum(type_counts.values())
    return total_count, type_counts, namespace_counts

if __name__ == "__main__":
    input_json = 'results/torch_type_completeness.json'
    output_file = 'results/missing_annotation_inferred_types.txt'

    total_count, global_counts, grouped_by_namespace = find_and_count_inferred_types(input_json)

    print(f"Total count of issues with missing type annotations: {total_count}")
    print("-" * 30)

    with open(output_file, 'w', encoding='utf-8') as f:
        if global_counts:
            f.write("Grouped by Inferred Type:\n")
            for inferred_type, count in global_counts.most_common():
                f.write(f'Inferred Type: "{inferred_type}", Count: {count}\n')
            f.write("\n")

            f.write("Grouped by Torch Namespace:\n")
            for namespace, count in grouped_by_namespace.most_common():
                f.write(f'Namespace: "{namespace}", Count: {count}\n')

            print(f"Successfully saved grouped results to '{output_file}'")
        else:
            f.write("No issues with missing type annotations were found.\n")
            print("No issues with missing type annotations were found.")
