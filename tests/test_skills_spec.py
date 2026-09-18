"""技能标准规约契约测试 (对标 agentskills.io 与 obra/superpowers 标准).

验证项：
1. 每个技能目录必须包含标准的 SKILL.md
2. 必须包含合法的 YAML Frontmatter (name 与 description 字段)
3. name 必须为合法 kebab-case 且与目录名严格一致
4. description 必须遵循 SDO 规范（以 'Use when...' 开头，纯声明触发时机）
5. 技能文档内的本地 Markdown 链接有效性检查（无断链/死链）
"""

import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).parent.parent.resolve()
SKILLS_DIR = REPO_ROOT / "skills"


def get_skill_dirs():
    """获取所有技能目录."""
    assert SKILLS_DIR.exists() and SKILLS_DIR.is_dir()
    return [d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith((".", "_"))]


@pytest.mark.parametrize("skill_dir", get_skill_dirs(), ids=lambda d: d.name)
def test_skill_has_skill_md(skill_dir: Path):
    """验证每个技能目录必须存在 SKILL.md."""
    skill_md = skill_dir / "SKILL.md"
    assert skill_md.exists(), f"技能目录 {skill_dir.name} 缺少 SKILL.md"
    assert skill_md.is_file(), f"{skill_md} 必须是普通文件"


@pytest.mark.parametrize("skill_dir", get_skill_dirs(), ids=lambda d: d.name)
def test_skill_frontmatter_validity(skill_dir: Path):
    """验证 YAML Frontmatter 格式合规性与 SDO 要求."""
    skill_md = skill_dir / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    # Frontmatter 必须以 --- 起始并以 --- 闭合
    assert content.startswith("---\n"), f"{skill_md} 必须以 YAML Frontmatter (---) 开头"
    parts = content.split("---\n", 2)
    assert len(parts) >= 3, f"{skill_md} 缺失闭合的 Frontmatter 分隔符 (---)"

    fm_text = parts[1]

    # 提取 name
    name_match = re.search(r"^name:\s*([^\n]+)$", fm_text, re.MULTILINE)
    assert name_match, f"{skill_md} Frontmatter 中缺少 'name' 字段"
    skill_name = name_match.group(1).strip().strip("\"'")
    
    # 验证 name 命名与目录名一致性及 kebab-case
    assert skill_name == skill_dir.name, f"{skill_md} 中的 name '{skill_name}' 与目录名 '{skill_dir.name}' 不一致"
    assert re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", skill_name), f"技能名称 '{skill_name}' 必须符合小写 kebab-case 格式"

    # 提取 description
    desc_match = re.search(r"^description:\s*(.+)$", fm_text, re.MULTILINE)
    assert desc_match, f"{skill_md} Frontmatter 中缺少 'description' 字段"
    description = desc_match.group(1).strip().strip("\"'")

    # 验证 SDO 规范：必须以 Use when 开头
    assert description.startswith("Use when"), f"{skill_md} 的 description 必须遵循 SDO 规范以 'Use when' 开头，当前为: '{description[:30]}...'"
    assert len(description) <= 1024, f"{skill_md} 的 description 超出 1024 字符限制"


@pytest.mark.parametrize("skill_dir", get_skill_dirs(), ids=lambda d: d.name)
def test_skill_markdown_links_integrity(skill_dir: Path):
    """验证 SKILL.md 内部引用的本地文件路径有效（死链检测）."""
    skill_md = skill_dir / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    # 匹配形如 [text](path) 的 Markdown 链接（排除 http/https/mailto/#锚点）
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for match in link_pattern.finditer(content):
        link_target = match.group(2).strip()
        if link_target.startswith(("http://", "https://", "mailto:", "#", "file://")):
            continue

        # 处理可能带锚点的情况，例如 templates/foo.md#section
        target_file = link_target.split("#")[0]
        if not target_file:
            continue

        resolved_path = (skill_dir / target_file).resolve()
        assert resolved_path.exists(), f"{skill_md} 中引用的链接 '{link_target}' 目标不存在: {resolved_path}"
