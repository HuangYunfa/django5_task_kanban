# 项目测试目录

本目录包含项目的各类测试，按功能和类型分类组织。

## 目录结构

- **api/**: API接口测试
  - 测试REST API的功能和性能
  - 验证API的认证、授权和数据处理

- **ui/**: 用户界面测试
  - 使用Playwright自动化测试前端界面
  - 验证页面渲染、交互和响应式设计

- **integration/**: 集成测试
  - 测试多个组件协同工作的功能
  - 验证系统的端到端工作流

- **unit/**: 单元测试
  - 测试独立组件和功能的正确性
  - 包括模型、表单、视图等测试

## 运行测试

全部测试:
```bash
pytest
```

特定类型测试:
```bash
pytest tests/ui/
pytest tests/api/
pytest tests/unit/
pytest tests/integration/
```

使用标记:
```bash
pytest -m ui
pytest -m "not slow"
pytest -m integration
```

## 测试标记

- `ui`: UI界面测试
- `api`: API接口测试
- `slow`: 耗时较长的测试
- `integration`: 集成测试

## 测试编写指南

1. 为新功能添加测试时，请放在相应的目录中
2. 使用适当的标记来分类测试
3. 遵循"AAA"(Arrange-Act-Assert)模式编写测试
4. 保持测试的独立性和可重复性
