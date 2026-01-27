#!/usr/bin/env python3
"""
Document Repository Service - Quick Start Script

Run this script to start the Document Repository Service.
"""
import uvicorn

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("📚 Document Repository Service (Unit 3)")
    print("=" * 60)
    print("\n📍 API available at:")
    print("   http://localhost:8002")
    print("\n📚 API Documentation:")
    print("   http://localhost:8002/docs")
    print("\n🔍 Search endpoint:")
    print("   GET http://localhost:8002/api/v1/documents/search?query=netsuite")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
