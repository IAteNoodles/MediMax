#!/usr/bin/env python3
"""
Test script to run the server on a different port
"""
import uvicorn
from app import app

if __name__ == "__main__":
    print("Starting test server on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)