"""
PyTorch Public API Import Generator

This script analyzes the PyTorch library to find all symbols that are part of the public API
and outputs them as import statements.

A symbol is considered public if:
1. It doesn't start with an underscore
2. It's importable from a module that also doesn't start with an underscore
3. It's accessible through the standard import mechanism

The script deduplicates symbols that are exposed in multiple modules but are actually
the same object, preferring the canonical location (where __module__ matches the import path).

The script also excludes symbols that do not originate from PyTorch.

Usage:
    python torch_public_api.py --output torch_imports.py

The output file will contain import statements like:
    from torch import Tensor
    from torch.nn import Module
    from torch.optim import SGD
"""

import sys
import importlib
import pkgutil
import inspect
import types
import argparse
from typing import Set, Dict, List, Any, Optional, Tuple
from collections import defaultdict
import warnings



warnings.filterwarnings('ignore')


class SymbolInfo:
    """Information about a symbol found in the API."""
    def __init__(self, name: str, obj: Any, module_path: str):
        self.name = name
        self.obj = obj
        self.module_path = module_path
        self.object_module = getattr(obj, '__module__', None)
        self.object_name = getattr(obj, '__name__', None)
        self.object_qualname = getattr(obj, '__qualname__', None)
        
    def get_canonical_key(self) -> str:
        """Get a key that uniquely identifies this symbol across modules."""
        # For objects with __module__ and __name__, use those
        if self.object_module and self.object_name:
            return f"{self.object_module}.{self.object_name}"
        
        # For objects with __qualname__, use module_path + qualname
        if self.object_qualname:
            return f"{self.module_path}.{self.object_qualname}"
        
        # Fallback to module_path + name
        return f"{self.module_path}.{self.name}"
    
    def is_canonical_location(self) -> bool:
        """Check if this symbol is in its canonical/defining location."""
        # If object has __module__ attribute, check if it matches our module path
        if self.object_module:
            return self.object_module == self.module_path
        
        # If no __module__, assume current location is canonical
        return True
    
    def __str__(self):
        return f"from {self.module_path} import {self.name}"


class TorchAPIExtractor:
    def __init__(self):
        self.all_symbols: List[SymbolInfo] = []
        self.visited_modules: Set[str] = set()
        self.failed_imports: List[str] = []
        
        # Define prefixes for modules that should be considered "torch" modules
        self.torch_module_prefixes = {
            'torch',
            'torchvision', 
            'torchaudio',
            'torchtext',
            'functorch',
            'torch_geometric',
            'torch_sparse',
            'torch_scatter',
            'torch_cluster',
        }
        
    def is_public_name(self, name: str) -> bool:
        """Check if a name is public (doesn't start with underscore)."""
        return not name.startswith('_')
    
    def is_torch_symbol(self, obj: Any, symbol_name: str, module_path: str) -> bool:
        """Check if an object originates from PyTorch or related libraries."""
        # Get the module where this object was defined
        obj_module = getattr(obj, '__module__', None)
        
        if obj_module is not None:
            # Check if the object's module starts with any torch prefix
            for prefix in self.torch_module_prefixes:
                if obj_module.startswith(prefix):
                    return True
            return False
        
        # For objects without __module__ (constants, built-ins, etc.)
        # We need to use heuristics based on the module they're found in
        # and some known patterns
        
        # If found in a torch module, it's likely a torch constant
        for prefix in self.torch_module_prefixes:
            if module_path.startswith(prefix):
                # Additional filtering for known external constants
                if self.is_known_external_constant(symbol_name, obj):
                    return False
                return True
        
        return False
    
    def is_known_external_constant(self, symbol_name: str, obj: Any) -> bool:
        """Check if a symbol is a known external constant that shouldn't be included."""
        # Known typing constants
        typing_constants = {
            'TYPE_CHECKING', 'Any', 'Union', 'Optional', 'List', 'Dict', 'Tuple', 
            'Callable', 'Iterator', 'Iterable', 'Sequence', 'Mapping', 'Set',
            'FrozenSet', 'Counter', 'Deque', 'DefaultDict', 'OrderedDict',
            'ChainMap', 'AsyncIterator', 'AsyncIterable', 'Awaitable', 'Coroutine',
            'AsyncGenerator', 'AsyncContextManager', 'ContextManager', 'Generic',
            'ClassVar', 'Final', 'Literal', 'TypedDict', 'Protocol', 'runtime_checkable',
            'overload', 'final', 'no_type_check', 'no_type_check_decorator',
            'TypeVar', 'TypeAlias', 'NewType', 'cast', 'assert_type', 'assert_never',
            'reveal_type', 'dataclass_transform', 'override', 'deprecated'
        }
        
        if symbol_name in typing_constants:
            return True
        
        # Known standard library constants
        stdlib_constants = {
            'os', 'sys', 'math', 'random', 'json', 'pickle', 'copy', 'deepcopy',
            'partial', 'reduce', 'wraps', 'lru_cache', 'cached_property',
            'abstractmethod', 'abstractproperty', 'abstractclassmethod', 'abstractstaticmethod',
            'ABC', 'ABCMeta', 'inf', 'nan', 'pi', 'e', 'tau'
        }
        
        if symbol_name in stdlib_constants:
            return True
        
        # Check for numpy-like constants by examining the value
        if isinstance(obj, (int, float, bool, str)) and symbol_name.isupper():
            # Constants that are all uppercase are often from external libraries
            # unless they're clearly torch-related
            torch_like_constants = {
                'CUDA_VERSION', 'CUDNN_VERSION', 'TORCH_VERSION', 'VERSION',
                'DEBUG', 'WARN', 'INFO', 'ERROR', 'CRITICAL'
            }
            if symbol_name not in torch_like_constants:
                return True
        
        # Check for common numpy constants
        numpy_constants = {
            'array', 'ndarray', 'dtype', 'float32', 'float64', 'int32', 'int64',
            'bool_', 'complex64', 'complex128', 'newaxis', 'nan', 'inf', 'pi',
            'e', 'euler_gamma', 'NINF', 'NZERO', 'PZERO', 'PINF'
        }
        
        if symbol_name in numpy_constants:
            return True
        
        return False
    
    def is_public_symbol(self, obj: Any, symbol_name: str, module_path: str) -> bool:
        """Check if an object should be considered a public symbol."""
        # Skip private objects
        if hasattr(obj, '__name__') and obj.__name__.startswith('_'):
            return False
        
        # Skip modules - we don't want to import modules themselves
        if inspect.ismodule(obj):
            return False
        
        # Skip symbols that don't originate from PyTorch
        if not self.is_torch_symbol(obj, symbol_name, module_path):
            return False
            
        # Include functions and classes
        if inspect.isfunction(obj) or inspect.isclass(obj):
            return True
            
        # Include constants and other objects that might be part of the API
        if not callable(obj):
            # Skip very large objects that are likely internal
            try:
                if hasattr(obj, '__sizeof__') and obj.__sizeof__() > 1000000:
                    return False
            except:
                pass
            return True
            
        # Include callable objects that aren't functions or classes
        if callable(obj):
            return True
            
        return False
    
    def get_module_symbols(self, module: types.ModuleType, module_name: str) -> Tuple[List[SymbolInfo], List[Tuple[str, str]]]:
        """Extract public symbols from a module."""
        symbols = []
        excluded_external = []
        
        try:
            # Get all attributes from the module
            for attr_name in dir(module):
                if not self.is_public_name(attr_name):
                    continue
                    
                try:
                    attr = getattr(module, attr_name)
                    
                    # Check if it's an external symbol (for reporting)
                    if not inspect.ismodule(attr) and not getattr(attr, '__name__', '').startswith('_'):
                        if not self.is_torch_symbol(attr, attr_name, module_name):
                            obj_module = getattr(attr, '__module__', 'unknown')
                            excluded_external.append((attr_name, obj_module))
                            continue
                    
                    if self.is_public_symbol(attr, attr_name, module_name):
                        symbol_info = SymbolInfo(attr_name, attr, module_name)
                        symbols.append(symbol_info)
                except (AttributeError, ImportError, RuntimeError):
                    # Some attributes might not be accessible
                    continue
                    
        except Exception as e:
            print(f"Error inspecting module {module_name}: {e}", file=sys.stderr)
            
        return symbols, excluded_external
    
    def import_module_safe(self, module_name: str) -> Optional[types.ModuleType]:
        """Safely import a module, handling errors gracefully."""
        try:
            return importlib.import_module(module_name)
        except Exception as e:
            self.failed_imports.append(f"{module_name}: {str(e)}")
            return None
    
    def discover_submodules(self, package_name: str, package_path: Optional[List[str]] = None) -> List[str]:
        """Discover all submodules in a package."""
        submodules = []
        
        try:
            if package_path is None:
                package = importlib.import_module(package_name)
                if hasattr(package, '__path__'):
                    package_path = package.__path__
                else:
                    return []
            
            for importer, modname, ispkg in pkgutil.iter_modules(package_path):
                if self.is_public_name(modname):
                    full_name = f"{package_name}.{modname}"
                    submodules.append(full_name)
                    
                    # Recursively discover submodules if it's a package
                    if ispkg:
                        try:
                            submodule = importlib.import_module(full_name)
                            if hasattr(submodule, '__path__'):
                                submodules.extend(self.discover_submodules(full_name, submodule.__path__))
                        except Exception:
                            continue
                            
        except Exception as e:
            print(f"Error discovering submodules for {package_name}: {e}", file=sys.stderr)
            
        return submodules
    
    def deduplicate_symbols(self) -> Dict[str, SymbolInfo]:
        """Deduplicate symbols, preferring canonical locations."""
        # Group symbols by their canonical key
        symbol_groups: Dict[str, List[SymbolInfo]] = defaultdict(list)
        
        for symbol in self.all_symbols:
            key = symbol.get_canonical_key()
            symbol_groups[key].append(symbol)
        
        # For each group, select the best symbol
        deduplicated = {}
        
        for key, symbols in symbol_groups.items():
            if len(symbols) == 1:
                # Only one location, use it
                best_symbol = symbols[0]
            else:
                # Multiple locations, prefer canonical location
                canonical_symbols = [s for s in symbols if s.is_canonical_location()]
                
                if canonical_symbols:
                    # Prefer the canonical location
                    best_symbol = canonical_symbols[0]
                    
                    # If multiple canonical locations, prefer shorter module path
                    if len(canonical_symbols) > 1:
                        best_symbol = min(canonical_symbols, key=lambda s: len(s.module_path))
                else:
                    # No canonical location found, prefer shorter module path
                    best_symbol = min(symbols, key=lambda s: len(s.module_path))
            
            # Use the symbol name as the final key for output
            output_key = f"{best_symbol.module_path}.{best_symbol.name}"
            deduplicated[output_key] = best_symbol
        
        return deduplicated
    
    def extract_api_symbols(self) -> Tuple[Dict[str, SymbolInfo], List[Tuple[str, str, str]]]:
        """Extract all public API symbols from torch."""
        excluded_external_all = []
        
        print("Importing torch...", file=sys.stderr)
        
        # Import main torch module
        torch_module = self.import_module_safe('torch')
        if torch_module is None:
            print("Failed to import torch", file=sys.stderr)
            return {}, []
        
        # Process main torch module
        print("Analyzing torch module...", file=sys.stderr)
        symbols, excluded_external = self.get_module_symbols(torch_module, 'torch')
        self.all_symbols.extend(symbols)
        excluded_external_all.extend([(name, module, 'torch') for name, module in excluded_external])
        self.visited_modules.add('torch')
        
        # Discover and process submodules
        print("Discovering submodules...", file=sys.stderr)
        submodules = self.discover_submodules('torch')
        
        print(f"Found {len(submodules)} submodules", file=sys.stderr)
        
        for i, module_name in enumerate(submodules):
            if module_name in self.visited_modules:
                continue
                
            print(f"Processing {module_name} ({i+1}/{len(submodules)})", file=sys.stderr)
            
            module = self.import_module_safe(module_name)
            if module is not None:
                symbols, excluded_external = self.get_module_symbols(module, module_name)
                self.all_symbols.extend(symbols)
                excluded_external_all.extend([(name, obj_module, module_name) for name, obj_module in excluded_external])
                self.visited_modules.add(module_name)
        
        print(f"Found {len(self.all_symbols)} total symbols before deduplication", file=sys.stderr)
        print(f"Excluded {len(excluded_external_all)} external symbols", file=sys.stderr)
        
        # Deduplicate symbols
        print("Deduplicating symbols...", file=sys.stderr)
        deduplicated = self.deduplicate_symbols()
        
        print(f"Reduced to {len(deduplicated)} unique symbols after deduplication", file=sys.stderr)
        
        return deduplicated, excluded_external_all
    
    def format_output(self, deduplicated_symbols: Dict[str, SymbolInfo]) -> str:
        """Format the deduplicated symbols as import statements."""
        output = []
        
        # Group by module for cleaner output
        module_symbols: Dict[str, List[str]] = defaultdict(list)
        
        for symbol in deduplicated_symbols.values():
            module_symbols[symbol.module_path].append(symbol.name)
        
        # Sort modules and symbols within each module
        for module in sorted(module_symbols.keys()):
            symbols = sorted(module_symbols[module])
            for symbol in symbols:
                output.append(f"from {module} import {symbol}")
        
        return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Extract all public API symbols from PyTorch as import statements",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path (required)',
        required=True
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output',
        default=False
    )
    parser.add_argument(
        '--show-duplicates',
        action='store_true',
        help='Show information about duplicate symbols found',
        default=False
    )
    parser.add_argument(
        '--show-external',
        action='store_true',
        help='Show information about external symbols that were excluded',
        default=False
    )
    
    args = parser.parse_args()
    
    # Create extractor and run analysis
    extractor = TorchAPIExtractor()
    
    print("Starting PyTorch API analysis...", file=sys.stderr)
    try:
        deduplicated_symbols, excluded_external = extractor.extract_api_symbols()
        
        # Show external symbols information if requested
        if args.show_external and excluded_external:
            print(f"\nExternal symbols excluded:", file=sys.stderr)
            # Group by source module
            external_by_module = defaultdict(list)
            for name, source_module, found_in_module in excluded_external:
                external_by_module[source_module].append((name, found_in_module))
            
            for source_module in sorted(external_by_module.keys())[:10]:  # Show first 10
                symbols = external_by_module[source_module]
                print(f"  From {source_module}: {len(symbols)} symbols", file=sys.stderr)
                for name, found_in in symbols[:3]:  # Show first 3 symbols
                    print(f"    {name} (found in {found_in})", file=sys.stderr)
                if len(symbols) > 3:
                    print(f"    ... and {len(symbols) - 3} more", file=sys.stderr)
            
            if len(external_by_module) > 10:
                print(f"  ... and {len(external_by_module) - 10} more source modules", file=sys.stderr)
        
        # Show duplicate information if requested
        if args.show_duplicates:
            print("\nDuplicate analysis:", file=sys.stderr)
            symbol_groups = defaultdict(list)
            for symbol in extractor.all_symbols:
                key = symbol.get_canonical_key()
                symbol_groups[key].append(symbol)
            
            duplicates = {k: v for k, v in symbol_groups.items() if len(v) > 1}
            if duplicates:
                print(f"Found {len(duplicates)} symbols with multiple locations:", file=sys.stderr)
                for key, symbols in list(duplicates.items())[:10]:  # Show first 10
                    print(f"  {key}:", file=sys.stderr)
                    for symbol in symbols:
                        canonical = " (canonical)" if symbol.is_canonical_location() else ""
                        print(f"    {symbol.module_path}.{symbol.name}{canonical}", file=sys.stderr)
                if len(duplicates) > 10:
                    print(f"  ... and {len(duplicates) - 10} more", file=sys.stderr)
        
        # Format output as import statements
        import_statements = extractor.format_output(deduplicated_symbols)
        
        # Write output to file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(import_statements)
        
        print(f"Import statements written to {args.output}", file=sys.stderr)
        
        if extractor.failed_imports and args.verbose:
            print(f"\nFailed to import {len(extractor.failed_imports)} modules:", file=sys.stderr)
            for failed in extractor.failed_imports[:10]:  # Show first 10
                print(f"  {failed}", file=sys.stderr)
            if len(extractor.failed_imports) > 10:
                print(f"  ... and {len(extractor.failed_imports) - 10} more", file=sys.stderr)
            
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()