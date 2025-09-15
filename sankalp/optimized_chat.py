"""
Optimized RAG Pipeline for Medical Documents - Using Smallest PDFs with Rate Limiting
This module implements a FAISS-based vector store with Gemini embeddings for
retrieving relevant medical information from the 5 smallest PDF documents.
"""

import os
import time
import logging
from typing import List, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of smallest PDFs (by file size)
SMALLEST_PDFS = [
    "PIIS0025619617301210.pdf",
    "mangalesh_2024_ic_240219_1727817893.89284.pdf", 
    "nihms-108999.pdf",
    "karmali-et-al-2014-a-systematic-examination-of-the-2013-acc-aha-pooled-cohort-risk-assessment-tool-for.pdf",
    "diagnostics-11-00943.pdf"
]


class OptimizedMedicalRAGPipeline:
    """
    Optimized RAG pipeline for medical document retrieval with rate limiting
    """
    
    def __init__(self, data_folder: str = "data", embeddings_model: str = "models/embedding-001"):
        """
        Initialize the optimized RAG pipeline
        
        Args:
            data_folder: Path to folder containing PDF documents
            embeddings_model: Google Gemini embedding model to use
        """
        self.data_folder = data_folder
        self.embeddings_model = embeddings_model
        self.vector_store = None
        self.embeddings = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Optimal chunk size for embeddings
            chunk_overlap=200,  # Good overlap for context preservation
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Initialize embeddings
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=self.embeddings_model,
                google_api_key=api_key
            )
            logger.info(f"Initialized embeddings with model: {self.embeddings_model}")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
        
        # Initialize the vector store
        self._initialize_vector_store()
    
    def _load_smallest_pdfs(self) -> List[Document]:
        """
        Load only the smallest PDF documents
        
        Returns:
            List of Document objects
        """
        documents = []
        
        for pdf_name in SMALLEST_PDFS:
            pdf_path = os.path.join(self.data_folder, pdf_name)
            
            if not os.path.exists(pdf_path):
                logger.warning(f"PDF not found: {pdf_path}")
                continue
                
            try:
                logger.info(f"Loading {pdf_name}")
                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                
                # Add metadata to documents
                for doc in docs:
                    doc.metadata['source_file'] = pdf_name
                    doc.metadata['file_path'] = pdf_path
                
                documents.extend(docs)
                logger.info(f"Loaded {len(docs)} pages from {pdf_name}")
                
            except Exception as e:
                logger.error(f"Error loading {pdf_path}: {e}")
                continue
        
        logger.info(f"Total documents loaded: {len(documents)}")
        return documents
    
    def _split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of chunked Document objects
        """
        logger.info("Splitting documents into chunks...")
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} document chunks")
        return chunks
    
    def _create_embeddings_with_batch(self, chunks: List[Document], batch_size: int = 25) -> FAISS:
        """
        Create FAISS vector store using proper batch embedding
        
        Args:
            chunks: List of document chunks
            batch_size: Optimal batch size for Gemini embeddings (25-100 works well)
            
        Returns:
            FAISS vector store
        """
        logger.info(f"Creating embeddings for {len(chunks)} chunks using batch processing (batch_size={batch_size})")
        
        vector_store = None
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)")
            
            try:
                if vector_store is None:
                    # Create initial vector store with first batch
                    vector_store = FAISS.from_documents(batch, self.embeddings)
                    logger.info(f"✅ Created initial vector store with batch {batch_num}")
                else:
                    # Add subsequent batches to existing vector store
                    batch_vector_store = FAISS.from_documents(batch, self.embeddings)
                    vector_store.merge_from(batch_vector_store)
                    logger.info(f"✅ Merged batch {batch_num} into vector store")
                
                # Small delay between batches to be respectful
                if i + batch_size < len(chunks):
                    time.sleep(1)  # 1 second delay between batches
                    
            except Exception as e:
                logger.error(f"Error processing batch {batch_num}: {e}")
                # If this is the first batch, we can't continue
                if vector_store is None:
                    raise Exception(f"Failed to create initial vector store: {e}")
                else:
                    logger.warning(f"Skipping batch {batch_num} due to error, continuing with existing vector store")
                    continue
        
        if vector_store is None:
            raise Exception("Failed to create vector store")
        
        logger.info(f"✅ Successfully created vector store with {len(chunks)} total chunks")
        return vector_store
    
    def _initialize_vector_store(self):
        """
        Initialize the FAISS vector store with document embeddings
        """
        try:
            # Check if vector store already exists
            vector_store_path = "optimized_faiss_index"
            if os.path.exists(vector_store_path):
                logger.info("Loading existing optimized FAISS vector store...")
                self.vector_store = FAISS.load_local(
                    vector_store_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("Successfully loaded existing vector store")
                return
            
            # Create new vector store
            logger.info("Creating new optimized FAISS vector store...")
            documents = self._load_smallest_pdfs()
            
            if not documents:
                logger.warning("No documents found. Creating minimal vector store.")
                # Create a minimal document for initialization
                dummy_doc = Document(
                    page_content="Medical knowledge base for cardiovascular disease research and clinical guidelines.",
                    metadata={"source": "system", "source_file": "system"}
                )
                chunks = [dummy_doc]
            else:
                chunks = self._split_documents(documents)
                
                # Use a reasonable number of chunks for efficient processing
                max_chunks = int(os.getenv('MAX_EMBEDDING_CHUNKS', '200'))
                if len(chunks) > max_chunks:
                    logger.warning(f"Limiting chunks to {max_chunks} for efficient processing")
                    chunks = chunks[:max_chunks]
            
            # Create FAISS vector store with efficient batch processing
            self.vector_store = self._create_embeddings_with_batch(chunks)
            
            # Save the vector store
            self.vector_store.save_local(vector_store_path)
            logger.info(f"Vector store saved to {vector_store_path}")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def search_documents(self, query: str, k: int = 3) -> List[Document]:
        """
        Search for relevant documents using similarity search
        
        Args:
            query: Search query
            k: Number of documents to retrieve (reduced for efficiency)
            
        Returns:
            List of relevant Document objects
        """
        if not self.vector_store:
            logger.error("Vector store not initialized")
            return []
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Retrieved {len(docs)} relevant documents for query: {query[:50]}...")
            return docs
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def generate_response(self, query: str, context_docs: Optional[List[Document]] = None) -> str:
        """
        Generate a response using Gemini with retrieved context
        
        Args:
            query: User query
            context_docs: Retrieved context documents
            
        Returns:
            Generated response
        """
        try:
            # If no context provided, search for relevant documents
            if context_docs is None:
                context_docs = self.search_documents(query)
            
            # Prepare context from retrieved documents
            context = ""
            if context_docs:
                context_parts = []
                for doc in context_docs:
                    source = doc.metadata.get('source_file', 'Unknown')
                    content = doc.page_content[:500]  # Limit content length
                    context_parts.append(f"Source: {source}\n{content}")
                context = "\n\n".join(context_parts)
            
            # Prepare the prompt with rate limiting in mind (shorter prompt)
            prompt = f"""You are a medical AI assistant with access to cardiovascular disease research papers. Based on the provided context, answer the user's question accurately and professionally.

Context:
{context}

Question: {query}

Answer based on the medical literature provided. If the context doesn't contain relevant information, provide general medical guidance and recommend consulting healthcare professionals.

Response:"""
            
            # Generate response using Gemini with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(prompt)
                    return response.text
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        wait_time = 30 * (attempt + 1)
                        logger.warning(f"Rate limit hit during generation. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        raise e
            
            return "I apologize, but I'm currently experiencing rate limiting issues. Please try again in a few minutes."
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error while processing your question. Please try again later or consult with a healthcare professional."
    
    def chat(self, message: str, patient_id: Optional[str] = None) -> str:
        """
        Main chat interface that combines retrieval and generation
        
        Args:
            message: User message/query
            patient_id: Optional patient identifier
            
        Returns:
            Generated response
        """
        logger.info(f"Processing chat message for patient {patient_id}: {message[:50]}...")
        
        try:
            # Search for relevant documents
            relevant_docs = self.search_documents(message)
            
            # Generate response
            response = self.generate_response(message, relevant_docs)
            
            logger.info(f"Generated response for patient {patient_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            return "I apologize, but I'm currently unable to process your request. Please try again later or consult with a healthcare professional."


# Global instance for use in FastAPI
optimized_rag_pipeline = None


def get_optimized_rag_pipeline() -> OptimizedMedicalRAGPipeline:
    """
    Get or create the global optimized RAG pipeline instance
    
    Returns:
        OptimizedMedicalRAGPipeline instance
    """
    global optimized_rag_pipeline
    if optimized_rag_pipeline is None:
        try:
            optimized_rag_pipeline = OptimizedMedicalRAGPipeline()
        except Exception as e:
            logger.error(f"Failed to initialize optimized RAG pipeline: {e}")
            raise
    return optimized_rag_pipeline


def chat_with_documents(message: str, patient_id: Optional[str] = None) -> str:
    """
    Convenience function for chatting with the optimized RAG pipeline
    
    Args:
        message: User message
        patient_id: Optional patient ID
        
    Returns:
        Generated response
    """
    try:
        pipeline = get_optimized_rag_pipeline()
        return pipeline.chat(message, patient_id)
    except Exception as e:
        logger.error(f"Error in chat_with_documents: {e}")
        return "I'm currently unable to process your request due to system limitations. Please try again later or consult with a healthcare professional."


if __name__ == "__main__":
    # Test the optimized RAG pipeline
    try:
        print("Initializing optimized RAG pipeline...")
        pipeline = OptimizedMedicalRAGPipeline()
        
        # Test query
        test_query = "What are the risk factors for cardiovascular disease?"
        print(f"\nTest query: {test_query}")
        
        response = pipeline.chat(test_query, "test_patient_001")
        print(f"\nResponse: {response}")
        
    except Exception as e:
        print(f"Error testing optimized RAG pipeline: {e}")
        import traceback
        traceback.print_exc()