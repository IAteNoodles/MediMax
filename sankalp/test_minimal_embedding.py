"""
Minimal test for batch embedding with Gemini
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

load_dotenv()

def test_minimal_batch_embedding():
    """Test batch embedding with minimal data"""
    try:
        # Initialize embeddings
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found")
            return
            
        embeddings = GoogleGenerativeAIEmbeddings(
            model='models/embedding-001',
            google_api_key=api_key
        )
        
        # Create minimal test documents
        test_docs = [
            Document(
                page_content="Cardiovascular disease is the leading cause of death worldwide.",
                metadata={"source": "test1"}
            ),
            Document(
                page_content="Risk factors include high blood pressure, high cholesterol, and smoking.",
                metadata={"source": "test2"}
            ),
            Document(
                page_content="Prevention includes regular exercise and a healthy diet.",
                metadata={"source": "test3"}
            )
        ]
        
        print(f"Creating FAISS vector store with {len(test_docs)} test documents...")
        
        # This uses batch embedding internally
        vector_store = FAISS.from_documents(test_docs, embeddings)
        
        print("✅ Vector store created successfully!")
        
        # Test search
        query = "What are cardiovascular risk factors?"
        results = vector_store.similarity_search(query, k=2)
        
        print(f"\n🔍 Search results for: '{query}'")
        for i, doc in enumerate(results, 1):
            print(f"{i}. {doc.page_content}")
            
        # Save for later use
        vector_store.save_local("minimal_faiss_index")
        print("💾 Vector store saved to minimal_faiss_index")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_minimal_batch_embedding()
    if success:
        print("\n🎉 Minimal batch embedding test successful!")
    else:
        print("\n💥 Test failed!")