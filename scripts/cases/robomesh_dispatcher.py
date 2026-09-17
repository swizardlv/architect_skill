"""案例 2: 工业级多机自主移动机器人(AMR)无人仓协同调度中枢 (RoboMesh-Dispatcher).

基于时空网格预约机制与动态局部避障算法，解决千台异构移动机器人在超大仓储空间的路径死锁与高并发调度问题。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "skills" / "00_orchestrator"))

from orchestrate_architecture_lifecycle import ArchitectureLifecycleFSM
from render_architecture_board import render_board


def run_robomesh_case_study(target_root: Path) -> None:
    """执行无人仓机器人协同调度中枢 (RoboMesh-Dispatcher) 架构全流程推演."""
    ws_root = target_root / "docs" / "architecture"
    ws_root.mkdir(parents=True, exist_ok=True)

    print(f"\n======================================================================")
    print(f" 🚀 启动案例推演: 无人仓机器人协同调度中枢 (RoboMesh-Dispatcher)")
    print(f" 🎯 目标工作区: {ws_root}")
    print(f"======================================================================\n")

    # 1. 初始化状态机
    fsm = ArchitectureLifecycleFSM(workspace_root=ws_root)
    if fsm.state_file.exists():
        fsm.state_file.unlink()
    fsm.resume_or_init()
    print(f"[阶段 0] 初始化完成，当前状态: {fsm.current_state.value}")

    # 2. INIT -> GRILLING
    fsm.advance()
    print(f"[阶段 1] 推进至需求深挖状态: {fsm.current_state.value}")

    # -------------------------------------------------------------
    # 模拟 Skill 1: grill_architecture_requirements 执行产出
    # -------------------------------------------------------------
    grounding_spec = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "status": "COMPLETED",
        "grounding_spec": {
            "project_name": "robomesh-autonomous-dispatch",
            "business_driver": "超级智慧物流中心占地 80,000 平方米，常驻 1,200 台异构自主移动机器人（AMR/AGV）。历史高峰期因窄巷道相向行驶与局部死锁导致全场瘫痪停摆（周均 8 次人工干预救援）。通过构建“时空网格预约 (Space-Time Reservation Table) + 动态窗口局部重规划”中枢，杜绝物理相撞与通道死锁，动态避障重规划耗时控制在 100ms 内，全场出库搬运吞吐量提升 40%。",
            "core_invariants": [
                "时空唯一硬互斥法则：在同一时空网格切片（1.2m x 1.2m，时间窗口 delta_t = 200ms）内，绝对只允许至多一台机器人占有预约，禁止空间重叠",
                "急停短路优先法则：激光雷达/急停开关触发的 E-Stop 信号享有绝对最高优先级，可在 20ms 内无条件让步并强制底盘机械抱死刹车",
                "物料载荷原子守恒法则：托盘在货位与机器人之间的移交状态必须满足严格原子性，禁止无载荷虚报或双重认领"
            ],
            "nfr_targets": {
                "throughput_qps": "并发管理 1,500 台机器人，遥测上报 20Hz (30,000 QPS 心跳与时空状态广播)",
                "p99_latency": "时空预约查询与冲突检测 P99 < 15ms；动态局部重路由规划 P95 < 80ms",
                "rpo_rto": "调度状态恢复 RTO < 5 秒 (基于共享内存与时空镜像快照自愈)，RPO = 0 (不可丢失物理分配日志)",
                "consistency_preference": "AP + 局部强一致 (全局态势最终一致，局部交叉路口时空锁强一致)",
                "resource_budget": "边缘调度计算集群单节点 CPU 核心占用 <= 60%，内存工作集驻留 <= 16GB"
            },
            "constraints": {
                "tech_stack_allowlist": ["Rust 1.75+", "Python 3.11+", "MQTT 5.0", "Redis 7 Cluster", "gRPC"],
                "ops_and_infrastructure": "仓内专用 5.8G 工业专网 + 边缘多机热备私有节点，全链路与公共外网物理隔离",
                "legacy_integrations": ["VDA 5050 国际通用机器人通信协议", "WMS 仓储出入库系统 (REST/gRPC)", "自动化立体库堆垛机与提升机控制系统"]
            },
            "anti_goals": [
                "本期不研发单机底盘激光 SLAM 导航算法本身（由机载控制器自主实现，中枢仅做时空协调）",
                "严禁允许云端通过公共互联网直接干预底盘电机脉冲信号"
            ]
        }
    }
    (ws_root / "00-grounding" / "grounding-spec.json").write_text(
        json.dumps(grounding_spec, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(" -> 产出资产: 00-grounding/grounding-spec.json 就绪")

    # 3. GRILLING -> GROUNDING (HITL 审批放行)
    fsm.advance(hitl_approved=True, reviewer_feedback="自动化仓储总工与安全专家已确认业务目标、VDA 5050 协议边界与三大物理防撞不变量")
    print(f"[阶段 2] 门禁与HITL通过，推进至约束与度量基准状态: {fsm.current_state.value}")

    # -------------------------------------------------------------
    # 模拟 Skill 2 & 3: distill_nfr_matrix & catalog_invariants
    # -------------------------------------------------------------
    nfr_matrix_content = """# RoboMesh 质量属性与非功能需求度量矩阵

## 1. 实时性能与高并发指标 (Real-Time Performance)
| 指标项 | 目标基准 | 极限阈值 | 度量方式 | 违约影响 |
|---|---|---|---|---|
| **时空预约冲突检测延迟** | P95 < 10ms | P99 < 20ms | 共享内存压测打点 | 路口通行预约排队，小车减速停滞 |
| **动态局部避障重路由耗时** | P50 < 40ms | P95 < 80ms | 算法求解时钟监控 | 机器人原地等待超时，阻碍后方行进队列 |
| **20Hz 遥测接入峰值能力** | 30,000 QPS | 50,000 QPS | MQTT Broker 压力测试 | 遥测丢包，数字孪生看板脱靶 |
| **时钟同步误差 (PTP)** | < 1.0ms | < 5.0ms | IEEE 1588 硬件时钟差 | 时空网格切片时间错位，产生虚假碰撞报警 |

## 2. 安全与工业高可用指标 (Safety & Availability)
| 质量维度 | 指标定义 | 保障策略 | 验收标准 |
|---|---|---|---|
| **急停信号穿透时延** | <= 20ms | 硬件急停信号专用旁路 UDP 广播与硬连线 | 任何突发异常下 20ms 内切断动力输出 |
| **死锁自动消除率** | 100% | 局部等待图有向环检测 + 动态倒退重分配 | 巷道无车组无限期对峙，自动脱困解耦 |
| **弱网生存能力** | 3 秒断网不撞车 | 航位推算 (Dead Reckoning) + 局部保留区 | 断网期间沿已有预约区间前行并在终点停车 |
"""
    (ws_root / "01-grounding" / "nfr-matrix.md").write_text(nfr_matrix_content, encoding="utf-8")

    constraints_content = """# RoboMesh 硬性约束与工业规范清单

## 1. 行业标准与物理协议边界
- **VDA 5050 (v2.0)**：所有与 AMR 底盘的通讯（Order, InstantAction, State, Visualization）必须符合 VDA 5050 国际通用标准。
- **CE/ISO 3691-4 工业安全标准**：软硬件急停与减速防撞保护机制必须满足工业自动化安全完整性要求 (SIL 2 / PL d)。

## 2. 运行时与硬件基础设施
- **边缘计算节点**：部署在仓内配电室工业边缘一体机，双机高可用热备，不依赖外部公网。
- **专网覆盖**：双频段 Wi-Fi 6 + 私网 5G 双网卡无缝漫游切换。
"""
    (ws_root / "01-grounding" / "constraints-and-assumptions.md").write_text(constraints_content, encoding="utf-8")
    print(" -> 产出资产: 01-grounding/nfr-matrix.md & constraints-and-assumptions.md 就绪")

    # 4. GROUNDING -> MODELING
    fsm.advance()
    print(f"[阶段 3] 门禁通过，推进至结构建模状态: {fsm.current_state.value}")

    # -------------------------------------------------------------
    # 模拟 Skill 4, 5, 6: C4 Context, Container, Domain & Diagrams
    # -------------------------------------------------------------
    c4_context = """flowchart TD
    subgraph Users ["操作人员与上游系统"]
        WMS["WMS / ERP 仓储管理系统"]
        Ops["中控室调度员 (Web Console)"]
    end

    subgraph SystemBoundary ["RoboMesh 工业仓储协同调度系统"]
        DispatchMesh["RoboMesh 调度中枢<br/>[集群系统]<br/>负责时空预约、多机避障与最优路径排程"]
    end

    subgraph Hardware ["物理外围设备与搬运装备"]
        AMR["AMR/AGV 移动机器人集群<br/>[1,200台 兼容 VDA 5050]"]
        Charger["自动换电 / 充电桩基站"]
        Conveyor["自动化提升机与立库出入库输送线"]
    end

    WMS -->|"下发搬运搬货工单 (REST/gRPC)"| DispatchMesh
    Ops -->|"实时态势大屏监控 / 人工介入 (WebSockets)"| DispatchMesh
    DispatchMesh -->|"下发时空分段轨迹与指令 (MQTT/VDA 5050)"| AMR
    AMR -->|"20Hz 遥测/位姿/避障上报"| DispatchMesh
    DispatchMesh -->|"预约与调度充放电"| Charger
    DispatchMesh -->|"协同货架交接与信号联锁"| Conveyor
"""
    (ws_root / "02-models" / "c4-context.mmd").write_text(c4_context, encoding="utf-8")

    c4_container = """flowchart TD
    subgraph RoboMesh ["RoboMesh 协同调度中枢"]
        Gateway["VDA 5050 协议网关<br/>[MQTT 5.0 Broker & Adapter]<br/>处理 30,000 QPS 遥测并标准化"]
        ReservationEngine["时空网格预约引擎 (STR-Core)<br/>[In-Memory 共享内存表]<br/>毫秒级时空互斥检测与网格占用锁"]
        PathSolver["CBS 动态路径重规划求解器<br/>[A* / Conflict-Based Search]<br/>全局最优轨迹生成与局部动态防碰撞重排"]
        DeadlockDetector["环形死锁态势扫描器<br/>[Background Daemon]<br/>有向等待图拓扑分析与自动解耦释放"]
        TwinDashboard["数字孪生大屏服务<br/>[FastAPI & WebSockets]<br/>百毫秒内仓储全景 3D 态势渲染数据分发"]
    end

    Gateway -->|"更新机器人最新位姿"| ReservationEngine
    Gateway -->|"上报行驶阻塞与遇障事件"| PathSolver
    ReservationEngine <-->|"冲突检测与预约锁定"| PathSolver
    ReservationEngine -->|"读取全场拓扑与机器人状态"| DeadlockDetector
    DeadlockDetector -->|"触发死锁避让重路由"| PathSolver
    ReservationEngine -->|"低频态势聚合广播"| TwinDashboard
"""
    (ws_root / "02-models" / "c4-container-overview.mmd").write_text(c4_container, encoding="utf-8")

    domain_model = """# RoboMesh 领域模型与时空状态机规范

## 1. 核心领域实体
- **时空网格单元 (SpaceTimeCell)**：`(grid_x, grid_y, time_window_start, time_window_end)`，表征三维（2D 平面 + 1D 时间）占用原子单位。
- **移动机器人 (AMRInstance)**：底盘唯一标识、硬件规格、载荷状态（空载/托盘）、电池电量、当前时空锚点。
- **分段运动轨迹 (TrajectoryPath)**：由有序的时空网格节点构成的轨迹序列，包含速度剖面与预定到达时间窗。

## 2. 机器人运动控制状态机 (State Machine)
```mermaid
stateDiagram-v2
    [*] --> IDLE : 开机自检通过
    IDLE --> ASSIGNED : 接收到搬运工单
    ASSIGNED --> RESERVING : 提交初始路线时空预约
    RESERVING --> NAVIGATING : 时空网格锁定成功
    RESERVING --> REROUTING : 发现网格冲突 / 被占用
    REROUTING --> RESERVING : 重规划生成新可行轨迹
    NAVIGATING --> OCCUPYING_TARGET : 抵达终点货位
    NAVIGATING --> OBSTACLE_WAITING : 传感器检测到突发静态障碍
    OBSTACLE_WAITING --> REROUTING : 超过 2 秒未消除触发局部绕障
    OCCUPYING_TARGET --> DELIVERED : 完成载荷升降移交
    DELIVERED --> CHARGING : 电量低于 20%
    DELIVERED --> IDLE : 待命分配下一任务
    NAVIGATING --> EMERGENCY_STOPPED : 接收到 E-Stop 信号 / 防撞雷达告警
    EMERGENCY_STOPPED --> IDLE : 人工或系统安全复位
```
"""
    (ws_root / "02-models" / "domain-logical-model.md").write_text(domain_model, encoding="utf-8")

    interaction_seq = """sequenceDiagram
    autonumber
    actor WMS as WMS 仓储系统
    participant GW as VDA 5050 网关
    participant Solver as CBS 路径求解器
    participant STR as 时空预约引擎 (STR-Core)
    participant AMR as AMR 底盘驱动器

    WMS->>Solver: 下发运单 (起点货位 A -> 终点货位 B)
    Solver->>STR: 查询时空拓扑图可用时隙
    STR-->>Solver: 返回时空空闲窗口列表
    Solver->>Solver: 计算无冲突最优时空轨迹 Trajectory
    Solver->>STR: 批量锁定 Trajectory 时空网格 (Atomically Lock)
    STR-->>Solver: 锁定确认成功 (Lease: 15s)
    Solver->>GW: 下发 VDA 5050 Order 指令
    GW->>AMR: MQTT 广播分段轨迹与速度控制参数

    loop 20Hz 实时跟踪与遇障反馈
        AMR->>GW: 遥测心跳 (当前坐标, 速度, 激光雷达点云)
        GW->>STR: 刷新位姿并推进时空网格释放进度
        alt 遇到突发异物阻挡 (动态障碍)
            AMR->>GW: 发送 Warning (Obstacle Blocked)
            GW->>Solver: 请求局部 5 米动态重规划
            Solver->>STR: 释放原前方时空预约，锁定绕障新网格
            STR-->>Solver: 局部网格锁定成功
            Solver->>GW: 下发局部绕障补丁 (Instant Action: Replace Trajectory)
            GW->>AMR: 更新瞬态运动路径
        end
    end

    AMR->>GW: 到达目标工位，货物举升交接完成
    GW->>STR: 彻底释放该任务所占全部时空网格
    GW->>WMS: 报告搬运工单圆满完成
"""
    (ws_root / "02-models" / "interaction-sequence.mmd").write_text(interaction_seq, encoding="utf-8")

    data_flow = """flowchart LR
    subgraph Ingestion ["高频遥测接入层"]
        AMR_Raw["1,200 台 AMR 底盘"] -->|"UDP/MQTT 20Hz"| Broker["高可用边缘 Broker"]
        Broker --> Dispatcher["遥测分发管线"]
    end

    subgraph HotState ["内存热态态势层"]
        Dispatcher -->|"位姿同步 (<5ms)"| ShmTable["时空预约共享内存表 (STR-Shm)"]
        ShmTable -->|"环路检测"| DeadlockScan["死锁拓扑检测器"]
    end

    subgraph Compute ["算法决策计算层"]
        DeadlockScan -->|"唤醒重排"| CBSSolver["CBS 路径规划求解器"]
        CBSSolver <-->|"网格加锁/释放"| ShmTable
        CBSSolver -->|"下发轨迹"| CommandQueue["底盘指令下发通道"]
    end

    subgraph ColdArchive ["持久化与态势大屏"]
        Dispatcher -->|"降采样 1Hz"| TimeSeriesDB["时序态势数据库 (IoT DB)"]
        TimeSeriesDB --> Dashboard["3D 态势孪生大屏"]
    end
"""
    (ws_root / "02-models" / "data-flow.mmd").write_text(data_flow, encoding="utf-8")
    print(" -> 产出资产: 02-models/ 下 5 维图谱全部就绪")

    # 渲染自包含画板
    render_board(ws_root)

    # 5. MODELING -> CONTRACTS
    fsm.advance()
    print(f"[阶段 4] 门禁通过，推进至决策与契约签署状态: {fsm.current_state.value}")

    # -------------------------------------------------------------
    # 模拟 Skill 7, 8, 9: ADR, FMEA & OpenAPI
    # -------------------------------------------------------------
    adr_content = """# ADR-001: 采用时空网格预约 (STR) 与 CBS 算法取代单机贪心重算

## 状态
已接受 (ACCEPTED) - 2026-09-17

## 上下文
在 1,200 台异构机器人密集作业的仓储物理空间中，若采用传统单机贪心规划与局部避障（如 DWA/TEB 独立避障），机器人极易在交叉路口形成“双向互锁对峙”或在狭窄巷道陷入死循环；而若每次冲突都执行全局全量 A* 重算，其时间复杂度随着机器人数量呈指数级组合爆炸，无法满足 100ms 实时重排指标。

## 架构决策
1. **统一引入离散化时空网格预约表 (Space-Time Reservation Table)**：将仓库三维空间划分为 `(x, y, delta_t)` 的时空体素（Voxel）。每个体素实行独占式原子锁。
2. **两阶段求解 (Conflict-Based Search, CBS)**：
   - 低层：单机在无冲突时空时隙内寻找启发式最短轨迹。
   - 高层：冲突树搜索。仅当两机发生时空相交时，才对冲突机器人施加互斥时空约束并局部重算。
3. **分层降级通道**：若 CBS 在 80ms 内无法收敛，降级为“优先级靠后者减速避让并原地等待”。

## 架构影响
- **正面收益**：
  - 彻底规避物理相向死锁，空间占用利用率提升 35% 以上。
  - 局部重规划时延稳定在 P95 < 50ms。
- **权衡代价**：
  - 时空预约表对各机器人车载时钟同步精度要求极高，必须配置 PTP (IEEE 1588) 达到亚毫秒级同步。
"""
    (ws_root / "03-decisions" / "ADR-001-space-time-reservation.md").write_text(adr_content, encoding="utf-8")

    adr_index = """# 架构决策记录索引 (ADR Index)

| 编号 | 决策标题 | 状态 | 决策人 | 影响范围 |
|---|---|---|---|---|
| [ADR-001](./ADR-001-space-time-reservation.md) | 采用时空网格预约 (STR) 与 CBS 算法取代单机贪心重算 | 已接受 | 调度架构组 / 安全官 | 路径计算核心、共享内存表、通信网关 |
"""
    (ws_root / "03-decisions" / "adr-index.md").write_text(adr_index, encoding="utf-8")

    openapi_yaml = """openapi: 3.0.3
info:
  title: RoboMesh 协同调度与任务分派接口规范
  version: 1.0.0
  description: 供 WMS 系统与中控台下发搬运任务、查询机器人状态及触发紧急调度的北向接口
paths:
  /api/v1/dispatch/tasks:
    post:
      summary: 创建并排程物料搬运任务
      operationId: createDispatchTask
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [task_id, source_grid, target_grid, payload_type]
              properties:
                task_id:
                  type: string
                source_grid:
                  type: object
                  properties:
                    x: {type: integer}
                    y: {type: integer}
                target_grid:
                  type: object
                  properties:
                    x: {type: integer}
                    y: {type: integer}
                payload_type:
                  type: string
                  enum: [STANDARD_PALLET, HEAVY_RACK, EMPTY_CARRIER]
      responses:
        '202':
          description: 任务已接收并完成时空预约锁定
        '409':
          description: 时空网格冲突或当前全场拥塞无法锁定路线
  /api/v1/safety/emergency-stop:
    post:
      summary: 全场或区域安全急停广播
      operationId: broadcastEmergencyStop
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [scope, reason]
              properties:
                scope:
                  type: string
                  enum: [ALL_ROBOTS, ZONE_AISLE_NORTH, ZONE_AISLE_SOUTH]
                reason:
                  type: string
      responses:
        '200':
          description: 急停信号已在 20ms 内穿透下发底盘抱死
"""
    (ws_root / "04-contracts" / "openapi.yaml").write_text(openapi_yaml, encoding="utf-8")

    fmea_content = """# RoboMesh 失效模式与工业容灾矩阵 (FMEA Matrix)

## 1. 核心工业失效模式分析
| 组件/故障点 | 潜在失效模式 | 发生概率 | 影响严重度 | 防御、降级与自愈策略 |
|---|---|---|---|---|
| **Wi-Fi 局域网抖动** | 机器人 1~3 秒内丢失遥测心跳 | 高 | 严重 (可能造成滞后误碰) | 1. 启用航位推算，机器人沿已锁定预留网格低速慢行。<br>2. 超过 3 秒未恢复则原地停车并亮黄灯闪烁。 |
| **时钟同步失步** | 某台机器人时钟漂移超过 100ms | 中 | 灾难 (时空网格窗口错位) | 1. 网关每次遥测校验时间戳差值。<br>2. 差值超 50ms 立即从时空表中剥离其预约，强制重新校时。 |
| **传感器误报障碍** | 反光柱或灰尘导致激光雷达假阳性 | 高 | 中 (局部降速堵车) | 1. 连续 3 帧点云置信度过滤。<br>2. 保持 2 秒以上确认为物理障碍物，启动局部重规划。 |
| **急停短路保护** | 某机器人急停无法靠软件刹车 | 极低 | 致命 | 1. 机载独立安全继电器硬件切断电机动力。<br>2. 周围 5 米同区域所有机器人被动原地制动锁定。 |
"""
    (ws_root / "03-decisions" / "failure-resilience-matrix.md").write_text(fmea_content, encoding="utf-8")
    print(" -> 产出资产: 03-decisions/ & 04-contracts/ 就绪")

    # 6. CONTRACTS -> SCAFFOLDING (HITL 审批放行)
    fsm.advance(hitl_approved=True, reviewer_feedback="安全委员会与现场调度经理已审核签署 OpenAPI 契约、FMEA 矩阵与 ADR-001")
    print(f"[阶段 5] 门禁与HITL通过，推进至工程骨架与交付排期: {fsm.current_state.value}")

    # -------------------------------------------------------------
    # 模拟 Skill 10 & 11: bootstrap_skeleton & delivery_milestones
    # -------------------------------------------------------------
    src_domain = target_root / "src" / "domain"
    src_ports = target_root / "src" / "ports"
    src_adapters = target_root / "src" / "adapters"
    src_domain.mkdir(parents=True, exist_ok=True)
    src_ports.mkdir(parents=True, exist_ok=True)
    src_adapters.mkdir(parents=True, exist_ok=True)

    (src_domain / "models.py").write_text('''"""RoboMesh 核心时空实体与硬互斥不变量校验 (只读核心)."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class RobotState(str, Enum):
    IDLE = "IDLE"
    ASSIGNED = "ASSIGNED"
    NAVIGATING = "NAVIGATING"
    OBSTACLE_WAITING = "OBSTACLE_WAITING"
    EMERGENCY_STOPPED = "EMERGENCY_STOPPED"

@dataclass(frozen=True)
class SpaceTimeVoxel:
    """时空体素切片: 2D 网格坐标 + 时间窗口."""
    x: int
    y: int
    t_start: int  # 毫秒时间戳
    t_end: int    # 毫秒时间戳
    robot_id: str

    def __post_init__(self) -> None:
        if self.t_start >= self.t_end:
            raise ValueError(f"时空体素时间窗口非法: t_start({self.t_start}) 必须小于 t_end({self.t_end})")

    def intersects(self, other: "SpaceTimeVoxel") -> bool:
        """检测两个时空体素是否存在空间与时间的硬互斥冲突."""
        if self.x != other.x or self.y != other.y:
            return False
        # 空间相同，检查时间窗口是否有重叠 (开放重叠判断)
        return max(self.t_start, other.t_start) < min(self.t_end, other.t_end)
''', encoding="utf-8")

    (src_ports / "dispatcher_port.py").write_text('''"""时空网格预约与路径规划端口 (依赖倒置只读接口)."""
from abc import ABC, abstractmethod
from typing import List
from src.domain.models import SpaceTimeVoxel

class SpaceTimeReservationPort(ABC):
    @abstractmethod
    def lock_trajectory(self, voxels: List[SpaceTimeVoxel]) -> bool:
        """尝试原子化预约整条轨迹的时空体素. 若有任何时空冲突则全部回滚并返回 False."""
        pass

    @abstractmethod
    def release_trajectory(self, robot_id: str) -> None:
        """释放指定机器人占用的全部未来时空体素."""
        pass
''', encoding="utf-8")

    (src_adapters / "spatial_reservation.py").write_text('''"""内存时空预约引擎适配器实现."""
from typing import Dict, List, Tuple
from src.domain.models import SpaceTimeVoxel
from src.ports.dispatcher_port import SpaceTimeReservationPort

class InMemorySpaceTimeReservationAdapter(SpaceTimeReservationPort):
    def __init__(self) -> None:
        # key: (x, y), value: list of booked SpaceTimeVoxel
        self._reservations: Dict[Tuple[int, int], List[SpaceTimeVoxel]] = {}

    def lock_trajectory(self, voxels: List[SpaceTimeVoxel]) -> bool:
        # TODO: [VibeCoding Slot] 实现基于区间重叠检测的高性能原子加锁
        for v in voxels:
            grid_key = (v.x, v.y)
            existing_list = self._reservations.get(grid_key, [])
            for existing in existing_list:
                if existing.intersects(v):
                    return False  # 存在硬时空冲突，拒绝加锁
        # 无冲突，执行锁定
        for v in voxels:
            grid_key = (v.x, v.y)
            if grid_key not in self._reservations:
                self._reservations[grid_key] = []
            self._reservations[grid_key].append(v)
        return True

    def release_trajectory(self, robot_id: str) -> None:
        # TODO: [VibeCoding Slot] 释放指定机器人所占用的全部网格
        for grid_key in list(self._reservations.keys()):
            self._reservations[grid_key] = [
                v for v in self._reservations[grid_key] if v.robot_id != robot_id
            ]
''', encoding="utf-8")

    # 生成防跑偏规则文件
    agent_rules_text = (REPO_ROOT / "templates" / "agent-rules-template.md").read_text(encoding="utf-8")
    (target_root / ".agent-rules.md").write_text(agent_rules_text, encoding="utf-8")

    roadmap_content = """# RoboMesh 落地交付路线图与穿刺演进规划

## 1. 核心技术风险聚焦
- **风险 1**：千台机器人在交叉路口时空体素高频并发锁定的 CAS 竞争开销与死锁。
- **风险 2**：工业 Wi-Fi 偶发漫游丢包时，机器人本地航位推算与云端时空表不同步。

## 2. Tracer Bullet (第 0 里程碑: 3 天闭环验证)
- **交付范围**：
  1. 搭建最小六边形骨架，构造 10x10 网格地图。
  2. 模拟两台机器人以对角相向路径行驶，检验时空预约引擎是否在相遇前 5 步识别时空重叠。
  3. 验证后到车辆自动原地等待 1 个时间窗口并顺畅通过。
- **DoD 验收标准**：
  - [ ] 零物理重合碰撞，两台机器人全部到达对角目标。
  - [ ] 自动化测试套件通过率 100%。

## 3. 纵向切片演进排期
| 阶段 | 交付切片 | 核心产物 | 验收门禁 |
|---|---|---|---|
| **Phase 1: 时空基座** | 内存时空体素表与互斥锁 | `STR-Core` 引擎与区间互斥检测 | 1000 组并发时空申请零冲突逃逸 |
| **Phase 2: 动态重排** | CBS 动态路径重排算法 | 局部窗口 A* 重路由求解器 | 50ms 内完成单机局部绕障重排 |
| **Phase 3: 协议总线** | VDA 5050 协议网关与心跳管线 | MQTT 20Hz 接入网关 | 30,000 QPS 遥测下 CPU 负载 < 50% |
| **Phase 4: 全场实测** | 仓储实地 1,200 台 AMR 联调 | 3D 态势大屏与现场物理防撞验收 | 连续 72 小时无人工干预安全运行 |
"""
    (ws_root / "04-execution" / "roadmap-and-first-step.md").write_text(roadmap_content, encoding="utf-8")

    skeleton_spec = {
        "skeleton_version": "1.0.0",
        "architecture_pattern": "Hexagonal / Ports-and-Adapters",
        "directories": ["src/domain", "src/ports", "src/adapters", "tests"],
        "immutable_paths": ["docs/architecture", "src/ports", "src/domain/models.py"],
        "slot_marker": "TODO: [VibeCoding Slot]",
        "rules_file": ".agent-rules.md"
    }
    (ws_root / "04-execution" / "walking-skeleton-spec.json").write_text(
        json.dumps(skeleton_spec, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    case_readme = """# RoboMesh: 工业级多机自主移动机器人(AMR)无人仓协同调度中枢

本项目是由 `architect_skill` 状态机驱动引擎自动生成的独立架构案例工程。

## 目录结构
- `docs/architecture/`：全生命周期架构资产（需求锚定、NFR矩阵、C4与状态机图谱、ADR、OpenAPI契约、交付演进）
- `docs/architecture/architecture_board.html`：自包含可交互架构画板（支持拖拽缩放、深浅色切换、SVG导出）
- `.agent-rules.md`：AI 编码防跑偏围栏与坏味道阻断守则
- `src/`：基于六边形架构生成的物理工程骨架
"""
    (target_root / "README.md").write_text(case_readme, encoding="utf-8")
    print(" -> 产出资产: 物理工程骨架、.agent-rules.md、README.md 与 roadmap-and-first-step.md 就绪")

    # 7. SCAFFOLDING -> FINALIZED
    fsm.advance()
    print(f"\n======================================================================")
    print(f" 🏁 案例推演完成！状态机已平滑推进至终态: {fsm.current_state.value}")
    print(f"======================================================================\n")

    report = fsm.get_status_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))
