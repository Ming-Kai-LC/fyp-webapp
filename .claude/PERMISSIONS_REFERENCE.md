# Claude Code Auto-Approved Commands Reference

This document lists all commands that are auto-approved in `.claude/settings.local.json`.

Last Updated: 2025-11-23

---

## File Operations

**Full CRUD Access:**
- `Read(*)` - Read any file
- `Edit(*)` - Edit any file
- `Write(*)` - Write any file

**Skill Files (Explicit):**
- `Read(.claude/skills/**/*.md)` - Read skill files
- `Edit(.claude/skills/**/*.md)` - Edit skill files
- `Write(.claude/skills/**/*.md)` - Write skill files
- `Read(.claude/CLAUDE.md)` - Read main documentation
- `Edit(.claude/CLAUDE.md)` - Edit main documentation
- `Write(.claude/CLAUDE.md)` - Write main documentation

---

## Django Management Commands

All commands run through virtual environment: `venv/Scripts/python.exe`

**General:**
- `venv/Scripts/python.exe:*` - Any Python command
- `venv/Scripts/python.exe manage.py:*` - Any Django management command

**Specific Commands:**
- `venv/Scripts/python.exe manage.py makemigrations:*` - Create migrations
- `venv/Scripts/python.exe manage.py migrate:*` - Apply migrations
- `venv/Scripts/python.exe manage.py runserver:*` - Start dev server
- `venv/Scripts/python.exe manage.py createsuperuser:*` - Create admin user
- `venv/Scripts/python.exe manage.py collectstatic:*` - Collect static files
- `venv/Scripts/python.exe manage.py shell:*` - Django shell
- `venv/Scripts/python.exe manage.py startapp:*` - Create new Django app
- `venv/Scripts/python.exe manage.py test:*` - Run tests
- `venv/Scripts/python.exe manage.py check:*` - System checks
- `venv/Scripts/python.exe manage.py showmigrations:*` - Show migration status
- `venv/Scripts/python.exe manage.py loaddata:*` - Load fixtures
- `venv/Scripts/python.exe manage.py dumpdata:*` - Dump data
- `django-admin:*` - Django admin commands

---

## Python & Package Management

**Python:**
- `python:*` - Any Python command

**Pip (Virtual Environment):**
- `pip:*` - Generic pip
- `pip install:*` - Install packages
- `venv/Scripts/pip.exe:*` - Any pip command in venv
- `venv/Scripts/pip.exe install:*` - Install packages in venv
- `venv/Scripts/pip.exe uninstall:*` - Uninstall packages
- `venv/Scripts/pip.exe freeze:*` - List installed packages
- `venv/Scripts/pip.exe list:*` - List packages

---

## Testing & Coverage

**Pytest:**
- `pytest:*` - Run pytest
- `venv/Scripts/python.exe -m pytest:*` - Run pytest via Python module

**Coverage:**
- `coverage:*` - Any coverage command
- `coverage run:*` - Run coverage
- `coverage report:*` - Show coverage report
- `coverage html:*` - Generate HTML coverage report
- `coverage xml:*` - Generate XML coverage report

---

## Git & GitHub

**Git:**
- `git:*` - Any git command
- `git add:*` - Stage files
- `git commit:*` - Create commits
- `git push:*` - Push to remote
- `git pull:*` - Pull from remote
- `git status:*` - Show status
- `git diff:*` - Show differences
- `git log:*` - Show commit history
- `git branch:*` - Branch operations
- `git checkout:*` - Checkout branches/files
- `git merge:*` - Merge branches
- `git stash:*` - Stash changes
- `git remote:*` - Remote operations

**GitHub CLI:**
- `gh:*` - Any gh command
- `gh pr:*` - Pull request operations
- `gh pr create:*` - Create pull requests
- `gh api:*` - GitHub API calls

---

## File System Commands

**Navigation:**
- `ls:*` - List files (Unix)
- `dir:*` - List files (Windows)
- `cd:*` - Change directory
- `pwd` - Print working directory

**File Operations:**
- `cat:*` - Display file contents
- `echo:*` - Print text
- `mkdir:*` - Create directories
- `touch:*` - Create empty files
- `cp:*` - Copy files
- `mv:*` - Move/rename files
- `find:*` - Find files
- `grep:*` - Search in files
- `tee:*` - Read from stdin and write to files
- `findstr:*` - Windows grep equivalent

---

## Utility Commands

**File Analysis:**
- `tree:*` - Display directory tree
- `tree /F` - Display directory tree with files (Windows)
- `which:*` - Locate command (Unix)
- `where:*` - Locate command (Windows)
- `wc:*` - Word count
- `wc -l:*` - Line count
- `head:*` - Show first lines
- `tail:*` - Show last lines
- `sort:*` - Sort lines
- `uniq:*` - Filter unique lines

**Network:**
- `curl:*` - Transfer data from URLs
- `wget:*` - Download files

---

## Code Quality Tools

**Formatters:**
- `black:*` - Python code formatter
- `isort:*` - Import sorter

**Linters:**
- `flake8:*` - Python linter
- `mypy:*` - Type checker
- `pylint:*` - Python linter
- `bandit:*` - Security linter

**Pre-commit:**
- `pre-commit:*` - Any pre-commit command
- `pre-commit run:*` - Run pre-commit hooks
- `pre-commit install:*` - Install pre-commit hooks

---

## Package Managers

- `npm:*` - Node package manager
- `yarn:*` - Yarn package manager
- `node:*` - Node.js runtime
- `poetry:*` - Python package manager

---

## System Commands (Windows)

- `set:*` - Set environment variables
- `done` - Command completion marker
- `nul` - Null device
- `timeout:*` - Delay execution
- `exit 0` - Exit with success
- `type:*` - Display file contents (Windows cat)
- `cls` - Clear screen (Windows)
- `clear` - Clear screen (Unix)

---

## Docker (Future Use)

- `docker:*` - Any Docker command
- `docker-compose:*` - Docker Compose
- `docker ps:*` - List containers
- `docker images:*` - List images
- `docker logs:*` - View container logs

---

## Web & Search

- `WebSearch` - Web search capability

---

## Miscellaneous

- `Bash(commontemplatetags__init__.py)` - Legacy command

---

## ⚠️ DENIED Commands (For Safety)

These commands are **ALWAYS BLOCKED**:

**Sensitive Files:**
- `Read(.env)` - Environment files
- `Read(.env.*)` - Environment variants
- `Read(**/.env)` - Nested env files
- `Read(**/secrets/**)` - Secrets directory
- `Read(**/credentials.json)` - Credentials
- `Edit(.env)` - Edit environment files
- `Edit(.env.*)` - Edit environment variants
- `Edit(**/.env)` - Edit nested env files

**Dangerous Commands:**
- `rm -rf /*` - Delete everything
- `rm -rf:*` - Force delete
- `sudo rm:*` - Root delete
- `sudo:*` - Root access
- `su:*` - Switch user
- `git push --force:*` - Force push
- `git push -f:*` - Force push (short)
- `python manage.py flush:*` - Delete all data
- `python manage.py dbshell:*` - Direct database access
- `dropdb:*` - Drop database
- `shutdown:*` - Shutdown system
- `reboot:*` - Reboot system
- `curl -X DELETE:*` - HTTP DELETE
- `wget -O /etc/*` - Download to system files
- `dd:*` - Disk operations

---

## Quick Usage Examples

### Create a new Django app
```bash
venv/Scripts/python.exe manage.py startapp my_new_app
```

### Run migrations
```bash
venv/Scripts/python.exe manage.py makemigrations
venv/Scripts/python.exe manage.py migrate
```

### Install package
```bash
venv/Scripts/pip.exe install package-name
```

### Run tests with coverage
```bash
venv/Scripts/python.exe -m pytest --cov=module_name
coverage report
coverage html
```

### Create git commit
```bash
git add .
git commit -m "feat(module): Add new feature"
```

### Create pull request
```bash
gh pr create --title "Title" --body "Description"
```

### Run code quality checks
```bash
black .
flake8 .
mypy .
```

---

## Notes

1. **Virtual Environment:** All Python/Django commands use `venv/Scripts/python.exe` (Windows)
2. **Wildcards:** Commands with `:*` accept any arguments
3. **Safety:** Dangerous commands are always blocked for security
4. **Skill Files:** Full CRUD access to `.claude/skills/` and `.claude/CLAUDE.md`
5. **Auto-Approval:** Commands listed in "allow" section run without asking permission

---

## Updating Permissions

To add new commands, edit `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(new-command:*)"
    ]
  }
}
```

Restart Claude Code after changes.
