# Skill Creation Examples

## Example 1: Create a Simple Utility Skill

**User Request:** "创建一个测试LED的skill"

**Workflow:**
1. Use `@skill-creator` to understand requirements
2. Create skill in `~/my_skills/led-tester`
3. Run: `~/my_skills/skill-manager/scripts/install_skill.sh led-tester`

## Example 2: Create a Skill with Scripts

**User Request:** "创建一个管理数据库的skill，包含Python脚本"

**Workflow:**
1. Use `@skill-creator` for database skill guidance
2. Create skill in `~/my_skills/db-manager`
3. Add scripts to `~/my_skills/db-manager/scripts/`
4. Run: `~/my_skills/skill-manager/scripts/install_skill.sh db-manager`

## Example 3: Update Existing Skill

**User Request:** "修改bin_test skill"

**Workflow:**
1. Edit files in `~/my_skills/bin_test/`
2. Changes automatically reflect in `~/.claude/skills/bin_test` (symlink)
3. No reinstallation needed

## Example 4: Remove a Skill

**User Request:** "删除skill-manager"

**Workflow:**
1. Remove symlink: `rm ~/.claude/skills/skill-manager`
2. Remove source: `rm -rf ~/my_skills/skill-manager`
