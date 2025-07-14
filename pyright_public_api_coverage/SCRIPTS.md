# Scripts Reference

This document provides detailed information about the analysis scripts used to understand PyTorch's type completeness issues.

## Core Analysis Scripts

### type_completeness_error_categorizer.py
**Purpose**: Categorizes all Pyright errors into predefined categories with counts and percentages.

**Usage**:
```bash
python type_completeness_error_categorizer.py
```

**Output**:
- `results/type_completeness_error_categorizer.txt` - Summary by category
- Console output with error counts and percentages

**Key Categories**:
1. Missing Parameter Annotation (30.70%)
2. Partially Unknown Parameter Type (24.98%)
3. Missing Return Annotation (15.38%)
4. Partially Unknown Return Type (13.18%)
5. Missing Type Annotation (6.22%)
6. Partially Unknown Base Class (4.05%)
7. Unknown Variable Type (1.51%)
8. Other (3.98%)

### missing_coverage_by_module.py
**Purpose**: Identifies modules with significant type completeness issues.

**Usage**:
```bash
python missing_coverage_by_module.py
```

**Output**:
- `results/missing_type_hints_by_submodule.txt` - Module-level breakdown
- Helps identify which teams/modules need attention

## Parameter Analysis Scripts

### missing_parameter_annotation.py
**Purpose**: Analyzes functions with missing parameter type annotations.

**Usage**:
```bash
python missing_parameter_annotation.py
```

**Output**:
- `results/missing_parameter_annotations.txt` - Most common missing parameters
- Identifies patterns like `**kwargs`, `device`, `dtype`

### partially_unknown_parameter_type.py
**Purpose**: Analyzes parameters with incomplete type annotations.

**Usage**:
```bash
python partially_unknown_parameter_type.py
```

**Output**:
- `results/partially_unknown_grouped_by_type.txt` - Grouped by incomplete types
- Heavily dominated by `Tensor` type incompleteness

## Return Type Analysis Scripts

### missing_return_annotation.py
**Purpose**: Identifies functions and methods without return type annotations.

**Usage**:
```bash
python missing_return_annotation.py
```

**Output**:
- `results/missing_return_types_by_class.txt` - Classes with missing return types
- Focuses on methods rather than standalone functions

### partially_unknown_return_type.py
**Purpose**: Analyzes functions with incomplete return type annotations.

**Usage**:
```bash
python partially_unknown_return_type.py
```

**Output**:
- `results/unknown_return_types_by_count.txt` - Most common incomplete return types

## Variable and Class Analysis Scripts

### missing_type_annotation.py
**Purpose**: Identifies variables missing explicit type annotations.

**Usage**:
```bash
python missing_type_annotation.py
```

**Output**:
- `results/missing_annotation_inferred_types.txt` - Variables with inferred types
- Shows modules with highest concentration of untyped variables

### partially_unknown_base_class.py
**Purpose**: Identifies classes with incompletely typed base classes.

**Usage**:
```bash
python partially_unknown_base_class.py
```

**Output**:
- `results/unknown_base_classes_by_count.txt` - Base classes needing type completion
- Shows inheritance hierarchy impact on type completeness

### partially_unknown_private_base_class.py
**Purpose**: Identifies private base classes that leak into public API.

**Usage**:
```bash
python partially_unknown_private_base_class.py
```

**Output**:
- `results/public_classes_with_private_unknown_base.txt` - Public classes with private bases
- Critical for API hygiene and type completeness

### unknown_variable_type.py
**Purpose**: Identifies variables with completely unknown types.

**Usage**:
```bash
python unknown_variable_type.py
```

**Output**:
- `results/unknown_variables_by_class_count.txt` - Variables by module/class

## Utility Scripts

### torch_missing_symbols.py
**Purpose**: Identifies symbols from public API missing from Pyright analysis.

**Usage**:
```bash
python torch_missing_symbols.py
```

**Output**:
- `missing_symbols.txt` - Public API symbols not analyzed by Pyright
- May help catch edge cases where PyTorch magic confuses Pyright

### ../torch_public_api.py
**Purpose**: Generates comprehensive list of all public API symbols.

**Usage** (from project root):
```bash
python torch_public_api.py --output torch_imports.py
```

**Output**:
- `torch_imports.py` - All public API symbols as import statements
- Defines canonical public API for analysis

## Output Files Reference

### Primary Analysis Files
- `torch_type_completeness.json` - Raw Pyright output (JSON)
- `torch_type_completeness.txt` - Human-readable Pyright summary
- `type_completeness_error_categorizer.txt` - Categorized error analysis

### Category-Specific Files
- `missing_parameter_annotations.txt` - Most common missing parameters
- `missing_return_types_by_class.txt` - Classes needing return types
- `missing_annotation_inferred_types.txt` - Variables needing type annotations
- `partially_unknown_grouped_by_type.txt` - Incomplete types by frequency
- `unknown_base_classes_by_count.txt` - Base classes needing completion
- `public_classes_with_private_unknown_base.txt` - Private symbol leakage
- `unknown_variables_by_class_count.txt` - Unknown variables by module
- `missing_type_hints_by_submodule.txt` - Module-level coverage analysis

### Utility Files
- `torch_imports.py` - Public API symbol imports
- `missing_symbols.txt` - Missing public API symbols

---

*For development setup, see [DEVELOPMENT.md](DEVELOPMENT.md). For common issues, see [COMMON_ISSUES.md](COMMON_ISSUES.md).*
