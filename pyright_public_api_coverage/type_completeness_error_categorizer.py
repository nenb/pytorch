#!/usr/bin/env python3
"""
PyRight Type Completeness Error Analyzer

This script analyzes pyright --verifytypes output and categorizes errors
according to predefined categories, providing counts and percentages.
"""

import json
import re
from typing import Dict, List, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class ErrorCategory:
    name: str
    description: str
    pattern: str
    examples: List[str]


class PyrightErrorAnalyzer:
    def __init__(self):
        self.error_categories = [
            ErrorCategory(
                name="Missing Parameter Annotation",
                description="Function arguments that are missing type annotations",
                pattern=r"Type annotation for parameter .* is missing",
                examples=["Type annotation for parameter \"zero_point\" is missing"]
            ),
            ErrorCategory(
                name="Partially Unknown Parameter Type",
                description="Function arguments with incomplete type annotations",
                pattern=r"Type of parameter .* is partially unknown",
                examples=["Type of parameter \"generator\" is partially unknown\\n  Parameter type is \"Generator | None\""]
            ),
            ErrorCategory(
                name="Missing Return Annotation",
                description="Methods/functions missing return type annotations",
                pattern=r"Return type annotation is missing",
                examples=["Return type annotation is missing"]
            ),
            ErrorCategory(
                name="Partially Unknown Return Type",
                description="Functions with incomplete return type annotations",
                pattern=r"Return type is partially unknown",
                examples=["Return type is partially unknown\\n  Return type is \"Tensor\""]
            ),
            ErrorCategory(
                name="Missing Type Annotation",
                description="Variables missing explicit type annotations",
                pattern=r"Type is missing type annotation and could be inferred differently by type checkers",
                examples=["Type is missing type annotation and could be inferred differently by type checkers\\n  Inferred type is \"dtype\""]
            ),
            ErrorCategory(
                name="Partially Unknown Base Class",
                description="Classes inheriting from incomplete base classes",
                pattern=r"Type of base class .* is partially unknown",
                examples=["Type of base class \"torch.nn.modules.instancenorm._InstanceNorm\" is partially unknown"]
            ),
            ErrorCategory(
                name="Unknown Variable Type",
                description="Variables with completely unknown types",
                pattern=r"Type unknown for variable",
                examples=["Type unknown for variable \"torch.fft.ifft2\""]
            )
        ]
        
        self.error_counts = defaultdict(int)
        self.total_errors = 0
        self.unmatched_errors = []

    def load_pyright_output(self, file_path: str) -> Dict[str, Any]:
        """Load pyright --verifytypes JSON output"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {}

    def extract_errors_from_symbols(self, symbols: List[Dict[str, Any]]) -> List[str]:
        """Extract error messages from symbol diagnostics (severity 'error' only)"""
        errors = []
        for symbol in symbols:
            if 'diagnostics' in symbol:
                for diagnostic in symbol['diagnostics']:
                    if 'message' in diagnostic and diagnostic.get('severity') == 'error':
                        errors.append(diagnostic['message'])
        return errors

    def categorize_error(self, error_message: str) -> str:
        """Categorize an error message based on predefined patterns"""
        for category in self.error_categories:
            if re.search(category.pattern, error_message):
                return category.name
        return "Other"

    def analyze_errors(self, data: Dict[str, Any]) -> None:
        """Analyze all errors in the pyright output"""
        if 'typeCompleteness' not in data:
            print("Error: No 'typeCompleteness' section found in data")
            return
            
        type_completeness = data['typeCompleteness']
        
        if 'symbols' not in type_completeness:
            print("Error: No 'symbols' section found in typeCompleteness")
            return
            
        symbols = type_completeness['symbols']
        errors = self.extract_errors_from_symbols(symbols)
        
        self.total_errors = len(errors)
        print(f"**Total Errors Found: {self.total_errors}**")
        
        # Categorize each error
        for error in errors:
            category = self.categorize_error(error)
            self.error_counts[category] += 1
            
            if category == "Other":
                self.unmatched_errors.append(error)

    def print_analysis_report(self) -> None:
        """Print a detailed analysis report"""
        print("\n" + "="*80)
        print("PYRIGHT TYPE COMPLETENESS ERROR ANALYSIS")
        print("="*80)
        
        if self.total_errors == 0:
            print("No errors found to analyze.")
            return
        
        # Sort categories by count (descending)
        sorted_categories = sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)
        
        for i, (category, count) in enumerate(sorted_categories, 1):
            percentage = (count / self.total_errors) * 100
            print(f"\n{i}. {category}")
            print(f"   Count: {count:,}")
            print(f"   Percentage: {percentage:.2f}% of total")
            
            # Find the category definition for description and examples
            category_def = next((cat for cat in self.error_categories if cat.name == category), None)
            if category_def:
                print(f"   Description: {category_def.description}")
                if category_def.examples:
                    print(f"   Example: \"{category_def.examples[0]}\"")
            elif category == "Other":
                print(f"   Description: Miscellaneous errors not matching predefined patterns")
                if self.unmatched_errors:
                    print(f"   Example: \"{self.unmatched_errors[0][:100]}...\"")
            
            print("-" * 60)

    def print_sample_unmatched_errors(self, limit: int = 10) -> None:
        """Print sample unmatched errors for analysis"""
        if not self.unmatched_errors:
            return
            
        print(f"\n{'='*80}")
        print(f"SAMPLE UNMATCHED ERRORS (showing first {min(limit, len(self.unmatched_errors))} of {len(self.unmatched_errors)})")
        print("="*80)
        
        for i, error in enumerate(self.unmatched_errors[:limit], 1):
            print(f"{i}. {error}")
            print("-" * 40)

    def generate_summary_stats(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        return {
            'total_errors': self.total_errors,
            'categorized_errors': sum(count for category, count in self.error_counts.items() if category != "Other"),
            'unmatched_errors': self.error_counts.get("Other", 0),
            'categories': dict(self.error_counts)
        }


def main():
    analyzer = PyrightErrorAnalyzer()
    
    # For this example, we'll use the provided data directly
    # In practice, you would load from a file like this:
    # data = analyzer.load_pyright_output("pyright_output.json")
    
    sample_data = analyzer.load_pyright_output("results/torch_type_completeness.json")
    
    # Analyze the errors
    analyzer.analyze_errors(sample_data)
    
    # Print the analysis report
    analyzer.print_analysis_report()
    
    # Print sample unmatched errors
    analyzer.print_sample_unmatched_errors()
    
    # Generate summary statistics
    stats = analyzer.generate_summary_stats()
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print("="*80)
    print(f"Total Errors: {stats['total_errors']:,}")
    print(f"Categorized Errors: {stats['categorized_errors']:,}")
    print(f"Unmatched Errors: {stats['unmatched_errors']:,}")
    print(f"Match Rate: {(stats['categorized_errors']/stats['total_errors']*100):.1f}%")


if __name__ == "__main__":
    main()