# Common Issues and Solutions

This document covers frequently encountered patterns in PyTorch's type completeness analysis and provides actionable solutions.

## Issue Categories

### 1. The `Tensor` Type Completeness Problem

**Problem**: The `Tensor` class is widely used but incompletely typed, causing cascading issues.

**Example Error**:
```
Type of parameter "other" is partially unknown
Parameter type is "Tensor | int"
```

**Root Cause**: The `Tensor` class itself lacks complete type information, so any function using `Tensor` becomes "partially unknown."

**Solution Strategy**:

TODO

### 2. Private Symbol Leakage

**Problem**: Private classes (starting with `_`) leak into public API, affecting type completeness.

**Major Example**: `_StorageBase` class
- 73 missing type hints
- Exposed through `UntypedStorage` inheritance
- Affects all storage-related public APIs

**Example Error**:
```
Type of base class "torch.storage._StorageBase" is partially unknown
```

**Detection**: Look for errors mentioning classes starting with `_` in public API contexts.

**Solutions**:

TODO

### 3. C++ Extension Missing Type Stubs

**Problem**: C++ extensions lack type stubs, causing "unknown variable type" errors.

**Common Modules**:
- `torch.fft.*`
- `torch.special.*`
- `torch.linalg.*`
- Various `torch._C.*` bindings

**Example Error**:
```
Type unknown for variable "torch.fft.ifft2"
```

**Solution**:

TODO

### 4. Module-Specific Issues

#### torch.ao Module
**Problem**: Newer module with limited type coverage.

**Impact**: Heavy contributor to missing annotations across all categories.

**Solution**: Systematic typing effort for `torch.ao` module.

**Approach**:
1. Start with most-used functions
2. Add parameter and return type annotations
3. Focus on public API surface

#### torch.nn.modules Hierarchy
**Problem**: Large inheritance hierarchy with incomplete base class typing.

**Impact**: Cascading effects where incomplete base classes affect all derived classes.

**Solution**: Bottom-up typing approach.

**Priority Order**:
1. `torch.nn.Module` base class
2. Common base classes (`_Loss`, `_WeightedLoss`, etc.)
3. Specific implementations

---

*For environment setup, see [DEVELOPMENT.md](DEVELOPMENT.md). For detailed analysis, see [ANALYSIS.md](ANALYSIS.md).*
