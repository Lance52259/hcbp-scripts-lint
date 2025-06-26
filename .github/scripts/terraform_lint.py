#!/usr/bin/env python3
"""
Terraform Scripts Lint Tool

A comprehensive linting tool for Terraform scripts using the unified rules management system.
This tool provides flexible rule execution, detailed reporting, and performance monitoring
across four rule categories: ST (Style/Format), IO (Input/Output), DC (Documentation/Comments), and SC (Security Code).

Key Features:
- Unified rules management with centralized coordination
- Flexible rule filtering and path exclusion
- Performance monitoring and detailed reporting
- GitHub Actions integration with artifact support
- Support for checking only changed files in Git
- Comprehensive error reporting with line numbers

Rule Categories:
- ST (Style/Format): Code formatting and style rules
- IO (Input/Output): Variable and output definition rules
- DC (Documentation/Comments): Comment and documentation rules
- SC (Security Code): Security and safety validation rules

Security Features:
- Local processing only, no network requests
- Read-only operations, no file modifications
- No data collection or transmission
- Minimal permission requirements

Author: Lance
License: Apache 2.0
"""

import os
import sys
import argparse
import re
import fnmatch
import subprocess
import time
from typing import List, Dict, Set, Optional, Tuple, Any, NamedTuple
import traceback

# Add rules directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

try:
    # Import the unified rules management system
    from rules import (
        RulesManager,
        RuleExecutionResult,
        BatchExecutionSummary,
        validate_terraform_file,
        get_all_available_rules,
        get_unified_rules_summary
    )
except ImportError as e:
    print(f"Error importing unified rules system: {e}")
    print("Please ensure the rules directory contains the unified rules management system.")
    sys.exit(1)


class ErrorRecord(NamedTuple):
    """Structured error record with file, line, rule and message information."""
    file_path: str
    line_number: Optional[int]
    rule_id: str
    message: str
    
    def to_summary_format(self) -> str:
        """Convert to summary format for display."""
        base_name = os.path.basename(self.file_path)
        if self.line_number:
            return f"{base_name}:{self.line_number} [{self.rule_id}] {self.message}"
        else:
            return f"{base_name} [{self.rule_id}] {self.message}"
    
    def to_detailed_format(self) -> str:
        """Convert to detailed format for legacy compatibility."""
        if self.line_number:
            return f"ERROR: {self.file_path} ({self.line_number}): [{self.rule_id}] {self.message}"
        else:
            return f"ERROR: {self.file_path}: [{self.rule_id}] {self.message}"


class WarningRecord(NamedTuple):
    """Structured warning record with file, line, rule and message information."""
    file_path: str
    line_number: Optional[int]
    rule_id: str
    message: str
    
    def to_summary_format(self) -> str:
        """Convert to summary format for display."""
        base_name = os.path.basename(self.file_path)
        if self.line_number:
            return f"{base_name}:{self.line_number} [{self.rule_id}] {self.message}"
        else:
            return f"{base_name} [{self.rule_id}] {self.message}"
    
    def to_detailed_format(self) -> str:
        """Convert to detailed format for legacy compatibility."""
        if self.line_number:
            return f"WARNING: {self.file_path} ({self.line_number}): [{self.rule_id}] {self.message}"
        else:
            return f"WARNING: {self.file_path}: [{self.rule_id}] {self.message}"


class LintReport:
    """Comprehensive lint report with detailed statistics."""
    
    def __init__(self, total_errors: int, total_warnings: int, total_violations: int,
                 files_processed: int, total_lines_processed: int, execution_time: float,
                 rules_executed: int, successful_rules: int, failed_rules: int,
                 errors_by_category: Dict[str, int], warnings_by_category: Dict[str, int],
                 performance_metrics: Dict[str, Any]):
        self.total_errors = total_errors
        self.total_warnings = total_warnings
        self.total_violations = total_violations
        self.files_processed = files_processed
        self.total_lines_processed = total_lines_processed
        self.execution_time = execution_time
        self.rules_executed = rules_executed
        self.successful_rules = successful_rules
        self.failed_rules = failed_rules
        self.errors_by_category = errors_by_category
        self.warnings_by_category = warnings_by_category
        self.performance_metrics = performance_metrics


class TerraformLinter:
    """
    Enhanced Terraform Scripts Linter using Unified Rules Management System

    A comprehensive linting tool that leverages the unified rules management system
    to provide consistent, efficient, and extensible Terraform script validation.

    Features:
    - Unified rules management with centralized coordination
    - Advanced rule filtering and path management
    - Performance monitoring and detailed analytics
    - Flexible reporting with multiple output formats
    - GitHub Actions integration with comprehensive artifact support
    - Git integration for changed-files-only mode
    """

    def __init__(self, ignored_rules: Set[str] = None, include_paths: List[str] = None,
                 exclude_paths: List[str] = None, changed_files_only: bool = False,
                 base_ref: str = None, rule_categories: List[str] = None):
        """
        Initialize the enhanced Terraform linter with unified rules management.

        Args:
            ignored_rules: Set of rule IDs to ignore during linting
            include_paths: List of path patterns to include (if specified, only these paths are checked)
            exclude_paths: List of path patterns to exclude from checking
            changed_files_only: If True, only check files changed in current commit/PR
            base_ref: Base reference for git diff (e.g., 'origin/main', 'HEAD~1')
            rule_categories: List of rule categories to execute (ST, IO, DC, SC). If None, all categories are used.
        """
        # Initialize unified rules manager
        self.rules_manager = RulesManager()
        
        # Configuration settings
        self.ignored_rules = ignored_rules or set()
        self.include_paths = include_paths or []
        self.exclude_paths = exclude_paths or []
        self.changed_files_only = changed_files_only
        self.base_ref = base_ref or 'HEAD~1'
        self.rule_categories = rule_categories or ["ST", "IO", "DC", "SC"]

        # Error and warning tracking - using structured records
        self.errors: List[ErrorRecord] = []
        self.warnings: List[WarningRecord] = []
        self.violations_by_category = {"ST": 0, "IO": 0, "DC": 0, "SC": 0}
        self.errors_by_category = {"ST": 0, "IO": 0, "DC": 0, "SC": 0}
        self.warnings_by_category = {"ST": 0, "IO": 0, "DC": 0, "SC": 0}

        # Performance metrics
        self.files_processed = 0
        self.total_lines_processed = 0
        self.start_time = None
        self.end_time = None
        self.execution_results = []

        # Print initialization summary
        summary = self.rules_manager.get_rules_summary()
        print(f"Initialized Terraform Linter with unified rules management:")
        print(f"- Total available rules: {summary['total_rules']}")
        print(f"- ST rules: {summary['rules_by_system']['ST']}")
        print(f"- IO rules: {summary['rules_by_system']['IO']}")
        print(f"- DC rules: {summary['rules_by_system']['DC']}")
        print(f"- SC rules: {summary['rules_by_system']['SC']}")
        if self.ignored_rules:
            print(f"- Ignored rules: {', '.join(sorted(self.ignored_rules))}")
        if self.rule_categories != ["ST", "IO", "DC", "SC"]:
            print(f"- Active categories: {', '.join(self.rule_categories)}")

    def should_ignore_rule(self, rule_id: str) -> bool:
        """
        Check if a specific rule should be ignored.

        Args:
            rule_id: The rule ID to check (e.g., 'ST.001')

        Returns:
            True if the rule should be ignored, False otherwise
        """
        return rule_id in self.ignored_rules

    def should_exclude_path(self, file_path: str) -> bool:
        """
        Check if a file path should be excluded from linting.

        Args:
            file_path: The file path to check

        Returns:
            True if the path should be excluded, False otherwise
        """
        # Performance optimization: Normalize path once
        normalized_path = os.path.normpath(file_path)

        # Check include paths first (if specified, only these are included)
        if self.include_paths:
            included = False
            for pattern in self.include_paths:
                # Handle directory patterns
                if '/' not in pattern and '*' not in pattern:
                    # Simple directory name - check if path starts with this directory
                    if (normalized_path.startswith(pattern + '/') or
                        normalized_path.startswith('./' + pattern + '/') or
                        file_path.startswith(pattern + '/') or
                        file_path.startswith('./' + pattern + '/')):
                        included = True
                        break
                # Handle glob patterns and exact paths
                elif (fnmatch.fnmatch(normalized_path, pattern) or
                      fnmatch.fnmatch(file_path, pattern) or
                      normalized_path.startswith(pattern + '/') or
                      file_path.startswith(pattern + '/')):
                    included = True
                    break
            if not included:
                return True

        # Check exclude paths
        for pattern in self.exclude_paths:
            # Handle directory patterns (e.g., "examples" should match "examples/*")
            if '/' not in pattern and '*' not in pattern:
                # Simple directory name - check if path starts with this directory
                if normalized_path.startswith(pattern + '/') or normalized_path.startswith('./' + pattern + '/'):
                    return True
            # Handle glob patterns
            elif fnmatch.fnmatch(normalized_path, pattern) or fnmatch.fnmatch(file_path, pattern):
                return True

        return False

    def _extract_line_number(self, message: str) -> Tuple[Optional[int], str]:
        """
        Extract line number from error message if present.
        
        Args:
            message: Error message that may contain line number
            
        Returns:
            Tuple of (line_number, cleaned_message)
        """
        # Pattern to match "Line X:" at the beginning of the message
        line_pattern = r'^Line (\d+):\s*(.+)$'
        match = re.match(line_pattern, message)
        
        if match:
            line_num = int(match.group(1))
            cleaned_message = match.group(2)
            return line_num, cleaned_message
        else:
            return None, message

    def log_error(self, file_path: str, rule_id: str, message: str, line_number: Optional[int] = None):
        """
        Log an error found during linting with enhanced categorization.

        Args:
            file_path: Path to the file where the error was found
            rule_id: ID of the rule that was violated
            message: Detailed error message (should not contain line number)
            line_number: Optional line number where the error occurred
        """
        if not self.should_ignore_rule(rule_id):
            # If line_number is explicitly provided, use it directly
            if line_number is not None:
                error_line_number = line_number
                cleaned_message = message
            else:
                # Fallback: extract line number from message for backward compatibility
                error_line_number, cleaned_message = self._extract_line_number(message)
            
            # Create structured error record
            error_record = ErrorRecord(
                file_path=file_path,
                line_number=error_line_number,
                rule_id=rule_id,
                message=cleaned_message
            )
            
            self.errors.append(error_record)
            
            # Categorize error by rule system
            category = rule_id.split('.')[0] if '.' in rule_id else 'UNKNOWN'
            if category in self.errors_by_category:
                self.errors_by_category[category] += 1
            
            # Print error in detailed format for console output
            print(error_record.to_detailed_format())

    def log_warning(self, file_path: str, rule_id: str, message: str, line_number: Optional[int] = None):
        """
        Log a warning found during linting with enhanced categorization.

        Args:
            file_path: Path to the file where the warning was found
            rule_id: ID of the rule that generated the warning
            message: Detailed warning message (should not contain line number)
            line_number: Optional line number where the warning occurred
        """
        if not self.should_ignore_rule(rule_id):
            # If line_number is explicitly provided, use it directly
            if line_number is not None:
                warning_line_number = line_number
                cleaned_message = message
            else:
                # Fallback: extract line number from message for backward compatibility
                warning_line_number, cleaned_message = self._extract_line_number(message)
            
            # Create structured warning record
            warning_record = WarningRecord(
                file_path=file_path,
                line_number=warning_line_number,
                rule_id=rule_id,
                message=cleaned_message
            )
            
            self.warnings.append(warning_record)
            
            # Categorize warning by rule system
            category = rule_id.split('.')[0] if '.' in rule_id else 'UNKNOWN'
            if category in self.warnings_by_category:
                self.warnings_by_category[category] += 1
            
            # Print warning in detailed format for console output
            print(warning_record.to_detailed_format())

    def find_tf_files(self, directory: str) -> List[str]:
        """
        Find all Terraform files in the specified directory with enhanced filtering.

        Args:
            directory: Directory to search for Terraform files

        Returns:
            List of paths to Terraform files that should be processed
        """
        tf_files = []

        for root, dirs, files in os.walk(directory):
            # Skip hidden directories for performance
            dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('__pycache__')]

            for file in files:
                if file.endswith(('.tf', '.tfvars')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory)

                    # Apply path filtering
                    if not self.should_exclude_path(relative_path):
                        tf_files.append(file_path)

        return sorted(tf_files)

    def read_file_content(self, file_path: str) -> Optional[str]:
        """
        Read file content with enhanced error handling.

        Args:
            file_path: Path to the file to read

        Returns:
            File content as string, or None if reading failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                # Try with different encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                    print(f"Warning: File {file_path} read with latin-1 encoding")
                    return content
            except Exception as e:
                print(f"Error reading file {file_path} with fallback encoding: {e}")
                return None
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                return None

    def lint_file(self, file_path: str) -> bool:
        """
        Lint a single Terraform file using the unified rules management system.

        Args:
            file_path: Path to the file to lint

        Returns:
            True if no errors found, False otherwise
        """
        print(f"Linting file: {file_path}")

        # Read file content
        content = self.read_file_content(file_path)
        if content is None:
            return False

        # Update performance metrics
        self.files_processed += 1
        lines_count = len(content.split('\n'))
        self.total_lines_processed += lines_count

        try:
            # Create rule filter based on configuration
            rule_filter = {
                "systems": self.rule_categories,
                "excluded_rules": list(self.ignored_rules)
            }

            # Execute rules using unified system
            batch_summary = self.rules_manager.validate_file(
                file_path, 
                content, 
                self.log_error,
                rule_filter
            )

            # Store execution results for reporting
            self.execution_results.append(batch_summary)

            # Update violation counts by category - sync with actual error/warning counts
            for category in ["ST", "IO", "DC", "SC"]:
                # Calculate violations for this category as errors + warnings
                category_violations = self.errors_by_category[category] + self.warnings_by_category[category]
                self.violations_by_category[category] = category_violations

            return batch_summary.failed_rules == 0

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            traceback.print_exc()
            return False

    def lint_directory(self, directory: str) -> bool:
        """
        Lint all Terraform files in a directory using unified rules management.

        Args:
            directory: Directory to lint

        Returns:
            True if no errors found, False otherwise
        """
        print(f"Linting directory: {directory}")
        self.start_time = time.time()

        # Get files to check based on mode
        if self.changed_files_only:
            tf_files = self.get_changed_files(directory)
            if not tf_files:
                print("No changed Terraform files found")
                # Important: Set end_time even when no files are found
                self.end_time = time.time()
                return True
            print(f"Checking only changed files: {len(tf_files)} files")
        else:
            tf_files = self.find_tf_files(directory)
            if not tf_files:
                print("No .tf files found to check")
                # Important: Set end_time even when no files are found
                self.end_time = time.time()
                return True
            print(f"Found {len(tf_files)} .tf files to check")

        success = True
        for file_path in tf_files:
            if not self.lint_file(file_path):
                success = False

        self.end_time = time.time()
        return success

    def _generate_line_distribution_report(self) -> Dict[str, Any]:
        """
        Generate error/warning distribution report by line numbers.
        
        Returns:
            Dictionary containing line distribution statistics
        """
        line_stats = {
            "errors_by_line": {},
            "warnings_by_line": {},
            "errors_without_line": [],
            "warnings_without_line": [],
            "rule_distribution": {},
            "file_statistics": {}
        }
        
        # Analyze errors by line numbers
        for error in self.errors:
            if error.line_number:
                line_key = f"Line {error.line_number}"
                if line_key not in line_stats["errors_by_line"]:
                    line_stats["errors_by_line"][line_key] = []
                line_stats["errors_by_line"][line_key].append({
                    "file": os.path.basename(error.file_path),
                    "rule_id": error.rule_id,
                    "message": error.message
                })
                
                # Track rule distribution
                if error.rule_id not in line_stats["rule_distribution"]:
                    line_stats["rule_distribution"][error.rule_id] = {"count": 0, "lines": set()}
                line_stats["rule_distribution"][error.rule_id]["count"] += 1
                line_stats["rule_distribution"][error.rule_id]["lines"].add(error.line_number)
            else:
                # Track errors without line numbers
                line_stats["errors_without_line"].append({
                    "file": os.path.basename(error.file_path),
                    "rule_id": error.rule_id,
                    "message": error.message
                })
                
                # Track rule distribution for errors without line numbers
                if error.rule_id not in line_stats["rule_distribution"]:
                    line_stats["rule_distribution"][error.rule_id] = {"count": 0, "lines": set()}
                line_stats["rule_distribution"][error.rule_id]["count"] += 1
        
        # Analyze warnings by line numbers
        for warning in self.warnings:
            if warning.line_number:
                line_key = f"Line {warning.line_number}"
                if line_key not in line_stats["warnings_by_line"]:
                    line_stats["warnings_by_line"][line_key] = []
                line_stats["warnings_by_line"][line_key].append({
                    "file": os.path.basename(warning.file_path),
                    "rule_id": warning.rule_id,
                    "message": warning.message
                })
                
                # Track rule distribution for warnings
                if warning.rule_id not in line_stats["rule_distribution"]:
                    line_stats["rule_distribution"][warning.rule_id] = {"count": 0, "lines": set()}
                line_stats["rule_distribution"][warning.rule_id]["count"] += 1
                line_stats["rule_distribution"][warning.rule_id]["lines"].add(warning.line_number)
            else:
                # Track warnings without line numbers
                line_stats["warnings_without_line"].append({
                    "file": os.path.basename(warning.file_path),
                    "rule_id": warning.rule_id,
                    "message": warning.message
                })
                
                # Track rule distribution for warnings without line numbers
                if warning.rule_id not in line_stats["rule_distribution"]:
                    line_stats["rule_distribution"][warning.rule_id] = {"count": 0, "lines": set()}
                line_stats["rule_distribution"][warning.rule_id]["count"] += 1
        
        # Generate file-level statistics
        file_line_counts = {}
        for error in self.errors:
            file_name = os.path.basename(error.file_path)
            if file_name not in file_line_counts:
                file_line_counts[file_name] = {"errors": set(), "warnings": set(), "errors_without_line": 0, "warnings_without_line": 0}
            if error.line_number:
                file_line_counts[file_name]["errors"].add(error.line_number)
            else:
                file_line_counts[file_name]["errors_without_line"] += 1
        
        for warning in self.warnings:
            file_name = os.path.basename(warning.file_path)
            if file_name not in file_line_counts:
                file_line_counts[file_name] = {"errors": set(), "warnings": set(), "errors_without_line": 0, "warnings_without_line": 0}
            if warning.line_number:
                file_line_counts[file_name]["warnings"].add(warning.line_number)
            else:
                file_line_counts[file_name]["warnings_without_line"] += 1
        
        # Convert sets to sorted lists for JSON serialization
        for file_name, counts in file_line_counts.items():
            line_stats["file_statistics"][file_name] = {
                "error_lines": sorted(list(counts["errors"])),
                "warning_lines": sorted(list(counts["warnings"])),
                "total_affected_lines": len(counts["errors"] | counts["warnings"]),
                "errors_without_line_count": counts["errors_without_line"],
                "warnings_without_line_count": counts["warnings_without_line"]
            }
        
        # Convert rule distribution sets to lists for JSON serialization
        for rule_id, data in line_stats["rule_distribution"].items():
            line_stats["rule_distribution"][rule_id]["lines"] = sorted(list(data["lines"]))
        
        return line_stats

    def generate_report(self, output_file: str = "terraform-lint-report.txt", format: str = "text") -> LintReport:
        """
        Generate a comprehensive lint report with enhanced statistics.

        Args:
            output_file: Path to the output report file
            format: Report format ('text' or 'json')

        Returns:
            LintReport object with detailed statistics
        """
        # Calculate execution time
        execution_time = (self.end_time - self.start_time) if (self.start_time and self.end_time) else 0.0

        # Aggregate execution statistics
        total_rules_executed = sum(result.total_rules for result in self.execution_results)
        successful_rules = sum(result.successful_rules for result in self.execution_results)
        failed_rules = sum(result.failed_rules for result in self.execution_results)
        total_violations = sum(result.total_violations for result in self.execution_results)

        # Create performance metrics with improved handling of small execution times
        if execution_time > 0.0001:  # Only calculate rates if execution time is meaningful
            performance_metrics = {
                "files_per_second": self.files_processed / execution_time,
                "lines_per_second": self.total_lines_processed / execution_time,
                "rules_per_second": total_rules_executed / execution_time,
                "avg_lines_per_file": self.total_lines_processed // self.files_processed if self.files_processed > 0 else 0
            }
        else:
            # For very fast executions, set reasonable default values
            performance_metrics = {
                "files_per_second": 0.0,
                "lines_per_second": 0.0,
                "rules_per_second": 0.0,
                "avg_lines_per_file": self.total_lines_processed // self.files_processed if self.files_processed > 0 else 0
            }

        # Get rules summary
        rules_summary = self.rules_manager.get_rules_summary()

        # Calculate correct counts - use actual errors and warnings lists
        total_errors = len(self.errors)
        total_warnings = len(self.warnings)
        # Total violations should be the sum of errors and warnings from actual detection
        actual_total_violations = total_errors + total_warnings

        # Generate line distribution statistics
        line_distribution = self._generate_line_distribution_report()

        if format == "json":
            # Generate JSON report
            report_data = {
                "metadata": {
                    "generated": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "unified_rules_manager_version": "1.0.0",
                    "report_format": "json"
                },
                "summary": {
                    "total_errors": total_errors,
                    "total_warnings": total_warnings,
                    "total_violations": actual_total_violations,
                    "files_processed": self.files_processed,
                    "total_lines_processed": self.total_lines_processed,
                    "execution_time": execution_time
                },
                "rule_execution": {
                    "total_rules_executed": total_rules_executed,
                    "successful_rules": successful_rules,
                    "failed_rules": failed_rules,
                    "success_rate": (successful_rules/total_rules_executed*100) if total_rules_executed > 0 else 0
                },
                "violations_by_category": {
                    "ST": {
                        "violations": self.violations_by_category['ST'],
                        "errors": self.errors_by_category['ST'],
                        "warnings": self.warnings_by_category['ST']
                    },
                    "IO": {
                        "violations": self.violations_by_category['IO'],
                        "errors": self.errors_by_category['IO'],
                        "warnings": self.warnings_by_category['IO']
                    },
                    "DC": {
                        "violations": self.violations_by_category['DC'],
                        "errors": self.errors_by_category['DC'],
                        "warnings": self.warnings_by_category['DC']
                    },
                    "SC": {
                        "violations": self.violations_by_category['SC'],
                        "errors": self.errors_by_category['SC'],
                        "warnings": self.warnings_by_category['SC']
                    }
                },
                "line_distribution": line_distribution,
                "detailed_errors": [error.to_detailed_format() for error in self.errors],
                "detailed_warnings": [warning.to_detailed_format() for warning in self.warnings],
                "summary_errors": [error.to_summary_format() for error in self.errors],
                "summary_warnings": [warning.to_summary_format() for warning in self.warnings],
                "performance_metrics": performance_metrics,
                "rules_system": {
                    "total_available_rules": rules_summary['total_rules'],
                    "active_categories": self.rule_categories,
                    "ignored_rules": list(sorted(self.ignored_rules)) if self.ignored_rules else []
                }
            }

            # Write JSON report
            try:
                import json
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)
                print(f"JSON report saved to: {output_file}")
            except Exception as e:
                print(f"Error writing JSON report to {output_file}: {e}")

            # For JSON format, we don't need report_content for file writing,
            # but we still need it for the console output logic below
            report_content = ""

        else:
            # Generate text report (existing logic)
            report_lines = [
                "=" * 60,
                "TERRAFORM SCRIPTS LINT REPORT (UNIFIED SYSTEM)",
                "=" * 60,
                f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "=== SUMMARY ===",
                f"Total Errors: {total_errors}",
                f"Total Warnings: {total_warnings}",
                f"Total Violations: {actual_total_violations}",
                f"Files Processed: {self.files_processed}",
                f"Total Lines Processed: {self.total_lines_processed:,}",
                f"Execution Time: {execution_time:.2f} seconds",
                "",
                "=== RULE EXECUTION STATISTICS ===",
                f"Total Rules Executed: {total_rules_executed}",
                f"Successful Rule Executions: {successful_rules}",
                f"Failed Rule Executions: {failed_rules}",
                f"Success Rate: {(successful_rules/total_rules_executed*100):.1f}%" if total_rules_executed > 0 else "N/A",
                ""
            ]

            # Add category breakdown
            if any(count > 0 for count in self.violations_by_category.values()):
                report_lines.extend([
                    "=== VIOLATIONS BY CATEGORY ===",
                    f"ST (Style/Format): {self.violations_by_category['ST']} violations, {self.errors_by_category['ST']} errors, {self.warnings_by_category['ST']} warnings",
                    f"IO (Input/Output): {self.violations_by_category['IO']} violations, {self.errors_by_category['IO']} errors, {self.warnings_by_category['IO']} warnings",
                    f"DC (Documentation): {self.violations_by_category['DC']} violations, {self.errors_by_category['DC']} errors, {self.warnings_by_category['DC']} warnings",
                    f"SC (Security Code): {self.violations_by_category['SC']} violations, {self.errors_by_category['SC']} errors, {self.warnings_by_category['SC']} warnings",
                    ""
                ])

            # Add line distribution report
            if (line_distribution["errors_by_line"] or line_distribution["warnings_by_line"] or 
                line_distribution["errors_without_line"] or line_distribution["warnings_without_line"]):
                report_lines.extend([
                    "=== LINE DISTRIBUTION REPORT ===",
                    ""
                ])
                
                # Errors by line number
                if line_distribution["errors_by_line"]:
                    report_lines.append("ERRORS BY LINE NUMBER:")
                    for line_key in sorted(line_distribution["errors_by_line"].keys(), 
                                         key=lambda x: int(x.split()[1])):
                        errors = line_distribution["errors_by_line"][line_key]
                        report_lines.append(f"  {line_key}: {len(errors)} error(s)")
                        for error in errors:
                            report_lines.append(f"    └─ {error['file']} [{error['rule_id']}] {error['message']}")
                    report_lines.append("")
                
                # Errors without line numbers
                if line_distribution["errors_without_line"]:
                    report_lines.append("ERRORS WITHOUT LINE NUMBERS:")
                    # Group by rule ID for better organization
                    errors_by_rule = {}
                    for error in line_distribution["errors_without_line"]:
                        rule_id = error["rule_id"]
                        if rule_id not in errors_by_rule:
                            errors_by_rule[rule_id] = []
                        errors_by_rule[rule_id].append(error)
                    
                    for rule_id in sorted(errors_by_rule.keys()):
                        errors = errors_by_rule[rule_id]
                        report_lines.append(f"  {rule_id}: {len(errors)} error(s)")
                        for error in errors:
                            report_lines.append(f"    └─ {error['file']} {error['message']}")
                    report_lines.append("")
                
                # Warnings by line number
                if line_distribution["warnings_by_line"]:
                    report_lines.append("WARNINGS BY LINE NUMBER:")
                    for line_key in sorted(line_distribution["warnings_by_line"].keys(), 
                                         key=lambda x: int(x.split()[1])):
                        warnings = line_distribution["warnings_by_line"][line_key]
                        report_lines.append(f"  {line_key}: {len(warnings)} warning(s)")
                        for warning in warnings:
                            report_lines.append(f"    └─ {warning['file']} [{warning['rule_id']}] {warning['message']}")
                    report_lines.append("")
                
                # Warnings without line numbers
                if line_distribution["warnings_without_line"]:
                    report_lines.append("WARNINGS WITHOUT LINE NUMBERS:")
                    # Group by rule ID for better organization
                    warnings_by_rule = {}
                    for warning in line_distribution["warnings_without_line"]:
                        rule_id = warning["rule_id"]
                        if rule_id not in warnings_by_rule:
                            warnings_by_rule[rule_id] = []
                        warnings_by_rule[rule_id].append(warning)
                    
                    for rule_id in sorted(warnings_by_rule.keys()):
                        warnings = warnings_by_rule[rule_id]
                        report_lines.append(f"  {rule_id}: {len(warnings)} warning(s)")
                        for warning in warnings:
                            report_lines.append(f"    └─ {warning['file']} {warning['message']}")
                    report_lines.append("")
                
                # Rule distribution by affected lines
                if line_distribution["rule_distribution"]:
                    report_lines.append("RULE VIOLATIONS SUMMARY:")
                    for rule_id in sorted(line_distribution["rule_distribution"].keys()):
                        rule_data = line_distribution["rule_distribution"][rule_id]
                        if rule_data["lines"]:
                            lines_str = ", ".join(map(str, rule_data["lines"]))
                            report_lines.append(f"  {rule_id}: {rule_data['count']} violation(s) on lines [{lines_str}]")
                        else:
                            report_lines.append(f"  {rule_id}: {rule_data['count']} violation(s) (no specific line numbers)")
                    report_lines.append("")
                
                # File statistics
                if line_distribution["file_statistics"]:
                    report_lines.append("FILE STATISTICS (AFFECTED LINES):")
                    for file_name in sorted(line_distribution["file_statistics"].keys()):
                        file_stats = line_distribution["file_statistics"][file_name]
                        report_lines.append(f"  {file_name}:")
                        if file_stats["error_lines"]:
                            error_lines_str = ", ".join(map(str, file_stats["error_lines"]))
                            report_lines.append(f"    ├─ Error lines: [{error_lines_str}]")
                        if file_stats["errors_without_line_count"] > 0:
                            report_lines.append(f"    ├─ Errors without line numbers: {file_stats['errors_without_line_count']}")
                        if file_stats["warning_lines"]:
                            warning_lines_str = ", ".join(map(str, file_stats["warning_lines"]))
                            report_lines.append(f"    ├─ Warning lines: [{warning_lines_str}]")
                        if file_stats["warnings_without_line_count"] > 0:
                            report_lines.append(f"    ├─ Warnings without line numbers: {file_stats['warnings_without_line_count']}")
                        
                        total_issues = (len(file_stats["error_lines"]) + 
                                      file_stats["errors_without_line_count"] + 
                                      len(file_stats["warning_lines"]) + 
                                      file_stats["warnings_without_line_count"])
                        report_lines.append(f"    └─ Total issues: {total_issues} ({file_stats['total_affected_lines']} with line numbers)")
                    report_lines.append("")

            # Add detailed errors
            if self.errors:
                report_lines.extend([
                    "=== DETAILED ERRORS ===",
                    *[f"  {error.to_detailed_format()}" for error in self.errors],
                    ""
                ])

            # Add detailed warnings
            if self.warnings:
                report_lines.extend([
                    "=== DETAILED WARNINGS ===", 
                    *[f"  {warning.to_detailed_format()}" for warning in self.warnings],
                    ""
                ])

            # Add summary errors with file:line format
            if self.errors:
                report_lines.extend([
                    "=== SUMMARY ERRORS (FILE:LINE) ===",
                    *[f"  {error.to_summary_format()}" for error in self.errors],
                    ""
                ])

            # Add summary warnings with file:line format
            if self.warnings:
                report_lines.extend([
                    "=== SUMMARY WARNINGS (FILE:LINE) ===",
                    *[f"  {warning.to_summary_format()}" for warning in self.warnings],
                    ""
                ])

            # Add performance metrics
            if self.files_processed > 0:
                report_lines.extend([
                        "=== PERFORMANCE METRICS ===",
                        f"Average Lines per File: {performance_metrics['avg_lines_per_file']:,}",
                        f"Files per Second: {performance_metrics['files_per_second']:.1f}",
                        f"Lines per Second: {performance_metrics['lines_per_second']:.1f}",
                        f"Rules per Second: {performance_metrics['rules_per_second']:.1f}",
                        ""
                    ])

            # Add rules system information
            report_lines.extend([
                "=== RULES SYSTEM INFORMATION ===",
                f"Unified Rules Manager Version: 1.0.0",
                f"Total Available Rules: {rules_summary['total_rules']}",
                f"Active Rule Categories: {', '.join(self.rule_categories)}",
                f"Ignored Rules: {', '.join(sorted(self.ignored_rules)) if self.ignored_rules else 'None'}",
                ""
            ])

            report_content = '\n'.join(report_lines)

            # Write to file
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                print(f"Text report saved to: {output_file}")
            except Exception as e:
                print(f"Error writing text report to {output_file}: {e}")

        # Also print summary to console
        print("\n" + "=" * 60)
        print("LINT SUMMARY")
        print("=" * 60)
        print(f"Files: {self.files_processed}, Lines: {self.total_lines_processed:,}")
        print(f"Errors: {total_errors}, Warnings: {total_warnings}, Violations: {actual_total_violations}")
        print(f"Execution Time: {execution_time:.2f}s")
        
        # Add errors with line numbers to console summary
        if self.errors:
            print(f"\nErrors Found ({total_errors}):")
            for error in self.errors[:10]:  # Limit to first 10 errors for readability
                print(f"  {error.to_summary_format()}")
            if total_errors > 10:
                print(f"  ... and {total_errors - 10} more errors (see report file for details)")
        
        # Add warnings with line numbers to console summary
        if self.warnings:
            print(f"\nWarnings Found ({total_warnings}):")
            for warning in self.warnings[:5]:  # Limit to first 5 warnings for readability
                print(f"  {warning.to_summary_format()}")
            if total_warnings > 5:
                print(f"  ... and {total_warnings - 5} more warnings (see report file for details)")
        
        print("=" * 60)

        # Create and return LintReport object
        return LintReport(
            total_errors=total_errors,
            total_warnings=total_warnings,
            total_violations=actual_total_violations,
            files_processed=self.files_processed,
            total_lines_processed=self.total_lines_processed,
            execution_time=execution_time,
            rules_executed=total_rules_executed,
            successful_rules=successful_rules,
            failed_rules=failed_rules,
            errors_by_category=self.errors_by_category.copy(),
            warnings_by_category=self.warnings_by_category.copy(),
            performance_metrics=performance_metrics
        )

    def get_changed_files(self, directory: str) -> List[str]:
        """
        Get list of changed Terraform files using git diff with enhanced error handling.

        Args:
            directory: Directory to check for changes

        Returns:
            List of changed Terraform files
        """
        changed_files = []
        
        try:
            # Store original working directory
            original_cwd = os.getcwd()
            
            # Convert directory to absolute path
            if not os.path.isabs(directory):
                directory = os.path.abspath(directory)
            
            print(f"Looking for changed files in directory: {directory}")
            print(f"Current working directory: {original_cwd}")
            print(f"Target directory (relative): {os.path.relpath(directory, original_cwd)}")
            
            # Check if we're in a git repository
            try:
                subprocess.run(['git', 'rev-parse', '--git-dir'], 
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                print("Confirmed we're in a git repository")
            except subprocess.CalledProcessError:
                print("Not in a git repository, cannot use changed-files-only mode")
                return []
            
            # Get changed files from git
            git_commands = []
            
            # Try different git diff strategies with better fallback
            if self.base_ref:
                base_ref = self.base_ref
                git_commands.extend([
                    f"git diff --name-only {base_ref}...HEAD",
                    f"git diff --name-only {base_ref} HEAD",
                    f"git diff --name-only {base_ref}",
                    f"git diff --name-only origin/main...HEAD",
                    f"git diff --name-only main...HEAD",
                    f"git diff --name-only origin/master...HEAD"
                ])
            else:
                git_commands.extend([
                    "git diff --name-only HEAD~1",
                    "git diff --name-only --cached",
                    "git ls-files --others --exclude-standard"
                ])
            
            all_changed_files = []
            # Try each git command until one succeeds
            for cmd in git_commands:
                try:
                    print(f"Trying git command: {cmd}")
                    # Use stdout=subprocess.PIPE, stderr=subprocess.PIPE for Python 3.6 compatibility
                    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
                    
                    if result.stdout.strip():
                        files = result.stdout.strip().split('\n')
                        print(f"Git command found {len(files)} changed files")
                        all_changed_files = files
                        break
                        
                except subprocess.CalledProcessError as e:
                    print(f"Git command failed: {cmd}")
                    print(f"Error: {e.stderr}")
                    continue
            
            if not all_changed_files:
                print("No changed files found by any git command")
                return []
            
            print(f"All changed files from git: {all_changed_files}")
            
            # Process each changed file
            for file in all_changed_files:
                file = file.strip()
                if not file:
                    continue
                    
                print(f"Processing file: {file}")
                
                # Only process Terraform files
                if not file.endswith(('.tf', '.tfvars')):
                    print(f"  Skipping non-Terraform file: {file}")
                    continue
                
                # Convert to absolute path from git root
                abs_file_path = os.path.abspath(file)
                print(f"  Absolute path: {abs_file_path}")
                
                # Check if file exists
                if not os.path.exists(abs_file_path):
                    print(f"  File does not exist: {abs_file_path}")
                    continue
                
                # Check if file is within or under target directory
                target_rel_path = os.path.relpath(directory, original_cwd)
                file_rel_path = os.path.relpath(abs_file_path, original_cwd)
                
                print(f"  Target directory (relative): {target_rel_path}")
                print(f"  File path (relative): {file_rel_path}")
                
                # Check if file is in target directory or subdirectory
                is_in_target = (
                    file_rel_path.startswith(target_rel_path + '/') or  # File is in subdirectory
                    file_rel_path == target_rel_path or                # File is the target (unlikely for .tf)
                    (target_rel_path == '.' and not '/' in file_rel_path) or  # Root directory, file in root
                    abs_file_path.startswith(directory + '/')          # Absolute path check
                )
                
                print(f"  Is in target directory: {is_in_target}")
                
                if is_in_target:
                    # Apply exclude path filtering
                    relative_path_for_filtering = os.path.relpath(abs_file_path, directory)
                    if not self.should_exclude_path(relative_path_for_filtering):
                        print(f"  ✅ Adding file: {abs_file_path}")
                        changed_files.append(abs_file_path)
                    else:
                        print(f"  ❌ Excluded by path filter: {relative_path_for_filtering}")
                else:
                    print(f"  ❌ Not in target directory")
            
            print(f"Final changed files list: {changed_files}")
            
            if not changed_files:
                print("No changed Terraform files found in target directory")
                
        except Exception as e:
            print(f"Error getting changed files: {e}")
            traceback.print_exc()
        
        return changed_files


def main():
    """Enhanced main entry point with unified rules management system support."""
    parser = argparse.ArgumentParser(
        description='Enhanced Terraform Scripts Lint Tool - Unified Rules Management System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Enhanced Features:
  - Unified rules management system with centralized coordination
  - Advanced performance monitoring and detailed analytics
  - Flexible rule filtering by category and severity
  - Comprehensive reporting with multiple output formats
  - Enhanced GitHub Actions integration

Examples:
  # Check current directory with all rules
  python3 terraform_lint.py

  # Check specific directory with performance monitoring
  python3 terraform_lint.py --directory ./infrastructure

  # Ignore specific rules and categories
  python3 terraform_lint.py --ignore-rules "ST.001,ST.003" --categories "ST,IO"

  # Include only specific paths with detailed reporting
  python3 terraform_lint.py --include-paths "modules/vpc,modules/compute"

  # Check only changed files with custom base reference
  python3 terraform_lint.py --changed-files-only --base-ref origin/main

  # Complex filtering with performance optimization
  python3 terraform_lint.py --directory ./prod --ignore-rules "ST.001" --exclude-paths "*.backup,test/*"

Rule Categories:
  ST (Style/Format): Code formatting and style rules
  IO (Input/Output): Variable and output definition rules  
  DC (Documentation/Comments): Comment and documentation rules
  SC (Security Code): Security and safety validation rules

Available Rules:
{chr(10).join(f"  {rule_id}: {info.get('name', 'Unknown rule')}" 
               for rule_id, info in [(rule_id, get_unified_rules_summary().get('system_summaries', {}).get(rule_id.split('.')[0], {}).get('rules', {}).get(rule_id, {})) 
                                   for rule_id in sorted(get_all_available_rules())] if info)}

System Information:
  Unified Rules Manager: v1.0.0
  Total Available Rules: {len(get_all_available_rules())}
  Rule Systems: ST, IO, DC, SC
        """
    )

    # Positional argument for backward compatibility (deprecated)
    parser.add_argument('target_dir', nargs='?',
                       help='Target directory to check (deprecated, use --directory instead)')

    # Main options
    parser.add_argument('-d', '--directory', default='.',
                       help='Target directory to check (default: current directory)')

    parser.add_argument('--ignore-rules',
                       help='Comma-separated list of rule IDs to ignore (e.g., ST.001,DC.001)')

    parser.add_argument('--categories',
                       help='Comma-separated list of rule categories to execute (ST,IO,DC,SC). Default: all categories')

    parser.add_argument('--include-paths',
                       help='Comma-separated list of paths to include (e.g., ./src,./modules)')

    parser.add_argument('--exclude-paths',
                       help='Comma-separated list of path patterns to exclude (e.g., examples/*,test/*)')

    parser.add_argument('--changed-files-only', action='store_true',
                       help='If set, only check files changed in current commit/PR')

    parser.add_argument('--base-ref',
                       help='Base reference for git diff (e.g., origin/main, HEAD~1)')

    parser.add_argument('--report-format', choices=['text', 'json', 'both'], default='text',
                       help='Output report format (default: text)')

    parser.add_argument('--performance-monitoring', action='store_true', default=True,
                       help='Enable detailed performance monitoring (default: enabled)')

    args = parser.parse_args()

    # Handle deprecated positional argument
    if args.target_dir:
        print("Warning: Positional argument is deprecated. Use --directory instead.")
        target_directory = args.target_dir
    else:
        target_directory = args.directory

    # Parse ignored rules
    ignored_rules = set()
    if args.ignore_rules:
        ignored_rules = set(rule.strip() for rule in args.ignore_rules.split(','))
        print(f"Ignoring rules: {', '.join(sorted(ignored_rules))}")

    # Parse rule categories
    rule_categories = ["ST", "IO", "DC", "SC"]  # Default to all categories
    if args.categories:
        rule_categories = [cat.strip().upper() for cat in args.categories.split(',')]
        print(f"Active categories: {', '.join(rule_categories)}")

    # Parse include paths
    include_paths = []
    if args.include_paths:
        include_paths = [path.strip() for path in args.include_paths.split(',')]
        print(f"Including paths: {', '.join(include_paths)}")

    # Parse exclude paths
    exclude_paths = []
    if args.exclude_paths:
        exclude_paths = [path.strip() for path in args.exclude_paths.split(',')]
        print(f"Excluding paths: {', '.join(exclude_paths)}")

    # Initialize enhanced linter
    linter = TerraformLinter(
        ignored_rules=ignored_rules,
        include_paths=include_paths,
        exclude_paths=exclude_paths,
        changed_files_only=args.changed_files_only,
        base_ref=args.base_ref,
        rule_categories=rule_categories
    )

    print(f"Starting enhanced Terraform lint check in: {target_directory}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")

    # Validate target directory
    if not os.path.exists(target_directory):
        print(f"Error: Directory '{target_directory}' does not exist")
        sys.exit(1)

    if not os.path.isdir(target_directory):
        print(f"Error: '{target_directory}' is not a directory")
        sys.exit(1)

    # Run linting with performance monitoring
    success = linter.lint_directory(target_directory)

    # Generate comprehensive report based on format
    if args.report_format == 'json':
        output_file = "terraform-lint-report.json"
        lint_report = linter.generate_report(output_file=output_file, format='json')
    elif args.report_format == 'both':
        # Generate both text and JSON reports
        text_output = "terraform-lint-report.txt"
        json_output = "terraform-lint-report.json"
        lint_report = linter.generate_report(output_file=text_output, format='text')
        linter.generate_report(output_file=json_output, format='json')
    else:
        output_file = "terraform-lint-report.txt"
        lint_report = linter.generate_report(output_file=output_file, format='text')

    # Enhanced exit code logic to distinguish different scenarios
    if lint_report.total_errors > 0:
        # Errors found - fail with exit code 1
        exit_code = 1
        print(f"Enhanced lint check completed with exit code: {exit_code} (errors found)")
    elif lint_report.files_processed == 0 and args.changed_files_only:
        # Changed-files-only mode with no files to process - exit code 2
        exit_code = 2
        print(f"Enhanced lint check completed with exit code: {exit_code} (no files to check in changed-files-only mode)")
    elif lint_report.files_processed == 0:
        # No files found in general - exit code 2
        exit_code = 2
        print(f"Enhanced lint check completed with exit code: {exit_code} (no files found)")
    else:
        # Success - files processed without errors
        exit_code = 0
        print(f"Enhanced lint check completed with exit code: {exit_code} (success)")
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
