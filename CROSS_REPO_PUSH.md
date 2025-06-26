# Cross-Repository Push Configuration Guide

## 问题场景

当您从个人仓库的分支推送到目标仓库时，GitHub Actions可能会遇到以下问题：

```
Error: A branch or tag with the name 'your-personal-branch-name' could not be found
```

这种情况通常发生在：
- 从个人fork推送到上游仓库
- 从临时分支推送到主分支
- 分支名在目标仓库中不存在

## 解决方案

### 1. 智能Checkout配置

使用以下配置可以自动处理跨仓库推送：

```yaml
steps:
- name: Smart Checkout for Cross-Repo Push
  uses: actions/checkout@v4
  with:
    # 自动选择正确的引用
    ref: ${{ github.event.pull_request.base.ref || github.ref }}
    fetch-depth: 0  # 获取完整历史用于git操作

# 备用checkout（如果主checkout失败）
- name: Fallback Checkout
  if: failure()
  uses: actions/checkout@v4
  with:
    ref: 'master'  # 或者 'main'，根据您的默认分支
    fetch-depth: 0
```

### 2. 推荐的工作流配置

#### 场景1：Pull Request触发

```yaml
name: Terraform Lint (PR)
on:
  pull_request:
    branches: [ master, main ]

jobs:
  terraform-lint:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout PR Changes
      uses: actions/checkout@v4
      with:
        # 检出PR的头部分支，而不是基础分支
        ref: ${{ github.event.pull_request.head.sha }}
        fetch-depth: 0

    - name: Run Terraform Lint
      uses: Lance52259/hcbp-scripts-lint@v1
      with:
        directory: '.'
        changed-files-only: 'true'
        base-ref: ${{ github.event.pull_request.base.sha }}
        fail-on-error: 'true'
```

#### 场景2：Push事件处理

```yaml
name: Terraform Lint (Push)
on:
  push:
    branches: [ master, main ]

jobs:
  terraform-lint:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout Pushed Changes
      uses: actions/checkout@v4
      with:
        # 使用推送后的提交
        ref: ${{ github.sha }}
        fetch-depth: 0

    - name: Run Terraform Lint
      uses: Lance52259/hcbp-scripts-lint@v1
      with:
        directory: '.'
        changed-files-only: 'true'
        base-ref: ${{ github.event.before }}
        fail-on-error: 'true'
```

#### 场景3：通用解决方案（推荐）

```yaml
name: Terraform Lint (Universal)
on:
  push:
    branches: [ master, main ]
  pull_request:
    branches: [ master, main ]

jobs:
  terraform-lint:
    runs-on: ubuntu-latest
    steps:
    # 通用checkout配置，自动处理不同场景
    - name: Universal Checkout
      uses: actions/checkout@v4
      with:
        ref: ${{ github.event.pull_request.head.sha || github.sha }}
        fetch-depth: 0

    # 错误处理和调试信息
    - name: Debug Git Information
      run: |
        echo "=== Git Debug Information ==="
        echo "Event: ${{ github.event_name }}"
        echo "Ref: ${{ github.ref }}"
        echo "SHA: ${{ github.sha }}"
        if [ "${{ github.event_name }}" = "pull_request" ]; then
          echo "PR Base: ${{ github.event.pull_request.base.ref }}"
          echo "PR Head: ${{ github.event.pull_request.head.ref }}"
          echo "PR Base SHA: ${{ github.event.pull_request.base.sha }}"
          echo "PR Head SHA: ${{ github.event.pull_request.head.sha }}"
        fi
        if [ "${{ github.event_name }}" = "push" ]; then
          echo "Before: ${{ github.event.before }}"
          echo "After: ${{ github.event.after }}"
        fi
        echo "Current branch: $(git branch --show-current)"
        echo "Recent commits:"
        git log --oneline -5
        echo "=========================="

    # 智能base-ref选择
    - name: Run Terraform Lint with Smart Base-Ref
      uses: Lance52259/hcbp-scripts-lint@v1
      with:
        directory: '.'
        changed-files-only: 'true'
        base-ref: ${{ 
          github.event_name == 'pull_request' && github.event.pull_request.base.sha ||
          github.event_name == 'push' && github.event.before != '0000000000000000000000000000000000000000' && github.event.before ||
          'HEAD~1'
        }}
        fail-on-error: 'false'  # 设为true如果要在错误时失败
        report-format: 'both'
```

### 3. Action配置优化

如果您是Action的维护者，可以在`action.yml`中添加内置的智能checkout：

```yaml
# 在action.yml的开头添加
runs:
  using: 'composite'
  steps:
    # 智能checkout步骤
    - name: Smart Checkout
      uses: actions/checkout@v4
      with:
        ref: ${{ github.event.pull_request.head.sha || github.sha }}
        fetch-depth: 0
        path: 'checkout-workspace'

    # 其他步骤...
```

### 4. 高级配置选项

#### 处理Merge Conflicts

```yaml
- name: Checkout with Merge Handling
  uses: actions/checkout@v4
  with:
    ref: ${{ github.event.pull_request.head.sha || github.sha }}
    fetch-depth: 0
    # 自动合并到目标分支（可选）
    token: ${{ secrets.GITHUB_TOKEN }}

- name: Merge Target Branch (for conflict detection)
  if: github.event_name == 'pull_request'
  run: |
    git config user.name "github-actions"
    git config user.email "github-actions@github.com"
    git fetch origin ${{ github.event.pull_request.base.ref }}
    git merge origin/${{ github.event.pull_request.base.ref }} --no-edit || {
      echo "Merge conflict detected, using PR changes only"
      git merge --abort
    }
```

#### 多分支支持

```yaml
- name: Multi-Branch Checkout
  uses: actions/checkout@v4
  with:
    ref: ${{ 
      github.event_name == 'pull_request' && github.event.pull_request.head.sha ||
      github.ref_name == 'master' && github.sha ||
      github.ref_name == 'main' && github.sha ||
      github.ref_name == 'develop' && github.sha ||
      'master'
    }}
    fetch-depth: 0
```

## 最佳实践

### 1. 始终使用fetch-depth: 0
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # 获取完整Git历史
```

### 2. 添加调试信息
```yaml
- name: Debug Environment
  run: |
    echo "Event: ${{ github.event_name }}"
    echo "Ref: ${{ github.ref }}"
    echo "SHA: ${{ github.sha }}"
    git log --oneline -3
```

### 3. 使用条件执行
```yaml
- name: PR Only Step
  if: github.event_name == 'pull_request'
  run: echo "This runs only for PRs"

- name: Push Only Step  
  if: github.event_name == 'push'
  run: echo "This runs only for pushes"
```

### 4. 错误恢复
```yaml
- name: Primary Checkout
  id: checkout_primary
  continue-on-error: true
  uses: actions/checkout@v4
  with:
    ref: ${{ github.event.pull_request.head.sha || github.sha }}
    fetch-depth: 0

- name: Fallback Checkout
  if: steps.checkout_primary.outcome == 'failure'
  uses: actions/checkout@v4
  with:
    ref: 'master'
    fetch-depth: 0
```

## 故障排除

### 常见错误及解决方法

1. **分支不存在错误**
   ```
   Error: A branch or tag with the name 'feature-branch' could not be found
   ```
   **解决方案**: 使用SHA而不是分支名
   ```yaml
   ref: ${{ github.sha }}
   ```

2. **权限错误**
   ```
   Error: Resource not accessible by integration
   ```
   **解决方案**: 确保token有足够权限
   ```yaml
   token: ${{ secrets.GITHUB_TOKEN }}
   ```

3. **Git历史不完整**
   ```
   Error: git diff failed
   ```
   **解决方案**: 使用完整深度
   ```yaml
   fetch-depth: 0
   ```

### 调试命令

在工作流中添加这些命令来调试问题：

```bash
# 查看Git状态
git status
git branch -a
git log --oneline -5

# 查看环境变量
env | grep GITHUB

# 查看事件负载
echo '${{ toJson(github.event) }}'
```

## 示例配置文件

完整的跨仓库推送友好的工作流文件示例，请参考：
- [.github/workflows/terraform-lint.example.yml](.github/workflows/terraform-lint.example.yml)

## 总结

通过使用上述配置，您可以确保GitHub Actions在跨仓库推送场景下正常工作，避免因分支不存在而导致的失败。关键点是：

1. 使用SHA而不是分支名进行checkout
2. 提供适当的回退机制
3. 获取完整的Git历史
4. 添加适当的调试信息
5. 根据事件类型智能选择base-ref 