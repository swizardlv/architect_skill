# 边界接口与交互契约全景规约 (Interface Contracts Overview)

> 架构层次：Layer 3 / 边界契约 (Boundary Contracts)  
> 状态：APPROVED / IN_REVIEW  
> 目标系统：[系统全称]  
> 责任架构师：[架构师姓名/代号]

---

## 1. 契约设计原则与交互规范 (Contract Principles)

### 1.1 核心设计规范
- **协议选型**：外部北向流量统一使用 RESTful / HTTPS (OpenAPI 3.1 规约)；内部南向服务间高性能通信采用 gRPC / Protobuf 强类型传输。
- **不可变语义与向后兼容**：严禁在未升级主版本号的情况下执行破坏性修改（例如重命名字段、删除字段或修改字段数据类型）。
- **零宽容模式校验**：接入层通过严格的 JSON Schema / Protobuf 反序列化校验器拦截非法畸形报文，拒绝隐式类型转换。

---

## 2. 接口端点与语义清单 (Endpoint Registry)

### 2.1 北向核心业务 API
| 路径 / 接口方法 | HTTP Method / RPC | 接口描述 | 幂等性保障 | 核心返回状态码 |
| :--- | :--- | :--- | :--- | :--- |
| `/api/v1/session` | `POST` | 创建核心会话 / 接入实体 | 是 (基于 `Idempotency-Key`) | 201 Created / 409 Conflict |
| `/api/v1/session/{id}` | `GET` | 查询当前实时聚合根状态 | 是 | 200 OK / 404 Not Found |
| `/api/v1/session/{id}/event` | `POST` | 上报业务度量或流转事件 | 否 (事件时序校验) | 202 Accepted / 400 Bad Request |
| `/api/v1/session/{id}/terminate` | `POST` | 正常归档或终止会话 | 是 | 200 OK / 412 Precondition Failed |

### 2.2 伴生文件索引
- 机器可解析的完整 API 规约参见：[`openapi.yaml`](openapi.yaml)。
- 该 OpenAPI 规范已在 CI 流程中配置自动化 lint 检查（如 Spectral / Redocly），确保字段描述与错误码定义完备。

---

## 3. 跨切面契约与防护机制 (Cross-Cutting Contracts)

### 3.1 统一请求头与上下文透传
| 请求头 (Header Name) | 必填 | 语义说明 | 示例 |
| :--- | :--- | :--- | :--- |
| `X-Request-ID` | 是 | 客户端生成的请求追踪唯一标识 | `c7a3b4c1-8d2e-4b6a-9f1e-8e5d2b1a3c4f` |
| `X-Idempotency-Key` | 针对写操作 | 幂等唯一指纹，服务端缓存 24 小时 | `idemp_txn_20260917_00129` |
| `traceparent` | 建议 | W3C 分布式追踪上下文 | `00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01` |
| `Authorization` | 是 | Bearer 格式的 JWT / 签名 Token | `Bearer eyJhbGciOi...` |

### 3.2 全局统一错误码与响应结构
所有非 2xx 异常响应均统一采用 RFC 7807 (Problem Details for HTTP APIs) 标准格式输出：

```json
{
  "type": "https://api.example.com/errors/INVARIANT_VIOLATION",
  "title": "Domain Invariant Violation",
  "status": 409,
  "detail": "当前账户处于冻结状态，拒绝扣减额度操作",
  "instance": "/api/v1/accounts/acc_10029/debit",
  "code": "ERR_ACCOUNT_FROZEN",
  "timestamp": "2026-09-17T11:00:00Z"
}
```
