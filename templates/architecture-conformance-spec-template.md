# 自动化架构合规扫描与防腐规约 (Architecture Conformance Specification)

> **治理视角**: 代码级架构防腐与 CI/CD 自动守卫 (Architecture as Tests & Conformance Gate)  
> **核心使命**: 将组件模型（CM）与运行模型（OM）的设计规约代码化为架构单元测试，嵌入持续集成流水线，实行“违规即熔断（Break the Build）”，杜绝因随意的 import 语句导致架构漂移与腐化。

---

## 1. 架构合规扫描策略概览 (Governance Policy Overview)

| 治理要素 | 规约配置与执行策略 |
| :--- | :--- |
| **CI/CD 触发时机** | **PR 第一道门禁 (Pull Request Gate)**：每次代码提交、创建 PR 或合并主干时全量自动触发 |
| **构建拦截效力** | **违规即熔断 (Break the Build)**：凡检测到严重分层违规或循环依赖，CI 立即中断并禁止代码合入 |
| **规则对齐模式** | **1:1 强映射**: 架构测试规则编号直接绑定组件模型（CM-XXX）与设计决策（ADR-XXX） |
| **存量治理原则** | **基线冻结 (Freezing Baseline)**: 存量违规锁定在历史基准库，增量代码“零容忍”全面拦截 |
| **技术实现工具** | **ArchUnit / AST 扫描插件 / Dependency-Check / ESLint Architecture Rule** |

---

## 2. 核心架构测试规则清单 (Architecture Test Rules & CM Mapping)

| 规则编号 | 规则名称与描述 | 关联组件/决策 | 扫描维度 | 拦截级别 | 预期校验行为 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ARCH-RULE-01` | **分层单向依赖校验** | `CM-001 ~ CM-006` | 分层与边界 | **致命 (Fatal - Break Build)** | Controller 严禁直接调用 Repository，Domain 层不得反向依赖基础设施 |
| `ARCH-RULE-02` | **无环依赖检查 (ADP)** | 全局包结构 | 分层与边界 | **致命 (Fatal - Break Build)** | 所有包与切片之间必须保持无环，禁止 A $\to$ B $\to$ C $\to$ A |
| `ARCH-RULE-03` | **跨限界上下文私有隔离** | `CM-002, CM-004` | 数据所有权 | **致命 (Fatal - Break Build)** | 严禁跨模块直接引用其他上下文内部私有实现类（必须通过公共 API 接口） |
| `ARCH-RULE-04` | **私有持久层访问阻断** | `CDM / CM-006` | 数据所有权 | **严重 (Critical)** | 组件严禁跨库跨表直接导入其他组件专属的 Entity 与 DAO |
| `ARCH-RULE-05` | **开源协议合规与漏洞** | 全局依赖包 | 供应链安全 | **严重 (Critical)** | 阻断引入强传染性 GPL/AGPL 协议依赖，阻断 CVSS $\ge$ 7.0 的高危 CVE |

---

## 3. 架构单元测试代码化实现 (Architecture as Tests - ArchUnit/AST)

```java
@AnalyzeClasses(packages = "com.enterprise.platform")
public class ArchitectureConformanceTest {

    // 1. 强制分层架构单向依赖 (CM 分层契约)
    @ArchTest
    public static final ArchRule layers_should_respect_architectural_hierarchy =
        layeredArchitecture()
            .consideringAllDependencies()
            .layer("Ingress").definedBy("..ingress..")
            .layer("Application").definedBy("..application..")
            .layer("Domain").definedBy("..domain..")
            .layer("Infrastructure").definedBy("..infrastructure..")
            
            .whereLayer("Ingress").mayNotBeAccessedByAnyLayer()
            .whereLayer("Domain").mayOnlyBeAccessedByLayers("Application", "Infrastructure")
            .whereLayer("Infrastructure").mayNotDependOnEachOther();

    // 2. 严禁循环依赖 (ADP 原则)
    @ArchTest
    public static final ArchRule packages_should_be_free_of_cycles =
        slices().matching("com.enterprise.platform.(*)..")
            .should().beFreeOfCycles();

    // 3. 跨限界上下文数据防腐 (禁止业务模块直连其他模块私有持久层)
    @ArchTest
    public static final ArchRule components_must_not_access_internal_persistence_directly =
        noClasses().that().resideInAPackage("..order..")
            .should().dependOnClassesThat().resideInAPackage("..clearing.infrastructure.dao..")
            .because("CM-004: 订单域必须通过清算域公共契约接口交互，严禁跨库直接访问持久层");
}
```

---

## 4. 架构特例豁免与时效台账 (Architecture Exceptions & Expiration Dates)

> 架构特例必须经首席架构师审批，且必须设定不可延期的失效时间戳（Expire Date），超期将自动恢复 CI 熔断：

| 豁免编号 | 违背规则 | 豁免模块与代码路径 | 豁免业务理由 | 批准人 (Approver) | 到期失效日 (Expire Date) | 清偿进展 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `EXCP-001` | `ARCH-RULE-03` | `com.platform.legacy.batch` | 历史老批处理直接读取底层报表，为保障双十一平稳运行特批 | 首席架构师 | **2026-11-30** | 重构中 (已解耦 50%) |
| `EXCP-002` | `ARCH-RULE-01` | `com.platform.hotfix.sync` | 线上突发故障应急热修复引入单向跨层依赖 | 质量总监 | **2026-10-15** | 待排期清偿 |

---

## 5. 基线冻结与架构健康度看板 (Baseline Freezing & Health Dashboard)

- **存量基线文件**: 位于 `.architecture/frozen_baseline.json`，锁定历史存量违规条目（如既有 24 处老代码违规）。
- **增量合规指标**: 增量代码违规熔断拦截率 = **100%**。
- **技术债务递减目标**: 随季度日常重构，基线违规条目每季度下调不低于 **30%**，直至清零。
- **本地开发者体验**: 集成 `pre-commit` Git 钩子，本地运行 `npm run arch-lint` / `mvn test-compile` 获得毫秒级即时反馈。
