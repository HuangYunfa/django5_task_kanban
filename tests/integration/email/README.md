# 邮件系统集成测试

本目录包含邮件系统相关的集成测试文件，主要测试：

## 测试内容

1. **邮件发送功能测试**
   - SMTP配置测试
   - 邮件后端测试
   - 邮件发送流程测试

2. **邮箱验证功能测试**
   - 验证邮件发送
   - 验证链接生成
   - 验证流程完整性

3. **邮件模板测试**
   - HTML邮件模板
   - 纯文本邮件模板
   - 邮件内容渲染

## 运行测试

```bash
# 运行所有邮件集成测试
pytest tests/integration/email/ -v

# 运行特定测试文件
python tests/integration/email/test_email_verification.py
```

## 配置要求

测试运行前需要确保邮件配置正确：
- Django settings中的EMAIL_BACKEND
- SMTP服务器配置（如使用真实SMTP）
- 测试用户和邮箱地址

## 注意事项

- 部分测试需要真实的SMTP服务器
- 测试过程中可能发送真实邮件，请使用测试邮箱
- console后端测试不会发送真实邮件
