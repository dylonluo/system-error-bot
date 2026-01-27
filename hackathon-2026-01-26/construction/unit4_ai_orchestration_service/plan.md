# Unit 4: AI Orchestration Service - Implementation Plan

## Overview
Simple Python implementation with in-memory storage and mock AI provider.

---

## Steps

- [x] 1. Create directory structure & requirements.txt
- [x] 2. Value Objects (query_id, query_text, intent, confidence_score, ai_response, processing_metrics, prompt)
- [x] 3. Entity (context_message)
- [x] 4. Aggregate (ai_query)
- [x] 5. Domain Services (intent_detection, prompt_engineering, response_generation, confidence_calculation)
- [x] 6. Domain Events & Repository Interface
- [x] 7. Infrastructure (in_memory_repository, mock_ai_provider, event_publisher)
- [x] 8. Application DTOs (requests, responses)
- [x] 9. Mock Clients (document_search, access_control, conversation_context)
- [x] 10. Application Services (process_query, detect_intent, get_query_details)
- [x] 11. API Layer (controller, error_handler, main.py)
- [x] 12. Demo script (calls application services directly)
- [x] 13. README.md

---

## Defaults I'll Use
- Mock AI returns pattern-based responses (NetSuite/TMS aware)
- Mock clients return realistic sample data
- Demo calls application services directly (no server needed)
- Generic NetSuite/TMS keywords (NS_ERROR, TMS-ERROR, create, configure, etc.)

---

## One Question

[Question] Is this scope okay, or do you want me to cut anything?
[Answer] am fine with this. yay
