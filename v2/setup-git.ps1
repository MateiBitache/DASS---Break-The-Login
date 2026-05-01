$projectPath = "d:\Proiect DASS"

if (Test-Path $projectPath) {
    Set-Location $projectPath
} else {
    Write-Host "[-] Path $projectPath not found." -ForegroundColor Red
    exit
}

Write-Host "[*] Initializing workspace configuration..." -ForegroundColor Cyan

# Initialize git if not already done
if (-not (Test-Path ".git")) {
    git init | Out-Null
    Write-Host "[+] Git repository initialized." -ForegroundColor Green
} else {
    Write-Host "[*] Git repository already present." -ForegroundColor Yellow
}

# Create .gitignore
Write-Host "[*] Generating .gitignore rules..." -ForegroundColor Cyan
@"
# Java
*.class
*.jar
*.war
*.ear
target/
.mvn/

# Spring Boot
application-local.yml
application-*.yml.bak

# IDE
.idea/
*.iml
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# Environment
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
.Python
venv/
ENV/

# Node
node_modules/
dist/
.angular/

# Temporary
*.tmp
*.bak
~*
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8

Write-Host "[+] .gitignore created successfully." -ForegroundColor Green

# Initial commit
Write-Host "[*] Staging files and creating initial commit..." -ForegroundColor Cyan
git add .
git commit -q -m "chore: initial project setup and configuration

- Initialize Spring Boot backend architecture
- Configure CI/CD and Docker environments
- Setup project documentation
- Prepare environment for production deployment"

Write-Host "[+] Initial commit executed." -ForegroundColor Green

# Create branches
Write-Host "[*] Configuring standard branch structure..." -ForegroundColor Cyan
git branch v1-vulnerable
git branch v2-secure
Write-Host "[+] Branches 'v1-vulnerable' and 'v2-secure' established." -ForegroundColor Green

# Create tags
Write-Host "[*] Applying version tags..." -ForegroundColor Cyan
git tag -a v1.0.0-vulnerable -m "Release v1.0.0 - Vulnerable baseline architecture"
git tag -a v2.0.0-secure -m "Release v2.0.0 - Secure architecture with hardened authentication"
Write-Host "[+] Tags applied: v1.0.0-vulnerable, v2.0.0-secure" -ForegroundColor Green

# Show branches and tags
Write-Host "`n[*] Repository Status:" -ForegroundColor Cyan
git branch -a
Write-Host ""
git log -1 --oneline

# Instructions for GitHub
Write-Host "`n[*] Deployment Instructions:" -ForegroundColor Yellow
Write-Host "  1. Link remote repository: git remote add origin <repository_url>"
Write-Host "  2. Push main branch:       git push -u origin main"
Write-Host "  3. Push all branches:      git push --all origin"
Write-Host "  4. Push tags:              git push --tags"

Write-Host "`n[+] Workspace setup completed successfully.`n" -ForegroundColor Green