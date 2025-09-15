"""
Test script for RAG pipeline with rate limiting and smaller dataset
"""
import os
import time
import logging
from dotenv import load_dotenv
from chat import MedicalRAGPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
load_dotenv()

def test_small_rag():
    """Test RAG pipeline with a smaller dataset"""
    try:
        # Create a test folder with just one PDF
        test_data_folder = "test_data"
        os.makedirs(test_data_folder, exist_ok=True)
        
        # Copy one small PDF for testing
        import shutil
        if os.path.exists("data/5.pdf"):  # This is one of the smaller PDFs (14 pages)
            shutil.copy("data/5.pdf", f"{test_data_folder}/5.pdf")
            print(f"✅ Copied test PDF to {test_data_folder}")
        
        # Initialize pipeline with test data folder
        print("Initializing RAG pipeline with limited dataset...")
        pipeline = MedicalRAGPipeline(data_folder=test_data_folder)
        
        # Test chat
        print("\nTesting chat functionality...")
        response = pipeline.chat(
            "What are the main cardiovascular risk factors mentioned in the document?", 
            "test_patient_001"
        )
        
        print(f"\n✅ Chat response generated successfully!")
        print(f"Response length: {len(response)} characters")
        print(f"Response preview:\n{response[:500]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_small_rag()
    if success:
        print("\n🎉 RAG pipeline test completed successfully!")
    else:
        print("\n💥 RAG pipeline test failed!")