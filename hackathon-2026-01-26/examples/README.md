# MCP Integration Examples

这个目录包含System Support Bot的MCP集成示例代码。

## 文件说明

### 1. `document-repository-mcp-server.js`
Document Repository MCP服务器，提供S3和Confluence文档检索功能。

**功能:**
- 搜索S3和Confluence中的文档
- 获取特定文档内容
- 基于用户角色过滤文档

**工具:**
- `search_documents` - 搜索文档
- `get_document` - 获取文档
- `filter_documents_by_access` - 过滤文档

### 2. `ai-orchestration-client.js`
AI Orchestration Service的MCP客户端，协调多个MCP服务器处理用户查询。

**功能:**
- 连接多个MCP服务器
- 并行搜索文档
- 生成AI响应
- 管理对话上下文

### 3. `package.json`
项目依赖配置

## 快速开始

### 安装依赖

```bash
cd hackathon-2026-01-26/examples
npm install
```

### 配置环境变量

创建 `.env` 文件:

```bash
# AWS配置
AWS_REGION=us-east-1
S3_BUCKET=company-docs

# Confluence配置
CONFLUENCE_URL=https://company.atlassian.net
CONFLUENCE_API_TOKEN=your_token_here

# OpenAI配置
OPENAI_API_KEY=your_openai_key_here
```

### 运行MCP服务器

#### 启动Document Repository服务器
```bash
npm run start:doc-repo
```

#### 测试MCP服务器
使用MCP Inspector工具测试:
```bash
npx @modelcontextprotocol/inspector node document-repository-mcp-server.js
```

### 运行AI Orchestration客户端

```bash
node ai-orchestration-client.js
```

## MCP服务器架构

```
┌─────────────────────────────────────────┐
│   AI Orchestration Service (Unit 4)    │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │      MCP Client                   │ │
│  │                                   │ │
│  │  - 并行调用多个MCP服务器          │ │
│  │  - 聚合和排序结果                 │ │
│  │  - 生成AI响应                     │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
              │
              │ MCP Protocol (stdio)
              │
    ┌─────────┴─────────┬─────────────┐
    │                   │             │
    ▼                   ▼             ▼
┌─────────┐      ┌──────────┐   ┌─────────┐
│Document │      │NetSuite  │   │Access   │
│Repository│      │MCP       │   │Control  │
│MCP Server│      │Server    │   │MCP      │
└─────────┘      └──────────┘   └─────────┘
    │                   │             │
    ▼                   ▼             ▼
┌─────────┐      ┌──────────┐   ┌─────────┐
│S3 +     │      │NetSuite  │   │Auth DB  │
│Confluence│      │API       │   │         │
└─────────┘      └──────────┘   └─────────┘
```

## API示例

### 搜索文档

```javascript
const result = await orchestrator.processQuery(
  'NetSuite报错: INVALID_KEY_OR_REF',
  'user123',
  'End User'
);

console.log(result);
// {
//   success: true,
//   response: "根据您的错误信息，我找到了以下相关文档...",
//   documents: [
//     {
//       id: "s3://company-docs/sops/netsuite-errors.pdf",
//       title: "NetSuite常见错误处理",
//       url: "https://...",
//       relevance: 0.95
//     },
//     ...
//   ],
//   intent: "error_troubleshooting"
// }
```

### 带对话历史的查询

```javascript
const conversationHistory = [
  { role: 'user', content: '什么是TMS集成？' },
  { role: 'assistant', content: 'TMS集成是运输管理系统与NetSuite的集成...' }
];

const result = await orchestrator.processQuery(
  '如何配置TMS集成？',
  'user789',
  'Administrator',
  conversationHistory
);
```

## MCP工具调用示例

### 直接调用MCP工具

```javascript
// 搜索文档
const docs = await orchestrator.callMCPTool(
  'document-repository',
  'search_documents',
  {
    query: 'NetSuite销售订单',
    sources: ['s3', 'confluence'],
    limit: 5,
    userRole: 'End User'
  }
);

// 获取文档
const doc = await orchestrator.callMCPTool(
  'document-repository',
  'get_document',
  {
    documentId: 's3://company-docs/sops/sales-order.pdf',
    userRole: 'End User'
  }
);
```

## 开发其他MCP服务器

### NetSuite MCP Server

```javascript
// netsuite-mcp-server.js
import { Server } from '@modelcontextprotocol/sdk/server/index.js';

class NetSuiteMCPServer {
  setupHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'search_netsuite_docs',
          description: '搜索NetSuite文档',
          inputSchema: {
            type: 'object',
            properties: {
              query: { type: 'string' },
              type: { 
                type: 'string', 
                enum: ['error', 'task', 'module'] 
              },
              userRole: { type: 'string' }
            },
            required: ['query', 'type']
          }
        },
        {
          name: 'get_error_documentation',
          description: '获取错误码文档',
          inputSchema: {
            type: 'object',
            properties: {
              errorCode: { type: 'string' },
              userRole: { type: 'string' }
            },
            required: ['errorCode']
          }
        }
      ]
    }));
  }
}
```

### Access Control MCP Server

```javascript
// access-control-mcp-server.js
class AccessControlMCPServer {
  setupHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'check_user_permissions',
          description: '检查用户权限',
          inputSchema: {
            type: 'object',
            properties: {
              userId: { type: 'string' },
              resource: { type: 'string' }
            },
            required: ['userId', 'resource']
          }
        },
        {
          name: 'get_user_role',
          description: '获取用户角色',
          inputSchema: {
            type: 'object',
            properties: {
              userId: { type: 'string' }
            },
            required: ['userId']
          }
        }
      ]
    }));
  }
}
```

## 测试

### 单元测试MCP服务器

```bash
# 使用MCP Inspector
npx @modelcontextprotocol/inspector node document-repository-mcp-server.js
```

在Inspector中测试工具调用:
1. 选择 `search_documents` 工具
2. 输入参数: `{ "query": "NetSuite", "userRole": "End User" }`
3. 查看返回结果

### 集成测试

```bash
node ai-orchestration-client.js
```

## 性能优化

### 并行查询
AI Orchestration同时调用多个MCP服务器，减少延迟:

```javascript
const searchPromises = [
  this.callMCPTool('document-repository', 'search_documents', {...}),
  this.callMCPTool('netsuite', 'search_netsuite_docs', {...}),
  this.callMCPTool('tms-integration', 'search_tms_docs', {...})
];

const results = await Promise.allSettled(searchPromises);
```

### 缓存
实现结果缓存减少重复查询:

```javascript
const cacheKey = `${query}-${userRole}`;
if (this.cache.has(cacheKey)) {
  return this.cache.get(cacheKey);
}
```

### 超时控制
设置超时避免长时间等待:

```javascript
const timeout = 5000; // 5秒
const result = await Promise.race([
  this.callMCPTool(...),
  new Promise((_, reject) => 
    setTimeout(() => reject(new Error('Timeout')), timeout)
  )
]);
```

## 部署

### Docker部署

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --production

COPY *.js ./

CMD ["node", "ai-orchestration-client.js"]
```

### Kubernetes部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-orchestration
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: ai-orchestration
        image: system-support-bot/ai-orchestration:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
```

## 监控

### 日志记录

```javascript
console.log({
  timestamp: new Date().toISOString(),
  userId,
  query,
  intent,
  documentsFound: documents.length,
  responseTime: Date.now() - startTime
});
```

### 指标收集

```javascript
// Prometheus metrics
queryCounter.inc({ intent, userRole });
responseTimeHistogram.observe(responseTime);
documentCountGauge.set(documents.length);
```

## 故障排查

### MCP服务器无法连接
```bash
# 检查服务器是否运行
ps aux | grep mcp-server

# 查看日志
tail -f /var/log/mcp-server.log
```

### 文档搜索返回空结果
- 检查S3/Confluence凭证
- 验证用户权限
- 查看搜索关键词

### AI响应质量差
- 调整temperature参数
- 优化系统提示
- 增加文档上下文

## 下一步

1. 实现其他MCP服务器（NetSuite、TMS、Access Control）
2. 添加缓存层（Redis）
3. 实现更复杂的意图检测
4. 添加语义搜索
5. 实现对话上下文管理
6. 添加监控和日志
7. 编写单元测试和集成测试

## 参考资料

- [MCP官方文档](https://modelcontextprotocol.io)
- [MCP SDK](https://github.com/modelcontextprotocol/sdk)
- [OpenAI API](https://platform.openai.com/docs)
- [AWS SDK for JavaScript](https://docs.aws.amazon.com/sdk-for-javascript/)
- [Confluence REST API](https://developer.atlassian.com/cloud/confluence/rest/v2/)
