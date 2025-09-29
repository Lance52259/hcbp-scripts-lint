# GitHub API Setup Guide

## Problem Description

The SC.004 rule needs to fetch available version lists from GitHub API when checking HuaweiCloud Provider versions. Unauthenticated GitHub API requests have strict rate limits:

- **Unauthenticated requests**: 60 requests per hour
- **Authenticated requests**: 5000 requests per hour

When rate limits are reached, the following error occurs:
```
[SC.004] Failed to fetch huaweicloud provider versions from GitHub: Failed to fetch versions from GitHub: HTTP Error 403: rate limit exceeded
```

## Solutions

### 1. Setup GitHub Authentication (Recommended)

#### Method 1: Personal Access Token

**Create GitHub Personal Access Token**

1. Visit [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token" > "Generate new token (classic)"
3. Set the following permissions:

#### Required Permissions (SC.004 Rule)

**Repository permissions:**
- `public_repo` - Access public repositories (recommended)
  - Or `repo` - Access all repositories (if private repository access is needed)

**Metadata permissions:**
- `read:org` - Read organization information (optional, for enterprise environments)

#### Permission Description

| Permission | Required | Description | Rate Limit Impact |
|------------|----------|-------------|-------------------|
| `public_repo` | ✅ Required | Access public repository releases information | 5000/hour |
| `repo` | ✅ Alternative | Access all repositories (including private) | 5000/hour |
| `read:org` | ⚠️ Optional | Read organization information | 5000/hour |
| `read:user` | ❌ Not needed | Read user information | 5000/hour |

#### Minimum Permission Configuration (Recommended)

For SC.004 rule, the minimum permission configuration is:
- ✅ `public_repo` - Access public repositories
- ❌ Other permissions - Not needed

#### Enterprise Environment Permission Configuration

If enterprise repository or organization information access is needed:
- ✅ `repo` - Access all repositories
- ✅ `read:org` - Read organization information
- ✅ `read:user` - Read user information (optional)

4. Set expiration time (recommend choosing a longer period)
5. Generate and copy the token

**Set Environment Variables**

**Linux/macOS:**
```bash
# Method 1: Use GITHUB_TOKEN (recommended)
export GITHUB_TOKEN="your_token_here"
export GITHUB_USERNAME="your_username"

# Method 2: Use GITHUB_PAT
export GITHUB_PAT="your_token_here"
export GITHUB_USERNAME="your_username"
```

**Windows:**
```cmd
set GITHUB_TOKEN=your_token_here
set GITHUB_USERNAME=your_username
```

**CI/CD Setup:**
```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  GITHUB_USERNAME: ${{ github.actor }}
```

#### Method 2: GitHub App Authentication

**Create GitHub App**

1. Visit [GitHub Settings > Developer settings > GitHub Apps](https://github.com/settings/apps)
2. Click "New GitHub App"
3. Set application information:

#### GitHub App Permission Configuration

**Repository permissions:**
- `Metadata: Read` - Read repository metadata (required)
- `Contents: Read` - Read repository content (optional, for accessing releases)

**Account permissions:**
- `Organization members: Read` - Read organization members (optional)
- `Plan: Read` - Read plan information (optional)

#### Permission Description

| Permission | Required | Description | Purpose |
|------------|----------|-------------|---------|
| `Metadata: Read` | ✅ Required | Read basic repository information | Access releases API |
| `Contents: Read` | ⚠️ Recommended | Read repository content | Better API access |
| `Organization members: Read` | ❌ Optional | Read organization members | Enterprise environment |
| `Plan: Read` | ❌ Optional | Read plan information | Enterprise environment |

#### Minimum Permission Configuration (Recommended)

For SC.004 rule, the minimum permission configuration is:
- ✅ `Metadata: Read` - Read repository metadata
- ❌ Other permissions - Not needed

#### Enterprise Environment Permission Configuration

If better enterprise support is needed:
- ✅ `Metadata: Read` - Read repository metadata
- ✅ `Contents: Read` - Read repository content
- ✅ `Organization members: Read` - Read organization members
- ✅ `Plan: Read` - Read plan information

4. Subscribe to events: Not needed
5. Generate Private Key and download
6. Install app to target repository

**Set Environment Variables**
```bash
export GITHUB_APP_TOKEN="your_app_token"
export GITHUB_APP_ID="your_app_id"
```

#### Method 3: Enterprise Authentication

**Use Enterprise GitHub App**
```bash
export GITHUB_APP_TOKEN="enterprise_app_token"
export GITHUB_APP_ID="enterprise_app_id"
export GITHUB_USERNAME="enterprise_account"
```

### 2. Environment Variable Priority

SC.004 rule checks authentication configuration in the following priority:

1. **GITHUB_APP_TOKEN** - GitHub App token (Bearer authentication)
2. **GITHUB_PAT** - Personal Access Token
3. **GITHUB_TOKEN** - Legacy token (backward compatibility)

**Username Identification Priority:**
1. **GITHUB_USERNAME** - Explicitly specified username
2. **GITHUB_APP_ID** - Generated from App ID (app-{id})
3. No username identification

### 3. Use Caching Mechanism

SC.004 rule now includes intelligent caching mechanism:

- **Cache Duration**: 24 hours
- **Cache Location**: System temporary directory
- **Auto Update**: Automatically refetch when cache expires

### 4. Retry Mechanism

Rule includes automatic retry logic:

- **Retry Count**: Maximum 3 times
- **Backoff Strategy**: Exponential backoff (1 minute, 2 minutes, 4 minutes)
- **Fallback**: Use predefined version list

### 5. Fallback Solution

When GitHub API is completely unavailable, the rule will use a predefined version list containing the latest stable versions.

## Verify Setup

### Check Environment Variables
```bash
# Check all related environment variables
echo "GITHUB_TOKEN: $GITHUB_TOKEN"
echo "GITHUB_PAT: $GITHUB_PAT"
echo "GITHUB_APP_TOKEN: $GITHUB_APP_TOKEN"
echo "GITHUB_USERNAME: $GITHUB_USERNAME"
echo "GITHUB_APP_ID: $GITHUB_APP_ID"
```

### Test API Access

**Personal Access Token Test:**
```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
     -H "User-Agent: hcbp-scripts-lint/1.0 (via $GITHUB_USERNAME)" \
     -H "Accept: application/vnd.github.v3+json" \
     "https://api.github.com/repos/huaweicloud/terraform-provider-huaweicloud/releases?per_page=1"
```

**GitHub App Token Test:**
```bash
curl -H "Authorization: Bearer $GITHUB_APP_TOKEN" \
     -H "User-Agent: hcbp-scripts-lint/1.0 (via app-$GITHUB_APP_ID)" \
     -H "Accept: application/vnd.github.v3+json" \
     "https://api.github.com/repos/huaweicloud/terraform-provider-huaweicloud/releases?per_page=1"
```

### Check Rate Limits
```bash
curl -I -H "Authorization: token $GITHUB_TOKEN" \
     -H "User-Agent: hcbp-scripts-lint/1.0" \
     "https://api.github.com/repos/huaweicloud/terraform-provider-huaweicloud/releases?per_page=1"
```

Check rate limit information in response headers:
- `X-RateLimit-Limit`: Hourly limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

## Best Practices

### 1. Development Environment
- Set up personal GitHub token
- Regularly update token
- Monitor API usage

### 2. CI/CD Environment
- Use GitHub Actions built-in token
- Or create dedicated service account token
- Set appropriate permission scope

### 3. Enterprise Environment
- Use GitHub App for authentication
- Configure enterprise-level API limits
- Consider using proxy or mirror

## Troubleshooting

### Common Issues

1. **Invalid Token**
   - Check if token is correct
   - Confirm token permission settings
   - Verify if token has expired

2. **Insufficient Permission Error**
   ```
   HTTP Error 403: Resource not accessible by integration
   ```
   **Solution:**
   - Check if token has `public_repo` or `repo` permission
   - Confirm GitHub App has `Metadata: Read` permission
   - Verify if token is installed to target repository

3. **Still Encountering Rate Limits**
   - Check if other processes are using API
   - Consider using different token
   - Wait for rate limit reset

4. **Cache Issues**
   - Delete cache file: `rm /tmp/hcbp_github_versions_cache.json`
   - Re-run check

### Permission Verification

#### Check Token Permissions
```bash
# Test API access permissions
curl -H "Authorization: token $GITHUB_TOKEN" \
     -H "User-Agent: hcbp-scripts-lint/1.0" \
     "https://api.github.com/repos/huaweicloud/terraform-provider-huaweicloud/releases?per_page=1"
```

#### Check GitHub App Permissions
```bash
# Test GitHub App access permissions
curl -H "Authorization: Bearer $GITHUB_APP_TOKEN" \
     -H "User-Agent: hcbp-scripts-lint/1.0" \
     "https://api.github.com/repos/huaweicloud/terraform-provider-huaweicloud/releases?per_page=1"
```

#### Permission Error Diagnosis

**Error 1: 401 Unauthorized**
- Token is invalid or expired
- Check if token is set correctly

**Error 2: 403 Forbidden - Resource not accessible**
- Insufficient permissions
- Check if `public_repo` permission exists

**Error 3: 403 Forbidden - API rate limit exceeded**
- Rate limit exceeded
- Use authenticated token to resolve

**Error 4: 404 Not Found**
- Repository doesn't exist or no access permission
- Check repository name and permissions

### Debug Mode

Set environment variable to enable detailed logging:
```bash
export HCBP_DEBUG=1
```

## Related Links

- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
