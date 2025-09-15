"""
RAG (Retrieval-Augmented Generation) Pipeline for Medical Documents
This module implements a FAISS-based vector store with Gemini embeddings for
retrieving relevant medical information from PDF documents.
"""

import os
import glob
from typing import List, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicalRAGPipeline:
    """
    RAG pipeline for medical document retrieval and question answering
    """
    
    def __init__(self, data_folder: str = "data", embeddings_model: str = "models/embedding-001"):
        """
        Initialize the RAG pipeline
        
        Args:
            data_folder: Path to folder containing PDF documents
            embeddings_model: Google Gemini embedding model to use
        """
        self.data_folder = data_folder
        self.embeddings_model = embeddings_model
        self.vector_store = None
        self.embeddings = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
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
    
    def _load_pdf_documents(self) -> List[Document]:
        """
        Load all PDF documents from the data folder
        
        Returns:
            List of Document objects
        """
        documents = []
        pdf_files = glob.glob(os.path.join(self.data_folder, "*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.data_folder}")
            return documents
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Loading {os.path.basename(pdf_file)}")
                loader = PyPDFLoader(pdf_file)
                docs = loader.load()
                
                # Add metadata to documents
                for doc in docs:
                    doc.metadata['source_file'] = os.path.basename(pdf_file)
                    doc.metadata['file_path'] = pdf_file
                
                documents.extend(docs)
                logger.info(f"Loaded {len(docs)} pages from {os.path.basename(pdf_file)}")
                
            except Exception as e:
                logger.error(f"Error loading {pdf_file}: {e}")
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
    
    def _initialize_vector_store(self):
        """
        Initialize the FAISS vector store with document embeddings
        """
        try:
            # Check if vector store already exists
            vector_store_path = "faiss_index"
            if os.path.exists(vector_store_path):
                logger.info("Loading existing FAISS vector store...")
                self.vector_store = FAISS.load_local(
                    vector_store_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("Successfully loaded existing vector store")
                return
            
            # Create new vector store
            logger.info("Creating new FAISS vector store...")
            documents = self._load_pdf_documents()
            
            if not documents:
                logger.warning("No documents found. Creating empty vector store.")
                # Create a dummy document to initialize the vector store
                dummy_doc = Document(
                    page_content="This is a placeholder document for initialization.",
                    metadata={"source": "system"}
                )
                chunks = [dummy_doc]
            else:
                chunks = self._split_documents(documents)
            
            # Limit chunks for testing to avoid quota issues
            max_chunks = int(os.getenv('MAX_EMBEDDING_CHUNKS', '100'))
            if len(chunks) > max_chunks:
                logger.warning(f"Limiting chunks to {max_chunks} to avoid quota issues")
                chunks = chunks[:max_chunks]
            
            # Create FAISS vector store with rate limiting
            logger.info(f"Creating embeddings for {len(chunks)} chunks...")
            self.vector_store = self._create_vector_store_with_retry(chunks)
            
            # Save the vector store
            self.vector_store.save_local(vector_store_path)
            logger.info(f"Vector store saved to {vector_store_path}")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def _create_vector_store_with_retry(self, chunks: List[Document], batch_size: int = 10):
        """
        Create vector store with retry logic and batching to handle rate limits
        
        Args:
            chunks: List of document chunks
            batch_size: Number of chunks to process at once
            
        Returns:
            FAISS vector store
        """
        import time
        
        # Process in batches to avoid rate limits
        vector_store = None
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)")
            
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    if vector_store is None:
                        # Create initial vector store
                        vector_store = FAISS.from_documents(batch, self.embeddings)
                    else:
                        # Add to existing vector store
                        batch_vector_store = FAISS.from_documents(batch, self.embeddings)
                        vector_store.merge_from(batch_vector_store)
                    
                    logger.info(f"✅ Batch {batch_num} processed successfully")
                    break
                    
                except Exception as e:
                    retry_count += 1
                    if "429" in str(e) or "quota" in str(e).lower():
                        wait_time = min(60 * retry_count, 300)  # Wait up to 5 minutes
                        logger.warning(f"Rate limit hit. Waiting {wait_time} seconds before retry {retry_count}/{max_retries}")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Error processing batch {batch_num}: {e}")
                        raise
            
            if retry_count >= max_retries:
                logger.error(f"Failed to process batch {batch_num} after {max_retries} retries")
                break
            
            # Small delay between batches to be respectful of API limits
            if i + batch_size < len(chunks):
                time.sleep(2)
        
        if vector_store is None:
            raise Exception("Failed to create vector store")
        
        return vector_store
    
    def search_documents(self, query: str, k: int = 5) -> List[Document]:
        """
        Search for relevant documents using similarity search
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            
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
                context = "\n\n".join([
                    f"Document: {doc.metadata.get('source_file', 'Unknown')}\n{doc.page_content}"
                    for doc in context_docs
                ])
            
            # Prepare the prompt
            prompt = f"""You are a medical AI assistant with access to cardiovascular disease research papers and clinical guidelines. 
Based on the provided context, answer the user's question accurately and professionally.

Context from medical literature:
{context}

User Question: {query}

Please provide a comprehensive answer based on the medical literature provided. If the context doesn't contain relevant information for the question, please state that clearly and provide general medical guidance while recommending consultation with healthcare professionals.

Response:"""
            
            # Generate response using Gemini
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}. Please try again or consult with a healthcare professional."
    
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
            # Add patient context to the query if provided
            enhanced_query = message
            if patient_id:
                enhanced_query = f"Patient ID {patient_id}: {message}"
            
            # Search for relevant documents
            relevant_docs = self.search_documents(enhanced_query)
            
            # Generate response
            response = self.generate_response(message, relevant_docs)
            
            logger.info(f"Generated response for patient {patient_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            return "I apologize, but I'm currently unable to process your request. Please try again later or consult with a healthcare professional."
    
    def add_documents(self, new_pdf_paths: List[str]):
        """
        Add new PDF documents to the existing vector store
        
        Args:
            new_pdf_paths: List of paths to new PDF files
        """
        try:
            new_documents = []
            for pdf_path in new_pdf_paths:
                if os.path.exists(pdf_path) and pdf_path.endswith('.pdf'):
                    loader = PyPDFLoader(pdf_path)
                    docs = loader.load()
                    
                    # Add metadata
                    for doc in docs:
                        doc.metadata['source_file'] = os.path.basename(pdf_path)
                        doc.metadata['file_path'] = pdf_path
                    
                    new_documents.extend(docs)
                    logger.info(f"Added {len(docs)} pages from {os.path.basename(pdf_path)}")
            
            if new_documents:
                # Split new documents
                new_chunks = self._split_documents(new_documents)
                
                # Add to existing vector store
                self.vector_store.add_documents(new_chunks)
                
                # Save updated vector store
                self.vector_store.save_local("faiss_index")
                logger.info(f"Added {len(new_chunks)} new chunks to vector store")
            
        except Exception as e:
            logger.error(f"Error adding new documents: {e}")


# Global instance for use in FastAPI
rag_pipeline = None


def get_rag_pipeline() -> MedicalRAGPipeline:
    """
    Get or create the global RAG pipeline instance
    
    Returns:
        MedicalRAGPipeline instance
    """
    global rag_pipeline
    if rag_pipeline is None:
        try:
            rag_pipeline = MedicalRAGPipeline()
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}")
            raise
    return rag_pipeline


def chat_with_documents(message: str, patient_id: Optional[str] = None) -> str:
    """
    Convenience function for chatting with the RAG pipeline
    
    Args:
        message: User message
        patient_id: Optional patient ID
        
    Returns:
        Generated response
    """
    try:
        pipeline = get_rag_pipeline()
        return pipeline.chat(message, patient_id)
    except Exception as e:
        logger.error(f"Error in chat_with_documents: {e}")
        return "I'm currently unable to process your request. Please try again later or consult with a healthcare professional."


if __name__ == "__main__":
    # Test the RAG pipeline
    try:
        print("Initializing RAG pipeline...")
        pipeline = MedicalRAGPipeline()
        
        # Test query
        test_query = "What are the risk factors for cardiovascular disease?"
        print(f"\nTest query: {test_query}")
        
        response = pipeline.chat(test_query, "test_patient_001")
        print(f"\nResponse: {response}")
        
    except Exception as e:
        print(f"Error testing RAG pipeline: {e}")