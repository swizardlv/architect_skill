"""架构生命周期主控状态机引擎 (Architecture Lifecycle FSM Orchestrator).

本模块实现确定性有限状态机（Deterministic FSM），用于调度和编排架构设计生命周期的
所有原子 Skill，严格执行单向基线推进、门禁校验（Gatekeeper Validation）以及
人类介入卡点（Human-in-the-Loop, HITL）。
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from render_architecture_board import validate_mermaid_syntax
except ImportError:
    from .render_architecture_board import validate_mermaid_syntax



class FSMState(str, Enum):
    """架构生命周期状态枚举."""

    INIT = "INIT"
    GRILLING = "GRILLING"
    GROUNDING = "GROUNDING"
    MODELING = "MODELING"
    CONTRACTS = "CONTRACTS"
    SCAFFOLDING = "SCAFFOLDING"
    FINALIZED = "FINALIZED"


class FSMError(Exception):
    """状态机异常基类."""


class StateTransitionError(FSMError):
    """非法状态跃迁异常."""


class GatekeeperError(FSMError):
    """门禁校验未通过异常."""


class ReviewRejectedError(FSMError):
    """人工审批打回异常."""


@dataclass
class GatekeeperResult:
    """门禁自检结果数据结构."""

    passed: bool
    state: FSMState
    required_artifacts: List[str]
    missing_artifacts: List[str] = field(default_factory=list)
    invalid_artifacts: List[Dict[str, str]] = field(default_factory=list)
    message: str = ""

    def summary(self) -> str:
        """返回门禁结果简报."""
        if self.passed:
            return f"[Gatekeeper: 通过] 状态 {self.state.value} 所需关键资产均已就绪并通过校验。"
        issues = []
        if self.missing_artifacts:
            issues.append(f"缺失文件: {', '.join(self.missing_artifacts)}")
        if self.invalid_artifacts:
            for item in self.invalid_artifacts:
                issues.append(f"文件格式错误: {item.get('path')} ({item.get('error')})")
        return f"[Gatekeeper: 拦截] 状态 {self.state.value} 门禁未达成 -> " + "; ".join(issues)


@dataclass
class TransitionRecord:
    """状态跃迁历史记录."""

    from_state: str
    to_state: str
    timestamp: str
    action: str
    hitl_approved: bool
    notes: str = ""


class ArchitectureLifecycleFSM:
    """主控架构生命周期有限状态机."""

    def __init__(
        self,
        workspace_root: Optional[Path | str] = None,
        config_path: Optional[Path | str] = None,
        auto_persist: bool = True,
    ) -> None:
        """初始化状态机引擎.

        Args:
            workspace_root: 架构产物输出根目录，默认基于项目根目录下的 docs/architecture
            config_path: FSM 配置文件路径，默认使用本模块同目录的 fsm_config.json
            auto_persist: 是否在每次状态改变后自动持久化到 .state.json
        """
        self.module_dir = Path(__file__).parent.resolve()
        self.repo_root = self.module_dir.parent.parent.resolve()

        if config_path is None:
            self.config_path = self.module_dir / "fsm_config.json"
        else:
            self.config_path = Path(config_path).resolve()

        self._load_config()

        if workspace_root is None:
            configured_ws = self.config.get("workspace_root", "docs/architecture")
            self.workspace_root = (self.repo_root / configured_ws).resolve()
        else:
            self.workspace_root = Path(workspace_root).resolve()

        self.state_file = self.workspace_root / self.config.get("state_persistence_file", ".state.json")
        self.auto_persist = auto_persist

        # 核心运行时状态
        self.current_state: FSMState = FSMState.INIT
        self.history: List[TransitionRecord] = []
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated_at": datetime.now(timezone.utc).isoformat(),
            "project_name": "unknown",
        }

        # 尝试从磁盘加载历史状态
        self.resume_or_init()

    def _load_config(self) -> None:
        """从 JSON 读取状态机配置."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"状态机配置文件未找到: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config: Dict[str, Any] = json.load(f)
        self.states_cfg: Dict[str, Any] = self.config.get("states", {})

    def resume_or_init(self) -> bool:
        """尝试从持久化文件中恢复状态，若不存在则初始化工作区.

        Returns:
            bool: True 表示成功恢复旧状态，False 表示新建初始状态。
        """
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                state_str = data.get("current_state", FSMState.INIT.value)
                self.current_state = FSMState(state_str)
                self.metadata = data.get("metadata", self.metadata)
                history_raw = data.get("history", [])
                self.history = [TransitionRecord(**item) for item in history_raw]
                return True
            except Exception as e:
                # 若文件损坏，记录警告并重置
                print(f"[警告] 读取持久化状态失败 ({e})，重新初始化状态机。", file=sys.stderr)

        # 默认初始状态
        self.current_state = FSMState.INIT
        self.history = []
        self.ensure_workspace_directories()
        if self.auto_persist:
            self.persist()
        return False

    def ensure_workspace_directories(self) -> None:
        """确保各阶段所需标准物理子目录就绪，杜绝废弃旧目录生成."""
        subdirs = [
            "00-state",
            "01-requirements",
            "02-architecture-design",
            "03-engineering-and-physics",
            "03-engineering-and-physics/adrs",
            "03-engineering-and-physics/contracts",
            "04-delivery-and-organization",
        ]
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        for sub in subdirs:
            (self.workspace_root / sub).mkdir(parents=True, exist_ok=True)

    def persist(self) -> None:
        """将状态机运行状态序列化保存到 .state.json."""
        self.ensure_workspace_directories()
        self.metadata["last_updated_at"] = datetime.now(timezone.utc).isoformat()
        payload = {
            "machine_name": self.config.get("machine_name", "architecture_lifecycle_fsm"),
            "version": self.config.get("version", "1.0.0"),
            "current_state": self.current_state.value,
            "metadata": self.metadata,
            "history": [asdict(record) for record in self.history],
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def resolve_artifact_path(self, rel_path: str) -> Path:
        """解析资产文件的绝对路径.

        特殊路径以 `.agent-rules.md` 开头时优先定位到 workspace_root（测试环境），
        若不存在则定位到仓库根目录 repo_root。其余路径定位到 workspace_root。
        """
        if rel_path == ".agent-rules.md" or rel_path.startswith(".agent-rules"):
            ws_file = self.workspace_root / rel_path
            if ws_file.exists():
                return ws_file
            return self.repo_root / rel_path
        return self.workspace_root / rel_path

    def validate_gatekeeper(self, state: FSMState) -> GatekeeperResult:
        """执行指定状态的准出门禁校验.

        Args:
            state: 要检查的目标状态

        Returns:
            GatekeeperResult: 校验结果对象
        """
        state_info = self.states_cfg.get(state.value, {})
        exit_gate = state_info.get("exit_gate", {})
        required_artifacts: List[str] = exit_gate.get("required_artifacts", [])

        missing: List[str] = []
        invalid: List[Dict[str, str]] = []

        for rel_path in required_artifacts:
            full_path = self.resolve_artifact_path(rel_path)
            if not full_path.exists():
                missing.append(rel_path)
                continue

            # 资产内容基本有效性校验
            try:
                content = full_path.read_text(encoding="utf-8").strip()
                if len(content) == 0:
                    invalid.append({"path": rel_path, "error": "文件内容为空"})
                    continue

                # 针对 JSON 文件进行语法结构校验
                if full_path.suffix.lower() == ".json":
                    try:
                        parsed = json.loads(content)
                        if not isinstance(parsed, dict) or not parsed:
                            invalid.append({"path": rel_path, "error": "JSON 内容必须是非空对象"})
                    except Exception as err:
                        invalid.append({"path": rel_path, "error": f"JSON 解析失败: {err}"})

                # 针对 Mermaid 文件 (.mmd) 进行静态语法门禁校验
                if full_path.suffix.lower() == ".mmd":
                    is_valid, err_msg = validate_mermaid_syntax(content)
                    if not is_valid:
                        invalid.append({"path": rel_path, "error": f"Mermaid 语法门禁未通过: {err_msg}"})

                # 针对 Markdown 文件中的内嵌 Mermaid 代码块进行语法门禁校验
                if full_path.suffix.lower() == ".md":
                    mermaid_blocks = re.findall(r"```mermaid\s*\n(.*?)\n```", content, re.DOTALL)
                    for idx, block in enumerate(mermaid_blocks, 1):
                        is_valid, err_msg = validate_mermaid_syntax(block)
                        if not is_valid:
                            invalid.append({
                                "path": rel_path,
                                "error": f"第 {idx} 个内嵌 Mermaid 图表语法错误: {err_msg}"
                            })

                # 针对 functional-requirements.md 进行深度语义校验: 必须包含具体功能需求规约(FR清单)
                if full_path.name.lower() == "functional-requirements.md":
                    has_fr = bool(re.search(r"(###?\s*.*(功能需求|FR-|\d+\.\s*功能需求))", content))
                    if not has_fr:
                        invalid.append({
                            "path": rel_path,
                            "error": "功能需求规约缺失: 仅包含用例(Use Cases)或角色画像(Persona)，未列出明确的系统功能需求(FR清单)"
                        })

                # 针对 architecture-requirements-checklist.md 进行深度语义校验: 必须包含 ARC 质量闭环追踪表
                if full_path.name.lower() == "architecture-requirements-checklist.md":
                    has_arc_table = bool(re.search(r"(ARC-\d+|质量属性类别|量化设计指标)", content))
                    if not has_arc_table:
                        invalid.append({
                            "path": rel_path,
                            "error": "ARC 质量保障清单缺失: 未包含量化指标追踪矩阵(ARC-xx)"
                        })

            except Exception as err:
                invalid.append({"path": rel_path, "error": f"读取异常: {err}"})

        # 针对 SCAFFOLDING 状态进行深度语义门禁校验
        if state == FSMState.SCAFFOLDING and len(missing) == 0 and len(invalid) == 0:
            spec_path = self.resolve_artifact_path("04-delivery-and-organization/walking-skeleton-spec.json")
            if not spec_path.exists():
                spec_path = self.resolve_artifact_path("04-execution/walking-skeleton-spec.json")
            if spec_path.exists():
                try:
                    spec_data = json.loads(spec_path.read_text(encoding="utf-8"))
                    required_dirs = spec_data.get("directories", [])
                    target_base = self.workspace_root.parent.parent
                    for req_dir in required_dirs:
                        d_path = target_base / req_dir
                        if not d_path.exists():
                            missing.append(f"骨架目录缺失: {req_dir}")
                except Exception as err:
                    invalid.append({"path": "04-delivery-and-organization/walking-skeleton-spec.json", "error": f"规范读取失败: {err}"})

        passed = (len(missing) == 0) and (len(invalid) == 0)
        message = "门禁检查通过" if passed else "门禁存在未达成项"
        return GatekeeperResult(
            passed=passed,
            state=state,
            required_artifacts=required_artifacts,
            missing_artifacts=missing,
            invalid_artifacts=invalid,
            message=message,
        )

    def get_hitl_prompt(self, state: FSMState) -> Optional[str]:
        """获取当前状态是否有需人类确认的卡点提示词."""
        state_info = self.states_cfg.get(state.value, {})
        exit_gate = state_info.get("exit_gate", {})
        if exit_gate.get("hitl_required", False):
            return exit_gate.get("review_prompt", "需要人工审查确认，是否批准推进？")
        return None

    def advance(
        self,
        action: Optional[str] = None,
        hitl_approved: bool = False,
        reviewer_feedback: str = "",
        hitl_prompt_callback: Optional[Callable[[str], bool]] = None,
    ) -> Tuple[FSMState, str]:
        """推进状态机至下一个确定性状态.

        Args:
            action: 显式触发动作（如 APPROVE, REJECT, START 等）；若为 None，则根据规则推断
            hitl_approved: 针对人类卡点是否直接授予放行
            reviewer_feedback: 人工审查意见
            hitl_prompt_callback: 交互式询问回调函数，入参为提示词，返回 bool 表示是否批准

        Returns:
            Tuple[FSMState, str]: 跃迁后的新状态与本次动作说明

        Raises:
            GatekeeperError: 前置门禁未满足
            ReviewRejectedError: 人工审查被拒绝
            StateTransitionError: 非法状态跃迁
        """
        if self.current_state == FSMState.FINALIZED:
            return FSMState.FINALIZED, "架构设计生命周期已处于终态 (FINALIZED)，无需再次推进。"

        state_info = self.states_cfg.get(self.current_state.value, {})
        transitions: Dict[str, str] = state_info.get("transitions", {})

        # 1. 检查当前状态的门禁（INIT 状态除外）
        if self.current_state != FSMState.INIT:
            gate_res = self.validate_gatekeeper(self.current_state)
            if not gate_res.passed:
                raise GatekeeperError(gate_res.summary())

        # 2. 检查人类卡点 (Human-in-the-Loop)
        hitl_prompt = self.get_hitl_prompt(self.current_state)
        approved = hitl_approved

        if hitl_prompt is not None:
            if not approved and hitl_prompt_callback is not None:
                approved = hitl_prompt_callback(hitl_prompt)

            if not approved:
                # 记录拒绝并触发打回流转
                if "REJECT" in transitions:
                    target_state_str = transitions["REJECT"]
                    target_state = FSMState(target_state_str)
                    self._record_transition(
                        from_state=self.current_state,
                        to_state=target_state,
                        action="REJECT",
                        hitl_approved=False,
                        notes=f"人工打回: {reviewer_feedback or '未提供理由'}",
                    )
                    self.current_state = target_state
                    if self.auto_persist:
                        self.persist()
                    raise ReviewRejectedError(f"人工审查拒绝放行，已回退至: {target_state.value}。意见: {reviewer_feedback}")
                else:
                    raise ReviewRejectedError("人工审查拒绝放行，当前状态未配置打回回退路径。")

        # 3. 确定目标跃迁状态
        chosen_action = action
        if chosen_action is None:
            if hitl_prompt is not None:
                chosen_action = "APPROVE"
            elif "START" in transitions:
                chosen_action = "START"
            elif "ARTIFACTS_VALIDATED" in transitions:
                chosen_action = "ARTIFACTS_VALIDATED"
            elif "MODELS_VALIDATED" in transitions:
                chosen_action = "MODELS_VALIDATED"
            elif "SKELETON_INITIALIZED" in transitions:
                chosen_action = "SKELETON_INITIALIZED"
            elif len(transitions) == 1:
                chosen_action = list(transitions.keys())[0]
            else:
                raise StateTransitionError(f"状态 {self.current_state.value} 存在多个候选跃迁动作，必须显式指定 action: {list(transitions.keys())}")

        if chosen_action not in transitions:
            raise StateTransitionError(f"动作 '{chosen_action}' 在状态 {self.current_state.value} 中不合法。有效动作: {list(transitions.keys())}")

        target_state_str = transitions[chosen_action]
        target_state = FSMState(target_state_str)

        # 4. 执行状态跃迁并记录
        old_state = self.current_state
        self._record_transition(
            from_state=old_state,
            to_state=target_state,
            action=chosen_action,
            hitl_approved=approved,
            notes=reviewer_feedback,
        )
        self.current_state = target_state

        if self.auto_persist:
            self.persist()

        return self.current_state, f"从 {old_state.value} 跃迁至 {target_state.value} [动作: {chosen_action}]"

    def _record_transition(
        self,
        from_state: FSMState,
        to_state: FSMState,
        action: str,
        hitl_approved: bool,
        notes: str = "",
    ) -> None:
        """记录状态跃迁历史."""
        record = TransitionRecord(
            from_state=from_state.value,
            to_state=to_state.value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            action=action,
            hitl_approved=hitl_approved,
            notes=notes,
        )
        self.history.append(record)

    def get_status_report(self) -> Dict[str, Any]:
        """获取当前生命周期状态概览报告."""
        current_cfg = self.states_cfg.get(self.current_state.value, {})
        gate_res = self.validate_gatekeeper(self.current_state) if self.current_state != FSMState.INIT else None

        return {
            "current_state": self.current_state.value,
            "description": current_cfg.get("description", ""),
            "active_skills": current_cfg.get("skills", []),
            "hitl_required": current_cfg.get("exit_gate", {}).get("hitl_required", False),
            "gatekeeper_passed": gate_res.passed if gate_res else True,
            "gatekeeper_summary": gate_res.summary() if gate_res else "初始状态无需门禁检查",
            "workspace_path": str(self.workspace_root),
            "state_file": str(self.state_file),
            "history_steps_count": len(self.history),
        }
