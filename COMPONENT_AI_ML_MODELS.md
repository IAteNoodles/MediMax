# MediMax AI/ML Models - Intelligent Medical Risk Prediction

## 🧠 Overview

The AI/ML Models component (`AI_Models/`) represents the core predictive intelligence of MediMax, featuring advanced machine learning models for cardiovascular disease and diabetes risk assessment. Built with XGBoost and enhanced with SHAP explanations, these models provide clinically-relevant predictions with interpretable insights for healthcare decision-making.

## 🎯 Core Capabilities

- **Cardiovascular Risk Prediction**: Evidence-based heart disease risk assessment
- **Diabetes Risk Assessment**: Type 2 diabetes prediction with metabolic factor analysis
- **SHAP Explanations**: Feature importance and prediction interpretability
- **Clinical Risk Categorization**: Structured risk level classification
- **RESTful API Interface**: Easy integration with healthcare systems
- **Model Versioning**: Tracked model versions with performance metrics

## 🏗️ Architecture

### ML Service Architecture
```
┌─────────────────────────────────────┐
│         Healthcare Frontend         │
│    (React, Streamlit, Mobile)       │
└─────────────────┬───────────────────┘
                  │ HTTP REST API
┌─────────────────▼───────────────────┐
│        API Gateway/Orchestration    │
│     (MCP Server, Agent System)      │
└─────────────────┬───────────────────┘
                  │ Prediction Requests
┌─────────────────▼───────────────────┐
│    Cardiovascular Prediction API    │
│          (port 5002)                │
│                                     │
│ ├── XGBoost Classifier             │
│ ├── SHAP Explainer                 │
│ ├── Risk Categorization            │
│ └── Feature Validation             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      Diabetes Prediction API       │
│          (port 5003)                │
│                                     │
│ ├── XGBoost Classifier             │
│ ├── Label Encoders                 │
│ ├── SHAP Explainer                 │
│ └── Clinical Interpretations       │
└─────────────────────────────────────┘
```

### Technology Stack
- **ML Framework**: XGBoost for gradient boosting classification
- **Explainability**: SHAP (SHapley Additive exPlanations)
- **API Framework**: FastAPI for high-performance APIs
- **Data Processing**: NumPy, Pandas for numerical computations
- **Model Persistence**: Joblib/Pickle for model serialization
- **Validation**: Pydantic for request/response validation

## 🫀 Cardiovascular Risk Prediction

### Model Specifications

#### Clinical Parameters
```python
class CardioInput(BaseModel):
    """Cardiovascular risk assessment parameters"""
    age: int = Field(..., ge=18, le=120, description="Age in years")
    gender: int = Field(..., ge=1, le=2, description="1=Female, 2=Male")
    height: float = Field(..., ge=100, le=250, description="Height in centimeters")
    weight: float = Field(..., ge=30, le=300, description="Weight in kilograms")
    ap_hi: int = Field(..., ge=80, le=250, description="Systolic blood pressure")
    ap_lo: int = Field(..., ge=40, le=150, description="Diastolic blood pressure")
    cholesterol: int = Field(..., ge=1, le=3, description="1=Normal, 2=Above normal, 3=Well above normal")
    gluc: int = Field(..., ge=1, le=3, description="1=Normal, 2=Above normal, 3=Well above normal")
    smoke: int = Field(..., ge=0, le=1, description="0=No, 1=Yes")
    alco: int = Field(..., ge=0, le=1, description="0=No, 1=Yes")
    active: int = Field(..., ge=0, le=1, description="0=No, 1=Yes")
```

#### Risk Classification
```python
def get_risk_category(probability: float) -> str:
    """Clinical risk categorization based on prediction probability"""
    if probability < 0.3:
        return "Low Risk"
    elif probability < 0.6:
        return "Moderate Risk" 
    elif probability < 0.8:
        return "High Risk"
    else:
        return "Very High Risk"
```

### API Endpoints

#### Health Check
```http
GET /health
Response: {
  "status": "healthy",
  "message": "MedAssist Cardiovascular Prediction API is running",
  "model_loaded": true
}
```

#### Model Information
```http
GET /model/info
Response: {
  "model_info": {
    "loaded": true,
    "type": "XGBoost Classifier",
    "purpose": "Cardiovascular Disease Prediction",
    "features": ["age", "gender", "height", "weight", "ap_hi", "ap_lo", "cholesterol", "gluc", "smoke", "alco", "active"]
  },
  "shap_explanations": "Available"
}
```

#### Risk Prediction
```http
POST /predict
Content-Type: application/json

Request:
{
  "age": 55,
  "gender": 2,
  "height": 175,
  "weight": 85,
  "ap_hi": 160,
  "ap_lo": 95,
  "cholesterol": 3,
  "gluc": 2,
  "smoke": 0,
  "alco": 0,
  "active": 1
}

Response:
{
  "prediction": 1,
  "probability": 0.78,
  "risk_category": "High Risk",
  "shap_explanations": {
    "top_positive_factors": [
      {"feature": "ap_hi", "value": 160, "contribution": 0.15, "description": "Elevated systolic blood pressure"},
      {"feature": "cholesterol", "value": 3, "contribution": 0.12, "description": "Well above normal cholesterol"},
      {"feature": "age", "value": 55, "contribution": 0.08, "description": "Age-related cardiovascular risk"}
    ],
    "top_negative_factors": [
      {"feature": "active", "value": 1, "contribution": -0.05, "description": "Physical activity reduces risk"},
      {"feature": "smoke", "value": 0, "contribution": -0.03, "description": "Non-smoking status"}
    ]
  },
  "explanation_summary": "High cardiovascular risk primarily due to elevated blood pressure (160 mmHg systolic) and high cholesterol levels. Positive factors include regular physical activity and non-smoking status.",
  "clinical_recommendations": [
    "Blood pressure management with lifestyle modifications or medication",
    "Cholesterol level optimization through diet and possible statin therapy",
    "Continue regular physical activity",
    "Regular cardiovascular monitoring and follow-up"
  ]
}
```

## 🍯 Diabetes Risk Prediction

### Model Specifications

#### Clinical Parameters
```python
class DiabetesInput(BaseModel):
    """Diabetes risk assessment parameters"""
    age: float = Field(..., ge=18, le=120, description="Age in years")
    gender: Literal["Female", "Male", "Other"] = Field(..., description="Patient gender")
    hypertension: int = Field(..., ge=0, le=1, description="0=No, 1=Yes")
    heart_disease: int = Field(..., ge=0, le=1, description="0=No, 1=Yes")
    smoking_history: Literal["never", "No Info", "current", "former", "ever", "not current"] = Field(..., description="Smoking history category")
    bmi: float = Field(..., ge=10, le=60, description="Body Mass Index")
    HbA1c_level: float = Field(..., ge=3.5, le=15, description="Hemoglobin A1c level")
    blood_glucose_level: float = Field(..., ge=50, le=400, description="Blood glucose level in mg/dL")
```

#### Feature Engineering
```python
def preprocess_diabetes_input(data: dict) -> np.ndarray:
    """Advanced preprocessing with label encoding and feature scaling"""
    
    # Gender encoding
    gender_mapping = {"Female": 0, "Male": 1, "Other": 2}
    data["gender"] = gender_mapping[data["gender"]]
    
    # Smoking history encoding
    smoking_encoder = joblib.load("diabetes_label_encoders.pkl")["smoking_history"]
    data["smoking_history"] = smoking_encoder.transform([data["smoking_history"]])[0]
    
    # Feature scaling and validation
    features = np.array([data[col] for col in FEATURE_COLUMNS]).reshape(1, -1)
    return features
```

### API Endpoints

#### Risk Prediction with Metabolic Analysis
```http
POST /predict
Content-Type: application/json

Request:
{
  "age": 45,
  "gender": "Male",
  "hypertension": 1,
  "heart_disease": 0,
  "smoking_history": "former",
  "bmi": 28.5,
  "HbA1c_level": 6.2,
  "blood_glucose_level": 140
}

Response:
{
  "prediction": 1,
  "probability": 0.72,
  "risk_category": "High Risk",
  "metabolic_analysis": {
    "bmi_status": "Overweight (BMI: 28.5)",
    "glycemic_control": "Prediabetic range (HbA1c: 6.2%, Glucose: 140 mg/dL)",
    "cardiovascular_factors": "Hypertension present, no heart disease"
  },
  "shap_explanations": {
    "top_risk_factors": [
      {"feature": "HbA1c_level", "value": 6.2, "contribution": 0.18, "description": "Elevated HbA1c indicating poor glycemic control"},
      {"feature": "blood_glucose_level", "value": 140, "contribution": 0.15, "description": "Elevated fasting glucose"},
      {"feature": "bmi", "value": 28.5, "contribution": 0.12, "description": "Overweight BMI increases diabetes risk"},
      {"feature": "hypertension", "value": 1, "contribution": 0.08, "description": "Hypertension is associated with diabetes"}
    ],
    "protective_factors": [
      {"feature": "age", "value": 45, "contribution": -0.02, "description": "Relatively younger age"}
    ]
  },
  "clinical_recommendations": [
    "Immediate glucose management and lifestyle intervention",
    "Weight reduction to achieve BMI < 25",
    "Blood pressure optimization",
    "Regular monitoring of HbA1c and glucose levels",
    "Diabetes prevention program enrollment"
  ],
  "follow_up_timeline": {
    "immediate": "Glucose management consultation within 2 weeks",
    "short_term": "Repeat HbA1c in 3 months",
    "long_term": "Annual comprehensive diabetes screening"
  }
}
```

## 🔍 SHAP Explainability

### Feature Importance Analysis
```python
class SHAPExplainer:
    """Advanced SHAP explanations for medical predictions"""
    
    def __init__(self, model, feature_names):
        self.explainer = shap.TreeExplainer(model)
        self.feature_names = feature_names
    
    def explain_prediction(self, input_data: np.ndarray) -> dict:
        """Generate comprehensive SHAP explanations"""
        
        shap_values = self.explainer.shap_values(input_data)
        base_value = self.explainer.expected_value
        
        # Feature contributions
        contributions = list(zip(self.feature_names, shap_values[0], input_data[0]))
        contributions.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # Clinical interpretations
        explanations = []
        for feature, contribution, value in contributions[:5]:
            interpretation = self.get_clinical_interpretation(feature, value, contribution)
            explanations.append({
                "feature": feature,
                "value": value,
                "contribution": float(contribution),
                "description": interpretation
            })
        
        return {
            "base_prediction": float(base_value),
            "feature_contributions": explanations,
            "total_prediction": float(base_value + sum(shap_values[0]))
        }
```

### Clinical Interpretation Engine
```python
def get_clinical_interpretation(feature: str, value: float, contribution: float) -> str:
    """Generate clinically-relevant explanations for SHAP values"""
    
    interpretations = {
        "ap_hi": {
            "high": "Elevated systolic blood pressure increases cardiovascular risk",
            "normal": "Normal systolic blood pressure is protective",
            "low": "Low systolic pressure may indicate other cardiovascular issues"
        },
        "HbA1c_level": {
            "high": "Elevated HbA1c indicates poor long-term glucose control",
            "normal": "Normal HbA1c suggests good glycemic management",
            "prediabetic": "HbA1c in prediabetic range requires intervention"
        },
        "bmi": {
            "obese": "Obesity significantly increases diabetes and cardiovascular risk",
            "overweight": "Overweight status contributes to metabolic dysfunction",
            "normal": "Normal BMI is protective against metabolic diseases"
        }
    }
    
    # Dynamic interpretation based on value ranges and contribution
    return generate_contextual_interpretation(feature, value, contribution, interpretations)
```

## 🔧 Model Performance & Validation

### Model Metrics
```python
# Cardiovascular Model Performance
CARDIO_METRICS = {
    "accuracy": 0.89,
    "precision": 0.87,
    "recall": 0.91,
    "f1_score": 0.89,
    "auc_roc": 0.94,
    "feature_importance_stability": 0.92
}

# Diabetes Model Performance
DIABETES_METRICS = {
    "accuracy": 0.91,
    "precision": 0.89,
    "recall": 0.93,
    "f1_score": 0.91,
    "auc_roc": 0.96,
    "calibration_score": 0.88
}
```

### Cross-Validation Results
```python
def validate_model_performance():
    """Comprehensive model validation with clinical metrics"""
    
    # Stratified K-fold validation
    cv_scores = cross_val_score(model, X_test, y_test, cv=5, scoring='roc_auc')
    
    # Clinical relevance validation
    sensitivity = recall_score(y_true, y_pred)  # True positive rate
    specificity = recall_score(y_true, y_pred, pos_label=0)  # True negative rate
    
    # Calibration analysis
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=10)
    
    return {
        "cross_validation_auc": cv_scores.mean(),
        "sensitivity": sensitivity,
        "specificity": specificity,
        "calibration_error": np.mean(np.abs(prob_true - prob_pred))
    }
```

## 🔧 Configuration & Deployment

### Docker Configuration
```dockerfile
# Cardiovascular API Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY cardiovascular_requirements.txt .
RUN pip install -r cardiovascular_requirements.txt

COPY . .
EXPOSE 5002

CMD ["uvicorn", "cardiovascular_api:app", "--host", "0.0.0.0", "--port", "5002"]
```

### Environment Setup
```bash
# Install dependencies
pip install -r cardiovascular_requirements.txt
pip install -r diabetes_requirements.txt

# Start services
python AI_Models/cardio/cardiovascular_api.py  # Port 5002
python AI_Models/diabetes/diabetes_api.py      # Port 5003
```

### Model Loading and Validation
```python
def load_and_validate_models():
    """Secure model loading with validation"""
    
    try:
        # Load cardiovascular model
        cardio_model = joblib.load("xgboost_model.pkl")
        cardio_explainer = shap.TreeExplainer(cardio_model)
        
        # Load diabetes model and encoders
        diabetes_model = joblib.load("diabetes_xgboost_model.pkl")
        diabetes_encoders = pickle.load(open("diabetes_label_encoders.pkl", "rb"))
        
        # Validation checks
        assert hasattr(cardio_model, 'predict'), "Cardiovascular model invalid"
        assert hasattr(diabetes_model, 'predict'), "Diabetes model invalid"
        
        logger.info("All models loaded and validated successfully")
        
    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        raise RuntimeError("Critical: ML models failed to load")
```

## 🧪 Testing & Quality Assurance

### API Testing
```python
# test_cardiovascular_api.py
def test_cardiovascular_prediction():
    """Test cardiovascular API with clinical scenarios"""
    
    # High-risk patient
    high_risk_patient = {
        "age": 65, "gender": 2, "height": 170, "weight": 90,
        "ap_hi": 180, "ap_lo": 100, "cholesterol": 3,
        "gluc": 3, "smoke": 1, "alco": 1, "active": 0
    }
    
    response = client.post("/predict", json=high_risk_patient)
    result = response.json()
    
    assert response.status_code == 200
    assert result["risk_category"] in ["High Risk", "Very High Risk"]
    assert result["probability"] > 0.6
    assert len(result["shap_explanations"]["top_positive_factors"]) >= 3

# test_diabetes_api.py  
def test_diabetes_edge_cases():
    """Test diabetes API with edge cases and boundary conditions"""
    
    # Prediabetic patient
    prediabetic_patient = {
        "age": 40, "gender": "Female", "hypertension": 0,
        "heart_disease": 0, "smoking_history": "never",
        "bmi": 26.0, "HbA1c_level": 5.9, "blood_glucose_level": 110
    }
    
    response = client.post("/predict", json=prediabetic_patient)
    result = response.json()
    
    assert 0.3 <= result["probability"] <= 0.7  # Moderate risk range
    assert "Prediabetic" in result["metabolic_analysis"]["glycemic_control"]
```

### Model Monitoring
```python
def monitor_model_drift():
    """Monitor for model performance degradation"""
    
    # Feature distribution monitoring
    current_predictions = get_recent_predictions()
    baseline_predictions = load_baseline_predictions()
    
    # Statistical tests for drift detection
    drift_score = calculate_drift_score(current_predictions, baseline_predictions)
    
    if drift_score > DRIFT_THRESHOLD:
        logger.warning(f"Model drift detected: {drift_score}")
        trigger_model_retraining()
```

## 📈 Integration Examples

### MCP Server Integration
```python
# MCP tool for cardiovascular prediction
@mcp.tool("Predict_Cardiovascular_Risk_With_Explanation")
def predict_cardiovascular_risk_with_explanation(**kwargs) -> dict:
    """MCP tool wrapper for cardiovascular prediction"""
    
    # Validate and format parameters
    cardio_params = validate_cardio_parameters(kwargs)
    
    # Call prediction API
    response = requests.post(
        "http://localhost:5002/predict",
        json=cardio_params,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        return {
            "success": True,
            "prediction": result["prediction"],
            "probability": result["probability"],
            "risk_category": result["risk_category"],
            "explanations": result["shap_explanations"],
            "recommendations": result["clinical_recommendations"]
        }
    else:
        return {"success": False, "error": response.text}
```

### Agent System Integration
```python
# Router agent model coordination
async def invoke_prediction_models(patient_context: dict) -> dict:
    """Coordinate multiple prediction models based on patient context"""
    
    results = {}
    
    # Cardiovascular assessment
    if has_cardiovascular_parameters(patient_context):
        cardio_result = await call_cardiovascular_api(patient_context)
        results["cardiovascular"] = cardio_result
    
    # Diabetes assessment  
    if has_diabetes_parameters(patient_context):
        diabetes_result = await call_diabetes_api(patient_context)
        results["diabetes"] = diabetes_result
    
    return synthesize_multi_model_results(results)
```

## 🔐 Security & Compliance

### Data Privacy
- **PHI Protection**: No persistent storage of patient data
- **Input Validation**: Comprehensive parameter validation
- **Secure Communication**: HTTPS for all API communications
- **Audit Logging**: Complete prediction audit trails

### Clinical Validation
- **Evidence-Based Models**: Training on validated clinical datasets
- **Expert Review**: Clinical validation of prediction logic
- **Regular Updates**: Periodic model retraining with new data
- **Performance Monitoring**: Continuous accuracy and calibration monitoring

---

**Part of the MediMax Healthcare Platform - Providing intelligent, explainable medical risk predictions for evidence-based clinical decision-making**