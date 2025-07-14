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

def find_missing_return_types_by_class(json_file):

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    class_counts = Counter()
    target_message = "Return type annotation is missing"
    
    symbols = data.get("typeCompleteness", {}).get("symbols", [])

    for symbol in symbols:
        has_missing_return = any(
            diagnostic.get('message') == target_message 
            for diagnostic in symbol.get('diagnostics', [])
        )

        if has_missing_return:
            full_name = symbol.get('name', '')
            if not full_name:
                continue

            # Split the name by the last dot to separate the method from the class
            parts = full_name.rsplit('.', 1)
            
            # If there's a dot, the class/module name is the part before it.
            # Otherwise, we'll consider the full name itself.
            class_name = parts[0] if len(parts) > 1 else full_name
            
            class_counts[class_name] += 1

    total_count = sum(class_counts.values())
    return total_count, class_counts

if __name__ == "__main__":
    input_json = 'results/torch_type_completeness.json'
    output_file = 'results/missing_return_types_by_class.txt'

    total_count, counts = find_missing_return_types_by_class(input_json)

    print(f"Total count of methods with missing return types: {total_count}")
    print("-" * 30)

    if counts:
        # The most_common() method sorts items by count in descending order
        sorted_items = counts.most_common()

        with open(output_file, 'w', encoding='utf-8') as f:
            for class_name, count in sorted_items:
                f.write(f"{class_name}: {count}\n")
        
        print(f"Successfully saved sorted results to '{output_file}'")
    else:
        print("No methods with missing return types were found.")