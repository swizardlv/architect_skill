---
name: conceptual-data-modeling
description: "Use when defining business entities and relationships, establishing data architecture boundaries, generating DDL schemas, or partitioning polyglot persistence stores"
---

# Conceptual Data Modeling (概念数据模型与多模存储)

## 概述

概念数据模型（CDM, Conceptual Data Model）确立了系统的核心业务实体、实体间关系以及数据生命周期边界。

在现代 AI 应用中，单一的关系型数据库往往无法承担全部形态的数据。架构师必须合理规划**结构化业务表、高并发热缓存、二进制对象存储以及非结构化向量/日志索引**的多模存储拓扑。

## 适用场景 (When to Use)

- 确立系统的核心实体模型（如用户、照片任务、算法配额、审计记录）；
- 绘制实体关系图（Mermaid erDiagram）；
- 编写可执行的 DDL 建表脚本骨架与索引策略；
- 规划海量非结构化数据（原图、去路人掩码、修复结果图）的存储与清理策略。

## 核心交付物与模板

1. **概念数据模型规格**：[conceptual-data-model-template.md](templates/conceptual-data-model-template.md)
2. **多模存储与数据架构**：[data-architecture-template.md](templates/data-architecture-template.md)

## 执行步骤与检查清单

### 步骤一：核心实体识别与关系抽取
- 提取关键实体，定义核心属性与业务语义；
- 使用 Mermaid `erDiagram` 表达一对一、一对多或多对多关系；
- 标明主键（PK）与逻辑外键（FK）。

### 步骤二：多模持久化划分 (Polyglot Persistence)
- **关系型数据库 (PostgreSQL / MySQL)**：存储强一致性核心实体（用户资产、订单、任务状态、审计台账）；
- **高速内存存储 (Redis)**：存储高频访问数据、分布式锁、任务队列与限流计数器；
- **对象存储 (COS / OSS / S3)**：存储大尺寸图片原图、掩码图与处理产出物；
- **分级过期与冷热存储**：定义生命周期规则（如临时生成图片保留 7 天自动转冷存或销毁）。

### 步骤三：DDL 模式骨架生成
- 编写清晰的 SQL DDL 语句；
- 所有表必须具备标准审计字段（`id`, `created_at`, `updated_at`, `is_deleted`）；
- 针对高频查询条件（如 `user_id` + `status`）建立复合索引；
- 显式声明字符集（UTF-8）与字段非空约束。

## 门禁与红线 (Hard Gate & Red Flags)

<HARD-GATE>
严禁将大尺寸二进制文件（如 Base64 编码的图片或音频）直接写入关系型数据库的 Text/Blob 字段中。所有多媒体数据必须走对象存储并通过 URL 关联。
数据模型必须包含清晰的物理 DDL 骨架和索引定义，严禁仅停留于口头概念说明。
</HARD-GATE>

| 偷懒想法 (Red Flag) | 真实法则 (Reality) |
| :--- | :--- |
| “图片数据直接 Base64 存数据库，省去了搭建对象存储的麻烦” | 二进制数据膨胀会严重拖垮数据库 IOPS 和备份速度，属于典型的架构反模式。 |
| “自增 ID 足够用，不需要关注分布式唯一标识” | 任务类表与外部交互频繁，暴露自增 ID 存在安全遍历风险，任务类推荐使用 UUIDv7 或雪花算法 ID。 |
