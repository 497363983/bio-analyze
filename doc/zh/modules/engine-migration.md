# Engine 迁移指南

## 概述

项目现已在 `bio_analyze_core.engine` 中提供共享的 engine 运行时。
这是一次 breaking architectural change，目标是用统一可复用的模型替代各业务模块内部各自维护的 engine 工厂和注册表。

首批完成迁移的领域包括：

- `quant`
- `docking`

## API 变更

### 新增共享 API

- `bio_analyze_core.engine.EngineSpec`
- `bio_analyze_core.engine.EngineConfig`
- `bio_analyze_core.engine.EngineContext`
- `bio_analyze_core.engine.BaseEngine`
- `bio_analyze_core.engine.EngineRegistry`
- `bio_analyze_core.engine.EngineManager`
- `bio_analyze_core.engine.register_engine`

### Quant 侧变更

- `BaseQuantifier` 现在构建在 `BaseEngine` 之上
- 新增量化后端时，应实现 `execute()` 而不是 `_run()`
- `QuantifierRegistry` 现在是共享 `EngineRegistry` 的兼容门面
- quant 引擎通过 `bio_analyze.engine` entry points 暴露，名称格式如 `quant:salmon`

### Docking 侧变更

- `BaseDockingEngine` 现在构建在 `BaseEngine` 之上
- `DockingEngineFactory` 仍然保留，但内部已转发到共享 engine 注册表
- docking 引擎通过 `bio_analyze.engine` entry points 暴露，名称格式如 `docking:vina`

## 旧接口到新接口映射

| 旧概念 | 新概念 |
| --- | --- |
| quant 私有注册表 | `EngineRegistry` + `quant` 领域 |
| docking 工厂私有 `_engines` 映射 | `EngineRegistry` + `docking` 领域 |
| 模块内自定义实例化逻辑 | `EngineManager.create_engine()` |
| 新 quant 后端中的 `_run()` | `execute()` |

## 迁移步骤

### 面向 Quant 后端

1. 继承 `BaseQuantifier`
2. 将 `_run()` 重命名并迁移为 `execute()`
3. 保留 `TOOL_NAME`、`MODE` 和 `REQUIRED_BINARIES`
4. 使用 `@register_quantifier` 注册
5. 如果以后端包形式分发，再把该引擎加入 `bio_analyze.engine` entry-point group

### 面向 Docking 引擎

1. 保持继承 `BaseDockingEngine`
2. 新增或确认 `ENGINE_NAME`
3. 在引擎构造函数中接受 `**kwargs`，保证共享 context/config 注入兼容
4. 通过 `DockingEngineFactory.register_engine()` 或包级 entry points 注册

### 面向未来其他领域

1. 基于 `BaseEngine` 创建领域专用 engine 基类
2. 先定义稳定的领域名
3. 使用 `EngineSpec(domain="<domain>", name="<engine>")`
4. 通过 `EngineManager` 实现运行时选择与动态切换

## 兼容性说明

- `QuantManager` 仍然是 quant 的主编排 API
- `DockingEngineFactory` 仍然是 docking 的主兼容 API
- 现有 quant 和 docking CLI 选项无需修改即可接入新运行时
- 动态切换只影响后续新建 engine 实例，不会强制迁移已经运行中的任务

## 回滚方案

### 代码回滚

1. 回退 `bio_analyze_core.engine`
2. 恢复 quant 模块原有的本地注册表实现
3. 恢复 docking 模块原有的私有工厂注册表实现
4. 从包元数据中移除 `bio_analyze.engine` entry points

### 运行层回滚

- 已生成的 quant `counts.csv`、manifest 和 docking summary 等输出保持数据兼容
- 当前已迁移领域的断点状态文件预计不需要为回滚做结构性转换
- 如果插件发现引发打包问题，可先禁用共享 entry points，仅保留包内注册

## 常见迁移错误

- 引擎构造函数不接受 `context` 或 `config`
  - 处理：接受 `**kwargs` 并继续透传给基类
- entry point 名称不符合 `<domain>:<engine_name>` 规范
  - 处理：重命名为规定格式
- 新 quant 后端仍实现 `_run()`
  - 处理：改为实现 `execute()`
