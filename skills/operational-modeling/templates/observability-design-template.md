# 可观测性与度量体系设计规约 (Observability Design)

> 架构层次：Layer 3 - 物理与工程权衡 (How & Resilience)  
> 状态：APPROVED (签署入基线)  
> 目标系统：[系统全称]  
> 责任架构师：[架构师姓名/代号]

---

## 1. 分布式全链路追踪 (Distributed Tracing)

### 1.1 协议规范与上下文传递
- **标准规范**：全面遵循 W3C TraceContext 标准（`traceparent` 与 `tracestate`）。
- **传播介质**：
  - HTTP / gRPC：通过 HTTP Headers / gRPC Metadata 自动注入并透传；
  - 异步消息队列：作为消息属性 (Message Properties) 在消费者端提取并延续 Span 上下文。

### 1.2 采样与降噪策略
- **常规请求**：基于自适应动态采样率（日常 1% 采样，降低 APM 存储与网络开销）。
- **强制 100% 采样条件**：
  1. 发生任意 HTTP 5xx 或领域异常；
  2. 请求端到端延迟超过 P99 阈值（如 > 500ms）；
  3. 涉及核心出金、调频调度或关键安全操作的事务请求。

---

## 2. 监控指标大屏体系 (Metrics: RED & USE Framework)

### 2.1 业务与服务核心指标 (RED Model)
| 指标项 (Metric Name) | 指标类型 | 告警阈值 | 监控含义与排查指引 |
| :--- | :--- | :--- | :--- |
| **Rate (吞吐率)** | Counter | 突降 50% 或 突增 300% (持续 1min) | 上游流量突变、网络断开或遭受攻击 |
| **Errors (错误率)** | Gauge/Ratio | 错误率 > 0.5% (持续 2min) | 代码异常、外部依赖故障或不变量冲突 |
| **Duration (延迟)** | Histogram | P99 延迟 > 800ms (持续 2min) | 数据库慢查询、线程池满或算力资源争用 |

### 2.2 基础设施饱和度指标 (USE Model)
| 资源维度 | 监控指标 | 警戒阈值 | 应对预案 |
| :--- | :--- | :--- | :--- |
| **CPU 使用率** | `node_cpu_utilization` | > 80% (持续 3min) | 触发 HPA 水平扩容 Pods |
| **内存使用率** | `node_memory_used_ratio` | > 85% | 排查内存泄漏，准备分流切机 |
| **磁盘/I-O 饱和度** | `node_disk_io_time_seconds` | IOPS 达到物理配额 90% | 数据分流，排查未加索引的全表扫描 |

---

## 3. 结构化审计日志标准 (Structured Audit Logging)

### 3.1 统一 JSON 日志字段格式
所有系统输出日志必须为符合规范的单行 JSON，必填字段如下：
```json
{
  "timestamp": "2026-09-17T11:20:00.123Z",
  "trace_id": "00-4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "service": "dispatch-core-service",
  "level": "INFO",
  "caller": "src/domain/models.py:45",
  "event_type": "POWER_DISPATCH_COMMITTED",
  "tenant_id": "tenant-001",
  "payload_digest": "sha256:e3b0c44298fc1c149afbf4c8996fb924...",
  "message": "调频调度批次成功锁定，瞬时功率代数守恒校验通过"
}
```

### 3.2 敏感数据脱敏规范 (PII Masking)
- 严禁在日志中打印未加密的明文个人身份信息（身份证、银行卡号、手机号、密码、私钥）。
- 手机号格式统一采用 `138****0000` 脱敏，卡号保留前 6 后 4 位。
