"""架构可视化画板渲染引擎 (Architecture Board HTML Renderer).

吸收 Archify 等现代化架构看板工具的精髓，将系统四层生命周期中产生的所有
编号规范输出物（需求、AOD/C4/CM/CDM/OM 图谱、ADR 决策、OpenAPI 契约、组织计划）
统一编译为单文件、自包含、支持深浅主题切换、平移缩放 (Pan & Zoom)、高清矢量导出
与全文规约阅读的交互式 HTML 架构看板。
看板内容严格按照输出物编号递增顺序组织与呈现。
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def synthesize_openapi_diagram(content: str, filename: str) -> str:
    """从 OpenAPI YAML/JSON 内容中提取路由端点并合成接口契约拓扑图."""
    title = "OpenAPI 3.0 API Specification"
    endpoints: List[Tuple[str, str, str]] = []
    try:
        import yaml
        data = yaml.safe_load(content)
        if isinstance(data, dict):
            title = data.get("info", {}).get("title", title)
            paths = data.get("paths", {})
            if isinstance(paths, dict):
                for p, pdata in paths.items():
                    if isinstance(pdata, dict):
                        for m, mdata in pdata.items():
                            if m.lower() in ("get", "post", "put", "delete", "patch"):
                                summary = mdata.get("summary", "") if isinstance(mdata, dict) else ""
                                endpoints.append((m.upper(), str(p), str(summary)))
    except Exception:
        m_title = re.search(r"title:\s*([^\n\r]+)", content)
        if m_title:
            title = m_title.group(1).strip("\"' ")
        path_matches = re.findall(r"(\/[a-zA-Z0-9_\-\/\{\}]+):\s*\n\s*([a-z]+):", content)
        for p, m in path_matches:
            endpoints.append((m.upper(), p, ""))

    if not endpoints:
        endpoints = [("GET", "/api/v1/status", "服务状态检查")]

    clean_title = re.sub(r'["\[\]]', "", title)
    lines = [
        "flowchart LR",
        '    Client["🌐 外部调用方 / API Client"]',
        f'    subgraph Spec ["⚡ {clean_title}"]',
        "        direction TB",
    ]
    for i, (m, p, s) in enumerate(endpoints[:15]):
        node_id = f"EP{i}"
        desc = f"<b>{m}</b> {p}"
        if s:
            clean_s = re.sub(r'["\[\]]', "", s)
            desc += f"<br><i>{clean_s}</i>"
        lines.append(f'        {node_id}["{desc}"]')
        lines.append(f"        Client --> {node_id}")
    lines.append("    end")
    return "\n".join(lines)


def synthesize_skeleton_diagram(content: str, filename: str) -> str:
    """从 Walking Skeleton JSON 规约中提取工程目录与分层依赖拓扑图."""
    try:
        data = json.loads(content)
    except Exception:
        data = {}

    pattern = data.get("architecture_pattern", "Hexagonal")
    dirs = data.get("directories", ["src", "tests"])
    immutables = set(data.get("immutable_paths", []))

    clean_pattern = re.sub(r'["\[\]]', "", str(pattern))
    lines = [
        "flowchart TD",
        f'    subgraph Skeleton ["🧩 物理工程骨架规约 ({clean_pattern} 架构)"]',
        "        direction TB",
    ]

    dir_nodes = []
    for i, d in enumerate(dirs):
        node_id = f"DIR{i}"
        tag = " (不可变边界强契约)" if d in immutables else ""
        role = ""
        if "domain" in d:
            role = "<br><i>纯领域核心实体与无依赖规则</i>"
        elif "ports" in d:
            role = "<br><i>驱动与被驱动端口契约接口</i>"
        elif "adapters" in d:
            role = "<br><i>基础设施、持久化与网络适配器</i>"
        elif "services" in d:
            role = "<br><i>业务用例编排与应用服务</i>"
        elif "tests" in d:
            role = "<br><i>物理验证与自动化契约测试</i>"

        lines.append(f'        {node_id}["📁 {d}{tag}{role}"]')
        dir_nodes.append((d, node_id))

    mapping = dict(dir_nodes)
    if "src/adapters" in mapping and "src/ports" in mapping:
        lines.append(f"        {mapping['src/adapters']} -->|依赖实现| {mapping['src/ports']}")
    if "src/services" in mapping and "src/ports" in mapping:
        lines.append(f"        {mapping['src/services']} -->|依赖调用| {mapping['src/ports']}")
    if "src/ports" in mapping and "src/domain" in mapping:
        lines.append(f"        {mapping['src/ports']} -->|定义契约| {mapping['src/domain']}")
    if "tests" in mapping and "src/domain" in mapping:
        lines.append(f"        {mapping['tests']} -.->|物理断言| {mapping['src/domain']}")

    lines.append("    end")
    return "\n".join(lines)


def extract_mermaid_code(file_path: Path) -> str:
    """从 .mmd 或 .md 文件中提取纯净的 Mermaid 图表源码，或从 OpenAPI/Spec 契约中智能合成拓扑图."""
    if not file_path.exists():
        return ""
    try:
        content = file_path.read_text(encoding="utf-8").strip()
    except Exception:
        return ""

    if file_path.suffix.lower() == ".mmd":
        return content

    # 若为 markdown 文件，正则提取第一个 ```mermaid 代码块 (兼容各种换行符与大小写)
    if file_path.suffix.lower() in (".md", ".markdown"):
        matches = re.findall(r"```(?:mermaid)\s*[\r\n]+(.*?)[\r\n]+```", content, re.DOTALL | re.IGNORECASE)
        if matches:
            return matches[0].strip()
        return ""

    # 若为 OpenAPI 接口契约规范文件 (.yaml/.yml/.json)
    if file_path.suffix.lower() in (".yaml", ".yml") or "openapi" in file_path.name.lower():
        if "openapi:" in content or "paths:" in content:
            return synthesize_openapi_diagram(content, file_path.name)

    # 若为 Walking Skeleton 工程骨架生成规约 (.json)
    if file_path.suffix.lower() == ".json" and ("walking-skeleton" in file_path.name.lower() or "scaffold" in file_path.name.lower()):
        return synthesize_skeleton_diagram(content, file_path.name)

    return ""


def validate_mermaid_syntax(code: str) -> Tuple[bool, str]:
    """静态检查 Mermaid 代码的语法基础合法性，防止前端渲染报错."""
    cleaned = code.strip()
    if not cleaned:
        return False, "Mermaid 代码为空"

    valid_headers = (
        "graph", "flowchart", "sequencediagram", "classdiagram",
        "statediagram", "statediagram-v2", "erdiagram", "gantt",
        "pie", "gitgraph", "c4context", "c4container", "c4component", "c4deployment"
    )
    # 忽略注释行与空行，获取首个有效指令
    effective_lines = [
        line.strip() for line in cleaned.splitlines()
        if line.strip() and not line.strip().startswith("%%")
    ]
    if not effective_lines:
        return False, "Mermaid 代码仅包含注释或空行"

    first_line = effective_lines[0].lower()
    if not any(first_line.startswith(h) for h in valid_headers):
        return False, f"未知的 Mermaid 图表声明: '{first_line}'，必须以有效图类型开头"

    # 检查未在引号内的裸 < 或 > 处于节点标签中
    unquoted_tag_pattern = re.compile(r'\[([^"\]]*?[<>][^"\]]*?)\]')
    matches = unquoted_tag_pattern.findall(cleaned)
    if matches:
        return False, f"节点文本包含未加双引号的 '<' 或 '>' 字符: '{matches[0]}'，必须使用双引号包裹"

    return True, ""


def parse_artifact_number(filename: str, rel_path: str) -> Tuple[str, str]:
    """从文件名或相对路径中提取出标准编号 (如 01-01, 02-04, 03-08-01 等)."""
    # 匹配例如 01-02 或 03-08-01
    m = re.search(r"\b(\d{2}-\d{2}(?:-\d{2})?)\b", filename)
    if m:
        return m.group(1), m.group(1)

    # 尝试从路径的父目录和文件名推断
    parts = Path(rel_path).parts
    if len(parts) >= 2:
        dir_m = re.match(r"^(\d{2})", parts[0])
        if dir_m:
            stage_num = dir_m.group(1)
            # 常见文件名映射
            known_mapping = {
                "business-drivers": f"{stage_num}-01",
                "functional-requirements": f"{stage_num}-02",
                "non-functional-requirements": f"{stage_num}-03",
                "nfr-matrix": f"{stage_num}-03",
                "architecture-requirements-checklist": f"{stage_num}-04",
                "constraints-and-assumptions": f"{stage_num}-05",
                "system-overview": f"{stage_num}-01",
                "architecture-overview-diagram": f"{stage_num}-02",
                "c4-context": f"{stage_num}-03",
                "component-model": f"{stage_num}-04",
                "c4-container-overview": f"{stage_num}-05",
                "domain-logical-model": f"{stage_num}-06",
                "conceptual-data-model": f"{stage_num}-06",
                "sequence-and-dataflow": f"{stage_num}-07",
                "operational-model": f"{stage_num}-01",
                "deployment-architecture": f"{stage_num}-02",
                "data-architecture": f"{stage_num}-03",
                "observability-design": f"{stage_num}-04",
                "failure-resilience-matrix": f"{stage_num}-05",
                "interface-contracts-overview": f"{stage_num}-06",
                "openapi": f"{stage_num}-07",
                "adr-index": f"{stage_num}-08-00",
                "organization-structure": f"{stage_num}-01",
                "estimation-and-plan": f"{stage_num}-02",
                "roadmap-and-first-step": f"{stage_num}-02",
                "first-step-poc": f"{stage_num}-03",
                "poc-charter-and-report": f"{stage_num}-03",
                "walking-skeleton-spec": f"{stage_num}-04",
                "agent-rules": f"{stage_num}-05",
            }
            for k, v in known_mapping.items():
                if k in filename.lower():
                    return v, v
            return f"{stage_num}-99", f"{stage_num}-99"

    return "99-99", "99-99"


def extract_artifact_title(file_path: Path, num_str: str) -> str:
    """提取输出物可读标题."""
    name_stem = file_path.stem
    # 去除前缀数字
    clean_name = re.sub(r"^\d{2}-\d{2}(?:-\d{2})?-?", "", name_stem)
    
    title_dictionary = {
        "business-drivers": "业务驱动力与商业目标 (Business Drivers)",
        "non-functional-requirements": "质量属性与 NFR 矩阵 (Non-Functional Requirements)",
        "nfr-matrix": "质量属性与 NFR 矩阵 (Non-Functional Requirements)",
        "functional-requirements": "核心功能需求与用例规约 (Functional Requirements)",
        "architecture-requirements-checklist": "架构需求核对清单 ARC (Architecture Requirements Checklist)",
        "constraints-and-assumptions": "硬约束、假设与不变量编目 (Constraints & Assumptions)",
        "system-overview": "系统架构总览与控制原则 (System Overview)",
        "architecture-overview-diagram": "5层架构全景概览图 (5-Layer AOD)",
        "c4-context": "C4 Context 系统上下文边界图 (System Context)",
        "component-model": "逻辑与物理组件模型 CM (Component Model)",
        "c4-container-overview": "C4 Container 容器拓扑图 (Container Overview)",
        "conceptual-data-model": "概念数据模型与统一语言词典 (CDM & Glossary)",
        "domain-logical-model": "领域逻辑模型与实体关系图 (Domain Logical Model)",
        "sequence-and-dataflow": "端到端交互时序与核心数据流 (Sequence & Data Flow)",
        "interaction-sequence": "端到端核心交互时序图 (Interaction Sequence)",
        "data-flow": "数据流向与生命周期状态机 (Data Flow Pipeline & FSM)",
        "operational-model": "物理运行模型与节点规范 OM (Operational Model)",
        "deployment-architecture": "部署拓扑与高可用基础设施 (Deployment Architecture)",
        "data-architecture": "数据架构与冷热分级存储 (Data Architecture)",
        "observability-design": "统一可观测性与告警指标 (Observability Design)",
        "failure-resilience-matrix": "FMEA 故障模式与容灾矩阵 (Failure Resilience Matrix)",
        "interface-contracts-overview": "系统边界强契约与接口规约概览 (Interface Contracts)",
        "openapi": "OpenAPI 3.0 标准接口规范契约 (OpenAPI Spec)",
        "adr-index": "架构决策记录全景索引 (ADR Index)",
        "organization-structure": "康威定律对齐与逆康威组织阵型 (Organization Structure)",
        "estimation-and-plan": "工作量科学估算与敏捷交付计划 (Estimation & Delivery Plan)",
        "first-step-poc": "破冰验证切片与破坏性混沌实验 (First-Step PoC)",
        "poc-charter-and-report": "破冰验证切片与破坏性混沌实验 (First-Step PoC)",
        "walking-skeleton-spec": "Walking Skeleton 物理工程骨架生成规约 (Scaffold Spec)",
        "agent-rules": "AI 与开发者执行纪律与安全围栏 (Engineering Guardrails)",
    }

    for k, v in title_dictionary.items():
        if k in clean_name.lower():
            return f"[{num_str}] {v}"

    # 从文件首行标题提取
    if file_path.suffix.lower() in (".md", ".markdown") and file_path.exists():
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
            for line in lines[:5]:
                if line.startswith("# "):
                    h1 = line.lstrip("# ").strip()
                    return f"[{num_str}] {h1}"
        except Exception:
            pass

    beautified = clean_name.replace("-", " ").replace("_", " ").title()
    return f"[{num_str}] {beautified}"


def get_layer_group(num_str: str) -> Tuple[int, str]:
    """根据编号前缀确定所属架构层级."""
    if num_str.startswith("01"):
        return 1, "Layer 1 · 业务与需求定义 (Requirements & Constraints)"
    if num_str.startswith("02"):
        return 2, "Layer 2 · 概念与逻辑架构设计 (Architecture & Structural Design)"
    if num_str.startswith("03"):
        return 3, "Layer 3 · 物理工程权衡与边界强契约 (Engineering & Physics Decisions)"
    if num_str.startswith("04"):
        return 4, "Layer 4 · 交付实施、组织阵型与工程围栏 (Delivery & Scaffolding)"
    return 5, "Layer 5 · 其他综合架构工件 (Supplementary Artifacts)"


def collect_artifacts(ws: Path) -> List[Dict[str, Any]]:
    """扫描工作区所有输出物，严格按编号排序解析."""
    items: List[Dict[str, Any]] = []
    seen_files = set()

    for file_path in sorted(ws.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.name.startswith(".") or "archive" in str(file_path):
            continue
        if file_path.suffix.lower() not in (".md", ".mmd", ".yaml", ".yml", ".json"):
            continue
        if file_path.name in (".state.json", "architecture_board.html"):
            continue

        rel_path = str(file_path.relative_to(ws))
        num_str, sort_key = parse_artifact_number(file_path.name, rel_path)
        layer_num, layer_title = get_layer_group(num_str)
        title = extract_artifact_title(file_path, num_str)

        raw_content = ""
        try:
            raw_content = file_path.read_text(encoding="utf-8")
        except Exception:
            pass

        mermaid_code = extract_mermaid_code(file_path)
        has_diagram = bool(mermaid_code.strip())
        if has_diagram:
            is_valid, err = validate_mermaid_syntax(mermaid_code)
            if not is_valid:
                print(f"⚠️ [Mermaid语法警告] {file_path.name}: {err}", file=sys.stderr)

        # 确定展示标签
        tag = "📄 文档"
        if file_path.suffix.lower() == ".mmd" or (has_diagram and file_path.suffix.lower() == ".md" and len(raw_content.splitlines()) < 40):
            tag = "📊 图表"
        elif file_path.suffix.lower() in (".yaml", ".yml"):
            tag = "⚡ 契约"
        elif "adr-" in file_path.name.lower():
            tag = "⚖️ 决策"
        elif file_path.suffix.lower() == ".json":
            tag = "🧩 规约"

        items.append({
            "num": num_str,
            "sort_key": sort_key,
            "layer_num": layer_num,
            "layer_title": layer_title,
            "title": title,
            "filename": file_path.name,
            "rel_path": rel_path,
            "has_diagram": has_diagram,
            "mermaid_code": mermaid_code,
            "raw_content": raw_content,
            "tag": tag,
            "file_ext": file_path.suffix.lower(),
        })
        seen_files.add(file_path.resolve())

    # 按编号排序键严格升序排列
    items.sort(key=lambda x: (x["sort_key"], x["rel_path"]))
    return items


def build_interactive_html(
    project_name: str,
    artifacts: List[Dict[str, Any]],
    metadata: Optional[Dict[str, str]] = None,
) -> str:
    """构建现代化、按编号严格展示的高颜值自包含 HTML 架构画板."""
    meta = metadata or {}
    status_tag = meta.get("status", "ACTIVE")

    artifacts_json = json.dumps(artifacts, ensure_ascii=False)

    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(project_name)} - 架构全景交互画板</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
  <script>
    if (typeof mermaid === "undefined") {{
      document.write('<script src="https://unpkg.com/mermaid@10.9.1/dist/mermaid.min.js"><\\/script>');
    }}
  </script>
  <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
  <script>
    if (typeof svgPanZoom === "undefined") {{
      document.write('<script src="https://unpkg.com/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"><\\/script>');
    }}
  </script>
  <script src="https://cdn.jsdelivr.net/npm/marked@12.0.1/marked.min.js"></script>
  <style>
    :root {{
      --bg-primary: #0f172a;
      --bg-secondary: #1e293b;
      --bg-tertiary: #334155;
      --bg-board: #0b0f19;
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --text-muted: #64748b;
      --accent: #38bdf8;
      --accent-hover: #0ea5e9;
      --accent-bg: rgba(56, 189, 248, 0.12);
      --border: #334155;
      --border-light: #1e293b;
      --card-bg: #1e293b;
      --badge-num: #0284c7;
      --badge-num-text: #ffffff;
      --sidebar-width: 330px;
    }}
    [data-theme="light"] {{
      --bg-primary: #f8fafc;
      --bg-secondary: #ffffff;
      --bg-tertiary: #e2e8f0;
      --bg-board: #f1f5f9;
      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #94a3b8;
      --accent: #0284c7;
      --accent-hover: #0369a1;
      --accent-bg: rgba(2, 132, 199, 0.08);
      --border: #cbd5e1;
      --border-light: #e2e8f0;
      --card-bg: #ffffff;
      --badge-num: #0284c7;
      --badge-num-text: #ffffff;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-primary);
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      transition: background-color 0.2s, color 0.2s;
    }}
    header {{
      height: 56px;
      background-color: var(--bg-secondary);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 20px;
      flex-shrink: 0;
      z-index: 20;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 16px;
      font-weight: 600;
      overflow: hidden;
    }}
    .brand-titles {{
      display: flex;
      flex-direction: column;
      gap: 2px;
      overflow: hidden;
    }}
    .brand span.title {{
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 520px;
      font-size: 15px;
      font-weight: 700;
      letter-spacing: 0.2px;
    }}
    .brand-titles .subtitle {{
      font-size: 11px;
      font-weight: normal;
      color: var(--text-muted);
      letter-spacing: 0.2px;
    }}
    .badge {{
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 9999px;
      background-color: #10b981;
      color: #ffffff;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      flex-shrink: 0;
    }}
    .project-card {{
      padding: 12px 14px;
      background: linear-gradient(135deg, rgba(56, 189, 248, 0.08), rgba(2, 132, 199, 0.16));
      border-bottom: 1px solid var(--border);
    }}
    .project-kicker {{
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--accent);
      margin-bottom: 3px;
    }}
    .project-title {{
      font-size: 13px;
      font-weight: 700;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .project-pill {{
      font-size: 11px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 9999px;
      background-color: var(--accent-bg);
      color: var(--accent);
      border: 1px solid var(--accent);
      white-space: nowrap;
      flex-shrink: 0;
    }}
    .controls {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    button, .btn {{
      padding: 6px 12px;
      font-size: 13px;
      font-weight: 500;
      border-radius: 6px;
      border: 1px solid var(--border);
      background-color: var(--bg-primary);
      color: var(--text-primary);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s;
    }}
    button:hover, .btn:hover {{
      border-color: var(--accent);
      color: var(--accent);
    }}
    .btn-primary {{
      background-color: var(--accent);
      color: #ffffff !important;
      border-color: var(--accent);
    }}
    .btn-primary:hover {{
      background-color: var(--accent-hover);
    }}
    .app-container {{
      flex: 1;
      display: flex;
      overflow: hidden;
    }}
    /* 左侧边栏 */
    aside.sidebar {{
      width: var(--sidebar-width);
      background-color: var(--bg-secondary);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      transition: width 0.2s;
    }}
    .sidebar-header {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .sidebar-header .title-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-secondary);
    }}
    .search-box {{
      width: 100%;
      padding: 6px 10px;
      border-radius: 6px;
      border: 1px solid var(--border);
      background-color: var(--bg-primary);
      color: var(--text-primary);
      font-size: 12px;
      outline: none;
    }}
    .search-box:focus {{
      border-color: var(--accent);
    }}
    .sidebar-list {{
      flex: 1;
      overflow-y: auto;
      padding: 8px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .layer-group-title {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--accent);
      padding: 10px 8px 4px 8px;
    }}
    .item-card {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 10px;
      border-radius: 6px;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.15s;
    }}
    .item-card:hover {{
      background-color: var(--accent-bg);
      border-color: var(--border);
    }}
    .item-card.active {{
      background-color: var(--accent-bg);
      border-color: var(--accent);
      font-weight: 600;
    }}
    .num-badge {{
      font-size: 11px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      background-color: var(--badge-num);
      color: var(--badge-num-text);
      flex-shrink: 0;
    }}
    .item-info {{
      flex: 1;
      overflow: hidden;
    }}
    .item-name {{
      font-size: 13px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      color: var(--text-primary);
    }}
    .item-tag {{
      font-size: 10px;
      color: var(--text-muted);
      margin-top: 2px;
    }}
    /* 右侧主视口 */
    main.content-area {{
      flex: 1;
      display: flex;
      flex-direction: column;
      background-color: var(--bg-board);
      overflow: hidden;
      position: relative;
    }}
    .content-toolbar {{
      height: 44px;
      background-color: var(--bg-secondary);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      flex-shrink: 0;
    }}
    .curr-meta {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 14px;
      font-weight: 600;
      overflow: hidden;
    }}
    .view-modes {{
      display: flex;
      align-items: center;
      background-color: var(--bg-primary);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 2px;
      gap: 2px;
    }}
    .mode-btn {{
      padding: 4px 10px;
      font-size: 12px;
      border-radius: 4px;
      border: none;
      background: transparent;
      color: var(--text-secondary);
      cursor: pointer;
    }}
    .mode-btn.active {{
      background-color: var(--accent);
      color: #ffffff;
      font-weight: 600;
    }}
    .viewport-body {{
      flex: 1;
      min-height: 0;
      min-width: 0;
      position: relative;
      overflow: hidden;
      display: flex;
      width: 100%;
      height: 100%;
    }}
    #viewer-container {{
      flex: 1;
      min-height: 0;
      min-width: 0;
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: grab;
      position: relative;
    }}
    #viewer-container:active {{
      cursor: grabbing;
    }}
    .mermaid-render {{
      flex: 1;
      min-height: 0;
      min-width: 0;
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }}
    #doc-container {{
      flex: 1;
      min-height: 0;
      min-width: 0;
      width: 100%;
      height: 100%;
      overflow-y: auto;
      padding: 32px 48px;
      background-color: var(--bg-primary);
      display: none;
    }}
    .markdown-body {{
      max-width: 960px;
      margin: 0 auto;
      line-height: 1.7;
      color: var(--text-primary);
    }}
    .markdown-body h1, .markdown-body h2, .markdown-body h3 {{
      margin-top: 24px;
      margin-bottom: 12px;
      color: var(--text-primary);
      border-bottom: 1px solid var(--border);
      padding-bottom: 6px;
    }}
    .markdown-body p, .markdown-body ul, .markdown-body ol {{
      margin-bottom: 16px;
    }}
    .markdown-body table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0;
    }}
    .markdown-body th, .markdown-body td {{
      border: 1px solid var(--border);
      padding: 8px 12px;
      text-align: left;
    }}
    .markdown-body th {{
      background-color: var(--bg-secondary);
    }}
    .markdown-body pre {{
      background-color: var(--bg-secondary);
      padding: 12px;
      border-radius: 6px;
      border: 1px solid var(--border);
      overflow-x: auto;
      margin-bottom: 16px;
    }}
    .markdown-body code {{
      font-family: ui-monospace, Menlo, Consolas, monospace;
      font-size: 13px;
    }}
    .zoom-toolbar {{
      position: absolute;
      bottom: 64px;
      right: 24px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 6px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
      z-index: 10;
    }}
    .zoom-toolbar button {{
      width: 32px;
      height: 32px;
      padding: 0;
      justify-content: center;
      border: none;
      background: transparent;
      font-size: 16px;
    }}
    footer.bottom-bar {{
      height: 40px;
      background-color: var(--bg-secondary);
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      flex-shrink: 0;
      font-size: 12px;
      color: var(--text-secondary);
    }}
    .nav-buttons {{
      display: flex;
      gap: 8px;
    }}
    .empty-state {{
      text-align: center;
      color: var(--text-secondary);
      padding: 60px;
    }}
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <span style="font-size: 22px;">🏛️</span>
      <div class="brand-titles">
        <span class="title">{html.escape(project_name)}</span>
        <span class="subtitle">Architecture Lifecycle Canvas · 架构全景交互画板</span>
      </div>
      <span class="badge">{html.escape(status_tag)}</span>
    </div>
    <div class="controls">
      <button id="theme-toggle" title="切换浅色/深色主题">🌓 主题</button>
      <button id="export-svg" class="btn" title="导出当前视图为矢量 SVG">📥 导出 SVG</button>
      <button id="reset-view" class="btn btn-primary" title="重置视角居中自适应">🎯 重置视角</button>
    </div>
  </header>

  <div class="app-container">
    <aside class="sidebar">
      <div class="project-card">
        <div class="project-kicker">🎯 架构工程项目</div>
        <div class="project-title" title="{html.escape(project_name)}">{html.escape(project_name)}</div>
      </div>
      <div class="sidebar-header">
        <div class="title-row">
          <span>📑 架构输出物清单 (按编号递增)</span>
          <span id="artifact-count" style="font-weight: normal; font-size: 11px;">共 {len(artifacts)} 项</span>
        </div>
        <input type="text" id="search-input" class="search-box" placeholder="🔍 搜索编号或名称 (如 01-01, AOD, OM)...">
      </div>
      <div class="sidebar-list" id="sidebar-list"></div>
    </aside>

    <main class="content-area">
      <div class="content-toolbar">
        <div class="curr-meta" id="curr-meta">
          <span class="project-pill" title="当前架构工程">{html.escape(project_name)}</span>
          <span class="num-badge" id="curr-num">--</span>
          <span id="curr-title">载入中...</span>
        </div>
        <div class="view-modes" id="view-mode-controls">
          <button class="mode-btn active" id="btn-mode-diagram">📊 架构图拓扑</button>
          <button class="mode-btn" id="btn-mode-doc">📄 详细设计规约</button>
        </div>
      </div>

      <div class="viewport-body">
        <div id="viewer-container">
          <div id="graph-target" class="mermaid-render"></div>
        </div>
        <div id="doc-container">
          <div class="markdown-body" id="doc-target"></div>
        </div>

        <div class="zoom-toolbar" id="zoom-toolbar">
          <button id="zoom-in" title="放大">+</button>
          <button id="zoom-out" title="缩小">−</button>
          <button id="zoom-reset" title="适应画布">⟲</button>
        </div>
      </div>

      <footer class="bottom-bar">
        <div id="curr-path">文件路径: --</div>
        <div class="nav-buttons">
          <button id="btn-prev" title="按编号切换至上一个 (快捷键: 左方向键)">⏮ 上一个输出物</button>
          <button id="btn-next" title="按编号切换至下一个 (快捷键: 右方向键)">⏭ 下一个输出物</button>
        </div>
      </footer>
    </main>
  </div>

  <script>
    const artifacts = /*__CANVAS_DATA_START__*/{artifacts_json}/*__CANVAS_DATA_END__*/;
    window.__CANVAS_DATA__ = artifacts;
    window.__CANVAS_PROJECT_NAME__ = "{project_name}";
    let currentIndex = 0;
    let currentMode = "diagram"; // "diagram" | "doc"
    let panZoomInstance = null;
    let currentTheme = localStorage.getItem("archify_theme") || "dark";

    document.documentElement.setAttribute("data-theme", currentTheme);

    function initMermaid(theme) {{
      if (typeof mermaid === "undefined") return;
      mermaid.initialize({{
        startOnLoad: false,
        theme: theme === "dark" ? "dark" : "default",
        securityLevel: "loose",
        flowchart: {{ useMaxWidth: false, htmlLabels: true, curve: "basis" }},
        themeVariables: theme === "dark" ? {{
          darkMode: true,
          background: "#0b0f19",
          primaryColor: "#1e3a8a",
          primaryTextColor: "#f8fafc",
          primaryBorderColor: "#38bdf8",
          lineColor: "#64748b",
          secondaryColor: "#1e293b",
          tertiaryColor: "#0f172a"
        }} : {{
          darkMode: false,
          background: "#ffffff",
          primaryColor: "#eff6ff",
          primaryTextColor: "#0f172a",
          primaryBorderColor: "#0284c7",
          lineColor: "#475569"
        }}
      }});
    }}

    function buildSidebar(filterText = "") {{
      const listEl = document.getElementById("sidebar-list");
      listEl.innerHTML = "";

      let currentLayer = null;

      artifacts.forEach((item, idx) => {{
        const searchMatch = !filterText ||
          item.num.toLowerCase().includes(filterText.toLowerCase()) ||
          item.title.toLowerCase().includes(filterText.toLowerCase()) ||
          item.rel_path.toLowerCase().includes(filterText.toLowerCase());

        if (!searchMatch) return;

        // 分组标题
        if (item.layer_title !== currentLayer) {{
          currentLayer = item.layer_title;
          const groupTitle = document.createElement("div");
          groupTitle.className = "layer-group-title";
          groupTitle.textContent = currentLayer;
          listEl.appendChild(groupTitle);
        }}

        const card = document.createElement("div");
        card.className = "item-card " + (idx === currentIndex ? "active" : "");
        card.dataset.index = idx;
        card.innerHTML = `
          <span class="num-badge">${{item.num}}</span>
          <div class="item-info">
            <div class="item-name" title="${{item.title}}">${{item.title.replace(/\\[.*?\\]\\s*/, "")}}</div>
            <div class="item-tag">${{item.tag}} · ${{item.filename}}</div>
          </div>
        `;
        card.onclick = () => selectItem(idx);
        listEl.appendChild(card);
      }});
    }}

    let currentRenderToken = 0;

    function selectItem(index) {{
      if (index < 0 || index >= artifacts.length) return;
      currentIndex = index;
      const item = artifacts[index];

      // 更新侧边栏高亮
      document.querySelectorAll(".item-card").forEach(el => {{
        el.classList.toggle("active", parseInt(el.dataset.index) === index);
      }});

      // 更新顶部与底栏元数据
      document.getElementById("curr-num").textContent = item.num;
      document.getElementById("curr-title").textContent = item.title;
      document.getElementById("curr-path").textContent = `文件路径: ${{item.rel_path}} (第 ${{index + 1}} / ${{artifacts.length}} 项)`;

      // 如果当前项包含图表，优先且自动切换到 diagram 视图
      if (item.has_diagram) {{
        document.getElementById("btn-mode-diagram").disabled = false;
        document.getElementById("btn-mode-diagram").style.opacity = "1";
        document.getElementById("btn-mode-diagram").title = "查看架构图拓扑";
        // 自动激活架构图视图
        setMode("diagram", true);
      }} else {{
        // 无图表项禁用拓扑按钮并自动切到文档规约
        document.getElementById("btn-mode-diagram").disabled = true;
        document.getElementById("btn-mode-diagram").style.opacity = "0.4";
        document.getElementById("btn-mode-diagram").title = "当前输出物未包含 Mermaid 架构图";
        setMode("doc", true);
      }}
    }}

    function setMode(mode, triggerRender = true) {{
      currentMode = mode;
      document.getElementById("btn-mode-diagram").classList.toggle("active", mode === "diagram");
      document.getElementById("btn-mode-doc").classList.toggle("active", mode === "doc");

      const viewContainer = document.getElementById("viewer-container");
      const docContainer = document.getElementById("doc-container");
      const zoomBar = document.getElementById("zoom-toolbar");

      if (mode === "diagram") {{
        viewContainer.style.display = "flex";
        docContainer.style.display = "none";
        zoomBar.style.display = "flex";
        if (triggerRender) {{
          renderDiagramView(artifacts[currentIndex]);
        }} else if (panZoomInstance) {{
          requestAnimationFrame(() => {{
            panZoomInstance && panZoomInstance.resize();
          }});
        }}
      }} else {{
        viewContainer.style.display = "none";
        docContainer.style.display = "block";
        zoomBar.style.display = "none";
        if (triggerRender) {{
          renderDocView(artifacts[currentIndex]);
        }}
      }}
    }}

    function renderDocView(item) {{
      const target = document.getElementById("doc-target");
      if (!item || !item.raw_content) {{
        target.innerHTML = "<div class='empty-state'>该文件暂无文本内容</div>";
        return;
      }}

      let markdownSource = "";
      const ext = (item.file_ext || "").toLowerCase();

      if (ext === ".yaml" || ext === ".yml") {{
        markdownSource = [
          "### ⚡ 接口强契约规约: " + item.filename,
          "",
          "> 规范标准: **OpenAPI 3.0 / YAML 边界接口契约** · 状态: `STRICT`",
          "",
          "```yaml",
          (item.raw_content || "").trim(),
          "```"
        ].join("\\n");
      }} else if (ext === ".json") {{
        let formattedJson = item.raw_content || "";
        try {{
          formattedJson = JSON.stringify(JSON.parse(item.raw_content), null, 2);
        }} catch (e) {{}}
        markdownSource = [
          "### 🧩 物理工程骨架规约: " + item.filename,
          "",
          "> 规范标准: **JSON Schema 物理脚手架结构规约** · 状态: `LOCKED`",
          "",
          "```json",
          formattedJson.trim(),
          "```"
        ].join("\\n");
      }} else if (ext === ".mmd") {{
        markdownSource = [
          "### 📊 架构图元源码: " + item.filename,
          "",
          "> 规范标准: **Mermaid 结构拓扑源代码**",
          "",
          "```mermaid",
          (item.raw_content || "").trim(),
          "```"
        ].join("\\n");
      }} else {{
        markdownSource = item.raw_content;
      }}

      if (typeof marked !== "undefined") {{
        target.innerHTML = marked.parse(markdownSource);
      }} else {{
        target.innerHTML = `<pre>${{markdownSource}}</pre>`;
      }}
    }}

    function renderDiagramView(item) {{
      const token = ++currentRenderToken;
      const target = document.getElementById("graph-target");
      if (panZoomInstance) {{
        panZoomInstance.destroy();
        panZoomInstance = null;
      }}
      target.innerHTML = "";

      if (!item || !item.has_diagram) {{
        target.innerHTML = '<div class="empty-state">该输出物未包含 Mermaid 架构图。点击右上角“详细设计规约”查看文档内容。</div>';
        return;
      }}

      const code = item.mermaid_code.trim();

      // 离线/物理隔离专网环境降级保护
      if (typeof mermaid === "undefined") {{
        const escapedCode = code.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        target.innerHTML = `
          <div class="empty-state" style="max-width: 680px; text-align: left; background: var(--card-bg); padding: 24px; border-radius: 8px; border: 1px solid var(--border);">
            <div style="font-size: 16px; font-weight: 600; color: #f59e0b; margin-bottom: 8px;">
              ⚠️ 当前处于离线/物理隔离专网环境 (Mermaid 脚本未就绪)
            </div>
            <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 16px; line-height: 1.6;">
              检测到外部 CDN 暂未加载就绪。图表数据完整无损，您可以在下方直接查阅该图的确定性 Mermaid 架构源码：
            </div>
            <pre style="background: var(--bg-board); padding: 12px; border-radius: 6px; font-family: monospace; font-size: 12px; overflow-x: auto; color: var(--text-primary); border: 1px solid var(--border);">${{escapedCode}}</pre>
          </div>
        `;
        return;
      }}

      // 使用合法的纯字母数字安全 ID
      const safeId = "mermaidChart" + Math.floor(Math.random() * 1000000000);
      const oldTemp = document.getElementById("d" + safeId);
      if (oldTemp) oldTemp.remove();

      try {{
        mermaid.render(safeId, code).then(result => {{
          // 若中途用户已切换至其他项，则放弃过期的渲染
          if (token !== currentRenderToken) return;

          target.innerHTML = result.svg;
          if (result.bindFunctions) {{
            result.bindFunctions(target);
          }}
          const svgEl = target.querySelector("svg");
          if (svgEl) {{
            svgEl.style.width = "100%";
            svgEl.style.height = "100%";
            svgEl.style.minWidth = "100%";
            svgEl.style.minHeight = "100%";
            svgEl.removeAttribute("max-width");
            svgEl.style.maxWidth = "none";

            requestAnimationFrame(() => {{
              if (token !== currentRenderToken) return;
              if (typeof svgPanZoom !== "undefined") {{
                try {{
                  panZoomInstance = svgPanZoom(svgEl, {{
                    zoomEnabled: true,
                    controlIconsEnabled: false,
                    fit: true,
                    center: true,
                    minZoom: 0.1,
                    maxZoom: 20,
                    dblClickZoomEnabled: true,
                    mouseWheelZoomEnabled: true
                  }});
                  panZoomInstance.resize();
                  panZoomInstance.fit();
                  panZoomInstance.center();
                }} catch (zoomErr) {{
                  console.warn("svgPanZoom 初始化警告:", zoomErr);
                }}
              }}
            }});
          }}
        }}).catch(err => {{
          if (token !== currentRenderToken) return;
          target.innerHTML = `<div class="empty-state" style="color: #ef4444; max-width: 680px; text-align: left; background: var(--card-bg); padding: 20px; border-radius: 8px; border: 1px solid var(--border);">
            <h3 style="margin-bottom: 8px;">Mermaid 图表渲染异常</h3>
            <p style="font-family: monospace; font-size: 12px; color: var(--text-secondary);">${{err.message || err}}</p>
            <pre style="margin-top: 12px; background: var(--bg-board); padding: 12px; border-radius: 6px; font-size: 11px; overflow-x: auto;">${{code}}</pre>
          </div>`;
        }});
      }} catch (err) {{
        if (token !== currentRenderToken) return;
        target.innerHTML = `<div class="empty-state" style="color: #ef4444;">渲染调用失败: ${{err}}</div>`;
      }}
    }}

    // 主题切换
    document.getElementById("theme-toggle").onclick = () => {{
      currentTheme = currentTheme === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", currentTheme);
      localStorage.setItem("archify_theme", currentTheme);
      initMermaid(currentTheme);
      if (currentMode === "diagram") {{
        renderDiagramView(artifacts[currentIndex]);
      }}
    }};

    // 缩放操作
    document.getElementById("zoom-in").onclick = () => panZoomInstance && panZoomInstance.zoomIn();
    document.getElementById("zoom-out").onclick = () => panZoomInstance && panZoomInstance.zoomOut();
    document.getElementById("zoom-reset").onclick = () => {{
      if (panZoomInstance) {{
        panZoomInstance.reset();
        panZoomInstance.fit();
        panZoomInstance.center();
      }}
    }};
    document.getElementById("reset-view").onclick = () => {{
      if (panZoomInstance) {{
        panZoomInstance.reset();
        panZoomInstance.fit();
        panZoomInstance.center();
      }}
    }};

    // 导出当前 SVG
    document.getElementById("export-svg").onclick = () => {{
      const svgEl = document.querySelector("#graph-target svg");
      if (!svgEl) {{
        alert("当前视图未展示架构图或未生成 SVG");
        return;
      }}
      const serializer = new XMLSerializer();
      const source = serializer.serializeToString(svgEl);
      const blob = new Blob([source], {{ type: "image/svg+xml;charset=utf-8" }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = (artifacts[currentIndex]?.num || "diagram") + "-" + (artifacts[currentIndex]?.filename || "architecture") + ".svg";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }};

    // 模式切换
    document.getElementById("btn-mode-diagram").onclick = () => setMode("diagram");
    document.getElementById("btn-mode-doc").onclick = () => setMode("doc");

    // 快速翻页 (前后切换)
    document.getElementById("btn-prev").onclick = () => {{
      if (currentIndex > 0) selectItem(currentIndex - 1);
    }};
    document.getElementById("btn-next").onclick = () => {{
      if (currentIndex < artifacts.length - 1) selectItem(currentIndex + 1);
    }};

    // 键盘左右快捷键
    window.addEventListener("keydown", (e) => {{
      if (e.target.tagName === "INPUT") return;
      if (e.key === "ArrowLeft") {{
        if (currentIndex > 0) selectItem(currentIndex - 1);
      }} else if (e.key === "ArrowRight") {{
        if (currentIndex < artifacts.length - 1) selectItem(currentIndex + 1);
      }}
    }});

    // 搜索过滤
    document.getElementById("search-input").addEventListener("input", (e) => {{
      buildSidebar(e.target.value.trim());
    }});

    // 启动初始渲染
    initMermaid(currentTheme);
    buildSidebar();
    if (artifacts.length > 0) {{
      // 优先选中第一个有图的项或第 0 项
      const firstDiagramIdx = artifacts.findIndex(a => a.has_diagram);
      selectItem(firstDiagramIdx >= 0 ? firstDiagramIdx : 0);
    }}
  </script>
</body>
</html>
"""
    return html_template


def resolve_project_display_name(ws: Path, given_name: str) -> str:
    """数据驱动解析项目展示名称，零硬编码任何具体业务案例.

    解析优先级：
    1. 显式指定的非默认名称；
    2. 需求/概览文档中的首个顶级标题（从 01-01-business-drivers.md、02-01-system-overview.md 等提取）；
    3. 工作区父级目录或当前目录的人类友好格式化名称。
    """
    if given_name and given_name != "Architecture Lifecycle Canvas":
        return given_name

    # 尝试从文档提取标题（纯数据驱动，适用于任何案例）
    doc_paths = [
        ws / "01-requirements" / "01-01-business-drivers.md",
        ws / "02-architecture-design" / "02-01-system-overview.md",
        ws / "README.md",
    ]
    for dp in doc_paths:
        if dp.exists():
            try:
                for line in dp.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line.startswith("# "):
                        # 去除可能存在的类似 # [01-01] 前缀
                        clean = re.sub(r"^#\s*(\[\d{2}-\d{2}\])?\s*", "", line).strip()
                        if clean and len(clean) >= 3 and clean not in ("Business Drivers & Goals", "System Architecture Overview"):
                            return clean
            except Exception:
                pass

    parent_name = ws.parent.name if ws.name == "architecture" else ws.name
    beautified = parent_name.replace("-", " ").replace("_", " ").title()
    return f"🏛️ {beautified} Architecture Canvas"


def render_board(
    workspace_root: Path | str,
    output_path: Optional[Path | str] = None,
    project_name: str = "Architecture Lifecycle Canvas",
) -> Path:
    """搜集工作区下的全部编号输出物工件并渲染为自包含 HTML 画板.

    Args:
        workspace_root: 架构资产根目录 (通常为 docs/architecture)
        output_path: 编译输出的 HTML 文件路径
        project_name: 项目显示名称

    Returns:
        Path: 生成的 HTML 绝对路径
    """
    ws = Path(workspace_root).resolve()
    artifacts = collect_artifacts(ws)
    actual_project_name = resolve_project_display_name(ws, project_name)

    # 若未找到任何工件，放置默认引导项
    if not artifacts:
        artifacts.append({
            "num": "00-01",
            "sort_key": "00-01",
            "layer_num": 1,
            "layer_title": "Layer 1 · 架构生命周期准备",
            "title": "[00-01] 待生成架构拓扑",
            "filename": "placeholder.mmd",
            "rel_path": "placeholder.mmd",
            "has_diagram": True,
            "mermaid_code": "graph TD\n    A[启动架构状态机] --> B[调用 02_structural_modeling 技能]\n    B --> C[生成 5 维高保真模型]\n",
            "raw_content": "# 待生成架构资产\n\n请运行 `python run.py --status` 启动架构状态机推进生命周期。",
            "tag": "📊 图表",
            "file_ext": ".mmd",
        })

    html_content = build_interactive_html(
        project_name=actual_project_name,
        artifacts=artifacts,
        metadata={"status": "ACTIVE"},
    )

    out = Path(output_path).resolve() if output_path else ws / "architecture_board.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_content, encoding="utf-8")
    return out


if __name__ == "__main__":
    import sys
    target_ws = sys.argv[1] if len(sys.argv) > 1 else "."
    proj_name = sys.argv[2] if len(sys.argv) > 2 else Path(target_ws).resolve().parent.parent.name
    generated_path = render_board(target_ws, project_name=proj_name)
    print(f"Architecture board generated at: {generated_path}")
