# 项目工具实用程序

本目录包含用于项目管理和维护的各种实用工具脚本。

## 工具分类

### 🔧 系统管理工具
- `reset_superuser_password.py` - 超级用户密码重置工具
- `verify_success_check.py` - 系统状态验证工具

### 📁 项目管理工具
- `organize_project.py` - 项目文件结构整理工具
- `organize_project_enhanced.py` - 改进版项目整理工具

### 🔍 验证工具
- `verify_*.py` - 各类功能验证脚本

## 使用方式

```bash
# 重置超级用户密码
python tools/utilities/reset_superuser_password.py

# 整理项目文件结构
python tools/utilities/organize_project_enhanced.py

# 验证系统状态
python tools/utilities/verify_success_check.py
```

## 注意事项

- 这些工具主要用于开发和维护，而非日常业务功能
- 部分工具可能修改数据库或文件结构，使用前请备份
- 建议在测试环境中先验证工具功能
