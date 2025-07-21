# PyTorch Type Completeness Initiative
## Executive Summary for Weekly Update 07/21

### Problem Statement
PyTorch's public API currently has **~37% type completeness** (measured by `pyright --verifytypes --ignoreexternal`). While core functionality has type hints, significant gaps exist that impact developer experience and IDE functionality.

**Type Completeness vs. Type Correctness:**
- **Type Completeness**: Public API coverage for external developers using PyTorch
- **Type Correctness**: Internal codebase consistency (broader, more complex problem)
- **Our Focus**: Type completeness - simpler scope, clearer ROI for users

### Business Impact
- **IDE Experience**: Better autocomplete, error detection, deprecated API hiding
- **API Discoverability**: Users can explore PyTorch capabilities through better tooling
- **Ecosystem Growth**: Third-party libraries get better typing support

### Current Analysis Results
From `pyright --verifytypes --ignoreexternal` output, **8 error categories** identified:

**Top 4 High-Impact Categories** (simplest fixes):
1. Missing parameter type annotations
2. Missing return type annotations  
3. Partially unknown parameter types
4. Partially unknown return types

**Key Finding**: **Tensor class represents biggest opportunity** - fixing it alone improves completeness from **37% → 47%** (10 percentage point gain).

### Implementation Plan

#### Phase 1: Tensor Class Type Completion (Highest ROI)
**Modular approach with independent, low-risk diffs:**

1. **`device` typing** in `torch/_C/__init__.py`
2. **`Sym*` classes typing** (potentially using `Protocols`)
3. **Isolated fixes** in `torch/_C/__init__.py`:
   - `__new__` kwargs
   - `Stream` class  
   - `Callable` type hints
4. **Pure Python layer** in `torch/_tensor.py`

**Potential New Addition**: Leverage `@deprecated` type hints to hide deprecated APIs in IDEs while maintaining backward compatibility.

**Result**: `Tensor` class becomes fully type complete

#### Phase 2: Expansion Options
Post-Tensor completion paths:
- Continue with `torch.nn.Module` class (next highest impact)
- Advanced IDE optimizations (shape/device mismatch detection)
- Other high-frequency error categories

### Success Metrics
- **Primary**: Type completeness percentage (target: 37% → 47%+)

### Next Steps
1. **Open Issues**: Create detailed GitHub issues with precise implementation specs for each module
2. **Implement**: Execute Phase 1 diffs in proposed order
3. **Plan Next Steps**: Evaluate results and determine Phase 2 direction based on impact

---