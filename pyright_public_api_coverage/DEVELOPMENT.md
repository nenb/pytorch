# Development Guide

This guide covers setting up a development environment for measuring and improving PyTorch's public API type completeness.

## Environment Setup

### Requirements
- Python 3.11+ (recommended)
- conda or similar environment manager
- Git access to PyTorch repository

### Standard PyTorch Development Setup

Follow the standard PyTorch development setup with **one critical difference** in the installation step.

#### 1. Get PyTorch Source
```bash
git clone https://github.com/pytorch/pytorch.git
cd pytorch
```

#### 2. Create Development Environment
```bash
conda create -n torch-type-completeness -c conda-forge python=3.11
conda activate torch-type-completeness
```

#### 3. Install Dependencies
Follow the standard [PyTorch dependency installation](https://github.com/pytorch/pytorch#install-dependencies) process.

### Critical: Modified Installation Process

⚠️ **Important**: Pyright's `--verifytypes` requires a **strict editable install**, but PyTorch currently doesn't support this mode.

**Strict editable installation** (won't work with `torch`):
```bash
python -m pip install --no-build-isolation -e -v . --config-settings editable_mode=strict  # DON'T USE THIS
```

**Required installation** (works with `torch` and `--verifytypes`):
```bash
python -m pip install --no-build-isolation -v .
```

#### 4. Install Pyright
```bash
conda install pyright
```

## Testing Type Completeness

### Basic Analysis
```bash
pyright --verifytypes torch --ignoreexternal
```

**Expected output**:
```
Exported symbols: 15,901
Known types: 6,003 (37.8%)
Ambiguous types: 802 (5.0%)
Unknown types: 9,096 (57.2%)
```

### Development Workflow

Since editable installs are disabled, you **MUST** reinstall after each change:

```bash
# 1. Make your changes to type annotations
# 2. Reinstall (30+ seconds)
python -m pip install --no-build-isolation -v .

# 3. Test type completeness
pyright --verifytypes torch --ignoreexternal
```

## Analysis Scripts

Located in `pyright_public_api_coverage/`, these scripts help identify specific improvement opportunities:

### Core Analysis Tools
```bash
# Categorize all error types
python type_completeness_error_categorizer.py

# Categorize all error types in public API only
python type_completeness_public_error_categorizer.py

# Find modules with missing coverage
python missing_coverage_by_module.py

# Identify public API symbols
python ../torch_public_api.py --output torch_imports.py
```

### Specific Error Analysis
```bash
# Missing parameter annotations
python missing_parameter_annotation.py

# Incomplete parameter types
python partially_unknown_parameter_type.py

# Missing return type annotations
python missing_return_annotation.py

# Incomplete return types
python partially_unknown_return_type.py

# Missing variable type annotations
python missing_type_annotation.py

# Incomplete base class typing
python partially_unknown_base_class.py

# Unknown variable types
python unknown_variable_type.py
```

## Understanding Script Outputs

### Error Categories
Scripts output files in `results/` directory:
- `torch_type_completeness.json` - Raw Pyright output
- `torch_type_completeness.txt` - Human-readable summary
- `*_by_*.txt` - Categorized analysis results

### Key Files to Monitor
- TODO

## Common Development Tasks

### Adding Parameter Type Annotations
1. Run `python missing_parameter_annotation.py`
2. Review `results/missing_parameter_annotations.txt`
3. Focus on high-frequency parameters (`**kwargs`, `device`, `dtype`, etc.)

### Fixing Tensor Type Completeness
1. Focus on `torch/_tensor.py` and related files
2. Add missing type annotations to `Tensor` class methods
3. Test impact: should improve ~25% of "partially unknown" errors

### TODO

## Troubleshooting

### Common Issues

**"Module not found" errors**:
- Ensure PyTorch is installed and `torch` can be imported in virtual environment
- Check that conda environment is activated!

**Pyright version issues**:
- Update to latest: `conda update pyright`
- Check version: `pyright --version`

**Analysis script failures**:
- Ensure working directory is correct
- Check that `results/torch_type_completeness.json` exists

---

*For detailed analysis results, see [ANALYSIS.md](ANALYSIS.md).*
