#!/bin/bash

set -e

RESET_REPO=false

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --reset) RESET_REPO=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Function to check if a command was successful
check_command() {
    if [ $? -ne 0 ]; then
        echo "Error: $1"
        exit 1
    fi
}

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) is not installed. Please install it first."
    exit 1
fi

# Check if user is authenticated with gh
gh auth status || (echo "Please run 'gh auth login' first." && exit 1)

# Reset repository if flag is set
if $RESET_REPO; then
    echo "Resetting repository..."
    rm -rf .git
    gh repo delete walkertraylor/invoice_system --yes || true
    gh repo create walkertraylor/invoice_system --private --confirm
else
    # Check if the repository already exists
    if gh repo view walkertraylor/invoice_system &>/dev/null; then
        echo "Repository already exists. Proceeding with updates."
    else
        echo "Creating GitHub repository..."
        gh repo create walkertraylor/invoice_system --private --confirm || true
    fi
fi

# Initialize git if not already initialized
if [ ! -d .git ]; then
    git init
    check_command "Failed to initialize git repository"
fi

# Create or update .gitignore file
cat > .gitignore << EOL
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
EOL

# Ensure the required directory structure exists
mkdir -p src data output

# Add all files
git add .
git add -f README.md  # Ensure README is added even if ignored

# Commit if there are changes
if ! git diff --cached --quiet; then
    git commit -m "Update project structure and files"
    check_command "Failed to commit files"
fi

# Add or update the remote using SSH
git remote remove origin 2>/dev/null || true
git remote add origin git@github.com:walkertraylor/invoice_system.git
check_command "Failed to add/update remote"

# Determine the current branch name
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Fetch the latest changes from the remote
git fetch origin

# Try to rebase on top of the remote branch
if git rebase origin/$BRANCH; then
    echo "Successfully rebased on top of remote branch."
else
    echo "Rebase failed. Aborting rebase and forcing push."
    git rebase --abort
fi

# Push to GitHub, force with lease to avoid conflicts
echo "Pushing to GitHub..."
git push -u origin "$BRANCH" --force-with-lease
check_command "Failed to push to GitHub"

echo "Repository updated and pushed to GitHub successfully!"
