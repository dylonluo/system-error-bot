# Domain Model - Unit 4: AI Orchestration Service

## Document Information
**Bounded Context:** AI Orchestration Context  
**Version:** 1.0  
**Date:** January 27, 2026  
**Technology:** Python/JavaScript  
**Database Schema:** `ai_orchestration`

---

## Bounded Context Definition

**Purpose:** Orchestrate AI query processing, manage conversation context, and generate responses with documentation links.

**Responsibilities:**
- **Prompt construction**: Build optimized prompts for AI models
- **Model invocation**: Call AI services (AWS Bedrock, OpenAI) via adapters
- Detect user intent from query text
- Manage conversation context (last 5 messages)
- Orchestrate document search (delegate to Document Repository Context)
- Generate AI responses with documentation links
- Determine when to suggest escalation
- Track AI usage metrics (tokens, cost, latency)

**Separation of Concerns:**
- **Prompt construction** (domain logic): PromptEngineeringService builds prompts with context
- **Model invocation** (infrastructure): IAIProvider adapters handle actual AI API calls
- **Model configuration versioning**: Prompt templates and model parameters versioned in domain layer

**What This Context Does NOT Do:**
- Store conversations (belongs to Chat Interface Context)
- Authenticate users (delegates to Access Control Context)
- Search documents directly (delegates to Document Repository Context)
- Implement business rules (this is orchestration-only - no domain rules beyond AI processing logic)

**Observability Metrics:**
- **Latency**: Total processing time, AI call time, document search time
- **Tokens**: Input tokens, output tokens, total tokens per query
- **Failures**: AI service errors, timeout count, fallback usage
- **Cost**: Per-query cost in USD, daily/monthly aggregates

---

## Aggregates

### 1. AIQuery (Aggregate Root)

**Description:** Represents a user query being processed by the AI system with its context and response.

**Aggregate Root:** AIQuery

**Entities:**
- AIQuery (root)
- ContextMessage

**Value Objects:**
- QueryId
- QueryText
- Intent
- ConfidenceScore
- AIResponse
- ProcessingMetrics

**Invariants:**
- Query text must not be empty
- Context limited to last 5 messages
- Response must include confidence score
- At most 5 documentation links per response
- Processing time must be tracked

**Lifecycle:**
- Created when query is submitted
- Context loaded from conversation history
- Processed by AI service
- Documents retrieved and filtered
- Response generated and returned
- Metrics recorded for analytics

---

## Entities

### AIQuery (Aggregate Root)

**Identity:** QueryId (UUID)

**Attributes:**
- queryId: QueryId
- conversationId: ConversationId (from Chat Interface Context)
- userId: UserId (from Access Control Context)
- queryText: QueryText
- intent: Intent
- context: List<ContextMessage> (last 5 messages)
- screenshot: Screenshot (optional)
- aiResponse: AIResponse
- documentationLinks: List<DocumentationLink> (max 5)
- confidenceScore: ConfidenceScore
- suggestEscalation: Boolean
- processingMetrics: ProcessingMetrics
- createdAt: Timestamp
- completedAt: Timestamp

**Behaviors:**
- addContext(messages): void
- detectIntent(): Intent
- processWithAI(): AIResponse
- retrieveDocuments(): List<Document>
- filterDocuments(documents, userAccessLevel): List<Document>
- generateResponse(): Response
- shouldEscalate(): Boolean
- calculateConfidence(): ConfidenceScore
- recordMetrics(): void

**Business Rules:**
- Query text minimum 2 characters, maximum 2000 characters
- Context limited to last 5 messages
- Maximum 5 documentation links in response
- Confidence below 0.5 suggests escalation
- Processing time target: < 5 seconds for 90% of queries
- Screenshot optional, maximum 5MB

---

### ContextMessage (Entity within AIQuery)

**Identity:** MessageId (from Chat Interface Context)

**Attributes:**
- messageId: MessageId
- role: MessageRole (user, assistant)
- content: String
- timestamp: Timestamp

**Behaviors:**
- isUserMessage(): Boolean
- isAssistantMessage(): Boolean
- getContent(): String

**Business Rules:**
- Only last 5 messages included in context
- Messages ordered by timestamp (oldest to newest)
- Content truncated if exceeds token limit

---

## Value Objects

### QueryId

**Attributes:**
- value: UUID

**Behaviors:**
- equals(other): Boolean
- toString(): String

**Invariants:**
- Must be a valid UUID

---

### QueryText

**Attributes:**
- value: String

**Behaviors:**
- equals(other): Boolean
- toString(): String
- length(): Integer
- extractKeywords(): List<String>

**Invariants:**
- Length: 2-2000 characters
- Cannot be empty or only whitespace

---

### Intent

**Attributes:**
- value: Enum (ERROR_TROUBLESHOOTING, TASK_GUIDANCE, GENERAL_QUESTION, OFF_TOPIC)
- confidence: Float (0.0-1.0)
- entities: Map<String, String> (extracted entities)

**Behaviors:**
- isErrorTroubleshooting(): Boolean
- isTaskGuidance(): Boolean
- isGeneralQuestion(): Boolean
- isOffTopic(): Boolean
- getEntity(key): String
- hasHighConfidence(): Boolean (>= 0.7)

**Invariants:**
- Must be one of the defined intents
- Confidence between 0.0 and 1.0

**Intent Definitions:**

**ERROR_TROUBLESHOOTING:**
- User is experiencing an error
- Entities: errorCode, systemName (NetSuite, TMS)
- Example: "I'm getting error NS_001 in NetSuite"

**TASK_GUIDANCE:**
- User wants to know how to perform a task
- Entities: taskType, systemName
- Example: "How do I create a sales order in NetSuite?"

**GENERAL_QUESTION:**
- User has a general question about NetSuite or TMS
- Entities: topic
- Example: "What is NetSuite?"

**OFF_TOPIC:**
- User's question is not related to NetSuite or TMS
- Entities: detectedTopic
- Example: "What's the weather today?", "How do I cook pasta?"

---

### ConfidenceScore

**Attributes:**
- value: Float (0.0-1.0)

**Behaviors:**
- isHigh(): Boolean (>= 0.7)
- isMedium(): Boolean (0.5-0.7)
- isLow(): Boolean (< 0.5)
- shouldEscalate(): Boolean (< 0.5)
- compareTo(other): Integer

**Invariants:**
- Must be between 0.0 and 1.0
- Higher score = more confident

---

### AIResponse

**Attributes:**
- content: String (AI-generated text)
- rawResponse: String (original AI output)
- tokensUsed: Integer
- model: String (e.g., "claude-3", "gpt-4")
- generatedAt: Timestamp

**Behaviors:**
- getContent(): String
- getTokensUsed(): Integer
- calculateCost(): Float

**Invariants:**
- Content must not be empty
- Tokens used must be positive

---

### ProcessingMetrics

**Attributes:**
- totalTime: Duration (milliseconds)
- aiProcessingTime: Duration
- documentSearchTime: Duration
- filteringTime: Duration
- tokensUsed: Integer
- cost: Float (USD)

**Behaviors:**
- getTotalTime(): Duration
- getAIProcessingTime(): Duration
- getCost(): Float
- meetsPerformanceTarget(): Boolean (< 5 seconds)

**Invariants:**
- All times must be non-negative
- Total time >= sum of component times

---

### Prompt

**Purpose:** Encapsulates prompt construction logic with versioning support

**Attributes:**
- systemPrompt: String
- userPrompt: String
- context: List<ContextMessage>
- temperature: Float (0.0-1.0)
- maxTokens: Integer
- **promptVersion**: String (e.g., "v1.0", "v1.1") - tracks prompt template version
- **modelConfig**: ModelConfiguration (model name, parameters)

**Behaviors:**
- build(): String
- addContext(messages): void
- estimateTokens(): Integer
- getVersion(): String

**Model Configuration Versioning:**
- Prompt templates versioned independently (v1.0, v1.1, etc.)
- Model configurations tracked (model name, temperature, max tokens)
- Changes to prompts or model configs logged for A/B testing and rollback
- Version stored with each AIQuery for audit trail

**Invariants:**
- System prompt must not be empty
- Temperature between 0.0 and 1.0
- Max tokens must be positive
- Prompt version must be specified

---

## Domain Events

### QueryProcessed

**Attributes:**
- queryId: QueryId
- conversationId: ConversationId
- userId: UserId
- intent: Intent
- confidenceScore: ConfidenceScore
- documentCount: Integer
- processingTime: Duration
- processedAt: Timestamp

**Triggered When:** AI query processing completes

**Consumers:** Communication & Analytics Context (for usage metrics)

---

### LowConfidenceDetected

**Attributes:**
- queryId: QueryId
- conversationId: ConversationId
- confidenceScore: ConfidenceScore
- suggestEscalation: Boolean
- detectedAt: Timestamp

**Triggered When:** AI confidence score is below threshold

**Consumers:** 
- Chat Interface Context (to suggest escalation)
- Communication & Analytics Context (for quality metrics)

---

### IntentDetected

**Attributes:**
- queryId: QueryId
- intent: Intent
- confidence: Float
- entities: Map<String, String>
- detectedAt: Timestamp

**Triggered When:** Intent is successfully detected

**Consumers:** Communication & Analytics Context (for intent analytics)

---

### OffTopicQueryDetected

**Attributes:**
- queryId: QueryId
- conversationId: ConversationId
- queryText: String (sanitized)
- detectedTopic: String (optional)
- detectedAt: Timestamp

**Triggered When:** User submits query not related to NetSuite or TMS

**Consumers:** 
- Communication & Analytics Context (for tracking off-topic attempts)
- Internal (for improving intent detection)

---

### AIServiceError

**Attributes:**
- queryId: QueryId
- errorType: String
- errorMessage: String
- retryCount: Integer
- occurredAt: Timestamp

**Triggered When:** AI service call fails

**Consumers:** 
- Internal (for retry logic)
- Communication & Analytics Context (for error tracking)

---

## Repositories

### IAIQueryRepository

**Purpose:** Persist and retrieve AIQuery aggregates

**Methods:**
- save(aiQuery: AIQuery): void
- findById(queryId: QueryId): AIQuery
- findByConversationId(conversationId: ConversationId): List<AIQuery>
- findByUserId(userId: UserId, limit: Integer): List<AIQuery>
- findLowConfidence(threshold: Float): List<AIQuery>
- deleteOlderThan(days: Integer): Integer

**Implementation Notes:**
- Uses `ai_orchestration.ai_queries` and `ai_orchestration.context_messages` tables
- Stores processing metrics for analytics
- Implements TTL for old queries (30 days)

---

## Domain Services

### IntentDetectionService

**Purpose:** Detect user intent from query text

**Methods:**
- detectIntent(queryText: String): Intent
- extractEntities(queryText: String, intent: Intent): Map<String, String>
- classifyIntent(queryText: String): Intent

**Business Rules:**
- Uses pattern matching and keywords for MVP
- Detects error codes (e.g., NS_001, TMS-ERROR-500)
- Identifies task-related keywords (create, update, delete, configure)
- Checks for NetSuite/TMS-related terms (NetSuite, TMS, SuiteScript, transport, shipping, order)
- Returns OFF_TOPIC if no NetSuite/TMS keywords detected
- Falls back to GENERAL_QUESTION if NetSuite/TMS mentioned but intent unclear

**Rationale:** This is a domain service because it contains business logic for intent classification that doesn't belong to a single aggregate.

---

### PromptEngineeringService

**Purpose:** Build optimized prompts for AI service

**Methods:**
- buildPrompt(query: AIQuery, context: List<ContextMessage>): Prompt
- buildSystemPrompt(): String
- buildUserPrompt(queryText: String, intent: Intent): String
- addContextToPrompt(prompt: Prompt, context: List<ContextMessage>): void

**Business Rules:**
- System prompt defines AI role: "Documentation link provider for NetSuite and TMS"
- Include user role and access level in prompt
- Include last 5 messages for context
- Optimize for concise responses with links
- Temperature: 0.3 (focused responses)

**Rationale:** This is a domain service because it contains prompt engineering logic that is core to AI processing.

---

### ResponseGenerationService

**Purpose:** Generate final response with documentation links

**Methods:**
- generateResponse(aiResponse: AIResponse, documents: List<Document>): Response
- generateOffTopicResponse(query: AIQuery): Response
- formatDocumentLinks(documents: List<Document>): List<DocumentationLink>
- limitLinks(documents: List<Document>, max: Integer): List<Document>
- groupLinksByCategory(documents: List<Document>): Map<String, List<Document>>

**Business Rules:**
- Maximum 5 documentation links per response
- Links grouped by category (error docs, task docs, general docs)
- Links include title, URL, description, format
- Response includes brief explanation of each link
- **Off-topic queries return polite rejection message with no document links**
- Off-topic response suggests contacting support for non-NetSuite/TMS questions

**Rationale:** This is a domain service because it orchestrates response generation across multiple components.

---

### ConfidenceCalculationService

**Purpose:** Calculate confidence score for AI responses

**Methods:**
- calculateConfidence(aiResponse: AIResponse, documents: List<Document>): ConfidenceScore
- scoreAIConfidence(aiResponse: AIResponse): Float
- scoreDocumentRelevance(documents: List<Document>): Float
- scoreIntentConfidence(intent: Intent): Float

**Business Rules:**
- AI response confidence: 50% weight
- Document relevance: 30% weight
- Intent confidence: 20% weight
- Threshold for escalation: 0.5

**Rationale:** This is a domain service because it contains complex scoring logic.

---

## Application Services

### ProcessAIQueryApplicationService

**Purpose:** Orchestrate AI query processing workflow

**Responsibilities:**
1. Validate user authentication (call Access Control Context)
2. Create AIQuery aggregate
3. Load conversation context (call Chat Interface Context)
4. Detect intent (call IntentDetectionService)
5. Build prompt (call PromptEngineeringService)
6. Call AI service via IAIProvider interface (infrastructure)
7. Search documents (call Document Repository Context)
8. Filter documents by access (call Access Control Context)
9. Generate response (call ResponseGenerationService)
10. Calculate confidence (call ConfidenceCalculationService)
11. Determine if escalation needed
12. Publish QueryProcessed event
13. Return response

**Not a Domain Service because:** It orchestrates across multiple contexts and handles infrastructure concerns.

---

## Policies

### ContextWindowPolicy

**Rule:** Only last 5 messages included in context

**Implementation:**
- Enforced in AIQuery.addContext()
- Messages ordered by timestamp
- Oldest messages dropped if exceeds limit

---

### EscalationSuggestionPolicy

**Rule:** Suggest escalation when confidence score is below 0.5

**Implementation:**
- Checked in AIQuery.shouldEscalate()
- Based on ConfidenceScore.shouldEscalate()
- Suggestion included in response

---

### OffTopicQueryPolicy

**Rule:** Reject queries not related to NetSuite or TMS

**Implementation:**
- Checked in IntentDetectionService.detectIntent()
- Returns OFF_TOPIC intent if no NetSuite/TMS keywords found
- Response: "I can only help with NetSuite and TMS-related questions. For other topics, please contact general support."
- No document search performed for off-topic queries
- User can escalate if they believe query was incorrectly classified

---

### DocumentLinkLimitPolicy

**Rule:** Maximum 5 documentation links per response

**Implementation:**
- Enforced in ResponseGenerationService.limitLinks()
- Top 5 by relevance score
- Remaining links discarded

---

### PerformanceTargetPolicy

**Rule:** 90% of queries processed in < 5 seconds

**Implementation:**
- Tracked in ProcessingMetrics
- Monitored via analytics
- Alerts triggered if target missed

---

### TokenLimitPolicy

**Rule:** Maximum tokens per query to control costs

**Implementation:**
- Max tokens: 500 for response
- Context truncated if exceeds token limit
- Tracked in ProcessingMetrics

---

## Business Rules Summary

### Query Processing Rules
1. Query text: 2-2000 characters
2. Context limited to last 5 messages
3. Maximum 5 documentation links per response
4. Confidence below 0.5 suggests escalation
5. Processing time target: < 5 seconds
6. Screenshot optional, maximum 5MB
7. **Off-topic queries (non-NetSuite/TMS) rejected with polite message**
8. **No document search for off-topic queries**

### Intent Detection Rules
1. Error codes detected automatically (NS_*, TMS-ERROR-*)
2. Task keywords: create, update, delete, configure, setup
3. **NetSuite/TMS keywords required: NetSuite, TMS, SuiteScript, transport, shipping, order, invoice, etc.**
4. **Returns OFF_TOPIC if no NetSuite/TMS keywords found**
5. Falls back to GENERAL_QUESTION if NetSuite/TMS mentioned but intent unclear
6. Intent confidence tracked separately

### Prompt Engineering Rules
1. System prompt defines AI role
2. Temperature: 0.3 (focused responses)
3. Max tokens: 500
4. Include user role and access level
5. Include last 5 messages for context

### Response Generation Rules
1. Maximum 5 documentation links
2. Links grouped by category
3. Brief explanation for each link
4. Format: title, URL, description, format
5. Confidence score included

### Confidence Calculation Rules
1. AI response confidence: 50% weight
2. Document relevance: 30% weight
3. Intent confidence: 20% weight
4. Threshold for escalation: 0.5
5. Score normalized to 0.0-1.0

---

## Aggregate Relationships

```
AIQuery (Aggregate Root)
├── queryId: QueryId (identity)
├── conversationId: ConversationId (reference to Chat Interface)
├── userId: UserId (reference to Access Control)
├── queryText: QueryText (value object)
├── intent: Intent (value object)
├── ContextMessages (entities, 0-5)
│   ├── ContextMessage 1
│   │   ├── messageId: MessageId
│   │   ├── role: MessageRole
│   │   └── content: String
│   ├── ContextMessage 2
│   └── ContextMessage N (max 5)
├── screenshot: Screenshot (value object, optional)
├── aiResponse: AIResponse (value object)
├── documentationLinks: List<DocumentationLink> (value objects, max 5)
├── confidenceScore: ConfidenceScore (value object)
├── processingMetrics: ProcessingMetrics (value object)
└── Timestamps (createdAt, completedAt)
```

---

## Consistency Boundaries

**Strong Consistency (within aggregate):**
- Query processing is atomic
- Context messages are consistent
- Metrics are accurate

**Eventual Consistency (across aggregates):**
- Analytics events published asynchronously
- Document metadata may be slightly stale
- Cost tracking updated periodically

---

## Integration Points

### Inbound (APIs this context provides)

**REST Endpoints:**
- POST /api/v1/ai/process-query - Process user query
- POST /api/v1/ai/detect-intent - Detect query intent
- GET /api/v1/ai/queries/{queryId} - Get query details

### Outbound (APIs this context consumes)

**Access Control Context:**
- POST /api/v1/auth/validate - Validate user token
- GET /api/v1/auth/users/{userId} - Get user profile and access level
- POST /api/v1/auth/filter-documents - Filter documents by access

**Document Repository Context:**
- GET /api/v1/documents/search - Search documents

**Chat Interface Context:**
- GET /api/v1/chat/conversations/{id} - Get conversation context

**External Systems (via Infrastructure):**
- AWS Bedrock API - AI processing (via IAIProvider interface)
- OpenAI API - Alternative AI provider (via IAIProvider interface)

---

## Infrastructure Concerns

**Not part of domain model, but noted for completeness:**

- AI service integration (AWS Bedrock, OpenAI) via adapters
- Prompt template management
- Token counting and cost calculation
- Rate limiting for AI API calls
- Retry logic for AI service failures
- Response caching for common queries
- Performance monitoring and alerting

---

## Notes

- This context is the "brain" of the system
- Orchestrates AI processing and document retrieval
- Does not store conversations (delegates to Chat Interface)
- Does not call AI services directly (uses infrastructure adapters)
- Implements hexagonal architecture (ports and adapters)
- MVP uses simple intent detection (advanced NLP deferred)
- Focus on providing documentation links, not troubleshooting

