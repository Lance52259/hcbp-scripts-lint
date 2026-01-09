#!/bin/bash

# HCBP Lint 部署脚本
# 通过 git clone 下载最新代码并部署到本地

set -e  # 遇到错误就退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
REPO_URL="https://github.com/chnsz/hcbp-scripts-lint.git"
INSTALL_BASE_DIR="$HOME/.local"
INSTALL_DIR="$INSTALL_BASE_DIR/bin"
TOOL_DIR="$INSTALL_BASE_DIR/share/terraform-linter"
SCRIPT_NAME="hcbp-lint"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  HCBP Lint 本地部署工具${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查必要的工具
echo -e "${YELLOW}检查系统环境...${NC}"

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 python3${NC}"
    echo "请先安装 Python 3.6 或更高版本"
    exit 1
fi
echo -e "${GREEN}✓ Python3: $(python3 --version)${NC}"

# 检查 Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 git${NC}"
    echo "请先安装 Git"
    exit 1
fi
echo -e "${GREEN}✓ Git: $(git --version)${NC}"

# 创建必要目录
echo -e "${YELLOW}创建目录结构...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$(dirname "$TOOL_DIR")"

# 删除旧版本（如果存在）
if [ -d "$TOOL_DIR" ]; then
    echo -e "${YELLOW}发现现有安装，正在更新...${NC}"
    rm -rf "$TOOL_DIR"
fi

# 克隆代码仓库
echo -e "${YELLOW}克隆最新代码...${NC}"
echo "仓库地址: $REPO_URL"
echo "安装位置: $TOOL_DIR"

if git clone "$REPO_URL" "$TOOL_DIR"; then
    echo -e "${GREEN}✓ 代码下载成功${NC}"
else
    echo -e "${RED}❌ 代码下载失败${NC}"
    exit 1
fi

# 验证 Python 脚本
echo -e "${YELLOW}验证工具...${NC}"
PYTHON_SCRIPT="$TOOL_DIR/.github/scripts/terraform_lint.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}❌ 未找到 Python 脚本: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# 测试脚本是否可执行
if python3 "$PYTHON_SCRIPT" --help > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 工具验证成功${NC}"
else
    echo -e "${RED}❌ 工具验证失败${NC}"
    exit 1
fi

# 创建可执行的包装脚本
echo -e "${YELLOW}创建可执行命令...${NC}"
WRAPPER_SCRIPT="$INSTALL_DIR/$SCRIPT_NAME"

cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash

# HCBP Lint 包装脚本
# 自动生成 - $(date)

LINTER_SCRIPT="$TOOL_DIR/.github/scripts/terraform_lint.py"

# 检查脚本是否存在
if [ ! -f "\$LINTER_SCRIPT" ]; then
    echo "错误: HCBP Lint 脚本未找到"
    echo "脚本路径: \$LINTER_SCRIPT"
    echo "请重新运行部署脚本"
    exit 1
fi

# 执行 linter，传递所有参数
exec python3 "\$LINTER_SCRIPT" "\$@"
EOF

# 设置执行权限
chmod +x "$WRAPPER_SCRIPT"
echo -e "${GREEN}✓ 可执行命令已创建: $WRAPPER_SCRIPT${NC}"

# 检查并配置 PATH
echo -e "${YELLOW}配置环境变量...${NC}"
PATH_ALREADY_SET=false

# 检查当前 PATH 是否包含 install directory
if [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then
    PATH_ALREADY_SET=true
    echo -e "${GREEN}✓ PATH 已包含 $INSTALL_DIR${NC}"
fi

# 确定需要配置的shell配置文件列表
SHELL_CONFIGS=()
if [ -n "$BASH_VERSION" ]; then
    # Bash shell - 配置多个文件以确保兼容性
    [ -f "$HOME/.bashrc" ] && SHELL_CONFIGS+=("$HOME/.bashrc")
    [ -f "$HOME/.bash_profile" ] && SHELL_CONFIGS+=("$HOME/.bash_profile")
    # 如果都不存在，创建 .bashrc
    if [ ${#SHELL_CONFIGS[@]} -eq 0 ]; then
        touch "$HOME/.bashrc"
        SHELL_CONFIGS+=("$HOME/.bashrc")
    fi
elif [ -n "$ZSH_VERSION" ]; then
    # Zsh shell
    [ -f "$HOME/.zshrc" ] && SHELL_CONFIGS+=("$HOME/.zshrc")
    if [ ${#SHELL_CONFIGS[@]} -eq 0 ]; then
        touch "$HOME/.zshrc"
        SHELL_CONFIGS+=("$HOME/.zshrc")
    fi
else
    # 其他shell或未知shell
    [ -f "$HOME/.profile" ] && SHELL_CONFIGS+=("$HOME/.profile")
    [ -f "$HOME/.bashrc" ] && SHELL_CONFIGS+=("$HOME/.bashrc")
    if [ ${#SHELL_CONFIGS[@]} -eq 0 ]; then
        touch "$HOME/.profile"
        SHELL_CONFIGS+=("$HOME/.profile")
    fi
fi

# 为每个配置文件添加PATH（如果需要）
PATH_ADDED=false
for SHELL_CONFIG in "${SHELL_CONFIGS[@]}"; do
    # 检查配置文件中是否已有 PATH 设置
    CONFIG_HAS_PATH=false
    if [ -f "$SHELL_CONFIG" ] && grep -q "$INSTALL_DIR" "$SHELL_CONFIG" 2>/dev/null; then
        CONFIG_HAS_PATH=true
    fi
    
    # 添加 PATH 到配置文件（如果需要）
    if [ "$CONFIG_HAS_PATH" = false ]; then
        echo -e "${YELLOW}添加 PATH 到 $SHELL_CONFIG${NC}"
        {
            echo ""
            echo "# HCBP Lint - $(date)"
            echo "export PATH=\"$INSTALL_DIR:\$PATH\""
        } >> "$SHELL_CONFIG"
        echo -e "${GREEN}✓ PATH 已添加到 $SHELL_CONFIG${NC}"
        PATH_ADDED=true
    else
        echo -e "${GREEN}✓ PATH 配置已存在于 $SHELL_CONFIG${NC}"
    fi
done

# 临时设置 PATH（如果有添加配置）
if [ "$PATH_ADDED" = true ]; then
    export PATH="$INSTALL_DIR:$PATH"
fi

# 创建配置文件
echo -e "${YELLOW}创建配置文件...${NC}"
cat > "$HOME/.hcbp-lint.conf" << 'EOF'
# HCBP Lint 配置文件
# 创建时间: $(date)

# 常用配置项
DEFAULT_CATEGORIES="ST,IO,DC,SC"
DEFAULT_REPORT_FORMAT="text"
DEFAULT_EXCLUDE_PATHS="*.backup,.terraform/*,test/*"

# 使用示例:
# hcbp-lint --directory ./terraform
# hcbp-lint --categories "ST,IO" 
# hcbp-lint --exclude-paths "test/*,examples/*"
EOF

echo -e "${GREEN}✓ 配置文件已创建: ~/.hcbp-lint.conf${NC}"

# 创建快速检查脚本
echo -e "${YELLOW}创建快速检查工具...${NC}"
cat > "$INSTALL_DIR/hcbp-lint-quick" << 'EOF'
#!/bin/bash

# HCBP Lint 快速检查工具
# 使用预设的常用配置

TARGET_DIR="${1:-.}"

echo "🔍 Terraform 代码快速检查"
echo "目标目录: $TARGET_DIR"
echo "检查规则: ST,IO,DC,SC"
echo "排除路径: *.backup,.terraform/*,test/*"
echo "========================================"

hcbp-lint \
    --directory "$TARGET_DIR" \
    --categories "ST,IO,DC,SC" \
    --exclude-paths "*.backup,.terraform/*,test/*" \
    --report-format text

RESULT=$?
echo "========================================"
if [ $RESULT -eq 0 ]; then
    echo "✅ 检查通过"
else
    echo "❌ 发现问题"
fi

exit $RESULT
EOF

chmod +x "$INSTALL_DIR/hcbp-lint-quick"
echo -e "${GREEN}✓ 快速检查工具已创建: hcbp-lint-quick${NC}"

# 最终测试
echo -e "${YELLOW}进行最终测试...${NC}"
if "$WRAPPER_SCRIPT" --help > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 部署成功！${NC}"
else
    echo -e "${RED}❌ 最终测试失败${NC}"
    exit 1
fi

# 显示部署信息
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}安装信息:${NC}"
echo "  工具目录: $TOOL_DIR"
echo "  可执行文件: $WRAPPER_SCRIPT"
echo "  配置文件: ~/.hcbp-lint.conf"
echo ""
echo -e "${YELLOW}使用方法:${NC}"
echo "  hcbp-lint --help                    # 查看帮助"
echo "  hcbp-lint --directory ./terraform   # 检查指定目录"
echo "  hcbp-lint-quick                     # 快速检查当前目录"
echo ""
echo -e "${YELLOW}环境配置:${NC}"
if [ "$PATH_ALREADY_SET" = true ]; then
    echo "  ✓ PATH 已配置，可直接使用命令"
else
    echo "  ⚠️  请运行以下命令激活环境:"
    for SHELL_CONFIG in "${SHELL_CONFIGS[@]}"; do
        echo "     source $SHELL_CONFIG"
    done
    echo "  或者重新打开终端"
    echo ""
    echo "  临时使用: 当前终端已可直接使用 hcbp-lint 命令"
fi

echo ""
echo -e "${YELLOW}测试安装:${NC}"
if command -v hcbp-lint &> /dev/null; then
    echo "  ✅ hcbp-lint 命令可用"
else
    echo "  ⚠️  请运行以下命令刷新环境:"
    for SHELL_CONFIG in "${SHELL_CONFIGS[@]}"; do
        echo "     source $SHELL_CONFIG"
    done
fi

echo ""
echo -e "${GREEN}开始使用 HCBP Lint 吧！${NC}"
