#!/bin/bash
# Test script for MediMax Multi-Agent API

echo "🧪 Testing MediMax Multi-Agent API"
echo "=================================="

# Test 1: Health check
echo -e "\n1. Testing health endpoint..."
curl -s http://localhost:8000/health | jq '.'

# Test 2: Get available models
echo -e "\n2. Getting available models..."
curl -s http://localhost:8000/models | jq '.available_models'

# Test 3: Patient assessment
echo -e "\n3. Testing patient assessment..."
curl -s -X POST http://localhost:8000/assess \
  -H "Content-Type: application/json" \
  -d '{
    "patient_history": "55-year-old male with hypertension",
    "symptoms": "Headache, fatigue, chest tightness",
    "query": "Assess cardiovascular risk",
    "age": 55,
    "gender": 1,
    "height": 175,
    "weight": 80,
    "ap_hi": 140,
    "ap_lo": 90,
    "cholesterol": 200,
    "gluc": 100,
    "smoke": 0,
    "alco": 0,
    "active": 1
  }' | jq '.'

echo -e "\n✅ API tests completed!"
echo -e "\nAPI Documentation: http://localhost:8000/docs"
