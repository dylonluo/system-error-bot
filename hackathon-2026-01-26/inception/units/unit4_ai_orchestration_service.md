# Unit 4: AI Orchestration Service (MVP)

## Unit Overview
**Purpose:** Orchestrates AI query processing, integrates with external AI services, manages prompt engineering, and coordinates responses from document repositories.

**Responsibility:** This unit serves as the central AI brain, processing user queries and orchestrating calls to document repositories and external AI services to generate documentation link responses.

**Team Size:** Can be built by a single development team

**MVP Timeline:** 3-4 weeks

---

## User Stories (2 stories)

### US-028: Get Help with NetSuite Core Functionality
**As a** user  
**I want to** get documentation links for NetSuite core features  
**So that** I can resolve NetSuite issues

**Priority:** Must Have (MVP)

**Acceptance Criteria:**
- AI understands basic NetSuite terminology
- AI can provide links for common NetSuite features
- AI links to relevant NetSuite documentation
- Documentation is filtered based on user's access permissions

**MVP Simplifications:**
- Limited to most common NetSuite modules
- Basic terminology understanding
- No advanced NetSuite customization support in MVP

---

### US-030: Get Help with TMS Integration
**As a** user  
**I want to** get documentation links for TMS integration  
**So that** I can resolve TMS integration issues

**Priority:** Must Have (MVP)

**Acceptance Criteria:**
- AI understands basic TMS integration concepts
- AI can provide links to TMS integration documentation
- AI provides integration error documentation links
- Documentation is filtered based on user's access permissions

**MVP Simplifications:**
- Limited to most common TMS integration scenarios
- Basic integration pattern support

---

## Dependencies

### Inbound Dependencies (APIs this unit consumes):
- **Access Control Service (Unit 2):** User permissions and access restrictions
- **Document Repository Service (Unit 3):** Document search and retrieval
- **External AI Provider API:** OpenAI, Azure OpenAI, or similar LLM service

### Outbound Dependencies (APIs this unit provides):
- AI query processing API
- Documentation link generation API
- Response generation API
- Context management API
- Intent detection API

---

## Key Responsibilities
1. **AI query processing and intent detection**
2. **Orchestration of document search**
3. Prompt engineering and optimization
4. Context window management (last 5 messages)
5. **Documentation link aggregation and ranking**
6. Response generation and formatting
7. Error handling and fallback strategies
8. Token usage tracking
9. Rate limiting
10. **Access restriction enforcement in responses**

---

## AI Orchestration Flow

### Query Processing Pipeline
1. **Receive query** from Chat Interface Service
2. **Validate user permissions** via Access Control Service
3. **Detect intent** (error troubleshooting, task guidance, general question)
4. **Search documents** via Document Repository Service
5. **Filter results** based on user access restrictions
6. **Rank and aggregate** documentation links (up to 5 links)
7. **Generate response** with AI
8. **Format response** with links
9. **Return to user** via Chat Interface

### Context Management
- Maintain last 5 messages from conversation
- Include user role and permissions in context
- Track conversation topic and focus
- Handle follow-up questions

---

## AI Capabilities

### Natural Language Understanding
- Parse user queries and extract intent
- Identify NetSuite modules and features mentioned
- Detect TMS integration-related queries
- Extract error codes and patterns
- Understand basic technical terminology

### Documentation Link Generation
- Search for relevant documentation via Unit 3
- Rank documentation by relevance (up to 5 links)
- Filter by user access permissions
- Generate clear link descriptions
- Group links by category (error docs, task docs, general docs)

### Response Generation
- Generate clear, concise responses
- Explain which documentation links are most relevant
- Provide brief summary of what each link contains
- Format responses with proper structure
- Suggest escalation when no documentation found

### Intent Detection
- Error troubleshooting (NetSuite errors, TMS integration errors)
- Task guidance (how to perform NetSuite tasks, TMS integration tasks)
- General questions (NetSuite features, TMS concepts)

---

## Prompt Engineering

### System Prompts
- Define AI assistant role: "Documentation link provider for NetSuite and TMS"
- Set tone: Professional, helpful, concise
- Specify output format: Brief response with up to 5 documentation links
- Include NetSuite and TMS-specific knowledge
- Emphasize: "Provide documentation links only, no troubleshooting"

### User Query Enhancement
- Add user role and permissions context
- Include last 5 messages from conversation
- Add relevant system information
- Add access restriction context

### Response Post-Processing
- Extract documentation links
- Format links with descriptions
- Limit to 5 links maximum
- Group links by category
- Flag when escalation is needed
- Remove unauthorized links

---

## AI Model Configuration

### Model Selection
- Primary model: GPT-4, Claude, or similar (for general queries)
- Fallback model for high availability

### Parameters
- Temperature: 0.3 (lower for more focused responses)
- Max tokens: 500 (concise responses with links)
- Top-p: 0.9
- Frequency penalty: 0.5
- Presence penalty: 0.3

---

## Error Handling

### AI Service Failures
- Retry logic with exponential backoff
- Fallback to alternative models
- Graceful degradation
- User-friendly error messages
- Suggest escalation on repeated failures

### Quality Issues
- Detect low-confidence responses
- Flag when no relevant documentation found
- Suggest escalation when uncertain
- Log quality issues for review

### Rate Limiting
- Track API usage per user/session
- Implement queuing for high load
- Provide usage feedback to users

---

## Access Restriction Enforcement

### Response Filtering
- All documentation links filtered by user permissions
- Remove unauthorized links before returning response
- Ensure compliance with access policies
- Log access attempts for audit

### Permission Checking
- Verify user permissions for each document link
- Enforce role-based restrictions
- Call Unit 2 for permission verification

---

## Performance Optimization

### Caching
- Cache common query responses
- Store frequently used prompts
- Cache model outputs for similar queries
- Invalidate cache appropriately

### Parallel Processing
- Parallel queries to document repository
- Asynchronous processing
- Optimize for latency

---

## Monitoring and Analytics

### Usage Tracking
- Token consumption per query
- Response time metrics
- Error rates and types
- Cost per query

### Quality Metrics
- User satisfaction ratings (from feedback)
- Response accuracy
- Escalation rates
- Documentation link relevance

---

## MVP Simplifications

### What's Included:
- Basic query understanding
- Simple document matching
- Limited context window (last 5 messages)
- Up to 5 documentation links per response
- Basic intent detection
- Access restriction enforcement

### What's Deferred:
- Advanced NLP features
- Semantic search
- Fine-tuned models
- Multi-turn complex reasoning
- Advanced error pattern analysis
- NetSuite system access
- SuiteAnswers integration

---

## Security Considerations
- Secure storage of API keys
- PII detection and redaction
- Content filtering for inappropriate queries
- Audit logging for all AI interactions
- Access restriction enforcement

---

## Notes
- This unit is the central AI brain of the system
- Orchestrates calls to document repository
- Does not store conversation data (delegates to Unit 1)
- Does not handle authentication (delegates to Unit 2)
- Focuses purely on AI processing and orchestration
- **Critical: Only provides documentation links, no troubleshooting**
- Must enforce access restrictions on all responses
- MVP focuses on basic AI capabilities with simple, functional implementation
- Response time target: < 5 seconds for 90% of queries
