---
name: boundary-contracts
description: "Use when specifying API contracts, defining asynchronous event schemas, generating OpenAPI/AsyncAPI specifications, or establishing anti-corruption layers"
---

# Boundary Contracts (系统边界与接口契约)

## 概述

边界契约是组件间、服务间以及与外部第三方交互的法定协议。严格的接口与数据契约能够有效解耦上下游开发，防止因语义歧义或数据漂移导致的集成灾难。

在 AI / Agent 系统中，除了传统的同步 RESTful 接口外，必须重点规范**异步任务轮询/推送契约、模型推理参数与结果 Payload 格式、以及错误与重试码体系**。

## 适用场景 (When to Use)

- 制定前后端分离的 API 协议（客户端小程序与后端 BFF）；
- 定义后台管理系统专用的管理与审计接口；
- 规范异步消息队列的事件载荷（Event Schema）；
- 为第三方 AI 模型接口编写防腐层（ACL）适配契约。

## 核心交付物与模板

- **接口契约全景规格**：[interface-contracts-overview-template.md](templates/interface-contracts-overview-template.md)

## 执行步骤与检查清单

### 步骤一：RESTful / HTTP 同步接口契约化
- 采用标准 HTTP 语义（GET / POST / PUT / DELETE）；
- 严格遵循统一的响应结构体：
  ```json
  {
    "code": 0,
    "message": "success",
    "data": {},
    "timestamp": 1726632000,
    "request_id": "req-uuid-12345"
  }
  ```
- 明确入参校验规则（非空、长度范围、数值边界、图片格式与尺寸限制）；
- 声明所有业务错误码（如 `10001: 余额不足`, `20002: 图片涉嫌违规`, `30005: 模型排队超时`）。

### 步骤二：异步任务轮询与事件契约 (Async Schema)
- 针对长耗时处理任务（如照片去路人），必须提供：
  1. `POST /api/v1/tasks` -> 立即返回 `202 Accepted`，携带 `task_id`；
  2. `GET /api/v1/tasks/{task_id}` -> 返回任务当前状态（`PENDING`, `PROCESSING`, `SUCCESS`, `FAILED`）与结果 URL。
- 定义消息队列中的 Event Payload，包含 `event_id`, `task_id`, `attempt_count`, `created_at` 等关键追踪元数据。

### 步骤三：幂等性与重试安全契约
- 对所有可能被网络重试触发的写请求，必须支持 `Idempotency-Key` 请求头；
- 明确声明当遇到相同 key 时的处理语义（直接返回上一次缓存结果或返回 409 Conflict）。

## 门禁与红线 (Hard Gate & Red Flags)

<HARD-GATE>
所有面向客户端和面向异步队列的接口，必须给出完整的 Request Payload 与 Response Payload JSON 样例。严禁使用“入参请见实体类”等模糊说明。
</HARD-GATE>

| 偷懒想法 (Red Flag) | 真实法则 (Reality) |
| :--- | :--- |
| “接口字段差不多就行，联调的时候再定” | 契约模糊是联调阶段撕扯与返工的根源，架构设计必须确立字段类型、必填项与枚举值。 |
| “不需要传递 request_id，报错再看服务器时间” | 分布式环境与异步任务链中缺少 trace_id/request_id 将导致生产故障排查如同大海捞针。 |
