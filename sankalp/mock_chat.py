"""
Mock RAG Pipeline for testing when API quotas are exhausted
"""
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class MockMedicalRAGPipeline:
    """
    Mock RAG pipeline for testing purposes when API quotas are exceeded
    """
    
    def __init__(self, data_folder: str = "data"):
        """Initialize mock pipeline"""
        self.data_folder = data_folder
        logger.info("Initialized mock RAG pipeline")
    
    def chat(self, message: str, patient_id: Optional[str] = None) -> str:
        """
        Mock chat interface that returns a sample response
        
        Args:
            message: User message/query
            patient_id: Optional patient identifier
            
        Returns:
            Mock response
        """
        logger.info(f"Mock chat for patient {patient_id}: {message[:50]}...")
        
        # Generate mock response based on common cardiovascular queries
        mock_responses = {
            "risk factors": """Based on the cardiovascular disease literature, the main risk factors include:

1. **Non-modifiable risk factors:**
   - Age (men ≥45 years, women ≥55 years)
   - Gender (men at higher risk at younger ages)
   - Family history of premature coronary heart disease
   - Genetic factors

2. **Modifiable risk factors:**
   - High blood pressure (hypertension)
   - High cholesterol levels (especially LDL cholesterol)
   - Diabetes mellitus
   - Smoking and tobacco use
   - Physical inactivity
   - Obesity (especially abdominal obesity)
   - Unhealthy diet high in saturated fats and trans fats

3. **Emerging risk factors:**
   - Chronic kidney disease
   - Sleep apnea
   - Chronic inflammatory conditions
   - Stress and depression

The American Heart Association and ACC/AHA guidelines emphasize that cardiovascular risk should be assessed using validated risk calculators that incorporate multiple risk factors to guide prevention strategies.

*Note: This is a mock response for testing purposes. Please consult with healthcare professionals for personalized medical advice.*""",
            
            "prevention": """Cardiovascular disease prevention strategies include:

**Primary Prevention:**
- Lifestyle modifications (diet, exercise, smoking cessation)
- Blood pressure management (target <130/80 mmHg)
- Cholesterol management with statins when indicated
- Diabetes prevention and management
- Weight management
- Regular cardiovascular risk assessment

**Secondary Prevention:**
- Comprehensive medical therapy
- Cardiac rehabilitation programs
- Aggressive risk factor modification
- Regular monitoring and follow-up

The 2019 ACC/AHA Primary Prevention Guidelines recommend a team-based approach to cardiovascular disease prevention.

*Note: This is a mock response for testing purposes. Please consult with healthcare professionals for personalized medical advice.*""",
            
            "treatment": """Treatment approaches for cardiovascular disease vary based on the specific condition but generally include:

**Medical Management:**
- Antiplatelet therapy (aspirin, clopidogrel)
- Beta-blockers for heart rate and blood pressure control
- ACE inhibitors or ARBs for blood pressure and cardiac protection
- Statins for cholesterol management
- Diabetes medications when indicated

**Interventional Procedures:**
- Percutaneous coronary intervention (PCI) with stenting
- Coronary artery bypass grafting (CABG)
- Valve repair or replacement procedures

**Lifestyle Interventions:**
- Cardiac rehabilitation programs
- Dietary counseling and nutrition therapy
- Exercise prescription and monitoring
- Smoking cessation programs

Treatment decisions should always be individualized based on patient characteristics, comorbidities, and shared decision-making between patients and healthcare providers.

*Note: This is a mock response for testing purposes. Please consult with healthcare professionals for personalized medical advice.*"""
        }
        
        # Simple keyword matching for mock responses
        message_lower = message.lower()
        if any(keyword in message_lower for keyword in ["risk", "factor", "cause"]):
            return mock_responses["risk factors"]
        elif any(keyword in message_lower for keyword in ["prevent", "prevention", "avoid"]):
            return mock_responses["prevention"]
        elif any(keyword in message_lower for keyword in ["treat", "treatment", "therapy", "medication"]):
            return mock_responses["treatment"]
        else:
            return f"""Thank you for your question about "{message}". 

Based on the medical literature in our database, cardiovascular health is a complex topic that involves multiple interconnected factors including genetics, lifestyle, and environmental influences.

For specific medical questions like yours, I recommend:
1. Consulting with a qualified healthcare professional
2. Reviewing evidence-based medical guidelines
3. Considering your individual risk factors and medical history

The cardiovascular disease research papers in our database contain extensive information about diagnosis, treatment, and prevention strategies that are continuously evolving as new research emerges.

*Note: This is a mock response for testing purposes when API quotas are exceeded. Please consult with healthcare professionals for personalized medical advice.*"""


# Mock function for the chat module
def mock_chat_with_documents(message: str, patient_id: Optional[str] = None) -> str:
    """
    Mock version of chat_with_documents for testing
    """
    pipeline = MockMedicalRAGPipeline()
    return pipeline.chat(message, patient_id)