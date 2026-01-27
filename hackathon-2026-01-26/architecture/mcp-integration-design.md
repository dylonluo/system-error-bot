# MCP Integration Design for System Support Bot

## 概述

使用Model Context Protocol (MCP)作为AI Orchestration Service的核心架构，实现模块化、可扩展的文档检索和AI响应系统。

---

## MCP服务器架构

### 1. Document Repository MCP Server
**职责：** 统一文档检索接口

**Tools:**
- `search_documents` - 搜索文档（支持S3、Confluence）
- `get_document` - 获取特定文档内容
- `list_documents_by_tag` - 按标签列出文档
- `check_document_access` - 检查用户文档访问权限

**Resources:**
- `confluence://pages/{page_id}` - Confluence页面
- `s3://bucket/path/to/doc` - S3文档

**Prompts:**
- `search_sop` - 搜索SOP文档的提示模板
- `search_prd` - 搜索PRD文档的提示模板

---

### 2. NetSuite MCP Server
**职责：** NetSuite相关查询和文档检索

**Tools:**
- `search_netsuite_docs` - 搜索NetSuite文档
- `get_error_documentation` - 获取错误码文档
- `search_custom_scripts` - 搜索自定义脚本（Post-MVP）
- `get_module_documentation` - 获取模块文档

**Resources:**
- `netsuite://error/{error_code}` - 错误文档
- `netsuite://module/{module_name}` - 模块文档
- `netsuite://script/{script_id}` - 自定义脚本（Post-MVP）

**Prompts:**
- `netsuite_error_help` - NetSuite错误帮助提示
- `netsuite_task_help` - NetSuite任务指导提示

---

### 3. TMS Integration MCP Server
**职责：** TMS集成相关查询

**Tools:**
- `search_tms_docs` - 搜索TMS文档
- `get_integration_error_docs` - 获取集成错误文档
- `list_integration_patterns` - 列出集成模式

**Resources:**
- `tms://integration/{integration_name}` - 集成文档
- `tms://error/{error_code}` - TMS错误文档

**Prompts:**
- `tms_integration_help` - TMS集成帮助提示
- `tms_error_help` - TMS错误帮助提示

---

### 4. Access Control MCP Server
**职责：** 用户权限和访问控制

**Tools:**
- `check_user_permissions` - 检查用户权限
- `filter_documents_by_access` - 按访问权限过滤文档
- `get_user_role` - 获取用户角色
- `validate_document_access` - 验证文档访问权限

**Resources:**
- `user://{user_id}/permissions` - 用户权限
- `role://{role_name}/access` - 角色访问规则

---

### 5. Analytics MCP Server (Post-MVP)
**职责：** 使用分析和报告

**Tools:**
- `log_query` - 记录查询
- `log_feedback` - 记录用户反馈
- `get_common_queries` - 获取常见查询
- `get_resolution_rate` - 获取解决率

**Resources:**
- `analytics://queries/recent` - 最近查询
- `analytics://metrics/resolution` - 解决率指标

---

## AI Orchestration Flow with MCP

### 查询处理流程

```
用户查询
    ↓
Chat Interface (Unit 1)
    ↓
AI Orchestration Service (Unit 4)
    ↓
┌─────────────────────────────────────┐
│  MCP Client (在AI Orchestration内)  │
│                                     │
│  1. 调用 Access Control MCP         │
│     → check_user_permissions        │
│                                     │
│  2. 并行调用文档检索 MCP             │
│     → Document Repository MCP       │
│     → NetSuite MCP                  │
│     → TMS Integration MCP           │
│                                     │
│  3. 过滤结果                         │
│     → filter_documents_by_access    │
│                                     │
│  4. 排序和聚合                       │
│     → 最多5个文档链接                │
│                                     │
│  5. 生成AI响应                       │
│     → 使用MCP Prompts               │
└─────────────────────────────────────┘
    ↓
返回响应给用户
```

---

## MCP配置示例

### mcp.json (MVP)

```json
{
  "mcpServers": {
    "document-repository": {
      "command": "node",
      "args": ["./mcp-servers/document-repository/index.js"],
      "env": {
        "AWS_REGION": "us-east-1",
        "S3_BUCKET": "company-docs",
        "CONFLUENCE_URL": "https://company.atlassian.net",
        "CONFLUENCE_API_TOKEN": "${CONFLUENCE_TOKEN}"
      }
    },
    "netsuite": {
      "command": "node",
      "args": ["./mcp-servers/netsuite/index.js"],
      "env": {
        "NETSUITE_ACCOUNT_ID": "${NETSUITE_ACCOUNT}",
        "NETSUITE_API_KEY": "${NETSUITE_KEY}"
      }
    },
    "tms-integration": {
      "command": "node",
      "args": ["./mcp-servers/tms-integration/index.js"],
      "env": {
        "TMS_API_URL": "${TMS_URL}",
        "TMS_API_KEY": "${TMS_KEY}"
      }
    },
    "access-control": {
      "command": "node",
      "args": ["./mcp-servers/access-control/index.js"],
      "env": {
        "AUTH_DB_URL": "${AUTH_DATABASE_URL}"
      }
    }
  }
}
```

---

## 技术栈

### MCP实现
- **MCP SDK:** `@modelcontextprotocol/sdk` (TypeScript/JavaScript)
- **传输层:** stdio (本地) 或 HTTP/SSE (远程)
- **AI模型:** OpenAI GPT-4 或 Azure OpenAI

### 后端服务
- **Runtime:** Node.js 18+
- **Framework:** Express.js (API Gateway)
- **MCP Client:** `@modelcontextprotocol/sdk/client`

### 数据存储
- **S3:** 文档存储
- **Confluence:** 知识库
- **PostgreSQL:** 用户权限、会话、分析数据

---

## MVP实现优先级

### Phase 1: 核心MCP服务器 (Week 1-2)
1. Document Repository MCP Server
   - S3集成
   - Confluence集成
   - 基础搜索功能

2. Access Control MCP Server
   - 用户权限检查
   - 文档访问过滤

### Phase 2: 领域特定MCP服务器 (Week 2-3)
3. NetSuite MCP Server
   - 错误文档检索
   - 模块文档检索

4. TMS Integration MCP Server
   - 集成文档检索
   - 错误文档检索

### Phase 3: AI Orchestration集成 (Week 3-4)
5. MCP Client集成到Unit 4
   - 并行调用多个MCP服务器
   - 结果聚合和排序
   - AI响应生成

---

## MCP的优势

### 1. 模块化
- 每个MCP服务器独立开发和部署
- 易于测试和维护
- 可以独立扩展

### 2. 标准化
- 统一的工具接口
- 标准的资源访问协议
- 一致的错误处理

### 3. 可扩展性
- 轻松添加新的数据源（ClickUp、SuiteAnswers）
- 支持Post-MVP功能扩展
- 可以替换或升级单个服务器

### 4. AI友好
- 内置Prompts支持
- 结构化的工具描述
- 易于AI理解和调用

### 5. 安全性
- 每个MCP服务器独立的权限控制
- 统一的访问控制检查
- 审计日志支持

---

## 与现有架构的映射

### Unit 2 (Access Control Service) → Access Control MCP Server
- 用户认证和授权
- 权限检查API → MCP Tools

### Unit 3 (Document Repository Service) → Document Repository MCP Server
- S3和Confluence集成
- 文档搜索API → MCP Tools

### Unit 4 (AI Orchestration Service) → MCP Client + AI Logic
- 集成所有MCP服务器
- 协调查询处理
- 生成AI响应

### Unit 5 (Communication Analytics) → Analytics MCP Server (Post-MVP)
- 查询日志
- 分析数据收集

---

## 开发路线图

### Week 1-2: MCP基础设施
- [ ] 设置MCP SDK
- [ ] 实现Document Repository MCP Server
- [ ] 实现Access Control MCP Server
- [ ] 单元测试

### Week 3-4: 领域MCP服务器
- [ ] 实现NetSuite MCP Server
- [ ] 实现TMS Integration MCP Server
- [ ] 集成测试

### Week 5-6: AI Orchestration集成
- [ ] MCP Client集成到Unit 4
- [ ] 并行查询实现
- [ ] 结果聚合和排序
- [ ] AI响应生成

### Week 7-8: 端到端测试
- [ ] 集成所有组件
- [ ] 性能优化
- [ ] 用户验收测试

---

## 性能考虑

### 并行查询
- 同时调用多个MCP服务器
- 使用Promise.all()并行处理
- 超时控制（5秒）

### 缓存策略
- 缓存常见查询结果
- 缓存文档元数据
- Redis缓存层

### 错误处理
- 单个MCP服务器失败不影响其他
- 优雅降级
- 重试机制

---

## 监控和日志

### MCP服务器监控
- 每个服务器的响应时间
- 错误率
- 调用频率

### 日志记录
- 所有MCP工具调用
- 用户查询和响应
- 权限检查结果

---

## 安全考虑

### API密钥管理
- 环境变量存储
- AWS Secrets Manager (生产环境)
- 定期轮换

### 访问控制
- 每个MCP调用验证用户权限
- 文档级别的访问控制
- 审计日志

### 数据保护
- 传输加密（TLS）
- 敏感数据脱敏
- PII检测和处理

---

## Post-MVP扩展

### 新增MCP服务器
- ClickUp MCP Server
- SuiteAnswers MCP Server
- Custom Scripts Analysis MCP Server

### 增强功能
- 语义搜索
- 高级错误模式分析
- 多轮对话上下文

### 集成
- Email escalation MCP Server
- Notification MCP Server
- Reporting MCP Server

---

## 总结

使用MCP架构可以：
1. ✅ 实现模块化、可维护的系统
2. ✅ 标准化AI与数据源的交互
3. ✅ 支持快速迭代和扩展
4. ✅ 提供清晰的服务边界
5. ✅ 简化AI Orchestration逻辑

MCP是这个项目的理想架构选择，特别适合需要集成多个数据源和服务的AI应用。
