/**
 * AI Orchestration Service - MCP Client
 * 协调多个MCP服务器处理用户查询
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import OpenAI from 'openai';

class AIOrchestrationService {
  constructor() {
    this.mcpClients = {};
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
  }

  // 初始化MCP客户端
  async initialize() {
    // 连接Document Repository MCP Server
    await this.connectMCPServer('document-repository', {
      command: 'node',
      args: ['./document-repository-mcp-server.js'],
    });

    // 连接Access Control MCP Server
    await this.connectMCPServer('access-control', {
      command: 'node',
      args: ['./access-control-mcp-server.js'],
    });

    // 连接NetSuite MCP Server
    await this.connectMCPServer('netsuite', {
      command: 'node',
      args: ['./netsuite-mcp-server.js'],
    });

    console.log('All MCP servers connected');
  }

  // 连接单个MCP服务器
  async connectMCPServer(name, config) {
    const client = new Client(
      {
        name: `ai-orchestration-${name}-client`,
        version: '1.0.0',
      },
      {
        capabilities: {},
      }
    );

    const transport = new StdioClientTransport({
      command: config.command,
      args: config.args,
      env: config.env,
    });

    await client.connect(transport);
    this.mcpClients[name] = client;
    console.log(`Connected to ${name} MCP server`);
  }

  // 处理用户查询
  async processQuery(query, userId, userRole, conversationHistory = []) {
    try {
      console.log(`Processing query: "${query}" for user role: ${userRole}`);

      // Step 1: 检测查询意图
      const intent = await this.detectIntent(query);
      console.log(`Detected intent: ${intent}`);

      // Step 2: 并行搜索文档
      const documents = await this.searchDocuments(query, userRole, intent);
      console.log(`Found ${documents.length} documents`);

      // Step 3: 生成AI响应
      const response = await this.generateResponse(
        query,
        documents,
        intent,
        conversationHistory
      );

      return {
        success: true,
        response,
        documents,
        intent,
      };
    } catch (error) {
      console.error('Error processing query:', error);
      return {
        success: false,
        error: error.message,
        suggestEscalation: true,
      };
    }
  }

  // 检测查询意图
  async detectIntent(query) {
    const lowerQuery = query.toLowerCase();

    // 简单的意图检测（实际应使用AI）
    if (lowerQuery.includes('error') || lowerQuery.includes('错误')) {
      return 'error_troubleshooting';
    } else if (
      lowerQuery.includes('how to') ||
      lowerQuery.includes('如何') ||
      lowerQuery.includes('怎么')
    ) {
      return 'task_guidance';
    } else {
      return 'general_question';
    }
  }

  // 搜索文档（并行调用多个MCP服务器）
  async searchDocuments(query, userRole, intent) {
    const searchPromises = [];

    // 调用Document Repository MCP
    searchPromises.push(
      this.callMCPTool('document-repository', 'search_documents', {
        query,
        sources: ['s3', 'confluence'],
        limit: 5,
        userRole,
      })
    );

    // 根据意图调用特定MCP服务器
    if (intent === 'error_troubleshooting') {
      // 调用NetSuite MCP搜索错误文档
      searchPromises.push(
        this.callMCPTool('netsuite', 'search_netsuite_docs', {
          query,
          type: 'error',
          userRole,
        })
      );
    } else if (intent === 'task_guidance') {
      // 调用NetSuite MCP搜索任务文档
      searchPromises.push(
        this.callMCPTool('netsuite', 'search_netsuite_docs', {
          query,
          type: 'task',
          userRole,
        })
      );
    }

    // 等待所有搜索完成
    const results = await Promise.allSettled(searchPromises);

    // 合并结果
    const allDocuments = [];
    results.forEach((result) => {
      if (result.status === 'fulfilled' && result.value.documents) {
        allDocuments.push(...result.value.documents);
      }
    });

    // 排序和去重
    const uniqueDocs = this.deduplicateDocuments(allDocuments);
    const sortedDocs = this.sortByRelevance(uniqueDocs);

    // 限制为最多5个文档
    return sortedDocs.slice(0, 5);
  }

  // 调用MCP工具
  async callMCPTool(serverName, toolName, args) {
    const client = this.mcpClients[serverName];
    if (!client) {
      throw new Error(`MCP server ${serverName} not connected`);
    }

    try {
      const result = await client.callTool({
        name: toolName,
        arguments: args,
      });

      // 解析结果
      if (result.content && result.content[0]) {
        const content = result.content[0].text;
        return JSON.parse(content);
      }

      return {};
    } catch (error) {
      console.error(`Error calling ${serverName}.${toolName}:`, error);
      return {};
    }
  }

  // 生成AI响应
  async generateResponse(query, documents, intent, conversationHistory) {
    // 构建系统提示
    const systemPrompt = this.buildSystemPrompt(intent);

    // 构建文档上下文
    const documentContext = this.buildDocumentContext(documents);

    // 构建对话历史
    const messages = [
      { role: 'system', content: systemPrompt },
      ...conversationHistory.slice(-5), // 最近5条消息
      {
        role: 'user',
        content: `用户查询: ${query}\n\n可用文档:\n${documentContext}\n\n请提供简洁的回答，并引用相关文档链接（最多5个）。`,
      },
    ];

    // 调用OpenAI
    const completion = await this.openai.chat.completions.create({
      model: 'gpt-4',
      messages,
      temperature: 0.3,
      max_tokens: 500,
    });

    return completion.choices[0].message.content;
  }

  // 构建系统提示
  buildSystemPrompt(intent) {
    const basePrompt = `你是一个专业的NetSuite和TMS系统支持助手。你的职责是帮助用户找到相关的文档链接来解决问题。

重要规则:
1. 只提供文档链接，不要尝试直接解决技术问题
2. 回答要简洁明了
3. 最多提供5个文档链接
4. 解释每个链接的相关性
5. 如果没有找到相关文档，建议用户联系人工支持`;

    const intentPrompts = {
      error_troubleshooting: '\n\n当前场景: 用户遇到错误，需要故障排除文档。',
      task_guidance: '\n\n当前场景: 用户需要任务指导文档。',
      general_question: '\n\n当前场景: 用户有一般性问题。',
    };

    return basePrompt + (intentPrompts[intent] || '');
  }

  // 构建文档上下文
  buildDocumentContext(documents) {
    if (documents.length === 0) {
      return '没有找到相关文档。';
    }

    return documents
      .map((doc, index) => {
        return `${index + 1}. [${doc.title}](${doc.url})
   来源: ${doc.source}
   类型: ${doc.type}
   相关性: ${(doc.relevance * 100).toFixed(0)}%`;
      })
      .join('\n\n');
  }

  // 去重文档
  deduplicateDocuments(documents) {
    const seen = new Set();
    return documents.filter((doc) => {
      if (seen.has(doc.id)) {
        return false;
      }
      seen.add(doc.id);
      return true;
    });
  }

  // 按相关性排序
  sortByRelevance(documents) {
    return documents.sort((a, b) => b.relevance - a.relevance);
  }

  // 关闭所有MCP连接
  async close() {
    for (const [name, client] of Object.entries(this.mcpClients)) {
      await client.close();
      console.log(`Closed ${name} MCP client`);
    }
  }
}

// 使用示例
async function main() {
  const orchestrator = new AIOrchestrationService();

  try {
    // 初始化
    await orchestrator.initialize();

    // 示例查询1: 错误排查
    console.log('\n=== Example 1: Error Troubleshooting ===');
    const result1 = await orchestrator.processQuery(
      'NetSuite报错: INVALID_KEY_OR_REF',
      'user123',
      'End User'
    );
    console.log('Response:', result1.response);
    console.log('Documents:', result1.documents.length);

    // 示例查询2: 任务指导
    console.log('\n=== Example 2: Task Guidance ===');
    const result2 = await orchestrator.processQuery(
      '如何在NetSuite中创建销售订单？',
      'user456',
      'End User'
    );
    console.log('Response:', result2.response);
    console.log('Documents:', result2.documents.length);

    // 示例查询3: 带对话历史
    console.log('\n=== Example 3: With Conversation History ===');
    const conversationHistory = [
      { role: 'user', content: '什么是TMS集成？' },
      { role: 'assistant', content: 'TMS集成是...' },
    ];
    const result3 = await orchestrator.processQuery(
      '如何配置TMS集成？',
      'user789',
      'Administrator',
      conversationHistory
    );
    console.log('Response:', result3.response);
    console.log('Documents:', result3.documents.length);
  } finally {
    // 清理
    await orchestrator.close();
  }
}

// 如果直接运行此文件
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export default AIOrchestrationService;
