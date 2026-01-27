# Off-Topic Query Handling

## Overview

The system now handles queries not related to NetSuite or TMS by detecting them early and providing a polite rejection message.

---

## Flow Diagram

```
User submits query: "What's the weather today?"
    ↓
AI Orchestration: IntentDetectionService
    ↓
Check for NetSuite/TMS keywords
    ├─ Found: NetSuite, TMS, SuiteScript, transport, etc.
    │   → Proceed with normal processing
    │
    └─ Not Found: No relevant keywords
        → Intent = OFF_TOPIC
        ↓
ResponseGenerationService.generateOffTopicResponse()
        ↓
Return to user:
"I can only help with NetSuite and TMS-related questions.
For other topics, please contact general support or escalate
if you believe this was incorrectly classified."
        ↓
No document search performed
No AI processing cost incurred
```

---

## Intent Types (Updated)

| Intent | Description | Example |
|--------|-------------|---------|
| ERROR_TROUBLESHOOTING | NetSuite/TMS error | "NS_001 error in NetSuite" |
| TASK_GUIDANCE | How to do something | "How to create sales order?" |
| GENERAL_QUESTION | NetSuite/TMS question | "What is NetSuite?" |
| **OFF_TOPIC** | **Not NetSuite/TMS** | **"What's the weather?"** |

---

## Detection Logic

### NetSuite/TMS Keywords (MVP)

**NetSuite Keywords:**
- NetSuite, NS, SuiteScript, SuiteCommerce, SuiteTalk
- Sales order, purchase order, invoice, customer, vendor
- ERP, accounting, financial, inventory

**TMS Keywords:**
- TMS, transport, transportation, shipping, freight
- Carrier, route, delivery, shipment, tracking
- Logistics, warehouse, distribution

**Error Codes:**
- NS_*, NETSUITE_*, TMS-ERROR-*, TMS_*

### Detection Rules

```python
def detectIntent(queryText):
    # 1. Check for error codes
    if hasErrorCode(queryText):
        return ERROR_TROUBLESHOOTING
    
    # 2. Check for NetSuite/TMS keywords
    if not hasNetSuiteOrTMSKeywords(queryText):
        return OFF_TOPIC  # ← New handling
    
    # 3. Check for task keywords
    if hasTaskKeywords(queryText):
        return TASK_GUIDANCE
    
    # 4. Default to general question
    return GENERAL_QUESTION
```

---

## Response Template

### Off-Topic Response

```
I can only assist with NetSuite and TMS-related questions.

Your question appears to be about: [detected topic]

For help with other topics:
• Contact general IT support: support@company.com
• Visit our help center: https://help.company.com

If you believe your question is related to NetSuite or TMS,
please rephrase it or click "Escalate to Support" below.
```

---

## User Experience

### Example 1: Clear Off-Topic

**User:** "What's the weather in New York?"

**System Response:**
```
I can only assist with NetSuite and TMS-related questions.

Your question appears to be about: weather

For help with other topics, please contact general IT support.
```

**Actions Available:**
- [Start New Query]
- [Escalate to Support] (if user believes it was misclassified)

---

### Example 2: Ambiguous Query

**User:** "How do I create an order?"

**System Response:**
```
I found documentation about creating orders in NetSuite:

1. NetSuite Sales Order Creation Guide
2. TMS Shipping Order Setup
...

Is this what you're looking for?
[Yes, this helped] [No, not what I need]
```

**Note:** "order" is a NetSuite/TMS keyword, so it's processed normally.

---

### Example 3: Incorrectly Classified

**User:** "NS integration with external API"

**System (incorrectly):** "I can only assist with NetSuite and TMS-related questions..."

**User Action:** Clicks [Escalate to Support]

**Escalation Email Includes:**
- Query text: "NS integration with external API"
- Classification: OFF_TOPIC
- Note: "User escalated after off-topic classification"

**Human Support:** Reviews and improves keyword list

---

## Benefits

### 1. Cost Savings
- No AI processing for off-topic queries
- No document search performed
- Faster response time

### 2. User Clarity
- Clear scope of system capabilities
- Immediate feedback
- Alternative support channels provided

### 3. Analytics
- Track off-topic query patterns
- Identify missing keywords
- Improve intent detection over time

---

## Analytics Tracking

### New Metrics

**Off-Topic Query Rate:**
```
off_topic_rate = (off_topic_queries / total_queries) * 100
```

**Top Off-Topic Topics:**
- Weather: 15 queries
- General IT: 12 queries
- HR questions: 8 queries
- etc.

**False Positive Rate:**
```
false_positive_rate = (escalated_off_topic / total_off_topic) * 100
```

---

## Domain Model Changes

### Updated Components

**Intent Value Object:**
- Added OFF_TOPIC enum value
- Added isOffTopic() behavior

**IntentDetectionService:**
- Added NetSuite/TMS keyword checking
- Returns OFF_TOPIC if no keywords found

**ResponseGenerationService:**
- Added generateOffTopicResponse() method
- Returns polite rejection message

**New Domain Event:**
- OffTopicQueryDetected (for analytics)

**New Policy:**
- OffTopicQueryPolicy (reject non-NetSuite/TMS queries)

---

## Implementation Notes

### Keyword List Management

**MVP Approach:**
- Hardcoded keyword list in IntentDetectionService
- Simple string matching (case-insensitive)

**Post-MVP Enhancement:**
- Store keywords in database (configurable)
- Use NLP for semantic matching
- Machine learning for classification
- Admin UI to manage keywords

### Edge Cases

**Case 1: Mixed Topics**
```
Query: "What's the weather and how do I create a NetSuite order?"
→ Detected: NetSuite keyword found
→ Intent: TASK_GUIDANCE
→ Response: Focuses on NetSuite order creation
```

**Case 2: Typos**
```
Query: "How do I use NetSute?" (typo)
→ Detected: Close match to "NetSuite"
→ Intent: GENERAL_QUESTION
→ Response: Provides NetSuite documentation
```

**Case 3: Abbreviations**
```
Query: "NS error 001"
→ Detected: "NS" is NetSuite abbreviation
→ Intent: ERROR_TROUBLESHOOTING
→ Response: Provides error documentation
```

---

## Testing Scenarios

### Test Cases

1. **Pure Off-Topic**
   - Input: "What's the weather?"
   - Expected: OFF_TOPIC intent, rejection message

2. **NetSuite Question**
   - Input: "How to create sales order in NetSuite?"
   - Expected: TASK_GUIDANCE intent, documentation links

3. **TMS Question**
   - Input: "TMS shipping error"
   - Expected: ERROR_TROUBLESHOOTING intent, documentation links

4. **Ambiguous**
   - Input: "How do I configure settings?"
   - Expected: OFF_TOPIC (no NetSuite/TMS context)

5. **With Context**
   - Previous: "I'm working on NetSuite"
   - Current: "How do I configure settings?"
   - Expected: TASK_GUIDANCE (context provides NetSuite relevance)

---

## Future Enhancements

### Phase 2 Improvements

1. **Semantic Understanding**
   - Use embeddings for keyword matching
   - Understand synonyms and related terms

2. **Context Awareness**
   - Consider previous messages in conversation
   - If user was discussing NetSuite, assume continuation

3. **Confidence Scoring**
   - Return confidence for OFF_TOPIC classification
   - Allow borderline cases to proceed with warning

4. **Learning System**
   - Track escalations after OFF_TOPIC classification
   - Automatically add missing keywords
   - Improve classification over time

---

## Summary

**Added:** OFF_TOPIC intent handling to reject non-NetSuite/TMS queries early, saving costs and providing clear user feedback.

**Impact:** 
- Reduced AI processing costs
- Clearer system boundaries
- Better user experience
- Improved analytics

