---
name: operational-modeling
description: "Use when mapping logical components to physical deployment nodes, designing high-availability topologies, formulating failure resilience matrices, or defining observability architecture"
---

# Operational Modeling (运行模型与系统韧性)

## 概述

运行模型（OM, Operational Model）描述系统在物理、虚拟或云原生环境下的运行拓扑。它回答了“代码与数据在哪里跑、网络如何通、高可用如何保障、故障如何自愈”的关键工程问题。

在 AI / Agent 时代，大模型推理的高耗时（秒级甚至十秒级）与不可预测的失败率，使得 OM 必须重点关注**异步任务解耦、网络隔离域、高并发削峰、故障韧性矩阵与全链路可观测性**。

## 适用场景 (When to Use)

- 将组件模型（CM）中的逻辑组件映射到物理服务器、Kubernetes 集群、Serverless 容器或边缘节点；
- 规划数据库主从复制、Redis 哨兵/集群以及对象存储跨区域备份；
- 制定应对外部依赖超时、并发限流和网络抖动的系统韧性策略；
- 建立从前端链路追踪到 AI 推理网关消耗的端到端监控体系。

## 核心交付物与模板

1. **运行模型规格说明**：[operational-model-template.md](templates/operational-model-template.md)
2. **故障韧性与容错矩阵**：[resilience-matrix-template.md](templates/resilience-matrix-template.md)
3. **部署与可观测性设计**：[deployment-and-observability-template.md](templates/deployment-and-observability-template.md) 与 [observability-design-template.md](templates/observability-design-template.md)

## 执行步骤与检查清单

### 步骤一：物理部署拓扑与网络分区
- 划分公网接入区（DMZ）、业务逻辑私有区（Private VPC）与数据持久化安全区；
- 明确服务间通信协议（gRPC / HTTPS / 内网 TCP）；
- 标注负载均衡（ALB/NLB）、API 网关与反向代理。

### 步骤二：制定故障韧性矩阵 (Failure Resilience Matrix)
针对所有可能发生的硬件、软件与第三方依赖故障进行防御设计：
- **外部 AI API 故障**：设计请求超时时间（如 15s）、指数退避重试（带随机抖动 Jitter）、熔断器（Circuit Breaker）与优雅降级方案；
- **任务堆积与流量洪峰**：采用异步消息队列（Redis Streams / RabbitMQ / Kafka）进行流量削峰与反压（Backpressure）；
- **死信队列 (DLQ)**：多次重试失败的任务必须进入死信队列，并向管理员告警，防止卡死 Worker。

### 步骤三：可观测性与审计架构 (Observability)
- **Tracing**：分布式链路追踪（传递 `trace_id` 与 `span_id`），涵盖前端、网关、业务服务与三方 API 调用；
- **Metrics**：关键指标监控（请求 QPS、P95/P99 延迟、错误率、Worker 队列深度、GPU/算力成本）；
- **Logging**：结构化日志（JSON 格式），严禁打印用户敏感隐私（手机号、明文凭证、原始敏感图）。

## 门禁与红线 (Hard Gate & Red Flags)

<HARD-GATE>
任何涉及非即时完成（耗时 > 1.5s）的 AI 模型计算任务，必须在运行模型中采用异步解耦设计。严禁在 Web 请求主线程中同步阻塞等待大模型推理。
</HARD-GATE>

| 偷懒想法 (Red Flag) | 真实法则 (Reality) |
| :--- | :--- |
| “用户少的时候同步等待没关系，加个 loading 动画就行” | 同步连接会迅速耗尽 Web 服务器的工作线程池，一旦外部接口抖动，会导致全站雪崩。 |
| “外部云服务高可用，我们不需要考虑故障降级” | 云服务依然会遭遇网络分区或突发限流，不具备兜底提示与重试机制的系统无法交付生产。 |
