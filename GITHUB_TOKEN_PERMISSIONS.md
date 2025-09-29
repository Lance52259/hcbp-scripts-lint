# GitHub Token Permissions Configuration Guide

## Required Permissions for SC.004 Rule

The SC.004 rule needs to access GitHub API to fetch HuaweiCloud Provider version information, therefore requiring appropriate permission configuration.

## Permission Requirements

### Personal Access Token Permissions

| Permission | Required | Description | Rate Limit |
|------------|----------|-------------|------------|
| `public_repo` | ✅ **Required** | Access public repository releases information | 5000/hour |
| `repo` | ✅ **Alternative** | Access all repositories (including private) | 5000/hour |
| `read:org` | ⚠️ **Optional** | Read organization information (enterprise environment) | 5000/hour |
| `read:user` | ❌ **Not needed** | Read user information | 5000/hour |

### GitHub App Permissions

| Permission | Required | Description | Purpose |
|------------|----------|-------------|---------|
| `Metadata: Read` | ✅ **Required** | Read basic repository information | Access releases API |
| `Contents: Read` | ⚠️ **Recommended** | Read repository content | Better API access |
| `Organization members: Read` | ❌ **Optional** | Read organization members | Enterprise environment |
| `Plan: Read` | ❌ **Optional** | Read plan information | Enterprise environment |

## Token Creation Steps

### Method 1: Personal Access Token

1. **Access GitHub Settings**
   - Open: https://github.com/settings/tokens
   - Click: "Generate new token" → "Generate new token (classic)"

2. **Configure Token**
   - **Note**: Fill in description (e.g., hcbp-scripts-lint)
   - **Expiration**: Choose expiration time (recommended: 90 days or No expiration)
   - **Select scopes**: Choose permissions

3. **Select Permissions**
   ```
   ✅ public_repo - Access public repositories
   ```

4. **Generate Token**
   - Click: "Generate token"
   - **Important**: Copy token immediately (only shown once)

5. **Set Environment Variables**
   ```bash
   export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
   export GITHUB_USERNAME="your_username"
   ```

### Method 2: GitHub App

1. **Create GitHub App**
   - Visit: https://github.com/settings/apps
   - Click: "New GitHub App"

2. **Configure App Information**
   - **GitHub App name**: hcbp-scripts-lint
   - **Homepage URL**: Your project URL
   - **User authorization callback URL**: Optional

3. **Set Permissions**
   ```
   Repository permissions:
   ✅ Metadata: Read
   ✅ Contents: Read (recommended)
   
   Account permissions:
   ❌ Organization members: Read (optional)
   ❌ Plan: Read (optional)
   ```

4. **Install App**
   - Generate Private Key and download
   - Install to target repository or organization

5. **Set Environment Variables**
   ```bash
   export GITHUB_APP_TOKEN="your_app_token"
   export GITHUB_APP_ID="your_app_id"
   ```

## Permission Verification

### Using Permission Check Tool

```bash
python3.10 check_github_permissions.py
```

### Manual Verification

```bash
# Test API access
curl -H "Authorization: token $GITHUB_TOKEN" \
     -H "User-Agent: hcbp-scripts-lint/1.0" \
     "https://api.github.com/repos/huaweicloud/terraform-provider-huaweicloud/releases?per_page=1"
```

### Expected Results

**Successful Response**:
```json
[
  {
    "tag_name": "v1.80.0",
    "published_at": "2024-01-01T00:00:00Z",
    "draft": false,
    "prerelease": false
  }
]
```

**Error Responses**:
- `401 Unauthorized` - Invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Repository doesn't exist

## Common Questions

### Q: Why is `public_repo` permission needed?

A: The SC.004 rule needs to access releases information from the `huaweicloud/terraform-provider-huaweicloud` repository, which requires repository access permission.

### Q: Can I use fewer permissions?

A: No. `public_repo` is the minimum required permission with no alternative.

### Q: Do enterprise environments need additional permissions?

A: If accessing enterprise repositories, `repo` permission is needed instead of `public_repo`.

### Q: What to do when token expires?

A: Regenerate the token and update environment variables, or set a longer expiration time.

## Security Recommendations

1. **Principle of Least Privilege**: Only grant necessary permissions
2. **Regular Rotation**: Regularly update tokens
3. **Environment Isolation**: Use different tokens for different environments
4. **Secure Storage**: Don't hardcode tokens in code
5. **Usage Monitoring**: Regularly check API usage

## Related Links

- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub Apps](https://docs.github.com/en/developers/apps/building-github-apps)
- [GitHub API Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
