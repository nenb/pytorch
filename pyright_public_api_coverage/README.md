# PyTorch Public API Type Completeness

This project analyzes and tracks the type completeness of PyTorch's public API using Microsoft's Pyright type checker. Type completeness measures how much of the public interface actually has proper type annotations, directly impacting developer experience and IDE support.

## 🎯 Quick Start

**Current Status**: 37.7% type completeness (6,003/15,901 symbols fully typed)

For PyTorch contributors looking to improve type completeness:
1. Read the [**Analysis Results**](ANALYSIS.md) to understand current gaps
2. Check the [**Development Guide**](DEVELOPMENT.md) for testing setup
3. Review [**Common Issues**](COMMON_ISSUES.md) for frequent patterns

## 📊 Current State (Key Findings)

- **Total API symbols analyzed**: 15,901 exported symbols
- **Fully typed**: 6,003 symbols (37.8%)
- **Partially typed**: 802 symbols (5.0%)
- **Untyped**: 9,096 symbols (57.2%)

**Top improvement opportunities**:
1. **Incomplete `Tensor` typing** (~ 10 % improvement) - `Tensor` class needs completion
2. **Untyped private base classes** (0.1 - 1% improvement for each class) - Several (untyped) private classes are used as base classes in the public API
3. **torch.ao** - It's a relatively new feature in `pytorch` and the largest contributor by submodule to type incompleteness

## 📋 Documentation Structure

| Document | Purpose | Audience |
|----------|---------|----------|
| **[Analysis Results](ANALYSIS.md)** | Detailed breakdown of type completeness findings | All contributors |
| **[Development Guide](DEVELOPMENT.md)** | Setup and testing instructions | Active contributors |
| **[Common Issues](COMMON_ISSUES.md)** | Frequent patterns and solutions | Type annotation writers |
| **[Scripts Reference](SCRIPTS.md)** | Analysis tool documentation | Maintainers |

## 🔧 Quick Analysis Commands

```bash
# Check type completeness (requires setup from DEVELOPMENT.md)
pyright --verifytypes torch --ignoreexternal

# Analyze specific error categories
python missing_parameter_annotation.py
python partially_unknown_parameter_type.py
python missing_return_annotation.py
```

## 🚀 Contributing

**High-impact areas for new contributors**:
- **torch.ao module**: Heavy contributor to missing annotations
- **Storage classes**: Private symbols leaking into public API
- **C++ extensions**: Missing type stubs for compiled modules

**Before starting**: Review the [Development Guide](DEVELOPMENT.md) for environment setup and testing procedures.

## 📈 Impact on Users

Type-complete APIs provide:
- **Better IDE support**: Accurate autocompletion and navigation
- **Improved developer experience**: Clear parameter types and return values
- **Reduced documentation dependency**: Types serve as inline documentation
- **Better static analysis**: More effective error detection in user code

## 🔍 Technical Background

*In Python, a symbol is any name that is not a keyword. Symbols can represent classes, functions, methods, variables, parameters, modules, type aliases, type variables, etc. Pyright's type completeness score is computed by counting the number of symbols with known types, ambiguous types, and unknown types.*

Pyright's `--verifytypes` analyzes exported symbols from installed packages, categorizing them as:
- **Known type**: Fully annotated with complete type information
- **Ambiguous type**: Partially annotated (e.g., uses incomplete types like `Tensor`)
- **Unknown type**: Missing type annotations entirely

This analysis focuses on **public API symbols only**. Pyright considers modules or functions whose names begin with a leading underscore as private/implementation details and will generally not include these in the type completeness score. The one exception to this rule is when symbols from private modules are used as part of the interface for public functions. See the Pyright [documentation](https://microsoft.github.io/pyright/#/typed-libraries?id=improving-type-completeness) for further details.

**Note:** In the Pyright results, `otherSymbolCounts` refer to symbols from private modules that have made their way somehow into the public API.

---

*For detailed technical information, see the individual documentation files linked above.*
