#!/usr/bin/env node

/**
 * Document Repository MCP Server
 * 提供S3和Confluence文档检索功能
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

// AWS S3 和 Confluence 客户端（示例）
import { S3Client, ListObjectsV2Command, GetObjectCommand } from '@aws-sdk/client-s3';
import axios from 'axios';

class DocumentRepositoryServer {
  constructor() {
    this.server = new Server(
      {
        name: 'document-repository',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
          resources: {},
          prompts: {},
        },
      }
    );

    // 初始化S3客户端
    this.s3Client = new S3Client({
      region: process.env.AWS_REGION || 'us-east-1',
    });

    // Confluence配置
    this.confluenceUrl = process.env.CONFLUENCE_URL;
    this.confluenceToken = process.env.CONFLUENCE_API_TOKEN;

    this.setupHandlers();
  }

  setupHandlers() {
    // 列出可用工具
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'search_documents',
          description: '搜索S3和Confluence中的文档',
          inputSchema: {
            type: 'object',
            properties: {
              query: {
                type: 'string',
                description: '搜索关键词',
              },
              sources: {
                type: 'array',
                items: { type: 'string', enum: ['s3', 'confluence'] },
                description: '搜索的数据源',
                default: ['s3', 'confluence'],
              },
              limit: {
                type: 'number',
                description: '返回结果数量限制',
                default: 5,
              },
              userRole: {
                type: 'string',
                description: '用户角色（用于权限过滤）',
              },
            },
            required: ['query'],
          },
        },
        {
          name: 'get_document',
          description: '获取特定文档内容',
          inputSchema: {
            type: 'object',
            properties: {
              documentId: {
                type: 'string',
                description: '文档ID（s3://bucket/key 或 confluence://pageId）',
              },
              userRole: {
                type: 'string',
                description: '用户角色（用于权限检查）',
              },
            },
            required: ['documentId'],
          },
        },
        {
          name: 'filter_documents_by_access',
          description: '根据用户权限过滤文档列表',
          inputSchema: {
            type: 'object',
            properties: {
              documents: {
                type: 'array',
                items: { type: 'object' },
                description: '文档列表',
              },
              userRole: {
                type: 'string',
                description: '用户角色',
              },
            },
            required: ['documents', 'userRole'],
          },
        },
      ],
    }));

    // 处理工具调用
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'search_documents':
          return await this.searchDocuments(args);
        case 'get_document':
          return await this.getDocument(args);
        case 'filter_documents_by_access':
          return await this.filterDocumentsByAccess(args);
        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });

    // 列出资源
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => ({
      resources: [
        {
          uri: 's3://company-docs/sops/',
          name: 'SOPs in S3',
          mimeType: 'application/x-directory',
        },
        {
          uri: 'confluence://space/DOCS',
          name: 'Documentation Space',
          mimeType: 'application/x-directory',
        },
      ],
    }));

    // 读取资源
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;
      
      if (uri.startsWith('s3://')) {
        return await this.readS3Resource(uri);
      } else if (uri.startsWith('confluence://')) {
        return await this.readConfluenceResource(uri);
      }
      
      throw new Error(`Unsupported resource URI: ${uri}`);
    });
  }

  // 搜索文档
  async searchDocuments(args) {
    const { query, sources = ['s3', 'confluence'], limit = 5, userRole } = args;
    const results = [];

    try {
      // 并行搜索S3和Confluence
      const searchPromises = [];

      if (sources.includes('s3')) {
        searchPromises.push(this.searchS3(query, limit));
      }

      if (sources.includes('confluence')) {
        searchPromises.push(this.searchConfluence(query, limit));
      }

      const searchResults = await Promise.all(searchPromises);
      
      // 合并结果
      searchResults.forEach(result => results.push(...result));

      // 按相关性排序（简化版）
      results.sort((a, b) => b.relevance - a.relevance);

      // 限制结果数量
      const limitedResults = results.slice(0, limit);

      // 过滤权限（简化版 - 实际应调用Access Control MCP）
      const filteredResults = this.simpleAccessFilter(limitedResults, userRole);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              query,
              totalResults: filteredResults.length,
              documents: filteredResults,
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ error: error.message }),
          },
        ],
        isError: true,
      };
    }
  }

  // 搜索S3
  async searchS3(query, limit) {
    const bucket = process.env.S3_BUCKET || 'company-docs';
    const results = [];

    try {
      const command = new ListObjectsV2Command({
        Bucket: bucket,
        Prefix: 'sops/', // 搜索SOPs目录
        MaxKeys: 50,
      });

      const response = await this.s3Client.send(command);

      if (response.Contents) {
        for (const item of response.Contents) {
          // 简单的关键词匹配
          if (item.Key.toLowerCase().includes(query.toLowerCase())) {
            results.push({
              id: `s3://${bucket}/${item.Key}`,
              title: item.Key.split('/').pop(),
              source: 's3',
              url: `https://${bucket}.s3.amazonaws.com/${item.Key}`,
              relevance: this.calculateRelevance(item.Key, query),
              lastModified: item.LastModified,
              type: 'SOP',
            });
          }
        }
      }
    } catch (error) {
      console.error('S3 search error:', error);
    }

    return results.slice(0, limit);
  }

  // 搜索Confluence
  async searchConfluence(query, limit) {
    const results = [];

    try {
      const response = await axios.get(
        `${this.confluenceUrl}/wiki/rest/api/content/search`,
        {
          params: {
            cql: `text ~ "${query}" AND type=page`,
            limit,
          },
          headers: {
            Authorization: `Bearer ${this.confluenceToken}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.data.results) {
        for (const page of response.data.results) {
          results.push({
            id: `confluence://${page.id}`,
            title: page.title,
            source: 'confluence',
            url: `${this.confluenceUrl}/wiki${page._links.webui}`,
            relevance: this.calculateRelevance(page.title, query),
            lastModified: page.version.when,
            type: 'Documentation',
          });
        }
      }
    } catch (error) {
      console.error('Confluence search error:', error);
    }

    return results;
  }

  // 获取文档
  async getDocument(args) {
    const { documentId, userRole } = args;

    try {
      if (documentId.startsWith('s3://')) {
        return await this.getS3Document(documentId);
      } else if (documentId.startsWith('confluence://')) {
        return await this.getConfluenceDocument(documentId);
      }

      throw new Error(`Unsupported document ID format: ${documentId}`);
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ error: error.message }),
          },
        ],
        isError: true,
      };
    }
  }

  // 过滤文档（简化版权限检查）
  async filterDocumentsByAccess(args) {
    const { documents, userRole } = args;

    const filtered = this.simpleAccessFilter(documents, userRole);

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            originalCount: documents.length,
            filteredCount: filtered.length,
            documents: filtered,
          }, null, 2),
        },
      ],
    };
  }

  // 简化的权限过滤（实际应调用Access Control MCP）
  simpleAccessFilter(documents, userRole) {
    if (userRole === 'Administrator') {
      return documents; // 管理员可以访问所有文档
    }

    // End User只能访问基础文档
    return documents.filter(doc => {
      return !doc.title.toLowerCase().includes('admin') &&
             !doc.title.toLowerCase().includes('internal');
    });
  }

  // 计算相关性（简化版）
  calculateRelevance(text, query) {
    const lowerText = text.toLowerCase();
    const lowerQuery = query.toLowerCase();
    
    if (lowerText === lowerQuery) return 1.0;
    if (lowerText.includes(lowerQuery)) return 0.8;
    
    // 简单的关键词匹配
    const queryWords = lowerQuery.split(' ');
    const matchCount = queryWords.filter(word => lowerText.includes(word)).length;
    return matchCount / queryWords.length * 0.6;
  }

  // 读取S3资源
  async readS3Resource(uri) {
    // 实现S3资源读取
    return {
      contents: [
        {
          uri,
          mimeType: 'text/plain',
          text: 'S3 resource content...',
        },
      ],
    };
  }

  // 读取Confluence资源
  async readConfluenceResource(uri) {
    // 实现Confluence资源读取
    return {
      contents: [
        {
          uri,
          mimeType: 'text/html',
          text: 'Confluence page content...',
        },
      ],
    };
  }

  // 获取S3文档
  async getS3Document(documentId) {
    // 实现S3文档获取
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            id: documentId,
            content: 'Document content from S3...',
          }),
        },
      ],
    };
  }

  // 获取Confluence文档
  async getConfluenceDocument(documentId) {
    // 实现Confluence文档获取
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            id: documentId,
            content: 'Document content from Confluence...',
          }),
        },
      ],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Document Repository MCP Server running on stdio');
  }
}

// 启动服务器
const server = new DocumentRepositoryServer();
server.run().catch(console.error);
