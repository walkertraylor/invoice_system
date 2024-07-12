#!/bin/bash

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to display usage information
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Manage the invoice system repository"
    echo
    echo "Options:"
    echo "  -h, --help        Show this help message"
    echo "  -r, --reset       Reset the repository (WARNING: This will delete all local changes)"
    echo "  -f, --force       Force push to remote (use with caution)"
    echo "  -m, --message     Specify a commit message (default: 'Update project')"
    echo "  -b, --branch      Specify a branch name (default: current branch)"
    echo
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Default values
RESET_REPO=false
FORCE_PUSH=false
COMMIT_MESSAGE="Update project"
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")

# Parse command line arguments
while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help) usage; exit 0 ;;
        -r|--reset) RESET_REPO=true; shift ;;
        -f|--force) FORCE_PUSH=true; shift ;;
        -m|--message) COMMIT_MESSAGE="$2"; shift 2 ;;
        -b|--branch) BRANCH="$2"; shift 2 ;;
        *) echo -e "${RED}Unknown parameter passed: $1${NC}"; usage; exit 1 ;;
    esac
done

# Check if gh CLI is installed
if ! command_exists gh; then
    echo -e "${RED}GitHub CLI (gh) is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if user is authenticated with gh
if ! gh auth status &>/dev/null; then
    echo -e "${YELLOW}Please run 'gh auth login' to authenticate with GitHub.${NC}"
    exit 1
fi

# Function to check if the repository already exists
repo_exists() {
    gh repo view walkertraylor/invoice_system &>/dev/null
}

# Reset repository if flag is set
if $RESET_REPO; then
    echo -e "${YELLOW}Resetting repository...${NC}"
    rm -rf .git
    gh repo delete walkertraylor/invoice_system --yes || true
    gh repo create walkertraylor/invoice_system --private --confirm
else
    # Check if the repository already exists
    if repo_exists; then
        echo -e "${GREEN}Repository already exists. Proceeding with updates.${NC}"
    else
        echo -e "${YELLOW}Creating GitHub repository...${NC}"
        gh repo create walkertraylor/invoice_system --private --confirm || true
    fi
fi

# Initialize git if not already initialized
if [ ! -d .git ]; then
    git init
    echo -e "${GREEN}Initialized git repository.${NC}"
fi

# Create or update .gitignore file
cat > .gitignore << EOF
# Sensitive data
data/payments.txt
data/payments_backup.txt

# Generated files
output/

# Python environment
.venv/
*.pyc
__pycache__/

# macOS system files
.DS_Store

# Temporary files
*.tmp
*.temp

# Logs
*.log

# Other potential sensitive files
*.key
*.pem
*.env
EOF

echo -e "${GREEN}Updated .gitignore file.${NC}"

# Ensure the required directory structure exists
mkdir -p src data output

# Add all files
git add .
git add -f README.md  # Ensure README is added even if ignored

# Commit if there are changes
if ! git diff --cached --quiet; then
    git commit -m "$COMMIT_MESSAGE"
    echo -e "${GREEN}Committed changes with message: $COMMIT_MESSAGE${NC}"
fi

# Add or update the remote using SSH
git remote remove origin 2>/dev/null || true
git remote add origin git@github.com:walkertraylor/invoice_system.git
echo -e "${GREEN}Updated remote origin.${NC}"

# Fetch the latest changes from the remote
git fetch origin

# Try to rebase on top of the remote branch
if git rebase origin/$BRANCH; then
    echo -e "${GREEN}Successfully rebased on top of remote branch.${NC}"
else
    echo -e "${YELLOW}Rebase failed. Aborting rebase and forcing push.${NC}"
    git rebase --abort
fi

# Push to GitHub
echo -e "${YELLOW}Pushing to GitHub...${NC}"
if $FORCE_PUSH; then
    git push -u origin "$BRANCH" --force
else
    git push -u origin "$BRANCH" --force-with-lease
fi

echo -e "${GREEN}Repository updated and pushed to GitHub successfully!${NC}"
