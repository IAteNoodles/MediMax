"""
Fallback Chat System - Works without embeddings when API quota is exceeded
This provides basic medical information responses without requiring embeddings
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FallbackMedicalChat:
    """
    Fallback medical chat system that works without embeddings
    """
    
    def __init__(self):
        """Initialize the fallback chat system"""
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Medical knowledge base (simplified)
        self.medical_knowledge = {
            "cardiovascular": """
            Cardiovascular Risk Factors:
            - High blood pressure (hypertension)
            - High cholesterol levels
            - Smoking and tobacco use
            - Diabetes
            - Obesity
            - Physical inactivity
            - Poor diet (high in saturated fats, trans fats, sodium)
            - Excessive alcohol consumption
            - Age (men >45, women >55)
            - Family history of heart disease
            - Chronic stress
            
            Prevention strategies include lifestyle modifications, regular exercise, 
            healthy diet, smoking cessation, and regular medical checkups.
            """,
            
            "heart disease": """
            Heart Disease Types and Symptoms:
            - Coronary artery disease: chest pain, shortness of breath
            - Heart attack: chest pain, arm pain, nausea, sweating
            - Heart failure: shortness of breath, fatigue, swelling
            - Arrhythmias: irregular heartbeat, palpitations
            
            Treatment may include medications, lifestyle changes, procedures,
            or surgery depending on the specific condition.
            """,
            
            "prevention": """
            Cardiovascular Disease Prevention:
            - Maintain healthy blood pressure (<120/80 mmHg)
            - Keep cholesterol levels in check
            - Exercise regularly (150 minutes moderate activity/week)
            - Eat a heart-healthy diet (Mediterranean-style)
            - Don't smoke or use tobacco
            - Limit alcohol consumption
            - Manage stress effectively
            - Get adequate sleep (7-9 hours/night)
            - Maintain healthy weight (BMI 18.5-24.9)
            """
        }
        
        logger.info("Fallback medical chat system initialized")
    
    def _get_relevant_knowledge(self, query: str) -> str:
        """Get relevant medical knowledge based on query keywords"""
        query_lower = query.lower()
        relevant_info = []
        
        # Check for cardiovascular-related keywords
        cardio_keywords = ["heart", "cardiovascular", "cardio", "blood pressure", "cholesterol", "coronary"]
        if any(keyword in query_lower for keyword in cardio_keywords):
            relevant_info.append(self.medical_knowledge["cardiovascular"])
            relevant_info.append(self.medical_knowledge["heart disease"])
        
        # Check for prevention-related keywords
        prevention_keywords = ["prevent", "prevention", "risk factors", "lifestyle", "diet", "exercise"]
        if any(keyword in query_lower for keyword in prevention_keywords):
            relevant_info.append(self.medical_knowledge["prevention"])
        
        # If no specific match, provide general cardiovascular info
        if not relevant_info:
            relevant_info.append(self.medical_knowledge["cardiovascular"])
        
        return "\n\n".join(relevant_info)
    
    def generate_response(self, query: str, patient_id: Optional[str] = None) -> str:
        """
        Generate a medical response using Gemini with fallback knowledge
        
        Args:
            query: User query
            patient_id: Optional patient ID
            
        Returns:
            Generated response
        """
        try:
            # Get relevant medical knowledge
            relevant_knowledge = self._get_relevant_knowledge(query)
            
            # Create prompt with medical context
            prompt = f"""You are a medical AI assistant specializing in cardiovascular health. 
Based on the medical knowledge provided and best practices, answer the user's question professionally and accurately.

Medical Knowledge Base:
{relevant_knowledge}

Patient Query: {query}
{f"Patient ID: {patient_id}" if patient_id else ""}

Instructions:
- Provide accurate medical information based on established guidelines
- Always recommend consulting healthcare professionals for personalized advice
- Be clear about limitations of AI medical advice
- Focus on evidence-based recommendations

Response:"""

            # Try to generate response with Gemini
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(prompt)
                    
                    if response.text:
                        return response.text
                    else:
                        return self._fallback_response(query)
                        
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        if attempt < max_retries - 1:
                            wait_time = 30 * (attempt + 1)
                            logger.warning(f"Rate limit hit. Waiting {wait_time} seconds...")
                            import time
                            time.sleep(wait_time)
                        else:
                            return self._fallback_response(query)
                    else:
                        logger.error(f"Error generating response: {e}")
                        return self._fallback_response(query)
            
            return self._fallback_response(query)
            
        except Exception as e:
            logger.error(f"Error in generate_response: {e}")
            return self._fallback_response(query)
    
    def _fallback_response(self, query: str) -> str:
        """Provide a fallback response when Gemini is unavailable"""
        relevant_knowledge = self._get_relevant_knowledge(query)
        
        return f"""Based on current medical guidelines and research:

{relevant_knowledge}

**Important Note:** This information is for educational purposes only and should not replace professional medical advice. Please consult with your healthcare provider for personalized recommendations and treatment options.

For cardiovascular health concerns, it's essential to:
1. Have regular checkups with your doctor
2. Monitor your blood pressure and cholesterol
3. Follow a heart-healthy lifestyle
4. Take prescribed medications as directed
5. Seek immediate medical attention for chest pain or other concerning symptoms

If you have specific health concerns or symptoms, please contact your healthcare provider immediately."""

    def chat(self, message: str, patient_id: Optional[str] = None) -> str:
        """
        Main chat interface
        
        Args:
            message: User message/query
            patient_id: Optional patient identifier
            
        Returns:
            Generated response
        """
        logger.info(f"Processing fallback chat for patient {patient_id}: {message[:50]}...")
        
        try:
            response = self.generate_response(message, patient_id)
            logger.info(f"Generated fallback response for patient {patient_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error in fallback chat: {e}")
            return "I apologize, but I'm currently experiencing technical difficulties. Please consult with a healthcare professional for medical advice."


# Global instance
fallback_chat = None


def get_fallback_chat() -> FallbackMedicalChat:
    """Get or create the global fallback chat instance"""
    global fallback_chat
    if fallback_chat is None:
        try:
            fallback_chat = FallbackMedicalChat()
        except Exception as e:
            logger.error(f"Failed to initialize fallback chat: {e}")
            raise
    return fallback_chat


def fallback_chat_with_documents(message: str, patient_id: Optional[str] = None) -> str:
    """
    Convenience function for the fallback chat system
    
    Args:
        message: User message
        patient_id: Optional patient ID
        
    Returns:
        Generated response
    """
    try:
        chat_system = get_fallback_chat()
        return chat_system.chat(message, patient_id)
    except Exception as e:
        logger.error(f"Error in fallback_chat_with_documents: {e}")
        return "I'm currently experiencing technical difficulties. Please consult with a healthcare professional for medical advice."


if __name__ == "__main__":
    # Test the fallback system
    try:
        print("Testing fallback medical chat system...")
        chat_system = FallbackMedicalChat()
        
        test_queries = [
            "What are the main risk factors for heart disease?",
            "How can I prevent cardiovascular disease?",
            "What are the symptoms of a heart attack?",
            "Tell me about healthy lifestyle choices for heart health."
        ]
        
        for query in test_queries:
            print(f"\n🩺 Query: {query}")
            response = chat_system.chat(query, "test_patient_001")
            print(f"📋 Response: {response[:200]}...")
            print("✅ Response generated successfully")
        
    except Exception as e:
        print(f"❌ Error testing fallback system: {e}")
        import traceback
        traceback.print_exc()