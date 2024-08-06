# Steps in using GIT

# Git standards

## Branch Names

1. Start with the reason for creations
   - bugfix
   - feature
   - refactor

Example: `feature/create-forum`

## Commit messages

Prefix should follow the following according to the code

```
build | ci | docs | feat | fix | perf | refactor | style | test | chore | revert | bump
```

Example: `feat: added fps counter to detection`

# Getting started

## Setting up your own feature / branch

1. `git clone <repo>` - clone repo if needed
2. `git checkout -b <feature/amazing-new-feature>`

## Making changes

3. `git add -A`
4. `git commit -a`
5. `git push` - git push upstream may be needed

## Fixing conflicts

6. Once all changes have been made make sure to get the latest from the branch you plan to merge into.
7. `git fetch` - Gets latest branches
8. `git switch <branch_name>` - switches branches to develop
9. `git pull` - gets the latest version
10. `git switch <feature/amazing-new-feature>`
11. `git merge <branch_name>` - merge develop
12. Open VScode (`code .`) and fix all conflicts
13. Repeat steps in [Making changes](#Making-changes)

## Pull Request to the desired branch and merge on Github

# Commonly used git commands

```git
git clone <repo name>               : Clone a repo
git fetch                           : Fetch information about any new branches
git pull                            : Pull the latest update from branch
git add -a                          : Add new files to git
git commit -A                       : Commit message
git switch <branch name>            : Switch to an existing branch
git checkout -b <new branch name>   : Create a new branch based on current branch
git merge <branch name>             : Merge current branch with another
```
