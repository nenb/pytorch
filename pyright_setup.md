# Development Guide

This guide covers setting up a development environment for measuring and improving PyTorch's public API type completeness.

## Environment Setup

### Requirements
- Python 3.11+ (recommended)
- conda or similar environment manager

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
conda install pyright=1.1.403
```

### Extra Notes for Installing `torch.distributed` on Mac

(**ONLY IF YOU ARE ON MACOS AND WANT TO INSTALL `torch.distributed`**): 

```
export USE_TENSORPIPE=0
export USE_GLOO=1      
export CC=clang
export CXX=clang++
export MACOSX_DEPLOYMENT_TARGET=14.6
export USE_LIBUV=0
```

Then `python -m pip install --no-build-isolation -v .`

## Testing Type Completeness

### Basic Analysis
```bash
pyright --verifytypes torch --ignoreexternal --outputjson
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
