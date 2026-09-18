"""针对架构画板渲染引擎 (render_architecture_board.py) 的单元测试.

测试范围涵盖：
- Mermaid 图元代码精确提取 (从 .mmd 及 markdown 代码块)
- 自包含交互式 HTML 骨架构建与配置注入
- 5 维视图搜集与端到端画板生成
"""

import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# 加入搜索路径
TEST_DIR = Path(__file__).parent.resolve()
REPO_ROOT = TEST_DIR.parent.resolve()
SCRIPTS_DIR = REPO_ROOT / "scripts"
POLISHER_DIR = REPO_ROOT / "skills" / "architecture-refinement" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(POLISHER_DIR))

from render_architecture_board import (  # noqa: E402
    build_interactive_html,
    extract_mermaid_code,
    render_board,
)
from document_polisher import ArchitectureDocumentPolisher  # noqa: E402


@pytest.fixture
def temp_ws() -> Generator[Path, None, None]:
    """创建临时测试工作区."""
    with tempfile.TemporaryDirectory(prefix="test_render_") as tmp:
        yield Path(tmp)


def test_extract_mermaid_code_from_mmd(temp_ws: Path) -> None:
    """测试从纯 .mmd 文件中提取代码."""
    mmd_file = temp_ws / "test.mmd"
    sample_code = "graph TD\n    A --> B\n"
    mmd_file.write_text(sample_code, encoding="utf-8")

    extracted = extract_mermaid_code(mmd_file)
    assert extracted.strip() == sample_code.strip()


def test_extract_mermaid_code_from_markdown(temp_ws: Path) -> None:
    """测试从包含 ```mermaid 块的 markdown 中提取代码."""
    md_file = temp_ws / "test.md"
    md_content = """# Title

Some text here.

```mermaid
stateDiagram-v2
    [*] --> Active
```

More explanations.
"""
    md_file.write_text(md_content, encoding="utf-8")

    extracted = extract_mermaid_code(md_file)
    assert "stateDiagram-v2" in extracted
    assert "[*] --> Active" in extracted
    assert "# Title" not in extracted


def test_build_interactive_html() -> None:
    """测试构建的 HTML 具有完整的控制组件与主题切换逻辑."""
    diagrams = [
        {"title": "Test Diagram", "code": "graph TD\n A --> B", "file": "test.mmd"}
    ]
    html_out = build_interactive_html("Test System", diagrams)

    assert "<!DOCTYPE html>" in html_out
    assert "Test System" in html_out
    assert "mermaid.initialize" in html_out
    assert "theme-toggle" in html_out
    assert "export-svg" in html_out
    assert "svgPanZoom" in html_out


def test_render_board_integration(temp_ws: Path) -> None:
    """测试从完整 02-architecture-design/ 目录提取 5 维图表并生成画板."""
    models_dir = temp_ws / "02-architecture-design"
    models_dir.mkdir(parents=True, exist_ok=True)

    (models_dir / "c4-context.mmd").write_text("graph TB\n C4Context", encoding="utf-8")
    (models_dir / "c4-container-overview.mmd").write_text("graph TB\n C4Container", encoding="utf-8")
    (models_dir / "domain-logical-model.md").write_text("```mermaid\nstateDiagram-v2\n [*] --> A\n```", encoding="utf-8")
    (models_dir / "interaction-sequence.mmd").write_text("sequenceDiagram\n A->>B: Call", encoding="utf-8")
    (models_dir / "data-flow.mmd").write_text("flowchart TD\n In --> Out", encoding="utf-8")

    out_file = temp_ws / "board.html"
    res_path = render_board(temp_ws, output_path=out_file, project_name="Full Mesh Arch")

    assert res_path.exists()
    assert res_path == out_file.resolve()
    content = res_path.read_text(encoding="utf-8")
    assert "Full Mesh Arch" in content
    assert "C4 Context" in content
    assert "Interaction Sequence" in content
    assert "Data Flow Pipeline" in content


def test_rendered_board_passes_js_syntax_and_audit(temp_ws: Path) -> None:
    """自动化硬门禁：确保编译出的自包含 HTML 通过真实 Node.js 语法分析与数据负载校验."""
    arch_dir = temp_ws / "docs" / "architecture"
    req_dir = arch_dir / "01-requirements"
    req_dir.mkdir(parents=True, exist_ok=True)
    (req_dir / "01-01-business-drivers.md").write_text(
        "# 🩺 SurgicalRobot Teleoperation - 微创手术机器人超低时延系统\n\n## 驱动力\n- 1ms 控制闭环",
        encoding="utf-8",
    )

    out_file = temp_ws / "test_board.html"
    board_path = render_board(arch_dir, output_path=out_file)

    polisher = ArchitectureDocumentPolisher(arch_dir)
    report = polisher.audit_rendered_board(board_path)

    assert report.is_valid, f"画板未能通过质量门禁审计: {report.errors}"
    assert report.js_syntax_passed, "内嵌 JavaScript 未能通过 Node.js 编译检查"
    assert report.data_payload_valid, "window.__CANVAS_DATA__ 数据未成功注入或 JSON 非法"
    assert report.artifacts_count >= 1, "工件数量必须大于等于 1"
    assert "SurgicalRobot" in report.project_name, f"项目名称解析异常: {report.project_name}"


def test_rendered_board_handles_newlines_and_quotes(temp_ws: Path) -> None:
    """自动化硬门禁：防退化测试，确保包含换行、双引号、多行代码块的工件不会引发 JS 语法崩溃."""
    arch_dir = temp_ws / "docs" / "architecture"
    des_dir = arch_dir / "02-architecture-design"
    des_dir.mkdir(parents=True, exist_ok=True)

    tricky_content = """# Title with "Double Quotes" and 'Single Quotes'
Line 1\r\nLine 2 with \\"escapes\\"
```json
{
  "key": "value with \\n newline and \\"nested quotes\\""
}
```
"""
    (des_dir / "02-01-system-overview.md").write_text(tricky_content, encoding="utf-8")

    out_file = temp_ws / "quotes_board.html"
    board_path = render_board(arch_dir, output_path=out_file, project_name="Tricky Quoting Project")

    polisher = ArchitectureDocumentPolisher(arch_dir)
    report = polisher.audit_rendered_board(board_path)

    assert report.is_valid, f"含复杂引号换行的画板未能通过审计: {report.errors}"
    assert report.js_syntax_passed, "含复杂引号换行的脚本未能通过 Node.js 语法检查"
