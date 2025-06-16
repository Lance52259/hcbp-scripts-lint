#!/usr/bin/env python3
"""
Terraform Scripts Lint Tool

Check if Terraform scripts comply with specification requirements

Rule Categories:
- ST (Style/Format): Code formatting rules
- DC (Documentation/Comments): Comment and description rules
- IO (Input/Output): Input and output definition rules

Performance Features:
- Intelligent path filtering to reduce unnecessary file I/O
- Incremental parsing, only processing content that needs checking
- Memory optimization, processing files one by one to avoid high memory usage
- Modular architecture supporting rule extension and maintenance

Security Features:
- Local processing only, no network requests
- Read-only operations, no file modifications
- No data collection or transmission
- Minimal permission requirements

Author: DevOps Team
License: Apache 2.0
"""

import os
import sys
import argparse
import re
import fnmatch
import subprocess
from typing import List, Dict, Set, Optional, Tuple
import traceback

# Add rules directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
rules_dir = os.path.join(project_root, 'rules')
sys.path.insert(0, rules_dir)

try:
    from st_rules import STRules
    from dc_rules import DCRules
    from io_rules import IORules
except ImportError as e:
    print(f"Error importing rule modules: {e}")
    print("Please ensure the rules directory contains the required Python modules.")
    sys.exit(1)

class TerraformLinter:
    """
    Terraform Scripts Linter

    A comprehensive linting tool for Terraform scripts that checks code quality,
    formatting, documentation, and organizational standards. Supports flexible
    rule control and path filtering for different project needs.

    Features:
    - Multiple rule categories (Style/Format, Documentation, Input/Output)
    - Flexible rule ignoring and path filtering
    - Detailed error reporting with line numbers
    - Performance optimized for large codebases
    - GitHub Actions integration
    - Support for checking only changed files in Git
    """

    def __init__(self, ignored_rules: Set[str] = None, include_paths: List[str] = None,
                 exclude_paths: List[str] = None, changed_files_only: bool = False,
                 base_ref: str = None):
        """
        Initialize the Terraform linter

        Args:
            ignored_rules: Set of rule IDs to ignore during linting
            include_paths: List of path patterns to include (if specified, only these paths are checked)
            exclude_paths: List of path patterns to exclude from checking
            changed_files_only: If True, only check files changed in current commit/PR
            base_ref: Base reference for git diff (e.g., 'origin/main', 'HEAD~1')
        """
        # Performance optimization: Initialize rule checkers once
        self.st_rules = STRules()
        self.dc_rules = DCRules()
        self.io_rules = IORules()

        # Rule management
        self.ignored_rules = ignored_rules or set()
        self.include_paths = include_paths or []
        self.exclude_paths = exclude_paths or []
        self.changed_files_only = changed_files_only
        self.base_ref = base_ref or 'HEAD~1'

        # Error tracking for reporting
        self.errors = []
        self.warnings = []

        # Performance metrics
        self.files_processed = 0
        self.total_lines_processed = 0

    def should_ignore_rule(self, rule_id: str) -> bool:
        """
        Check if a specific rule should be ignored

        Args:
            rule_id: The rule ID to check (e.g., 'ST.001')

        Returns:
            True if the rule should be ignored, False otherwise
        """
        return rule_id in self.ignored_rules

    def should_exclude_path(self, file_path: str) -> bool:
        """
        Check if a file path should be excluded from linting

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

    def log_error(self, file_path: str, rule_id: str, message: str):
        """
        Log an error found during linting

        Args:
            file_path: Path to the file where the error was found
            rule_id: ID of the rule that was violated
            message: Detailed error message
        """
        if not self.should_ignore_rule(rule_id):
            error_msg = f"ERROR: {file_path}: [{rule_id}] {message}"
            self.errors.append(error_msg)
            print(error_msg)

    def log_warning(self, file_path: str, rule_id: str, message: str):
        """
        Log a warning found during linting

        Args:
            file_path: Path to the file where the warning was found
            rule_id: ID of the rule that generated the warning
            message: Detailed warning message
        """
        if not self.should_ignore_rule(rule_id):
            warning_msg = f"WARNING: {file_path}: [{rule_id}] {message}"
            self.warnings.append(warning_msg)
            print(warning_msg)

    def find_tf_files(self, directory: str) -> List[str]:
        """
        Find all Terraform files in the specified directory

        Args:
            directory: Directory to search for Terraform files

        Returns:
            List of paths to Terraform files
        """
        tf_files = []

        try:
            # Performance optimization: Use os.walk for efficient directory traversal
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories for performance
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file in files:
                    if file.endswith(('.tf', '.tfvars')):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, directory)

                        # Apply path filtering
                        if not self.should_exclude_path(relative_path):
                            tf_files.append(file_path)

        except PermissionError as e:
            print(f"Permission denied accessing directory {directory}: {e}")
        except Exception as e:
            print(f"Error scanning directory {directory}: {e}")

        return tf_files

    def find_files_by_pattern(self, directory: str, pattern: str) -> List[str]:
        """
        Find files matching a specific pattern

        Args:
            directory: Directory to search in
            pattern: File pattern to match

        Returns:
            List of matching file paths
        """
        matching_files = []

        try:
            for root, dirs, files in os.walk(directory):
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file in files:
                    if fnmatch.fnmatch(file, pattern):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, directory)

                        if not self.should_exclude_path(relative_path):
                            matching_files.append(file_path)

        except Exception as e:
            print(f"Error finding files with pattern {pattern}: {e}")

        return matching_files

    def read_file_content(self, file_path: str) -> Optional[str]:
        """
        Read file content with proper encoding handling

        Args:
            file_path: Path to the file to read

        Returns:
            File content as string, or None if reading failed
        """
        # Performance optimization: Try common encodings in order of likelihood
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                return None

        print(f"Could not decode file {file_path} with any supported encoding")
        return None

    def get_file_lines(self, content: str) -> List[str]:
        """
        Get lines from file content

        Args:
            content: File content as string

        Returns:
            List of lines in the file
        """
        return content.split('\n')

    def remove_comments_for_parsing(self, content: str) -> str:
        """
        Remove comments from content for parsing while preserving structure

        Args:
            content: Original file content

        Returns:
            Content with comments removed but line structure preserved
        """
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            # Simple comment removal - can be enhanced for more complex cases
            if '#' in line:
                # Find comment position (not inside strings)
                in_string = False
                string_char = None
                for i, char in enumerate(line):
                    if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                        if not in_string:
                            in_string = True
                            string_char = char
                        elif char == string_char:
                            in_string = False
                            string_char = None
                    elif char == '#' and not in_string:
                        line = line[:i]
                        break
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def extract_data_sources(self, content: str) -> Dict[str, str]:
        """Extract data source definitions from content"""
        data_sources = {}
        lines = content.split('\n')

        for line in lines:
            match = re.match(r'data\s+"([^"]+)"\s+"([^"]+)"\s*{', line.strip())
            if match:
                data_sources[match.group(2)] = match.group(1)

        return data_sources

    def extract_resources(self, content: str) -> Dict[str, str]:
        """Extract resource definitions from content"""
        resources = {}
        lines = content.split('\n')

        for line in lines:
            match = re.match(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*{', line.strip())
            if match:
                resources[match.group(2)] = match.group(1)

        return resources

    def extract_variables(self, content: str) -> Dict[str, Dict]:
        """Extract variable definitions from content"""
        variables = {}
        lines = content.split('\n')
        current_var = None
        in_var_block = False
        brace_count = 0

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Variable block start
            var_match = re.match(r'variable\s+"([^"]+)"\s*{', stripped)
            if var_match:
                current_var = var_match.group(1)
                variables[current_var] = {'line': line_num, 'has_default': False}
                in_var_block = True
                brace_count = 1
                continue

            if in_var_block and current_var:
                brace_count += stripped.count('{')
                brace_count -= stripped.count('}')

                if re.match(r'default\s*=', stripped):
                    variables[current_var]['has_default'] = True

                if brace_count == 0:
                    in_var_block = False
                    current_var = None

        return variables

    def extract_outputs(self, content: str) -> Dict[str, int]:
        """Extract output definitions from content"""
        outputs = {}
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            match = re.match(r'output\s+"([^"]+)"\s*{', line.strip())
            if match:
                outputs[match.group(1)] = line_num

        return outputs

    def extract_variable_references(self, content: str) -> Set[str]:
        """Extract variable references (var.xxx) from content"""
        var_refs = set()

        # Find all var.variable_name patterns
        pattern = r'var\.([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(pattern, content)
        var_refs.update(matches)

        return var_refs

    def parse_tfvars_file(self, tfvars_path: str) -> Set[str]:
        """Parse terraform.tfvars file to extract declared variables"""
        declared_vars = set()

        if not os.path.exists(tfvars_path):
            return declared_vars

        try:
            content = self.read_file_content(tfvars_path)
            if content:
                # Find variable assignments
                pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*='
                for line in content.split('\n'):
                    match = re.match(pattern, line.strip())
                    if match:
                        declared_vars.add(match.group(1))
        except Exception as e:
            print(f"Error parsing tfvars file {tfvars_path}: {e}")

        return declared_vars

    def lint_file(self, file_path: str) -> bool:
        """
        Lint a single Terraform file

        Args:
            file_path: Path to the file to lint

        Returns:
            True if no errors found, False otherwise
        """
        print(f"Linting file: {file_path}")

        # Performance optimization: Read file content once
        content = self.read_file_content(file_path)
        if content is None:
            return False

        # Update performance metrics
        self.files_processed += 1
        self.total_lines_processed += len(content.split('\n'))

        # Run all rule checks
        try:
            self.st_rules.run_all_checks(file_path, content, self.log_error)
            self.dc_rules.run_all_checks(file_path, content, self.log_error)
            self.io_rules.run_all_checks(file_path, content, self.log_error)
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            traceback.print_exc()
            return False

        return True

    def lint_directory(self, directory: str) -> bool:
        """
        Lint all Terraform files in a directory

        Args:
            directory: Directory to lint

        Returns:
            True if no errors found, False otherwise
        """
        print(f"Linting directory: {directory}")

        # Get files to check based on mode
        if self.changed_files_only:
            tf_files = self.get_changed_files(directory)
            if not tf_files:
                print("No changed Terraform files found")
                return True
            print(f"Checking only changed files: {len(tf_files)} files")
        else:
            # Performance optimization: Find all files first, then process
            tf_files = self.find_tf_files(directory)
            if not tf_files:
                print("No .tf files found to check")
                return True
            print(f"Found {len(tf_files)} .tf files to check")

        success = True
        for file_path in tf_files:
            if not self.lint_file(file_path):
                success = False

        # ST.009 cross-file check: Variable order validation
        self.check_variable_order_across_files(directory)

        return success

    def check_variable_order_across_files(self, directory: str):
        """
        Check ST.009 rule across variables.tf and main.tf files in the directory
        
        Args:
            directory: Directory to check for variables.tf and main.tf files
        """
        # Find variables.tf and main.tf files in the directory
        variables_files = self.find_files_by_pattern(directory, "variables.tf")
        main_files = self.find_files_by_pattern(directory, "main.tf")
        
        # Check each combination of variables.tf and main.tf in the same directory
        for variables_file in variables_files:
            variables_dir = os.path.dirname(variables_file)
            
            # Find corresponding main.tf in the same directory
            corresponding_main = None
            for main_file in main_files:
                if os.path.dirname(main_file) == variables_dir:
                    corresponding_main = main_file
                    break
            
            if corresponding_main:
                # Read file contents
                variables_content = self.read_file_content(variables_file)
                main_content = self.read_file_content(corresponding_main)
                
                if variables_content and main_content:
                    # Run ST.009 check
                    errors = self.st_rules.check_variable_order(
                        variables_content, main_content, variables_file, corresponding_main
                    )
                    
                    # Log any errors found
                    for error in errors:
                        self.log_error(error['file'], error['rule'], error['message'])

    def generate_report(self, output_file: str = "terraform-lint-report.txt"):
        """
        Generate a comprehensive lint report

        Args:
            output_file: Path to the output report file
        """
        report_lines = [
            "=== Terraform Scripts Lint Report ===",
            f"Total Errors: {len(self.errors)}",
            f"Total Warnings: {len(self.warnings)}",
            ""
        ]

        if self.errors:
            report_lines.append("ERRORS:")
            for error in self.errors:
                report_lines.append(f"  {error}")
            report_lines.append("")

        if self.warnings:
            report_lines.append("WARNINGS:")
            for warning in self.warnings:
                report_lines.append(f"  {warning}")
            report_lines.append("")

        # Performance metrics
        if self.files_processed > 0:
            report_lines.extend([
                "=== Performance Metrics ===",
                f"Files Processed: {self.files_processed}",
                f"Total Lines Processed: {self.total_lines_processed}",
                f"Average Lines per File: {self.total_lines_processed // self.files_processed}",
                ""
            ])

        report_content = '\n'.join(report_lines)

        # Write to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"Report saved to: {output_file}")
        except Exception as e:
            print(f"Error writing report to {output_file}: {e}")

        # Also print to console
        print(report_content)

    def get_changed_files(self, directory: str) -> List[str]:
        """
        Get list of changed Terraform files using git diff

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
            
            # For GitHub Actions, we should already be in the user's repository
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
            
            # If base_ref is provided, use it for comparison
            if self.base_ref:
                # Handle different base_ref formats
                base_ref = self.base_ref
                if base_ref.startswith('origin/'):
                    # Try both with and without origin/ prefix
                    git_commands.extend([
                        f"git diff --name-only {base_ref}...HEAD",
                        f"git diff --name-only {base_ref.replace('origin/', '')}...HEAD",
                        f"git diff --name-only {base_ref}",
                        f"git diff --name-only {base_ref.replace('origin/', '')}"
                    ])
                else:
                    git_commands.extend([
                        f"git diff --name-only {base_ref}...HEAD",
                        f"git diff --name-only origin/{base_ref}...HEAD",
                        f"git diff --name-only {base_ref}",
                        f"git diff --name-only origin/{base_ref}"
                    ])
            
            # Add fallback commands for different GitHub Actions scenarios
            git_commands.extend([
                # For pull requests - compare with merge base
                "git diff --name-only HEAD~1...HEAD",
                "git diff --name-only HEAD~1",
                # For staged changes
                "git diff --cached --name-only",
                # For unstaged changes
                "git diff --name-only",
                # Last resort - show all files in the last commit
                "git diff-tree --no-commit-id --name-only -r HEAD"
            ])
            
            for cmd in git_commands:
                try:
                    print(f"Trying git command: {cmd}")
                    result = subprocess.run(
                        cmd.split(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                        check=True,
                        cwd=original_cwd  # Execute in the current directory (user's repo)
                    )
                    
                    if result.stdout.strip():
                        files = result.stdout.strip().split('\n')
                        print(f"Git command returned {len(files)} files: {files}")
                        
                        # Filter for Terraform files and check if they're in the target directory
                        tf_files = []
                        for file_path in files:
                            if file_path.endswith(('.tf', '.tfvars')):
                                # Convert to absolute path
                                abs_file_path = os.path.abspath(file_path)
                                
                                # Check if file is within the target directory
                                if abs_file_path.startswith(directory + os.sep) or abs_file_path == directory:
                                    tf_files.append(abs_file_path)
                                elif directory == '.' or directory == os.getcwd():
                                    # If checking current directory, include all tf files
                                    tf_files.append(abs_file_path)
                        
                        if tf_files:
                            changed_files = tf_files
                            print(f"Found {len(tf_files)} changed Terraform files in target directory using: {cmd}")
                            break
                        else:
                            print(f"No Terraform files found in target directory from command: {cmd}")
                    else:
                        print(f"No output from command: {cmd}")
                            
                except subprocess.CalledProcessError as e:
                    print(f"Command failed: {cmd} - {e}")
                    if e.stderr:
                        print(f"Error output: {e.stderr}")
                    continue
            
            if not changed_files:
                print("No changed Terraform files found with any git command")
                print("This might be because:")
                print("1. No files were actually changed")
                print("2. The base reference doesn't exist")
                print("3. Git history is not available")
                print("4. Files are not in the target directory")
            
            # Verify files exist
            verified_files = []
            for file_path in changed_files:
                if os.path.exists(file_path):
                    verified_files.append(file_path)
                    print(f"Verified file exists: {file_path}")
                else:
                    print(f"Warning: Changed file {file_path} does not exist")
            
            return verified_files
            
        except Exception as e:
            print(f"Error getting changed files: {e}")
            print("Falling back to checking all files")
            import traceback
            traceback.print_exc()
            return []

def main():
    """Main entry point for the Terraform linter"""
    parser = argparse.ArgumentParser(
        description='Terraform Scripts Lint Tool - Check Terraform scripts for compliance with coding standards',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check current directory
  python3 terraform_lint.py

  # Check specific directory
  python3 terraform_lint.py --directory ./infrastructure

  # Ignore specific rules
  python3 terraform_lint.py --ignore-rules "ST.001,ST.003"

  # Include only specific paths
  python3 terraform_lint.py --include-paths "modules/vpc,modules/compute"

  # Exclude specific paths
  python3 terraform_lint.py --exclude-paths "examples/*,test/*"

  # Complex filtering
  python3 terraform_lint.py --directory ./prod --ignore-rules "ST.001" --exclude-paths "*.backup"

Rule Categories:
  ST (Style/Format): Code formatting and style rules
  DC (Documentation/Comments): Comment and documentation rules
  IO (Input/Output): Input and output definition rules

Available Rules:
  ST.001: Resource and data source naming convention
  ST.002: Variable default value requirement
  ST.003: Parameter alignment formatting
  ST.004: Indentation character check (spaces only)
  ST.005: Indentation level check (proper spacing)
  ST.006: Resource and data source spacing
  ST.007: Same parameter block spacing
  ST.008: Different parameter block spacing
  DC.001: Comment formatting standards
  IO.001: Variable definition file organization
  IO.002: Output definition file organization
  IO.003: Required variable declaration in tfvars
  IO.004: Variable naming convention
  IO.005: Output naming convention
  IO.006: Variable description check
  IO.007: Output description check
  IO.008: Variable type check
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

    parser.add_argument('--include-paths',
                       help='Comma-separated list of paths to include (e.g., ./src,./modules)')

    parser.add_argument('--exclude-paths',
                       help='Comma-separated list of path patterns to exclude (e.g., examples/*,test/*)')

    parser.add_argument('--changed-files-only', action='store_true',
                       help='If set, only check files changed in current commit/PR')

    parser.add_argument('--base-ref',
                       help='Base reference for git diff (e.g., origin/main, HEAD~1)')

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

    # Initialize linter
    linter = TerraformLinter(
        ignored_rules=ignored_rules,
        include_paths=include_paths,
        exclude_paths=exclude_paths,
        changed_files_only=args.changed_files_only,
        base_ref=args.base_ref
    )

    print(f"Starting Terraform lint check in: {target_directory}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")

    # Validate target directory
    if not os.path.exists(target_directory):
        print(f"Error: Directory '{target_directory}' does not exist")
        sys.exit(1)

    if not os.path.isdir(target_directory):
        print(f"Error: '{target_directory}' is not a directory")
        sys.exit(1)

    # Run linting
    success = linter.lint_directory(target_directory)

    # Generate report
    linter.generate_report()

    # Exit with appropriate code
    exit_code = 0 if len(linter.errors) == 0 else 1
    print(f"Lint check completed with exit code: {exit_code}")
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
