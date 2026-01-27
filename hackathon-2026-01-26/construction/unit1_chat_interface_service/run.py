#!/usr/bin/env python3
"""
Castlery AI Support - Quick Start Script

Run this script to start the Chat Interface Service with the frontend UI.
"""
import uvicorn

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🏰 Castlery AI Support - Chat Interface Service")
    print("=" * 60)
    print("\n📍 Open your browser and navigate to:")
    print("   http://localhost:8000")
    print("\n📚 API Documentation:")
    print("   http://localhost:8000/docs")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
