#!/bin/bash
# Install skill by creating symlink from ~/.claude/skills to ~/my_skills

set -e

SKILL_NAME="$1"
SOURCE_DIR="$HOME/my_skills/$SKILL_NAME"
LINK_DIR="$HOME/.claude/skills/$SKILL_NAME"

if [ -z "$SKILL_NAME" ]; then
    echo "Usage: $0 <skill-name>"
    exit 1
fi

# Check if source exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Skill source not found: $SOURCE_DIR"
    echo "Create the skill first using @skill-creator"
    exit 1
fi

# Check if SKILL.md exists
if [ ! -f "$SOURCE_DIR/SKILL.md" ]; then
    echo "Error: SKILL.md not found in $SOURCE_DIR"
    exit 1
fi

# Remove existing symlink if present
if [ -L "$LINK_DIR" ]; then
    echo "Removing existing symlink: $LINK_DIR"
    rm "$LINK_DIR"
fi

# Create symlink
echo "Creating symlink: $LINK_DIR -> $SOURCE_DIR"
ln -s "$SOURCE_DIR" "$LINK_DIR"

# Verify
if [ -L "$LINK_DIR" ]; then
    echo "Success! Skill installed."
    echo "Source: $(realpath $SOURCE_DIR)"
    echo "Link: $LINK_DIR"
else
    echo "Error: Failed to create symlink"
    exit 1
fi
