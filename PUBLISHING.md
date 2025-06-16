# Publishing Guide for Terraform Scripts Lint Action

This document provides comprehensive instructions for publishing the Terraform Scripts Lint Action to GitHub Marketplace
and using it in projects.

## Table of Contents

- [Publishing to GitHub Marketplace](#publishing-to-github-marketplace)
- [Version Management](#version-management)
- [Usage Options](#usage-options)
- [Testing Before Publishing](#testing-before-publishing)
- [Maintenance and Updates](#maintenance-and-updates)
- [Distribution Strategies](#distribution-strategies)

## Publishing to GitHub Marketplace

### Prerequisites

1. **Repository Requirements**:
   - Public GitHub repository
   - Valid `action.yml` file in repository root
   - Proper README.md with usage instructions
   - LICENSE file (Apache 2.0 in our case)

2. **Action Metadata**:
   - Ensure `action.yml` has proper metadata:
     - `name`: Clear, descriptive action name
     - `description`: Concise description of functionality
     - `author`: Author information
     - `branding`: Icon and color for marketplace

### Step-by-Step Publishing Process

#### 1. Prepare for Release

```bash
# Ensure all tests pass
python3 .github/scripts/terraform_lint.py --help
python3 .github/scripts/terraform_lint.py --directory test

# Verify action.yml is valid
cat action.yml

# Check README.md has proper usage examples
cat README.md
```

#### 2. Create a Release Tag

```bash
# Create and push a version tag
git tag -a v1.0.0 -m "Initial release of Terraform Scripts Lint Action"
git push origin v1.0.0

# Create major version tag (recommended for actions)
git tag -a v1 -m "Version 1.x"
git push origin v1
```

#### 3. Create GitHub Release

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Choose the tag you created (e.g., `v1.0.0`)
4. Fill in release information:
   - **Release title**: `v1.0.0 - Initial Release`
   - **Description**: Include changelog and features
   - **Assets**: Optionally attach additional files

#### 4. Publish to Marketplace

1. In the release creation page, check "Publish this Action to the GitHub Marketplace"
2. Choose a category (e.g., "Code quality")
3. Verify the action metadata
4. Click "Publish release"

### Example Release Notes Template

```markdown
## Terraform Scripts Lint Action v1.0.0

### Features
- ✅ Comprehensive Terraform script linting
- ✅ Flexible rule control with `ignore-rules` parameter
- ✅ Path filtering with `include-paths` and `exclude-paths`
- ✅ Detailed error reporting and GitHub Actions integration
- ✅ Support for multiple Terraform file types (.tf, .tfvars)

### Supported Rules
- **ST (Style/Format)**: ST.001, ST.002, ST.003, ST.004, ST.005, ST.006, ST.007, ST.008
- **DC (Documentation/Comments)**: DC.001
- **IO (Input/Output)**: IO.001, IO.002, IO.003, IO.004, IO.005, IO.006, IO.007, IO.008

### Usage
``yaml
- name: Terraform Lint
  uses: Lance52259/hcbp-scripts-lint@v1
  with:
    directory: '.'
    ignore-rules: 'ST.001,ST.003'
    exclude-paths: 'examples/*'
``

### What's Changed
- Initial release with core linting functionality
- GitHub Actions integration
- Comprehensive documentation and examples
```

## Version Management

### Semantic Versioning

Follow semantic versioning (SemVer) for releases:

- **MAJOR** (v1.0.0 → v2.0.0): Breaking changes
- **MINOR** (v1.0.0 → v1.1.0): New features, backward compatible
- **PATCH** (v1.0.0 → v1.0.1): Bug fixes, backward compatible

### Version Tag Strategy

```bash
# For version 1.2.3, create these tags:
git tag -a v1.2.3 -m "Release version 1.2.3"
git tag -a v1.2 -m "Latest 1.2.x release" -f
git tag -a v1 -m "Latest 1.x release" -f

# Push all tags
git push origin v1.2.3
git push origin v1.2 -f
git push origin v1 -f
```

### Recommended Tag Usage for Users

- **Specific version**: `Lance52259/hcbp-scripts-lint@v1.2.3` (most stable)
- **Minor version**: `Lance52259/hcbp-scripts-lint@v1.2` (get patches)
- **Major version**: `Lance52259/hcbp-scripts-lint@v1` (get features)
- **Latest**: `Lance52259/hcbp-scripts-lint@main` (bleeding edge, not recommended)

## Usage Options

### 1. Published Action (Recommended)

```yaml
# Use specific version (most stable)
- uses: Lance52259/hcbp-scripts-lint@v1.0.0

# Use major version (get updates)
- uses: Lance52259/hcbp-scripts-lint@v1

# Use minor version (balance stability and updates)
- uses: Lance52259/hcbp-scripts-lint@v1.0
```

### 2. Local Action (Copy to Repository)

```yaml
# Copy entire action to your repository
- uses: ./
```

**Pros**: Full control, no external dependencies
**Cons**: Manual updates required

### 3. Fork and Reference

```yaml
# Fork the repository and reference your fork
- uses: YOUR_USERNAME/hcbp-scripts-lint@v1
```

**Pros**: Control over updates, can customize
**Cons**: Need to maintain your fork

### 4. Direct Repository Reference

```yaml
# Reference the original repository directly
- uses: Lance52259/hcbp-scripts-lint@main
```

**Pros**: Always latest version
**Cons**: May break if main branch changes

## Testing Before Publishing

### Local Testing

```bash
# Test basic functionality
python3 .github/scripts/terraform_lint.py --directory test

# Test with parameters
python3 .github/scripts/terraform_lint.py --directory test --ignore-rules "ST.001"

# Test path filtering
python3 .github/scripts/terraform_lint.py --exclude-paths "test/*"
```

### GitHub Actions Testing

Create a test workflow in your repository:

```yaml
name: Test Action Before Publishing

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  test-action:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Test Local Action
      uses: ./
      with:
        directory: 'test'
        fail-on-error: 'false'
```

### Integration Testing

Test with different scenarios:

1. **Empty directory**: No .tf files
2. **Clean code**: No violations
3. **Multiple violations**: Various rule violations
4. **Path filtering**: Include/exclude paths
5. **Rule ignoring**: Ignore specific rules

## Maintenance and Updates

### Regular Maintenance Tasks

1. **Monitor Issues**: Respond to user-reported issues
2. **Update Dependencies**: Keep Python dependencies current
3. **Security Updates**: Address security vulnerabilities
4. **Documentation**: Keep README and examples updated
5. **Testing**: Ensure compatibility with new Terraform versions

### Update Process

1. **Develop**: Make changes in feature branches
2. **Test**: Thoroughly test changes
3. **Document**: Update CHANGELOG.md
4. **Release**: Create new version tag
5. **Announce**: Update marketplace listing

### Backward Compatibility

- Maintain backward compatibility within major versions
- Deprecate features before removing them
- Provide migration guides for breaking changes

## Distribution Strategies

### GitHub Marketplace

**Advantages**:
- Discoverable by GitHub users
- Integrated with GitHub Actions
- Automatic updates for users
- Usage analytics

**Requirements**:
- Public repository
- Valid action.yml
- Proper documentation
- Regular maintenance

### Alternative Distribution

1. **Docker Hub**: Package as Docker image
2. **PyPI**: Distribute as Python package
3. **Direct Download**: Provide downloadable releases
4. **Documentation Site**: Host comprehensive docs

### Marketing and Promotion

1. **README**: Comprehensive usage examples
2. **Blog Posts**: Write about the tool
3. **Community**: Engage with Terraform community
4. **Social Media**: Share updates and features
5. **Conferences**: Present at DevOps events

## Troubleshooting Common Publishing Issues

### Action Not Found

**Problem**: Users get "Unable to resolve action" error
**Solution**:
- Ensure action.yml exists in repository root
- Verify repository is public
- Check tag/branch exists

### Marketplace Rejection

**Problem**: Action rejected from marketplace
**Solution**:
- Review marketplace guidelines
- Ensure proper metadata in action.yml
- Add comprehensive README
- Include proper LICENSE file

### Version Conflicts

**Problem**: Users experiencing issues with versions
**Solution**:
- Use semantic versioning consistently
- Maintain major version tags
- Document breaking changes clearly
- Provide migration guides

### Performance Issues

**Problem**: Action runs slowly in CI/CD
**Solution**:
- Optimize Python script performance
- Add caching for dependencies
- Provide path filtering options
- Document performance best practices

## Support and Community

### Support Channels

- **GitHub Issues**: Primary support channel
- **Discussions**: Community Q&A
- **Documentation**: Comprehensive guides
- **Examples**: Real-world usage examples

### Contributing Guidelines

1. **Issues**: Report bugs and request features
2. **Pull Requests**: Contribute code improvements
3. **Documentation**: Help improve docs
4. **Testing**: Add test cases
5. **Community**: Help other users

### Metrics and Analytics

Track action usage through:
- GitHub Marketplace analytics
- Repository insights
- Issue/PR activity
- Community feedback

## Conclusion

Publishing a GitHub Action requires careful planning, thorough testing, and ongoing maintenance. By following this
guide, you can successfully publish and maintain the Terraform Scripts Lint Action, providing value to the community
while ensuring reliability and security.

Remember to:
- Test thoroughly before publishing
- Maintain backward compatibility
- Respond to community feedback
- Keep documentation updated
- Monitor for security issues

For questions or support, please open an issue in the repository or start a discussion in the GitHub Discussions
section.
