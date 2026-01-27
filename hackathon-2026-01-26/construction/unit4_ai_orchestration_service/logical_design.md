# Logical Design - Unit 4: AI Orchestration Service

## Document Information
**Bounded Context:** AI Orchestration Context  
**Version:** 1.0  
**Date:** January 27, 2026  
**Architecture Style:** Hexagonal Architecture (Ports & Adapters)  
**Technology Stack:** Python/FastAPI or Node.js/Express (framework-agnostic design)

---

## 1. Architecture Overview

### 1.1 Architectural Style
**Hexagonal Architecture** - Domain at center, AI providers as swappable adapters:

```
┌─────────────────────────────────────────────────────────────┐
│                    Inbound Adapters                          │
│              (REST API Controllers)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Inbound Ports                              │
│         (Application Service Interfaces)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Domain Core                                 │
│  (AIQuery Aggregate, Intent Detection, Prompt Engineering)   │
│                                                              │
│  Defines Outbound Ports (Interfaces):                        │
│  - IAIProvider (AWS Bedrock, OpenAI, etc.)                   │
│  - IDocumentSearchClient                                     │
│  - IAccessControlClient                                      │
│  - IConversationContextClient                                │
│  - IAIQueryRepository                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 Outbound Adapters                            │
│  - BedrockAIAdapter (implements IAIProvider)                 │
│  - OpenAIAdapter (implements IAIProvider)                    │
│  - DocumentSearchHTTPClient (implements IDocumentSearchClient)│
│  - AccessControlHTTPClient (implements IAccessControlClient) │
│  - ConversationContextHTTPClient (implements IConversationContextClient)│
│  - PostgreSQLAIQueryRepository (implements IAIQueryRepository)│
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Why Hexagonal for This Service?

**Multiple AI Providers:**
- AWS Bedrock (primary for MVP)
- OpenAI (alternative/fallback)
- Future: Anthropic Claude direct, Google Gemini

**Benefits:**
- Easy to swap AI providers
- Domain logic independent of AI service
- Highly testable with mock AI responses
- Can implement fallback strategies
- Cost optimization by switching providers

---

## 2. Component Structure

### 2.1 Inbound Adapters (API Layer)

#### REST Controllers

**AIQueryController**
- **Responsibility:** Handle HTTP requests for AI query processing
- **Endpoints:**
  - `POST /api/v1/ai/process-query` → processQuery()
  - `POST /api/v1/ai/detect-intent` → detectIntent()
  - `GET /api/v1/ai/queries/{queryId}` → getQuery()

#### DTOs (Data Transfer Objects)

**Request DTOs:**
- ProcessQueryRequest (query, context, screenshot)
- DetectIntentRequest (query)

**Response DTOs:**
- ProcessQueryResponse (response, documentationLinks, confidence, suggestEscalation, processingTime)
- DetectIntentResponse (intent, entities, confidence)
- QueryDetailsResponse (queryId, intent, response, metrics)

---

### 2.2 Inbound Ports (Application Service Interfaces)

#### Application Service Interfaces

**IProcessAIQueryUseCase**
- processQuery(query, conversationId, userId) → AIResponse

**IDetectIntentUseCase**
- detectIntent(query) → Intent

**IGetQueryDetailsUseCase**
- getQueryDetails(queryId, userId) → AIQuery

---

### 2.3 Domain Core

#### Aggregates

**AIQuery (Aggregate Root)**
- **Identity:** QueryId
- **Entities:** ContextMessage (collection, max 5)
- **Value Objects:** QueryText, Intent, ConfidenceScore, AIResponse, ProcessingMetrics
- **Key Methods:**
  - addContext(messages) → void
  - detectIntent() → Intent
  - processWithAI() → AIResponse
  - retrieveDocuments() → List<Document>
  - filterDocuments(documents, userAccessLevel) → List<Document>
  - generateResponse() → Response
  - shouldEscalate() → Boolean
  - calculateConfidence() → ConfidenceScore
  - recordMetrics() → void

#### Entities

**ContextMessage**
- **Identity:** MessageId
- **Attributes:** role, content, timestamp
- **Key Methods:**
  - isUserMessage() → Boolean
  - isAssistantMessage() → Boolean
  - getContent() → String

#### Value Objects

**QueryId** - UUID wrapper
**QueryText** - String (2-2000 chars)
**Intent** - Enum (ERROR_TROUBLESHOOTING, TASK_GUIDANCE, GENERAL_QUESTION, OFF_TOPIC) + confidence + entities
**ConfidenceScore** - Float (0.0-1.0)
**AIResponse** - content, rawResponse, tokensUsed, model, generatedAt
**ProcessingMetrics** - totalTime, aiProcessingTime, documentSearchTime, filteringTime, tokensUsed, cost
**Prompt** - systemPrompt, userPrompt, context, temperature, maxTokens

#### Domain Services

**IntentDetectionService**
- **Responsibility:** Detect user intent from query
- **Operations:**
  - detectIntent(queryText) → Intent
  - extractEntities(queryText, intent) → Map<String, String>
  - classifyIntent(queryText) → Intent
- **Business Rules:**
  - Detects error codes (NS_*, TMS-ERROR-*)
  - Identifies task keywords (create, update, delete, configure)
  - Checks for NetSuite/TMS keywords
  - Returns OFF_TOPIC if no NetSuite/TMS keywords found

**PromptEngineeringService**
- **Responsibility:** Build optimized prompts for AI
- **Operations:**
  - buildPrompt(query, context) → Prompt
  - buildSystemPrompt() → String
  - buildUserPrompt(queryText, intent) → String
  - addContextToPrompt(prompt, context) → void
- **Business Rules:**
  - System prompt: "Documentation link provider for NetSuite and TMS"
  - Include user role and access level
  - Include last 5 messages for context
  - Temperature: 0.3 (focused responses)

**ResponseGenerationService**
- **Responsibility:** Generate final response with links
- **Operations:**
  - generateResponse(aiResponse, documents) → Response
  - generateOffTopicResponse(query) → Response
  - formatDocumentLinks(documents) → List<DocumentationLink>
  - limitLinks(documents, max) → List<Document>
  - groupLinksByCategory(documents) → Map<String, List<Document>>
- **Business Rules:**
  - Maximum 5 documentation links
  - Off-topic queries: Polite rejection message, no links
  - Links grouped by category

**ConfidenceCalculationService**
- **Responsibility:** Calculate confidence score
- **Operations:**
  - calculateConfidence(aiResponse, documents) → ConfidenceScore
  - scoreAIConfidence(aiResponse) → Float
  - scoreDocumentRelevance(documents) → Float
  - scoreIntentConfidence(intent) → Float
- **Algorithm:**
  - AI response confidence: 50% weight
  - Document relevance: 30% weight
  - Intent confidence: 20% weight
  - Threshold for escalation: 0.5

#### Domain Events

- QueryProcessed
- LowConfidenceDetected
- IntentDetected
- OffTopicQueryDetected
- AIServiceError

---

### 2.4 Outbound Ports (Interfaces Defined by Domain)

#### AI Provider Interface

**IAIProvider**
- **Purpose:** Abstract AI service providers
- **Operations:**
  - generateResponse(prompt) → AIResponse
  - estimateCost(prompt) → Float
  - isAvailable() → Boolean
  - getModelName() → String
- **Implementations:**
  - BedrockAIAdapter (AWS Bedrock)
  - OpenAIAdapter (OpenAI GPT)
  - MockAIAdapter (for testing)

#### Repository Interfaces

**IAIQueryRepository**
- save(aiQuery) → void
- findById(queryId) → AIQuery
- findByConversationId(conversationId) → List<AIQuery>
- findByUserId(userId, limit) → List<AIQuery>
- findLowConfidence(threshold) → List<AIQuery>
- deleteOlderThan(days) → Integer

#### External Service Interfaces

**IDocumentSearchClient**
- **Purpose:** Search documents via Document Repository Context
- **Operations:**
  - search(query, filters) → List<Document>

**IAccessControlClient**
- **Purpose:** Validate tokens and filter documents
- **Operations:**
  - validateToken(token) → User
  - filterDocuments(documents, userId) → List<Document>

**IConversationContextClient**
- **Purpose:** Retrieve conversation context
- **Operations:**
  - getConversationHistory(conversationId, limit) → List<Message>

**ICacheProvider**
- **Purpose:** Cache AI responses and intent detection
- **Operations:**
  - get(key) → Value
  - set(key, value, ttl) → void

---

### 2.5 Outbound Adapters (Implementations)

#### AI Provider Adapters

**BedrockAIAdapter (implements IAIProvider)**
- **Responsibility:** Integrate with AWS Bedrock
- **Operations:**
  - generateResponse(prompt) → AIResponse
    - Connect to AWS Bedrock using boto3 (Python) or AWS SDK (Node.js)
    - Use Claude 3 model (anthropic.claude-3-sonnet-20240229-v1:0)
    - Handle streaming responses
    - Track token usage
    - Calculate cost
  - estimateCost(prompt) → Float
  - isAvailable() → Boolean
  - getModelName() → String
- **Configuration:** AWS region, model ID, credentials
- **Error Handling:** Retry on throttling, fallback to OpenAI

**OpenAIAdapter (implements IAIProvider)**
- **Responsibility:** Integrate with OpenAI
- **Operations:**
  - generateResponse(prompt) → AIResponse
    - Call OpenAI API
    - Use GPT-4 or GPT-3.5-turbo
    - Track token usage
    - Calculate cost
  - estimateCost(prompt) → Float
  - isAvailable() → Boolean
  - getModelName() → String
- **Configuration:** API key, model name
- **Error Handling:** Retry on rate limits

**MockAIAdapter (implements IAIProvider)**
- **Responsibility:** Mock AI for testing
- **Operations:**
  - generateResponse(prompt) → AIResponse (predefined responses)
  - Used in unit tests and development

#### Repository Adapters

**PostgreSQLAIQueryRepository (implements IAIQueryRepository)**
- **Responsibility:** Persist AI queries
- **Implementation:** Uses `ai_orchestration` schema
- **Features:**
  - Store query, intent, response, metrics
  - TTL-based cleanup (30 days)

#### External Service Adapters

**DocumentSearchHTTPClient (implements IDocumentSearchClient)**
- **Responsibility:** Call Document Repository Context
- **Operations:**
  - search(query, filters) → List<Document>
    - GET /api/v1/documents/search
- **Error Handling:** Retry on transient failures, return empty list on failure

**AccessControlHTTPClient (implements IAccessControlClient)**
- **Responsibility:** Call Access Control Context
- **Operations:**
  - validateToken(token) → User
    - POST /api/v1/auth/validate
  - filterDocuments(documents, userId) → List<Document>
    - POST /api/v1/auth/filter-documents
- **Error Handling:** Fail fast on auth errors

**ConversationContextHTTPClient (implements IConversationContextClient)**
- **Responsibility:** Call Chat Interface Context
- **Operations:**
  - getConversationHistory(conversationId, limit) → List<Message>
    - GET /api/v1/chat/conversations/{id}
- **Error Handling:** Return empty context on failure

**RedisCacheAdapter (implements ICacheProvider)**
- **Responsibility:** Cache AI responses
- **Operations:**
  - get(key), set(key, value, ttl)
- **Configuration:** Redis host, port, TTL (1 hour for responses)

---

### 2.6 Application Services (Implement Inbound Ports)

**ProcessAIQueryApplicationService (implements IProcessAIQueryUseCase)**
- **Responsibility:** Orchestrate AI query processing
- **Dependencies:**
  - IAccessControlClient
  - IConversationContextClient
  - IntentDetectionService
  - PromptEngineeringService
  - IAIProvider
  - IDocumentSearchClient
  - ResponseGenerationService
  - ConfidenceCalculationService
  - IAIQueryRepository
- **Workflow:**
  1. Validate user authentication
  2. Create AIQuery aggregate
  3. Load conversation context (last 5 messages)
  4. Detect intent
  5. If OFF_TOPIC: Return rejection message, skip AI processing
  6. Build prompt
  7. Call AI provider
  8. Search documents
  9. Filter documents by access level
  10. Generate response
  11. Calculate confidence
  12. Determine if escalation needed
  13. Save AIQuery
  14. Publish QueryProcessed event
  15. Return response

**DetectIntentApplicationService (implements IDetectIntentUseCase)**
- **Responsibility:** Detect intent only (lightweight operation)
- **Dependencies:**
  - IntentDetectionService
- **Workflow:**
  1. Detect intent from query text
  2. Extract entities
  3. Return intent with confidence

---

## 3. Data Flow Diagrams

### 3.1 Process Query Flow (Happy Path)

```
User Request (query, conversationId)
    ↓
AIQueryController.processQuery()
    ↓
ProcessAIQueryApplicationService.execute()
    ├─→ AccessControlHTTPClient.validateToken()
    │       ↓
    │   [Access Control Context]
    │       ↓
    │   Return User
    ├─→ ConversationContextHTTPClient.getConversationHistory()
    │       ↓
    │   [Chat Interface Context]
    │       ↓
    │   Return last 5 messages
    ├─→ AIQuery.addContext(messages)
    ├─→ IntentDetectionService.detectIntent(query)
    │   ├─→ Check for NetSuite/TMS keywords
    │   ├─→ Extract error codes, task keywords
    │   └─→ Return Intent (ERROR_TROUBLESHOOTING, TASK_GUIDANCE, etc.)
    ├─→ If intent = OFF_TOPIC:
    │   ├─→ ResponseGenerationService.generateOffTopicResponse()
    │   ├─→ Save AIQuery with OFF_TOPIC intent
    │   ├─→ Publish OffTopicQueryDetected event
    │   └─→ Return rejection message (no AI call, no document search)
    ├─→ PromptEngineeringService.buildPrompt(query, context, intent)
    │   ├─→ Build system prompt
    │   ├─→ Build user prompt with intent
    │   ├─→ Add conversation context
    │   └─→ Return Prompt
    ├─→ BedrockAIAdapter.generateResponse(prompt)
    │       ↓
    │   [AWS Bedrock API]
    │       ↓
    │   Return AIResponse (text, tokens, model)
    ├─→ DocumentSearchHTTPClient.search(query, filters)
    │       ↓
    │   [Document Repository Context]
    │       ↓
    │   Return List<Document>
    ├─→ AccessControlHTTPClient.filterDocuments(documents, userId)
    │       ↓
    │   [Access Control Context]
    │       ↓
    │   Return filtered documents
    ├─→ ResponseGenerationService.generateResponse(aiResponse, documents)
    │   ├─→ Limit to 5 links
    │   ├─→ Group by category
    │   └─→ Format response
    ├─→ ConfidenceCalculationService.calculateConfidence()
    │   ├─→ Score AI confidence (50%)
    │   ├─→ Score document relevance (30%)
    │   ├─→ Score intent confidence (20%)
    │   └─→ Return ConfidenceScore
    ├─→ AIQuery.shouldEscalate() - Check if confidence < 0.5
    ├─→ AIQuery.recordMetrics() - Track processing time, tokens, cost
    ├─→ AIQueryRepository.save(aiQuery)
    ├─→ EventPublisher.publish(QueryProcessed)
    ├─→ If low confidence: EventPublisher.publish(LowConfidenceDetected)
    ↓
Return ProcessQueryResponse
```

### 3.2 Off-Topic Query Flow

```
User Request (query = "What's the weather today?")
    ↓
AIQueryController.processQuery()
    ↓
ProcessAIQueryApplicationService.execute()
    ├─→ AccessControlHTTPClient.validateToken()
    ├─→ IntentDetectionService.detectIntent(query)
    │   ├─→ Check for NetSuite/TMS keywords
    │   │       ↓
    │   │   No keywords found
    │   └─→ Return Intent.OFF_TOPIC
    ├─→ ResponseGenerationService.generateOffTopicResponse()
    │   └─→ Return: "I can only help with NetSuite and TMS-related questions. 
    │                 For other topics, please contact general support."
    ├─→ AIQueryRepository.save(aiQuery with OFF_TOPIC intent)
    ├─→ EventPublisher.publish(OffTopicQueryDetected)
    ↓
Return ProcessQueryResponse (rejection message, no links, no AI call)
```

### 3.3 AI Provider Fallback Flow

```
ProcessAIQueryApplicationService.execute()
    ├─→ BedrockAIAdapter.generateResponse(prompt)
    │       ↓
    │   [AWS Bedrock API]
    │       ↓
    │   Error: Throttling / Service Unavailable
    │       ↓
    │   Retry 3 times with exponential backoff
    │       ↓
    │   Still failing
    │       ↓
    │   Return error to application service
    ├─→ Catch error, log failure
    ├─→ Fallback to OpenAIAdapter.generateResponse(prompt)
    │       ↓
    │   [OpenAI API]
    │       ↓
    │   Return AIResponse
    ├─→ Continue with document search and response generation
    ↓
Return ProcessQueryResponse (with fallback indicator)
```

---

## 4. Database Schema Design

### 4.1 Schema: `ai_orchestration`

#### Table: `ai_queries`
```
ai_queries
├── query_id (UUID, PK)
├── conversation_id (UUID, NOT NULL)
├── user_id (UUID, NOT NULL)
├── query_text (TEXT, NOT NULL)
├── intent (ENUM: error_troubleshooting, task_guidance, general_question, off_topic)
├── intent_confidence (DECIMAL(3,2))
├── intent_entities (JSONB) - extracted entities
├── ai_response_content (TEXT)
├── ai_response_model (VARCHAR(100))
├── ai_response_tokens (INTEGER)
├── confidence_score (DECIMAL(3,2))
├── suggest_escalation (BOOLEAN)
├── processing_time_ms (INTEGER)
├── ai_processing_time_ms (INTEGER)
├── document_search_time_ms (INTEGER)
├── cost_usd (DECIMAL(10,6))
├── created_at (TIMESTAMP, NOT NULL)
├── completed_at (TIMESTAMP)
└── INDEX on conversation_id, INDEX on user_id, INDEX on intent
```

#### Table: `context_messages`
```
context_messages
├── context_message_id (UUID, PK)
├── query_id (UUID, FK to ai_queries)
├── message_id (UUID, NOT NULL) - from Chat Interface Context
├── role (ENUM: user, assistant)
├── content (TEXT)
├── timestamp (TIMESTAMP)
├── position (INTEGER) - order in context (1-5)
└── INDEX on query_id, position
```

#### Table: `documentation_links`
```
documentation_links
├── link_id (UUID, PK)
├── query_id (UUID, FK to ai_queries)
├── document_id (UUID, NOT NULL) - from Document Repository Context
├── title (VARCHAR(500))
├── url (VARCHAR(1000))
├── description (TEXT)
├── source (ENUM: s3, confluence)
├── format (ENUM: webpage, pdf)
├── relevance (DECIMAL(3,2))
├── position (INTEGER) - order in response (1-5)
└── INDEX on query_id, position
```

---

## 5. API-to-Component Mapping

### 5.1 Endpoint Mappings

| HTTP Method | Endpoint | Controller | Application Service | Domain Services | Adapters |
|-------------|----------|------------|---------------------|-----------------|----------|
| POST | /api/v1/ai/process-query | AIQueryController | ProcessAIQueryApplicationService | IntentDetectionService, PromptEngineeringService, ResponseGenerationService, ConfidenceCalculationService | BedrockAIAdapter, DocumentSearchHTTPClient, AccessControlHTTPClient |
| POST | /api/v1/ai/detect-intent | AIQueryController | DetectIntentApplicationService | IntentDetectionService | - |
| GET | /api/v1/ai/queries/{id} | AIQueryController | GetQueryDetailsApplicationService | - | AIQueryRepository |

---

## 6. Integration Points

### 6.1 Outbound Integrations

**Access Control Context (Synchronous REST)**
- Endpoint: `POST /api/v1/auth/validate`
- Purpose: Validate user token
- Adapter: AccessControlHTTPClient

- Endpoint: `POST /api/v1/auth/filter-documents`
- Purpose: Filter documents by access level
- Adapter: AccessControlHTTPClient

**Document Repository Context (Synchronous REST)**
- Endpoint: `GET /api/v1/documents/search`
- Purpose: Search documents
- Adapter: DocumentSearchHTTPClient

**Chat Interface Context (Synchronous REST)**
- Endpoint: `GET /api/v1/chat/conversations/{id}`
- Purpose: Get conversation context
- Adapter: ConversationContextHTTPClient

**AWS Bedrock (External System)**
- API: AWS Bedrock Runtime API
- Purpose: Generate AI responses
- Adapter: BedrockAIAdapter
- Authentication: AWS credentials (IAM role)

**OpenAI (External System, Fallback)**
- API: OpenAI API
- Purpose: Generate AI responses (fallback)
- Adapter: OpenAIAdapter
- Authentication: API key

### 6.2 Inbound Integrations

**Chat Interface Context**
- Calls: `POST /api/v1/ai/process-query`
- Purpose: Process user queries

---

## 7. Error Handling Strategy

### 7.1 Error Categories

**Validation Errors (400 Bad Request)**
- Empty query text
- Query text exceeds 2000 characters
- Invalid conversation ID

**Authentication Errors (401 Unauthorized)**
- Invalid token
- Expired token

**External Service Errors (500/503)**
- AI provider unavailable (Bedrock, OpenAI)
- Document Repository unavailable
- Access Control unavailable

**AI Provider Errors**
- Throttling (429)
- Content filtering (400)
- Token limit exceeded (400)

### 7.2 AI Provider Error Handling

**Retry Strategy:**
- Throttling: Retry 3 times with exponential backoff (1s, 2s, 4s)
- Transient failures: Retry 3 times
- Permanent failures: Fallback to alternative provider

**Fallback Strategy:**
- Primary: AWS Bedrock
- Fallback: OpenAI
- If both fail: Return error, suggest retry

**Circuit Breaker:**
- If Bedrock fails 10 times in 5 minutes, open circuit for 1 minute
- Use OpenAI during circuit open period

---

## 8. Security Considerations

### 8.1 Authentication
- All endpoints require valid JWT token
- Token validated via Access Control Context

### 8.2 Input Validation
- Query text: 2-2000 characters
- Sanitize input to prevent prompt injection
- Screenshot: Max 5MB (validated by Chat Interface)

### 8.3 AI Provider Security
- AWS Bedrock: Use IAM roles with least privilege
- OpenAI: API key stored securely (environment variable)
- Never expose API keys in responses or logs

### 8.4 Prompt Injection Prevention
- Sanitize user input
- Use system prompts to constrain AI behavior
- Validate AI responses before returning

### 8.5 Data Privacy
- Never log user queries with PII
- Redact sensitive information in logs
- Comply with AI provider data policies

---

## 9. Performance Considerations

### 9.1 Caching Strategy
- Intent detection results: 5-minute TTL (Redis)
- Common query responses: 1-hour TTL (Redis)
- Document search results: 5-minute TTL (via Document Repository)

### 9.2 Parallel Processing
- Search documents while AI processes query (parallel)
- Filter documents while formatting response (parallel)

### 9.3 AI Provider Optimization
- Use streaming responses for faster perceived performance
- Limit max tokens to control cost and latency
- Cache common prompts

### 9.4 Response Time Targets
- Process query: < 5 seconds (90th percentile)
- Detect intent: < 200ms
- Off-topic rejection: < 500ms (no AI call)

---

## 10. Cost Management

### 10.1 Token Usage Tracking
- Track tokens per query
- Calculate cost per query
- Monitor daily/monthly costs

### 10.2 Cost Optimization
- Use cheaper models for simple queries (GPT-3.5 vs GPT-4)
- Limit max tokens (500 for responses)
- Cache common responses
- Use intent detection to skip AI for off-topic queries

### 10.3 Budget Alerts
- Alert if daily cost exceeds threshold
- Alert if token usage spikes
- Dashboard for cost monitoring

---

## 11. Deployment Considerations

### 11.1 Service Deployment
- Containerized application (Docker)
- Stateless service (horizontal scaling)
- Environment-specific configuration

### 11.2 AI Provider Configuration
- AWS Bedrock: Region, model ID, credentials
- OpenAI: API key, model name
- Fallback order: Bedrock → OpenAI

### 11.3 Monitoring
- Health check endpoint: `GET /health`
- AI provider health checks
- Metrics: Query latency, AI latency, token usage, cost
- Alerts: High error rate, slow queries, high cost

---

## 12. Testing Strategy

### 12.1 Unit Tests
- Domain layer: Test aggregates, entities, value objects, domain services
- Intent detection logic
- Prompt engineering
- Confidence calculation
- Coverage target: 80%+

### 12.2 Integration Tests
- Test with MockAIAdapter (no real AI calls)
- Test with mock external services
- Test error handling and retries

### 12.3 AI Provider Tests
- Test BedrockAIAdapter with real API (integration tests)
- Test OpenAIAdapter with real API (integration tests)
- Test fallback behavior
- Test cost calculation

### 12.4 Contract Tests
- Verify API contracts with Chat Interface Context
- Verify API contracts with Document Repository Context
- Verify API contracts with Access Control Context

---

## 13. Benefits of Hexagonal Architecture

### 13.1 AI Provider Flexibility
- Easy to swap AI providers (Bedrock ↔ OpenAI)
- Easy to add new providers (Anthropic, Google Gemini)
- Easy to implement fallback strategies

### 13.2 Testability
- Domain logic tested without real AI calls
- Mock adapters for unit tests
- Easy to test different AI responses

### 13.3 Cost Optimization
- Easy to switch to cheaper providers
- Easy to implement provider selection logic
- Easy to A/B test different models

---

## 14. Future Enhancements (Post-MVP)

- Advanced intent detection with ML models
- Multi-turn conversation support (beyond 5 messages)
- Streaming responses for real-time feedback
- Fine-tuned models for NetSuite/TMS
- A/B testing different AI providers
- Advanced prompt engineering (few-shot learning)
- Query rewriting for better results
- Semantic search integration

---

## Notes

- Hexagonal architecture essential for this service (multiple AI providers)
- Adapters enable easy provider switching and fallback
- Domain logic isolated from AI service specifics
- Off-topic query handling prevents wasted AI calls
- Intent detection optimizes AI usage
- Confidence calculation enables smart escalation
- Cost tracking critical for budget management
