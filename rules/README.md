# Terraform Lint Rules

This directory contains implementation code and detailed descriptions for all Terraform script checking rules.

## Directory Structure

```
rules/
├── README.md          # This file, overall rule documentation and usage guide
├── introduction.md    # Detailed introduction and examples for all rules
│                      # - Rule categories and purposes
│                      # - Detailed rule descriptions
│                      # - Correct and incorrect examples
│                      # - Best practices and guidelines
├── st_rules.py        # ST (Style/Format) code formatting rules implementation
│                      # - Resource naming conventions
│                      # - Variable default values
│                      # - Parameter alignment
├── dc_rules.py        # DC (Documentation/Comments) comment and description rules implementation
│                      # - Comment format checking
│                      # - Description completeness
└── io_rules.py        # IO (Input/Output) input and output definition rules implementation
                       # - File location validation
                       # - Required parameter checking
                       # - Output definition validation
```

## Rule Categories

### ST (Style/Format) - Code Formatting Rules
- **ST.001**: Resource and data source naming convention check
  - Ensures consistent naming patterns for resources and data sources
  - Improves code readability and maintainability
  - Facilitates resource tracking and management

- **ST.002**: Variable default value check
  - Ensures all variables have appropriate default values
  - Improves module usability and flexibility
  - Reduces configuration complexity for users

- **ST.003**: Parameter alignment check
  - Maintains consistent parameter formatting
  - Improves code readability and aesthetics
  - Follows Terraform community formatting standards

### DC (Documentation/Comments) - Comment and Description Rules
- **DC.001**: Comment format check
  - Ensures consistent comment formatting
  - Improves code documentation quality
  - Facilitates automated documentation processing

### IO (Input/Output) - Input and Output Definition Rules
- **IO.001**: Variable definition file location check
  - Ensures variables are defined in the correct file
  - Maintains project structure consistency
  - Improves code organization and maintainability

- **IO.002**: Output definition file location check
  - Ensures outputs are defined in the correct file
  - Maintains clear module interfaces
  - Improves output management and documentation

- **IO.003**: Required parameter declaration check
  - Ensures all required parameters are properly declared
  - Prevents runtime errors from missing parameters
  - Improves module reliability and usability

- **IO.004**: Variable naming convention check
  - Ensures variables follow consistent naming patterns
  - Improves code readability and maintainability
  - Prevents naming conflicts and confusion

- **IO.005**: Output naming convention check
  - Ensures outputs follow consistent naming patterns
  - Improves module interface clarity
  - Maintains consistent output naming standards

## Rule Implementation Architecture

Each rule type is implemented as an independent Python class:

- `STRules`: Handles all ST type rules
- `DCRules`: Handles all DC type rules
- `IORules`: Handles all IO type rules

Each class provides the following standard interface:

- `run_all_checks(file_path, content, log_error_func)`: Run all checks for this type
- `get_rule_info(rule_id)`: Get information for a specific rule
- `get_all_rules()`: Get all rule information for this type

## Usage

```python
from rules.st_rules import STRules
from rules.dc_rules import DCRules
from rules.io_rules import IORules

# Create rule checker instances
st_checker = STRules()
dc_checker = DCRules()
io_checker = IORules()

# Error logging function
def log_error(file_path, rule_id, message):
    print(f"ERROR: {file_path}: [{rule_id}] {message}")

# Run all checks
st_checker.run_all_checks(file_path, content, log_error)
dc_checker.run_all_checks(file_path, content, log_error)
io_checker.run_all_checks(file_path, content, log_error)
```

## Adding New Rules

To add new rules, follow these steps:

1. Determine rule category (ST/DC/IO)
2. Add rule implementation in the corresponding rule file
3. Update rule metadata dictionary
4. Add detailed description in `introduction.md`
5. Update main README.md documentation

## Rule ID Convention

- Rule ID format: `{Category}.{Three-digit number}`
- Category codes: ST, DC, IO
- Numbers start from 001 and increment
- Examples: ST.001, DC.001, IO.001

## Error Message Format

All rule error messages follow a unified format:

```
ERROR: {file_path}: [{rule_id}] {error_description}
```

Example:

```
ERROR: main.tf: [ST.001] Resource 'huaweicloud_vpc' instance name 'myvpc' should be 'test'
```
