---
name: skill-manager
description: Manage skill lifecycle including creation and installation. Use when users want to create a new skill or install existing skills. Creates skills in ~/my_skills by default and installs via symlink to ~/.claude/skills.
---

# Skill Manager

Manage skill lifecycle: creation, installation, and symlink management.

## Workflow

1. **Create Skill** - Use `@skill-creator` to guide the creation process
2. **Initialize** - Create skill structure in `~/my_skills/<skill-name>`
3. **Install** - Create symlink in `~/.claude/skills/<skill-name>` pointing to `~/my_skills/<skill-name>`

## Usage

### Create a New Skill

When user wants to create a skill:

1. Reference `@skill-creator` for skill creation guidance
2. Create skill in `~/my_skills/<skill-name>`
3. Run installation script to create symlink

```bash
# Create symlink for the new skill
~/my_skills/skill-manager/scripts/install_skill.sh <skill-name>
```

### Manual Installation

```bash
# Create symlink manually
ln -s ~/my_skills/<skill-name> ~/.claude/skills/<skill-name>

# Verify symlink
ls -la ~/.claude/skills/<skill-name>
```

## Directory Structure

```
~/my_skills/
├── skill-manager/          # This skill
│   ├── SKILL.md
│   ├── scripts/
│   │   └── install_skill.sh
│   └── references/
├── <new-skill>/           # Skills created here
└── ...

~/.claude/skills/          # Symlinks point here
├── <new-skill> -> ~/my_skills/<new-skill>
└── ...
```

## Key Points

- **Source**: Skills stored in `~/my_skills/`
- **Installation**: Symlinks in `~/.claude/skills/` point to source
- **Updates**: Modify source in `~/my_skills/`, symlink stays valid
- **Removal**: Remove both symlink and source directory

## Installation Script

The `install_skill.sh` script handles symlink creation:

```bash
~/my_skills/skill-manager/scripts/install_skill.sh <skill-name>
```

This script:
1. Checks if skill exists in `~/my_skills/`
2. Creates symlink in `~/.claude/skills/`
3. Reports success/failure status
