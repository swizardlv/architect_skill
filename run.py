#!/usr/bin/env python3
"""架构设计生命周期主控启动入口脚本 (run.py).

提供交互式与批处理命令行界面，用于驱动架构有限状态机推进、门禁检查与人工审批。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

# 将当前目录和 00_orchestrator 目录加入 Python 搜索路径
CURRENT_DIR = Path(__file__).parent.resolve()
ORCHESTRATOR_DIR = CURRENT_DIR / "skills" / "00_orchestrator"
sys.path.insert(0, str(CURRENT_DIR))
sys.path.insert(0, str(ORCHESTRATOR_DIR))

from orchestrate_architecture_lifecycle import (  # noqa: E402
    ArchitectureLifecycleFSM,
    FSMState,
    GatekeeperError,
    ReviewRejectedError,
    StateTransitionError,
)
from render_architecture_board import render_board  # noqa: E402


def print_banner() -> None:
    """打印终端启动横幅."""
    banner = """
======================================================================
       Architecture Lifecycle Orchestration Engine (Deterministic FSM)
       Deterministic Shell + Stochastic Core | 架构状态机驱动引擎
======================================================================
"""
    print(banner)


def generate_sample_assets(fsm: ArchitectureLifecycleFSM) -> None:
    """生成整套标准架构样本资产，以便进行端到端全链路验证."""
    ws = fsm.workspace_root
    templates_dir = fsm.repo_root / "templates"
    fsm.ensure_workspace_directories()

    # 1. 00-grounding/grounding-spec.json
    grounding_json = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "status": "COMPLETED",
        "grounding_spec": {
            "project_name": "ai-assisted-coding-mesh",
            "business_driver": "解决传统 AI 编程助手随意重构代码破坏架构边界的痛点，通过确定性外壳提供物理围栏。",
            "core_invariants": [
                "状态单向跃迁，禁止未定义的回滚",
                "只读契约目录禁止直接修改",
                "domain 层严禁引入外部持久化或网络适配器",
            ],
            "nfr_targets": {
                "throughput_qps": "均值 500 QPS，峰值 2000 QPS",
                "p99_latency": "P95 < 200ms, P99 < 800ms",
                "rpo_rto": "RPO < 1m, RTO < 5m",
                "consistency_preference": "CP",
                "resource_budget": "单次任务 Token 消耗 <= 8,000",
            },
            "constraints": {
                "tech_stack_allowlist": ["Python 3.11+", "FastAPI", "SQLite", "Redis"],
                "ops_and_infrastructure": "独立容器沙箱、无公网直连写权限",
                "legacy_integrations": ["企业统一 IAM gRPC 接口", "Git 仓库 SSH 接口"],
            },
            "anti_goals": [
                "本期不做跨集群多活自动调度",
                "禁止引入未经验证的自主多智能体通信",
            ],
        },
    }
    (ws / "00-grounding" / "grounding-spec.json").write_text(
        json.dumps(grounding_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 2. 01-grounding/nfr-matrix.md & constraints-and-assumptions.md
    nfr_tmpl = templates_dir / "nfr-matrix-template.md"
    if nfr_tmpl.exists():
        (ws / "01-grounding" / "nfr-matrix.md").write_text(nfr_tmpl.read_text(encoding="utf-8"), encoding="utf-8")

    const_tmpl = templates_dir / "constraints-template.md"
    if const_tmpl.exists():
        (ws / "01-grounding" / "constraints-and-assumptions.md").write_text(
            const_tmpl.read_text(encoding="utf-8"), encoding="utf-8"
        )

    # 3. 02-models/
    c4_context_code = """graph TB
    classDef personStyle fill:#f0fdfa,stroke:#0d9488,stroke-width:2px,color:#134e4a;
    classDef coreStyle fill:#eff6ff,stroke:#2563eb,stroke-width:3px,color:#1e3a8a;
    classDef secStyle fill:#fffbeb,stroke:#d97706,stroke-width:2px,color:#78350f;
    classDef extStyle fill:#f8fafc,stroke:#64748b,stroke-width:2px,stroke-dasharray: 4 4,color:#1e293b;
    classDef obsStyle fill:#faf5ff,stroke:#9333ea,stroke-width:2px,color:#581c87;

    subgraph Users ["参与角色 (Actors)"]
        dev["👤 研发工程师 / 用户<br/>[发起架构设计与修改任务]"]:::personStyle
        reviewer["🛡️ 技术评审人<br/>[审查决策并签署生产审批]"]:::personStyle
    end

    subgraph EnterpriseBoundary ["企业安全边界 (Enterprise Trust Zone)"]
        core["⚙️ 目标系统: 架构设计与执行引擎<br/>[双环控制外壳 + 概率推理内核]"]:::coreStyle
        iam["🔐 企业统一 IAM / SSO<br/>[身份验证与 RBAC 权限中心]"]:::secStyle
        gitRepo["📦 私有 Git 仓库服务<br/>[版本基线拉取与补丁持久化]"]:::extStyle
    end

    subgraph ExternalServices ["外部云与模型生态 (Untrusted External)"]
        modelGw["🌐 大语言模型推理网关<br/>[语义推理 / 结构化解析]"]:::extStyle
        observability["📊 统一可观测平台<br/>[收集链路 Traces, Logs, Metrics]"]:::obsStyle
    end

    dev -->|"1. 提交设计需求 [CLI / HTTPS]"| core
    reviewer -->|"2. 签署阶段审批 [HTTPS Web UI]"| core
    core -->|"3. 校验身份令牌 [gRPC]"| iam
    core -->|"4. 拉取基线 / 推送受控代码 [SSH via ACL]"| gitRepo
    core -->|"5. 下发剪枝 Prompt / 接收输出 [HTTPS via Semantic ACL]"| modelGw
    core -.->|"6. 异步上报指标链路 [OTLP / gRPC]"| observability
"""
    (ws / "02-models" / "c4-context.mmd").write_text(c4_context_code, encoding="utf-8")

    domain_md_code = """# Domain Logical Model

## 1. 限界上下文与聚合划分
- **ArchitectureLifecycleJob (Aggregate Root)**: 守护任务单向状态机与门禁

## 2. 核心生命周期状态机
```mermaid
stateDiagram-v2
    classDef happyPath fill:#f0fdf4,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef retryPath fill:#fffbeb,stroke:#d97706,stroke-width:2px,color:#78350f;
    classDef termPath fill:#fef2f2,stroke:#dc2626,stroke-width:2px,color:#7f1d1d;

    [*] --> INIT
    INIT --> GRILLING: START
    GRILLING --> GROUNDED: 退出门禁满足并经人工确认
    GROUNDED --> MODELING: 结构建模
    MODELING --> CONTRACTED: 契约签署
    CONTRACTED --> SCAFFOLDED: 骨架就绪
    SCAFFOLDED --> FINALIZED: 架构锁定交付
    
    MODELING --> FAILED_RETRYABLE: 校验未通过
    FAILED_RETRYABLE --> MODELING: 负向假设自愈 [重试 < 3]
    FAILED_RETRYABLE --> FAILED_TERMINATED: 超过上限熔断
    
    FINALIZED --> [*]
    FAILED_TERMINATED --> [*]

    class INIT,GRILLING,GROUNDED,MODELING,CONTRACTED,SCAFFOLDED,FINALIZED happyPath;
    class FAILED_RETRYABLE retryPath;
    class FAILED_TERMINATED termPath;
```
"""
    (ws / "02-models" / "domain-logical-model.md").write_text(domain_md_code, encoding="utf-8")

    c4_container_code = """graph TB
    classDef feStyle fill:#f0f9ff,stroke:#0284c7,stroke-width:2px,color:#0c4a6e;
    classDef shellStyle fill:#f8fafc,stroke:#334155,stroke-width:2px,color:#0f172a;
    classDef coreEngineStyle fill:#eff6ff,stroke:#1d4ed8,stroke-width:3px,color:#1e3a8a;
    classDef dbStyle fill:#f0fdf4,stroke:#15803d,stroke-width:2px,color:#14532d;
    classDef cacheStyle fill:#fff1f2,stroke:#e11d48,stroke-width:2px,color:#881337;
    classDef sandboxStyle fill:#faf5ff,stroke:#7e22ce,stroke-width:2px,color:#581c87;

    subgraph ClientLayer ["接入与呈现层 (Access Layer)"]
        cli["🖥️ 主控 CLI / API Gateway<br/>[参数解析 / 鉴权拦截 / 格式反序列化]"]:::feStyle
    end

    subgraph DeterministicShell ["确定性控制外壳 (Deterministic Shell)"]
        fsmEngine["⚙️ 状态机调度引擎 (FSM Engine)<br/>[单向基线演进 / 门禁自检 / 挂起审批]"]:::shellStyle
        stateDb[("🗄️ 持久化状态库 (SQLite / PostgreSQL)<br/>[状态记录 / 阶段元数据 / 审计日志 (ACID)]")]:::dbStyle
    end

    subgraph StochasticCore ["概率推理内核 (Stochastic Core)"]
        agentRunner["🧠 认知智能体执行器 (Agent Core)<br/>[语义推理 / 补丁推演 / 负向反思]"]:::coreEngineStyle
        contextProxy["🧩 上下文剪枝中间件<br/>[AST 骨架压缩 / 错误堆栈剪枝 / 提示词组装]"]:::coreEngineStyle
        memoryCache[("⚡ 短期工作记忆与账本 (Redis / Cache)<br/>[会话上下文 / 已证伪假设账本]")]:::cacheStyle
    end

    subgraph SandboxLayer ["受限执行与验证沙箱 (Execution Sandbox)"]
        sandboxEnv["🛡️ 受控运行沙箱 (Docker / Subprocess)<br/>[只读契约锁定 / 补丁应用 / 30s超时测试强杀]"]:::sandboxStyle
    end

    cli -->|"1. 提交设计任务 / 审批指令 [CLI / HTTP]"| fsmEngine
    fsmEngine -->|"2. 写入状态跃迁与审计日志 [SQL]"| stateDb
    fsmEngine -->|"3. 下发当前阶段认知任务包 [Internal Call]"| agentRunner
    agentRunner <-->|"4. 获取剪枝视图与提取符号 [Local Protocol]"| contextProxy
    contextProxy <-->|"5. 读写短期上下文与负向账本 [RESP / Key-Value]"| memoryCache
    agentRunner -->|"6. 应用精准行级补丁 [Sandbox IPC via Port]"| sandboxEnv
    sandboxEnv -->|"7. 返回带超时拦截的测试断言 [JSON Output]"| agentRunner
    agentRunner -->|"8. 交付阶段生成资产 [Artifacts Commit]"| fsmEngine
"""
    (ws / "02-models" / "c4-container-overview.mmd").write_text(c4_container_code, encoding="utf-8")

    sequence_code = """sequenceDiagram
    autonumber
    actor Dev as 开发者 (Developer)
    participant FSM as 状态机调度引擎 (FSM)
    participant Agent as 认知智能体 (Agent Core)
    participant Ctx as 上下文剪枝中间件
    participant SB as 受限运行沙箱 (Sandbox)
    participant Ledger as 负向假设账本 (Ledger)

    Dev->>FSM: 触发代码变更/修复任务
    activate FSM
    FSM->>Agent: 下发当前上下文与目标测试用例
    activate Agent
    Agent->>Ctx: 请求受限行范围与 AST 骨架
    Ctx-->>Agent: 返回已剪枝的高信噪比上下文
    Agent->>Agent: 推演行级精准补丁 (apply_targeted_patch)
    Agent->>SB: 在沙箱中应用补丁并触发单元测试
    activate SB
    alt 测试在 30s 内顺利通过 (Happy Path)
        SB-->>Agent: 自动化测试通过 (0 Errors)
        Agent-->>FSM: 提交生成补丁与自检报告
        FSM-->>Dev: 推进至下一阶段 / 提示人工验收
    else 产生死循环或断言失败 (Failure & Self-Correction)
        SB--XSB: 触发 30s 硬超时强杀 (SIGKILL)
        SB-->>Agent: 返回剪枝后的错误堆栈 (Pruned Trace)
        deactivate SB
        Agent->>Ledger: 写入本次已证伪假设与错误特征
        Agent->>Agent: 反思并推翻上一轮假设，重新规划方案
    end
    deactivate Agent
    deactivate FSM
"""
    (ws / "02-models" / "interaction-sequence.mmd").write_text(sequence_code, encoding="utf-8")

    dataflow_code = """flowchart TD
    classDef inputStyle fill:#f0f9ff,stroke:#0284c7,stroke-width:2px,color:#0c4a6e;
    classDef hotDbStyle fill:#f0fdf4,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef cacheStyle fill:#fff1f2,stroke:#e11d48,stroke-width:2px,color:#881337;
    classDef coldStyle fill:#f8fafc,stroke:#64748b,stroke-width:2px,stroke-dasharray: 4 4,color:#334155;

    Inflow["📥 外部事件 / 用户设计输入"]:::inputStyle
    
    subgraph HotZone ["热数据工作区 (Hot Zone - 毫秒级)"]
        RedisMem[("⚡ 易失性工作内存 (Redis)<br/>• 活跃会话上下文<br/>• 负向假设账本<br/>• 未提交 Diff 暂存")]:::cacheStyle
    end
    
    subgraph WarmZone ["持久化业务区 (Warm Zone - ACID)"]
        StateDb[("🗄️ 关系型状态库 (SQLite / PostgreSQL)<br/>• FSM 状态跃迁历史<br/>• 架构元数据<br/>• 已签署契约与 ADR")]:::hotDbStyle
    end
    
    subgraph ColdZone ["温冷归档与追踪区 (Cold Zone - 分析与合规)"]
        AuditStorage[("📦 归档存储 / 对象存储<br/>• 完整历史快照<br/>• 分布式 OTLP Trace 日志<br/>• 180 天审计留痕")]:::coldStyle
    end
    
    Inflow -->|"写入瞬时状态"| RedisMem
    Inflow -->|"阶段完成持久化"| StateDb
    StateDb -.->|"异步批量打包沉降"| AuditStorage
"""
    (ws / "02-models" / "data-flow.mmd").write_text(dataflow_code, encoding="utf-8")

    # 4. 03-decisions & 04-contracts
    (ws / "03-decisions" / "adr-index.md").write_text(
        "# ADR Index\n\n- [ADR-001: 确定性状态机外壳与受限沙箱](ADR-001-fsm-shell.md)",
        encoding="utf-8",
    )

    adr_tmpl = templates_dir / "adr-template.md"
    if adr_tmpl.exists():
        (ws / "03-decisions" / "ADR-001-fsm-shell.md").write_text(
            adr_tmpl.read_text(encoding="utf-8"), encoding="utf-8"
        )

    res_tmpl = templates_dir / "resilience-matrix-template.md"
    if res_tmpl.exists():
        (ws / "03-decisions" / "failure-resilience-matrix.md").write_text(
            res_tmpl.read_text(encoding="utf-8"), encoding="utf-8"
        )

    openapi_content = """openapi: 3.1.0
info:
  title: Architecture Lifecycle API
  version: 1.0.0
paths:
  /api/v1/jobs:
    get:
      summary: 获取任务列表
      responses:
        '200':
          description: OK
"""
    (ws / "04-contracts" / "openapi.yaml").write_text(openapi_content, encoding="utf-8")

    # 5. 04-execution & .agent-rules.md
    agent_rules_tmpl = templates_dir / "agent-rules-template.md"
    if agent_rules_tmpl.exists():
        (fsm.repo_root / ".agent-rules.md").write_text(
            agent_rules_tmpl.read_text(encoding="utf-8"), encoding="utf-8"
        )

    (ws / "04-execution" / "roadmap-and-first-step.md").write_text(
        "# Roadmap & First Step\n\n## Milestone 0: Tracer Bullet PoC\n跑通带超时的沙箱执行与补丁定位。",
        encoding="utf-8",
    )

    skeleton_spec = {
        "skeleton_version": "1.0.0",
        "architecture_pattern": "Hexagonal",
        "directories": ["src/domain", "src/ports", "src/adapters", "tests"],
        "immutable_paths": ["docs/architecture", "src/ports"],
        "rules_file": ".agent-rules.md",
    }
    (ws / "04-execution" / "walking-skeleton-spec.json").write_text(
        json.dumps(skeleton_spec, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("[成功] 演示架构资产已生成至工作区，可直接进行全链路测试。")


def run_interactive(fsm: ArchitectureLifecycleFSM, auto_approve: bool = False) -> None:
    """运行交互式推进循环."""
    print(f"[当前状态] {fsm.current_state.value}")
    report = fsm.get_status_report()
    print(f"[阶段说明] {report['description']}")

    while fsm.current_state != FSMState.FINALIZED:
        print("\n" + "-" * 60)
        print(f"正在准备从当前状态推进: {fsm.current_state.value}")

        # 检查门禁
        if fsm.current_state != FSMState.INIT:
            gate_res = fsm.validate_gatekeeper(fsm.current_state)
            print(f"门禁状态: {gate_res.summary()}")
            if not gate_res.passed:
                print(f"[拦截] 无法跃迁：请先补充所需资产文件后重试。")
                break

        # 人类介入检查
        prompt = fsm.get_hitl_prompt(fsm.current_state)
        approved = False
        feedback = ""

        if prompt is not None:
            print(f"\n[HITL 人机审核卡点] {prompt}")
            if auto_approve:
                print("[自动放行] 检测到 --auto-approve 标志，直接签署通过。")
                approved = True
            else:
                user_input = input("请输入审批意见 [Y: 批准 / N: 打回并输入理由]: ").strip()
                if user_input.lower() in ("y", "yes", ""):
                    approved = True
                else:
                    approved = False
                    feedback = input("请输入打回原因/修改诉求: ").strip() or "未附带详细说明"

        try:
            new_state, msg = fsm.advance(
                hitl_approved=approved,
                reviewer_feedback=feedback,
            )
            print(f"[推进成功] {msg}")
        except ReviewRejectedError as r_err:
            print(f"[审批打回] {r_err}")
            break
        except GatekeeperError as g_err:
            print(f"[门禁拦截] {g_err}")
            break
        except StateTransitionError as s_err:
            print(f"[流转错误] {s_err}")
            break

    if fsm.current_state == FSMState.FINALIZED:
        print("\n======================================================================")
        print(" [达成] 架构生命周期已推进至终态 FINALIZED，全部基线与围栏锁定就绪！")
        print("======================================================================\n")


def main() -> None:
    """CLI 主入口函数."""
    parser = argparse.ArgumentParser(
        description="架构设计生命周期主控引擎 (Deterministic FSM Orchestrator)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--status", action="store_true", help="显示当前架构状态与门禁检查报告")
    parser.add_argument("--step", action="store_true", help="单步执行一次状态跃迁")
    parser.add_argument("--auto-approve", action="store_true", help="自动批准人机卡点 (HITL)")
    parser.add_argument("--reset", action="store_true", help="重置当前状态为 INIT 并清空历史状态文件")
    parser.add_argument("--init-sample-assets", action="store_true", help="快速生成符合规范的演示架构资产")
    parser.add_argument("--render-board", action="store_true", help="将 02-models/ 图表编译为自包含交互式 HTML 画板")
    parser.add_argument("--workspace", type=str, default=None, help="自定义架构工作区目录路径")

    args = parser.parse_args()

    print_banner()

    fsm = ArchitectureLifecycleFSM(workspace_root=args.workspace)

    if args.render_board:
        out_html = render_board(fsm.workspace_root)
        print(f"[画板生成成功] 自包含交互式架构全景画板已生成至:\nfile://{out_html}")
        return

    if args.reset:
        if fsm.state_file.exists():
            fsm.state_file.unlink()
        fsm.resume_or_init()
        print("[重置完成] 状态机已恢复为初始状态: INIT")
        return

    if args.init_sample_assets:
        generate_sample_assets(fsm)
        return

    if args.status:
        report = fsm.get_status_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    if args.step:
        prompt = fsm.get_hitl_prompt(fsm.current_state)
        approved = args.auto_approve
        feedback = ""
        if prompt and not approved:
            choice = input(f"[HITL 卡点: {prompt}]\n是否批准? [y/N]: ").strip().lower()
            approved = (choice in ("y", "yes"))
            if not approved:
                feedback = input("输入打回意见: ").strip()

        try:
            new_state, msg = fsm.advance(hitl_approved=approved, reviewer_feedback=feedback)
            print(f"[推进成功] {msg}")
        except Exception as e:
            print(f"[推进失败] {e}", file=sys.stderr)
            sys.exit(1)
        return

    # 默认模式：交互式推演
    run_interactive(fsm, auto_approve=args.auto_approve)


if __name__ == "__main__":
    main()
