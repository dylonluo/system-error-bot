#!/usr/bin/env python3
"""
AI Orchestration Service - Quick Start Script

Run this script to start the AI Orchestration Service with Bedrock integration.
"""
import uvicorn

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🤖 AI Orchestration Service (Unit 4)")
    print("=" * 60)
    print("\n📍 API available at:")
    print("   http://localhost:8003")
    print("\n📚 API Documentation:")
    print("   http://localhost:8003/docs")
    print("\n🔍 Process query endpoint:")
    print("   POST http://localhost:8003/api/v1/ai/process-query")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )
