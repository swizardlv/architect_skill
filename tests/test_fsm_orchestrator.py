"""针对架构主控状态机 (Architecture Lifecycle FSM) 的单元测试.

测试范围涵盖：
- 状态初始化与默认值
- 门禁（Gatekeeper）资产检查与缺失拦截
- 非法 JSON 资产校验与拦截
- 人类介入卡点（HITL）审批放行与打回机制
- 状态持久化与断点恢复 (.state.json)
- 端到端全生命周期平滑推进至终态 FINALIZED
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# 将 00_orchestrator 加入 sys.path 以支持模块导入
TEST_DIR = Path(__file__).parent.resolve()
REPO_ROOT = TEST_DIR.parent.resolve()
ORCHESTRATOR_DIR = REPO_ROOT / "skills" / "00_orchestrator"
sys.path.insert(0, str(ORCHESTRATOR_DIR))

from orchestrate_architecture_lifecycle import (  # noqa: E402
    ArchitectureLifecycleFSM,
    FSMState,
    GatekeeperError,
    ReviewRejectedError,
    StateTransitionError,
)


@pytest.fixture
def temp_workspace() -> Generator[Path, None, None]:
    """为测试创建临时的架构工作区目录."""
    temp_dir = Path(tempfile.mkdtemp(prefix="test_arch_workspace_"))
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_initial_state(temp_workspace: Path) -> None:
    """测试状态机新建时的初始状态与默认工作区."""
    fsm = ArchitectureLifecycleFSM(workspace_root=temp_workspace)
    assert fsm.current_state == FSMState.INIT
    assert len(fsm.history) == 0
    assert (temp_workspace / ".state.json").exists()


def test_advance_init_to_grilling(temp_workspace: Path) -> None:
    """测试从 INIT 跃迁至 GRILLING."""
    fsm = ArchitectureLifecycleFSM(workspace_root=temp_workspace)
    new_state, msg = fsm.advance()
    assert new_state == FSMState.GRILLING
    assert fsm.current_state == FSMState.GRILLING
    assert len(fsm.history) == 1
    assert fsm.history[0].from_state == "INIT"
    assert fsm.history[0].to_state == "GRILLING"


def test_gatekeeper_blocks_when_artifact_missing(temp_workspace: Path) -> None:
    """测试当缺少必要资产时，门禁检查必须拦截推进."""
    fsm = ArchitectureLifecycleFSM(workspace_root=temp_workspace)
    fsm.advance()  # 进入 GRILLING

    # 在没有创建 grounding-spec.json 的情况下尝试推进，必须抛出 GatekeeperError
    with pytest.raises(GatekeeperError) as exc_info:
        fsm.advance(hitl_approved=True)

    assert "缺失文件" in str(exc_info.value)
    assert fsm.current_state == FSMState.GRILLING


def test_gatekeeper_blocks_invalid_json(temp_workspace: Path) -> None:
    """测试当资产为非法 JSON 时，门禁拦截."""
    fsm = ArchitectureLifecycleFSM(workspace_root=temp_workspace)
    fsm.advance()  # 进入 GRILLING

    # 在 GRILLING 阶段准备正常资产
    req_dir = temp_workspace / "01-requirements"
    req_dir.mkdir(parents=True, exist_ok=True)
    (req_dir / "business-drivers.md").write_text("# Drivers", encoding="utf-8")
    (req_dir / "functional-requirements.md").write_text("# Functional\n### 功能需求清单\n- FR-01: 校验", encoding="utf-8")

    fsm.advance(hitl_approved=True)  # 进入 GROUNDING
    (req_dir / "non-functional-requirements.md").write_text("# NFR", encoding="utf-8")
    (req_dir / "architecture-requirements-checklist.md").write_text("# ARC\n| ARC-01 | 质量属性类别 | 量化设计指标 |", encoding="utf-8")
    (req_dir / "constraints-and-assumptions.md").write_text("# Constraints", encoding="utf-8")

    fsm.advance()  # 进入 MODELING
    arch_dir = temp_workspace / "02-architecture-design"
    arch_dir.mkdir(parents=True, exist_ok=True)
    (arch_dir / "system-overview.md").write_text("# Overview", encoding="utf-8")
    (arch_dir / "architecture-overview-diagram.md").write_text("# AOD", encoding="utf-8")
    (arch_dir / "component-model.md").write_text("# CM", encoding="utf-8")
    (arch_dir / "domain-logical-model.md").write_text("# Domain", encoding="utf-8")
    (arch_dir / "c4-context.mmd").write_text("graph TD\nA --> B", encoding="utf-8")
    (arch_dir / "c4-container-overview.mmd").write_text("graph TD\nC --> D", encoding="utf-8")

    fsm.advance()  # 进入 CONTRACTS
    eng_dir = temp_workspace / "03-engineering-and-physics"
    (eng_dir / "adrs").mkdir(parents=True, exist_ok=True)
    (eng_dir / "contracts").mkdir(parents=True, exist_ok=True)
    (eng_dir / "operational-model.md").write_text("# OM", encoding="utf-8")
    (eng_dir / "deployment-architecture.md").write_text("# Deploy", encoding="utf-8")
    (eng_dir / "data-architecture.md").write_text("# Data", encoding="utf-8")
    (eng_dir / "observability-design.md").write_text("# Obs", encoding="utf-8")
    (eng_dir / "failure-resilience-matrix.md").write_text("# Resilience", encoding="utf-8")
    (eng_dir / "adrs" / "adr-index.md").write_text("# ADR", encoding="utf-8")
    (eng_dir / "contracts" / "openapi.yaml").write_text("openapi: 3.1.0", encoding="utf-8")
    (eng_dir / "contracts" / "interface-contracts-overview.md").write_text("# Contracts", encoding="utf-8")

    fsm.advance(hitl_approved=True)  # 进入 SCAFFOLDING
    scaff_dir = temp_workspace / "04-delivery-and-organization"
    scaff_dir.mkdir(parents=True, exist_ok=True)
    (scaff_dir / "organization-structure.md").write_text("# Org", encoding="utf-8")
    (scaff_dir / "estimation-and-plan.md").write_text("# Plan", encoding="utf-8")
    (scaff_dir / "first-step-poc.md").write_text("# PoC", encoding="utf-8")
    (temp_workspace / ".agent-rules.md").write_text("# Rules", encoding="utf-8")

    # 写入损坏的 JSON
    broken_json = scaff_dir / "walking-skeleton-spec.json"
    broken_json.write_text("{ broken json: invalid }", encoding="utf-8")

    with pytest.raises(GatekeeperError) as exc_info:
        fsm.advance()

    assert "JSON 解析失败" in str(exc_info.value) or "门禁存在未达成项" in str(exc_info.value)


def test_hitl_rejection_in_grilling(temp_workspace: Path) -> None:
    """测试在 GRILLING 阶段如果人工审批未批准，必须拦截并记录打回."""
    fsm = ArchitectureLifecycleFSM(workspace_root=temp_workspace)
    fsm.advance()  # 进入 GRILLING

    # 写入合法的 Layer 1 资产
    req_dir = temp_workspace / "01-requirements"
    req_dir.mkdir(parents=True, exist_ok=True)
    (req_dir / "business-drivers.md").write_text("# Drivers", encoding="utf-8")
    (req_dir / "functional-requirements.md").write_text("# Functional\n### 功能需求清单\n- FR-01: 校验", encoding="utf-8")

    # 人工审核被拒绝 (hitl_approved=False)
    with pytest.raises(ReviewRejectedError) as exc_info:
        fsm.advance(hitl_approved=False, reviewer_feedback="NFR 延迟指标缺少明确数值")

    assert "人工审查拒绝放行" in str(exc_info.value)
    assert fsm.current_state == FSMState.GRILLING
    assert any(rec.action == "REJECT" for rec in fsm.history)


def test_state_persistence_and_resume(temp_workspace: Path) -> None:
    """测试状态机持久化至 .state.json 并在重新实例化后成功恢复."""
    fsm1 = ArchitectureLifecycleFSM(workspace_root=temp_workspace)
    fsm1.advance()  # 进入 GRILLING
    assert fsm1.current_state == FSMState.GRILLING

    # 写入 Layer 1 资产并批准跃迁至 GROUNDING
    req_dir = temp_workspace / "01-requirements"
    req_dir.mkdir(parents=True, exist_ok=True)
    (req_dir / "business-drivers.md").write_text("# Drivers", encoding="utf-8")
    (req_dir / "functional-requirements.md").write_text("# Functional\n### 功能需求清单\n- FR-01: 校验", encoding="utf-8")

    fsm1.advance(hitl_approved=True)
    assert fsm1.current_state == FSMState.GROUNDING

    # 重新实例化第二个 FSM 对象，模拟程序重启
    fsm2 = ArchitectureLifecycleFSM(workspace_root=temp_workspace)
    assert fsm2.current_state == FSMState.GROUNDING
    assert len(fsm2.history) == 2


def test_full_lifecycle_progression(temp_workspace: Path) -> None:
    """测试从 INIT 一路平滑推进至终态 FINALIZED 的全闭环."""
    fsm = ArchitectureLifecycleFSM(workspace_root=temp_workspace)

    # 1. INIT -> GRILLING
    state, _ = fsm.advance()
    assert state == FSMState.GRILLING

    # 准备 GRILLING 资产
    req_dir = temp_workspace / "01-requirements"
    req_dir.mkdir(parents=True, exist_ok=True)
    (req_dir / "business-drivers.md").write_text("# Drivers", encoding="utf-8")
    (req_dir / "functional-requirements.md").write_text("# Functional\n### 功能需求清单\n- FR-01: 指令接入校验", encoding="utf-8")

    # 2. GRILLING -> GROUNDING (HITL 批准)
    state, _ = fsm.advance(hitl_approved=True)
    assert state == FSMState.GROUNDING

    # 准备 GROUNDING 资产
    (req_dir / "non-functional-requirements.md").write_text("# NFR Matrix\nSLA 99.999% P99 < 30ms", encoding="utf-8")
    (req_dir / "architecture-requirements-checklist.md").write_text("# ARC\n| ARC-01 | 质量属性类别 | 量化设计指标 |", encoding="utf-8")
    (req_dir / "constraints-and-assumptions.md").write_text("# Constraints", encoding="utf-8")

    # 3. GROUNDING -> MODELING
    state, _ = fsm.advance()
    assert state == FSMState.MODELING

    # 准备 MODELING 资产
    arch_dir = temp_workspace / "02-architecture-design"
    arch_dir.mkdir(parents=True, exist_ok=True)
    (arch_dir / "system-overview.md").write_text("# System Overview", encoding="utf-8")
    (arch_dir / "architecture-overview-diagram.md").write_text("# AOD Overview", encoding="utf-8")
    (arch_dir / "component-model.md").write_text("# Component Model", encoding="utf-8")
    (arch_dir / "domain-logical-model.md").write_text("# Domain Model", encoding="utf-8")
    (arch_dir / "c4-context.mmd").write_text("graph TD\nA --> B", encoding="utf-8")
    (arch_dir / "c4-container-overview.mmd").write_text("graph TD\nC --> D", encoding="utf-8")

    # 4. MODELING -> CONTRACTS
    state, _ = fsm.advance()
    assert state == FSMState.CONTRACTS

    # 准备 CONTRACTS 资产
    eng_dir = temp_workspace / "03-engineering-and-physics"
    (eng_dir / "adrs").mkdir(parents=True, exist_ok=True)
    (eng_dir / "contracts").mkdir(parents=True, exist_ok=True)
    (eng_dir / "operational-model.md").write_text("# Operational Model", encoding="utf-8")
    (eng_dir / "deployment-architecture.md").write_text("# Deployment Architecture", encoding="utf-8")
    (eng_dir / "data-architecture.md").write_text("# Data Architecture", encoding="utf-8")
    (eng_dir / "observability-design.md").write_text("# Observability", encoding="utf-8")
    (eng_dir / "failure-resilience-matrix.md").write_text("# Resilience", encoding="utf-8")
    (eng_dir / "adrs" / "adr-index.md").write_text("# ADR Index", encoding="utf-8")
    (eng_dir / "contracts" / "openapi.yaml").write_text("openapi: 3.1.0", encoding="utf-8")
    (eng_dir / "contracts" / "interface-contracts-overview.md").write_text("# Interface Contracts", encoding="utf-8")

    # 5. CONTRACTS -> SCAFFOLDING (HITL 批准)
    state, _ = fsm.advance(hitl_approved=True)
    assert state == FSMState.SCAFFOLDING

    # 准备 SCAFFOLDING 资产
    scaff_dir = temp_workspace / "04-delivery-and-organization"
    scaff_dir.mkdir(parents=True, exist_ok=True)
    (temp_workspace / ".agent-rules.md").write_text("# Rules", encoding="utf-8")
    (scaff_dir / "organization-structure.md").write_text("# Org", encoding="utf-8")
    (scaff_dir / "estimation-and-plan.md").write_text("# Plan", encoding="utf-8")
    (scaff_dir / "first-step-poc.md").write_text("# PoC", encoding="utf-8")
    (scaff_dir / "walking-skeleton-spec.json").write_text(json.dumps({"skeleton": True}), encoding="utf-8")

    # 6. SCAFFOLDING -> FINALIZED
    state, _ = fsm.advance()
    assert state == FSMState.FINALIZED

    # 在 FINALIZED 下再次推进，应平稳停留在终态
    state_final, msg = fsm.advance()
    assert state_final == FSMState.FINALIZED
    assert "已处于终态" in msg

