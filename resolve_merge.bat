@echo off
set /p BRANCH_NAME="Enter the feature branch name (e.g., 00y008-codex/generate-laravel-migration-tasks-from-legacy-php-files): "

echo Fetching latest changes from origin...
git fetch origin

echo Checking out the feature branch: %BRANCH_NAME%
git checkout %BRANCH_NAME%

echo Merging main into %BRANCH_NAME% and resolving conflicts by accepting incoming changes...
git merge origin/main --no-commit --no-ff

echo Resolving conflicts by accepting 'theirs' (incoming changes)...
git diff --name-only --diff-filter=U | findstr /v /c:"^$" > conflicted_files.txt
for /f "tokens=*" %%f in (conflicted_files.txt) do (
    echo Resolving %%f
    git checkout --theirs "%%f"
)
del conflicted_files.txt

echo Staging resolved files...
git add .

echo Committing the merge...
git commit -m "Automated merge: Resolved conflicts by accepting incoming changes from main"

echo Force pushing the branch...
git push origin %BRANCH_NAME% --force

echo Merge and push complete.
pause