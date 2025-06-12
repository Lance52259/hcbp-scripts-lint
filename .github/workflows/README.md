# GitHub Actions Workflows

This directory contains example GitHub Actions workflows that demonstrate how to use the Terraform Scripts Lint Tool in
your CI/CD pipeline.

## Files

### `terraform-lint.yml`

This is a comprehensive example workflow that shows various ways to integrate the Terraform Scripts Lint Tool into your
GitHub Actions pipeline. It includes:

- **Basic Usage**: Simple linting with default settings
- **Advanced Configuration**: Custom path filtering and rule ignoring
- **Multi-Environment Testing**: Matrix strategy for different environments
- **Integration Examples**: How to combine with other Terraform tools
- **Performance Tips**: Optimization suggestions for large repositories

## Reference

### [terraform-lint.example.yml](terraform-lint.example.yml)

## How to Use

1. **Copy the Example File**:

   ```bash
   cp .github/workflows/terraform-lint.example.yml .github/workflows/terraform-lint.yml
   ```

2. **Customize for Your Project**:
   - Modify the trigger conditions (`on:` section)
   - Adjust directory paths and file patterns
   - Configure rule ignoring based on your needs
   - Set appropriate failure conditions

3. **Basic Setup Example**:

   ```yaml
   name: Terraform Lint
   on: [push, pull_request]

   jobs:
     terraform-lint:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Terraform Lint
           uses: Lance52259/hcbp-scripts-lint@v1
           with:
             directory: './terraform'
             fail-on-error: 'true'
   ```

## Common Use Cases

### 1. Development Environment (Flexible)

```yaml
- name: Development Lint
  uses: Lance52259/hcbp-scripts-lint@v1
  with:
    directory: './dev'
    ignore-rules: 'ST.001,ST.003'  # Allow flexible naming
    fail-on-error: 'false'
```

### 2. Production Environment (Strict)

```yaml
- name: Production Lint
  uses: Lance52259/hcbp-scripts-lint@v1
  with:
    directory: './prod'
    fail-on-error: 'true'  # Enforce all rules
```

### 3. Module Validation

```yaml
- name: Module Lint
  uses: Lance52259/hcbp-scripts-lint@v1
  with:
    include-paths: './modules'
    exclude-paths: 'modules/*/examples/*'
    fail-on-error: 'true'
```

## Integration with Other Tools

The example workflow also shows how to integrate with:

- `terraform fmt` for formatting checks
- `terraform validate` for syntax validation
- Path filtering to run only on Terraform file changes
- Artifact uploading for lint reports

## Troubleshooting

Common issues and solutions are documented in the example workflow file. Check the comments for:

- Path configuration problems
- Permission issues
- Rule configuration errors
- Performance optimization tips

## Contributing

If you have additional workflow examples or improvements, please contribute them back to the project!
