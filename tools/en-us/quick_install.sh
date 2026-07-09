#!/bin/bash

# HCBP Lint Deployment Script
# Download latest code via git clone and deploy locally

set -e  # Exit on error

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables
REPO_URL="https://github.com/chnsz/hcbp-scripts-lint.git"
INSTALL_BASE_DIR="$HOME/.local"
INSTALL_DIR="$INSTALL_BASE_DIR/bin"
TOOL_DIR="$INSTALL_BASE_DIR/share/terraform-linter"
SCRIPT_NAME="hcbp-lint"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  HCBP Lint Local Deployment Tool${NC}"
echo -e "${BLUE}========================================${NC}"

# Check required tools
echo -e "${YELLOW}Checking system environment...${NC}"

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 not found${NC}"
    echo "Please install Python 3.6 or higher"
    exit 1
fi
echo -e "${GREEN}✓ Python3: $(python3 --version)${NC}"

# Check Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Error: git not found${NC}"
    echo "Please install Git first"
    exit 1
fi
echo -e "${GREEN}✓ Git: $(git --version)${NC}"

# Create necessary directories
echo -e "${YELLOW}Creating directory structure...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$(dirname "$TOOL_DIR")"

# Remove old version (if exists)
if [ -d "$TOOL_DIR" ]; then
    echo -e "${YELLOW}Found existing installation, updating...${NC}"
    rm -rf "$TOOL_DIR"
fi

# Clone repository
echo -e "${YELLOW}Cloning latest code...${NC}"
echo "Repository URL: $REPO_URL"
echo "Installation path: $TOOL_DIR"

if git clone "$REPO_URL" "$TOOL_DIR"; then
    echo -e "${GREEN}✓ Code download successful${NC}"
else
    echo -e "${RED}❌ Code download failed${NC}"
    exit 1
fi

# Verify Python script
echo -e "${YELLOW}Verifying tool...${NC}"
PYTHON_SCRIPT="$TOOL_DIR/.github/scripts/terraform_lint.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}❌ Python script not found: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# Test if script is executable
VERIFY_OUTPUT="$(python3 "$PYTHON_SCRIPT" --help 2>&1)"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Tool verification successful${NC}"
else
    echo -e "${RED}❌ Tool verification failed${NC}"
    echo "$VERIFY_OUTPUT"
    exit 1
fi

# Create executable wrapper script
echo -e "${YELLOW}Creating executable command...${NC}"
WRAPPER_SCRIPT="$INSTALL_DIR/$SCRIPT_NAME"

cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash

# HCBP Lint Wrapper Script
# Auto-generated - $(date)

LINTER_SCRIPT="$TOOL_DIR/.github/scripts/terraform_lint.py"

# Check if script exists
if [ ! -f "\$LINTER_SCRIPT" ]; then
    echo "Error: HCBP Lint script not found"
    echo "Script path: \$LINTER_SCRIPT"
    echo "Please re-run the deployment script"
    exit 1
fi

# Execute linter, passing all arguments
export HCBP_LINT_TOOL_NAME="$SCRIPT_NAME"
export HCBP_LINT_TOOL_DIR="$TOOL_DIR"
exec python3 "\$LINTER_SCRIPT" "\$@"
EOF

# Set execute permissions
chmod +x "$WRAPPER_SCRIPT"
echo -e "${GREEN}✓ Executable command created: $WRAPPER_SCRIPT${NC}"

# Check and configure PATH
echo -e "${YELLOW}Configuring environment variables...${NC}"
PATH_ALREADY_SET=false

# Check if current PATH contains install directory
if [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then
    PATH_ALREADY_SET=true
    echo -e "${GREEN}✓ PATH already contains $INSTALL_DIR${NC}"
fi

# Determine shell configuration files to configure
SHELL_CONFIGS=()
if [ -n "$BASH_VERSION" ]; then
    # Bash shell - configure multiple files for compatibility
    [ -f "$HOME/.bashrc" ] && SHELL_CONFIGS+=("$HOME/.bashrc")
    [ -f "$HOME/.bash_profile" ] && SHELL_CONFIGS+=("$HOME/.bash_profile")
    # If none exist, create .bashrc
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
    # Other shells or unknown shell
    [ -f "$HOME/.profile" ] && SHELL_CONFIGS+=("$HOME/.profile")
    [ -f "$HOME/.bashrc" ] && SHELL_CONFIGS+=("$HOME/.bashrc")
    if [ ${#SHELL_CONFIGS[@]} -eq 0 ]; then
        touch "$HOME/.profile"
        SHELL_CONFIGS+=("$HOME/.profile")
    fi
fi

# Add PATH to each configuration file (if needed)
PATH_ADDED=false
for SHELL_CONFIG in "${SHELL_CONFIGS[@]}"; do
    # Check if configuration file already has PATH setting
    CONFIG_HAS_PATH=false
    if [ -f "$SHELL_CONFIG" ] && grep -q "$INSTALL_DIR" "$SHELL_CONFIG" 2>/dev/null; then
        CONFIG_HAS_PATH=true
    fi
    
    # Add PATH to configuration file (if needed)
    if [ "$CONFIG_HAS_PATH" = false ]; then
        echo -e "${YELLOW}Adding PATH to $SHELL_CONFIG${NC}"
        {
            echo ""
            echo "# HCBP Lint - $(date)"
            echo "export PATH=\"$INSTALL_DIR:\$PATH\""
        } >> "$SHELL_CONFIG"
        echo -e "${GREEN}✓ PATH added to $SHELL_CONFIG${NC}"
        PATH_ADDED=true
    else
        echo -e "${GREEN}✓ PATH configuration already exists in $SHELL_CONFIG${NC}"
    fi
done

# Temporarily set PATH (if configuration was added)
if [ "$PATH_ADDED" = true ]; then
    export PATH="$INSTALL_DIR:$PATH"
fi

# Create configuration file
echo -e "${YELLOW}Creating configuration file...${NC}"
cat > "$HOME/.hcbp-lint.conf" << 'EOF'
# HCBP Lint Configuration File
# Created: $(date)

# Common configuration options
DEFAULT_CATEGORIES="ST,IO,DC,SC"
DEFAULT_REPORT_FORMAT="text"
DEFAULT_EXCLUDE_PATHS="*.backup,.terraform/*,test/*"

# Usage examples:
# hcbp-lint --directory ./terraform
# hcbp-lint --categories "ST,IO" 
# hcbp-lint --exclude-paths "test/*,examples/*"
EOF

echo -e "${GREEN}✓ Configuration file created: ~/.hcbp-lint.conf${NC}"

# Create quick check script
echo -e "${YELLOW}Creating quick check tool...${NC}"
cat > "$INSTALL_DIR/hcbp-lint-quick" << 'EOF'
#!/bin/bash

# HCBP Lint Quick Check Tool
# Uses predefined common configurations

TARGET_DIR="${1:-.}"

echo "🔍 Terraform Code Quick Check"
echo "Target directory: $TARGET_DIR"
echo "Check rules: ST,IO,DC,SC"
echo "Exclude paths: *.backup,.terraform/*,test/*"
echo "========================================"

hcbp-lint \
    --directory "$TARGET_DIR" \
    --categories "ST,IO,DC,SC" \
    --exclude-paths "*.backup,.terraform/*,test/*" \
    --report-format text

RESULT=$?
echo "========================================"
if [ $RESULT -eq 0 ]; then
    echo "✅ Check passed"
else
    echo "❌ Issues found"
fi

exit $RESULT
EOF

chmod +x "$INSTALL_DIR/hcbp-lint-quick"
echo -e "${GREEN}✓ Quick check tool created: hcbp-lint-quick${NC}"

# Final test
echo -e "${YELLOW}Performing final test...${NC}"
if "$WRAPPER_SCRIPT" --help > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
else
    echo -e "${RED}❌ Final test failed${NC}"
    exit 1
fi

# Display deployment information
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🎉 Deployment completed!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Installation Information:${NC}"
echo "  Tool directory: $TOOL_DIR"
echo "  Executable file: $WRAPPER_SCRIPT"
echo "  Configuration file: ~/.hcbp-lint.conf"
echo ""
echo -e "${YELLOW}Usage:${NC}"
echo "  hcbp-lint --help                    # Show help"
echo "  hcbp-lint --directory ./terraform   # Check specified directory"
echo "  hcbp-lint-quick                     # Quick check current directory"
echo ""
echo -e "${YELLOW}Environment Configuration:${NC}"
if [ "$PATH_ALREADY_SET" = true ]; then
    echo "  ✓ PATH already configured, commands ready to use"
else
    echo "  ⚠️  Please run the following commands to activate environment:"
    for SHELL_CONFIG in "${SHELL_CONFIGS[@]}"; do
        echo "     source $SHELL_CONFIG"
    done
    echo "  Or restart your terminal"
    echo ""
    echo "  Temporary use: hcbp-lint command is available in current terminal"
fi

echo ""
echo -e "${YELLOW}Test Installation:${NC}"
if command -v hcbp-lint &> /dev/null; then
    echo "  ✅ hcbp-lint command available"
else
    echo "  ⚠️  Please run the following commands to refresh environment:"
    for SHELL_CONFIG in "${SHELL_CONFIGS[@]}"; do
        echo "     source $SHELL_CONFIG"
    done
fi

echo ""
echo -e "${GREEN}Start using HCBP Lint!${NC}"
