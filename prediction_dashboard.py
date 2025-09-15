import streamlit as st
import joblib
import pickle
import numpy as np
import pandas as pd
import shap
import warnings
from datetime import datetime
import os

warnings.filterwarnings("ignore")

# Configure page
st.set_page_config(
    page_title="MediMax AI Prediction Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .prediction-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .risk-high {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
    }
    .risk-low {
        background-color: #e8f5e8;
        border-left: 5px solid #4caf50;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🏥 MediMax AI Prediction Dashboard</h1>', unsafe_allow_html=True)
st.markdown("### Advanced Health Risk Assessment using Machine Learning")

# Model loading and caching
@st.cache_resource
def load_cardio_model():
    """Load the cardiovascular prediction model"""
    try:
        model_path = os.path.join("AI_Models", "cardio", "xgboost_model.pkl")
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            st.success("✅ Cardiovascular model loaded successfully!")
            return model
        else:
            st.error(f"❌ Cardiovascular model file not found at: {model_path}")
            return None
    except Exception as e:
        st.error(f"❌ Error loading cardiovascular model: {str(e)}")
        return None

@st.cache_resource
def load_diabetes_model():
    """Load the diabetes prediction model and encoders"""
    try:
        model_path = os.path.join("AI_Models", "diabetes", "diabetes_xgboost_model.pkl")
        encoders_path = os.path.join("AI_Models", "diabetes", "diabetes_label_encoders.pkl")
        features_path = os.path.join("AI_Models", "diabetes", "diabetes_feature_info.pkl")
        
        # Check which files exist
        files_status = {
            "model": os.path.exists(model_path),
            "encoders": os.path.exists(encoders_path),
            "features": os.path.exists(features_path)
        }
        
        st.write("Debug: File existence status:", files_status)
        
        if not files_status["model"]:
            st.error(f"❌ Diabetes model file not found at: {model_path}")
            return None, None, None
            
        model = joblib.load(model_path)
        
        encoders = None
        if files_status["encoders"]:
            try:
                with open(encoders_path, "rb") as f:
                    encoders = pickle.load(f)
                st.write("Debug: Loaded encoders:", list(encoders.keys()) if encoders else "None")
            except Exception as e:
                st.warning(f"Warning: Could not load encoders: {str(e)}")
        else:
            st.warning("⚠️ Diabetes label encoders file not found, using default encoding")
        
        features = None
        if files_status["features"]:
            try:
                with open(features_path, "rb") as f:
                    features = pickle.load(f)
            except Exception as e:
                st.warning(f"Warning: Could not load features: {str(e)}")
        else:
            st.warning("⚠️ Diabetes features file not found")
            
        st.success("✅ Diabetes model loaded successfully!")
        return model, encoders, features
    except Exception as e:
        st.error(f"❌ Error loading diabetes model: {str(e)}")
        return None, None, None

# Load models at startup
cardio_model = load_cardio_model()
diabetes_model, diabetes_encoders, diabetes_features = load_diabetes_model()

# Helper functions
def predict_cardio_risk(data):
    """Predict cardiovascular risk using the loaded model"""
    if cardio_model is None:
        return {"error": "Cardiovascular model not available"}
    
    try:
        # Convert age to days if it's in years (assuming input is in years)
        age_days = data["age"] * 365.25 if data["age"] <= 150 else data["age"]
        
        # Prepare features in the correct order
        features = np.array([[
            age_days,
            data["gender"],
            data["height"],
            data["weight"],
            data["ap_hi"],
            data["ap_lo"],
            data["cholesterol"],
            data["gluc"],
            data["smoke"],
            data["alco"],
            data["active"]
        ]])
        
        # Make prediction
        prediction = cardio_model.predict(features)[0]
        prediction_proba = cardio_model.predict_proba(features)[0]
        
        # Calculate BMI for additional insights
        bmi = data["weight"] / ((data["height"] / 100) ** 2)
        
        # Calculate feature importance using the model's feature_importances_
        feature_names = ['age', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 'cholesterol', 'gluc', 'smoke', 'alco', 'active']
        feature_importance = dict(zip(feature_names, cardio_model.feature_importances_))
        
        # Create explanation
        explanation = {
            "input_values": data,
            "calculated_bmi": round(bmi, 2),
            "age_in_days": int(age_days),
            "feature_contributions": feature_importance,
            "model_confidence": float(max(prediction_proba)),
            "risk_factors": []
        }
        
        # Add risk factor analysis
        if data["age"] > 50:
            explanation["risk_factors"].append("Age > 50 years increases cardiovascular risk")
        if data["ap_hi"] > 140 or data["ap_lo"] > 90:
            explanation["risk_factors"].append("High blood pressure (>140/90 mmHg)")
        if bmi > 25:
            explanation["risk_factors"].append(f"BMI {bmi:.1f} indicates overweight/obesity")
        if data["cholesterol"] > 1:
            explanation["risk_factors"].append("Elevated cholesterol levels")
        if data["gluc"] > 1:
            explanation["risk_factors"].append("Elevated glucose levels")
        if data["smoke"] == 1:
            explanation["risk_factors"].append("Smoking significantly increases risk")
        if data["alco"] == 1:
            explanation["risk_factors"].append("Alcohol consumption may contribute to risk")
        if data["active"] == 0:
            explanation["risk_factors"].append("Lack of physical activity increases risk")
        
        return {
            "prediction": int(prediction),
            "prediction_probability": float(prediction_proba[1]),
            "risk_level": "High Risk" if prediction == 1 else "Low Risk",
            "explanation": explanation,
            "feature_importance": feature_importance,
            "calculated_bmi": round(bmi, 2)
        }
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

def predict_diabetes_risk(data):
    """Predict diabetes risk using the loaded model"""
    if diabetes_model is None:
        return {"error": "Diabetes model not available"}
    
    try:
        # Prepare the data with original column names
        input_data = {
            'gender': data['gender'],
            'age': data['age'],
            'hypertension': data['hypertension'],
            'heart_disease': data['heart_disease'],
            'smoking_history': data['smoking_history'],
            'bmi': data['bmi'],
            'HbA1c_level': data['HbA1c_level'],
            'blood_glucose_level': data['blood_glucose_level']
        }
        
        # Create DataFrame
        df = pd.DataFrame([input_data])
        
        # Apply label encoders for categorical columns and rename to match training format
        if diabetes_encoders and 'gender' in diabetes_encoders:
            try:
                df['gender_encoded'] = diabetes_encoders['gender'].transform(df['gender'])
            except ValueError as e:
                st.warning(f"Warning: Unknown gender category '{df['gender'].iloc[0]}'. Using default encoding.")
                df['gender_encoded'] = 1 if df['gender'].iloc[0].lower() == 'male' else 0
        else:
            # Manual encoding if no encoder available
            df['gender_encoded'] = 1 if df['gender'].iloc[0].lower() == 'male' else 0
        
        if diabetes_encoders and 'smoking_history' in diabetes_encoders:
            try:
                df['smoking_encoded'] = diabetes_encoders['smoking_history'].transform(df['smoking_history'])
            except ValueError as e:
                st.warning(f"Warning: Unknown smoking history '{df['smoking_history'].iloc[0]}'. Using default encoding.")
                # Manual fallback encoding
                smoking_map = {'never': 0, 'No Info': 1, 'current': 2, 'former': 3, 'ever': 4, 'not current': 5}
                df['smoking_encoded'] = smoking_map.get(df['smoking_history'].iloc[0], 0)
        else:
            # Manual encoding if no encoder available
            smoking_map = {'never': 0, 'No Info': 1, 'current': 2, 'former': 3, 'ever': 4, 'not current': 5}
            df['smoking_encoded'] = smoking_map.get(df['smoking_history'].iloc[0], 0)
        
        # Keep all columns initially for debugging
        st.write("Debug: DataFrame columns after encoding:", df.columns.tolist())
        st.write("Debug: DataFrame shape:", df.shape)
        
        # Reorder columns to match expected training format
        expected_columns = ['age', 'hypertension', 'heart_disease', 'bmi', 'HbA1c_level', 'blood_glucose_level', 'gender_encoded', 'smoking_encoded']
        
        # Ensure all expected columns exist
        for col in expected_columns:
            if col not in df.columns:
                st.error(f"Missing column: {col}")
                return {"error": f"Missing required column: {col}"}
        
        df = df[expected_columns]
        
        # Ensure all columns are numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        st.write("Debug: Final DataFrame for prediction:", df.head())
        
        # Make prediction
        prediction = diabetes_model.predict(df)[0]
        prediction_proba = diabetes_model.predict_proba(df)[0]
        
        # Calculate feature importance using the model's feature_importances_
        feature_names = expected_columns
        feature_importance = dict(zip(feature_names, diabetes_model.feature_importances_))
        
        # Create explanation with both original and processed data
        explanation = {
            "input_values": input_data,
            "processed_values": df.iloc[0].to_dict(),
            "feature_contributions": feature_importance,
            "model_confidence": float(max(prediction_proba)),
            "risk_factors": []
        }
        
        # Add risk factor analysis
        if data['age'] > 45:
            explanation["risk_factors"].append("Age > 45 years increases diabetes risk")
        if data['bmi'] > 25:
            explanation["risk_factors"].append("BMI > 25 indicates overweight/obesity")
        if data['HbA1c_level'] > 6.5:
            explanation["risk_factors"].append("HbA1c > 6.5% indicates poor glucose control")
        if data['blood_glucose_level'] > 126:
            explanation["risk_factors"].append("Fasting glucose > 126 mg/dL is concerning")
        if data['hypertension'] == 1:
            explanation["risk_factors"].append("Hypertension is a diabetes risk factor")
        if data['heart_disease'] == 1:
            explanation["risk_factors"].append("Heart disease is associated with diabetes")
        if data['smoking_history'] in ['current', 'ever']:
            explanation["risk_factors"].append("Smoking history increases diabetes risk")
        
        return {
            "prediction": int(prediction),
            "prediction_probability": float(prediction_proba[1]),
            "risk_level": "High Risk" if prediction == 1 else "Low Risk",
            "explanation": explanation,
            "feature_importance": feature_importance
        }
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

def display_prediction_result(title, result, risk_type="cardio"):
    """Display prediction results in a formatted card"""
    if "error" in result:
        st.error(f"❌ {title} Prediction Failed: {result['error']}")
        return
    
    # Determine risk level
    risk_score = result.get("prediction_probability", 0)
    risk_prediction = result.get("prediction", 0)
    
    risk_class = "risk-high" if risk_prediction == 1 else "risk-low"
    risk_text = "HIGH RISK" if risk_prediction == 1 else "LOW RISK"
    risk_color = "🔴" if risk_prediction == 1 else "🟢"
    
    st.markdown(f"""
    <div class="prediction-card {risk_class}">
        <h3>{risk_color} {title} Prediction</h3>
        <h2>Risk Level: {risk_text}</h2>
        <p><strong>Risk Probability:</strong> {risk_score:.2%}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display confidence metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Risk Score", f"{risk_score:.3f}")
    with col2:
        confidence = result.get("explanation", {}).get("model_confidence", max(risk_score, 1-risk_score))
        st.metric("Model Confidence", f"{confidence:.2%}")
    with col3:
        st.metric("Classification", risk_text)
    
    # Display additional calculated metrics
    if "calculated_bmi" in result:
        st.info(f"📊 **Calculated BMI:** {result['calculated_bmi']} kg/m²")
    
    # Display detailed explanation
    if "explanation" in result:
        with st.expander(f"📊 {title} Detailed Analysis", expanded=True):
            explanation = result["explanation"]
            
            # Input values section
            st.subheader("📝 Input Data")
            input_df = pd.DataFrame([explanation["input_values"]])
            st.dataframe(input_df, use_container_width=True)
            
            # Risk factors section
            if explanation.get("risk_factors"):
                st.subheader("⚠️ Identified Risk Factors")
                for factor in explanation["risk_factors"]:
                    st.warning(f"• {factor}")
            else:
                st.success("✅ No significant risk factors identified")
            
            # Additional metrics for diabetes
            if risk_type == "diabetes" and "processed_values" in explanation:
                st.subheader("🔢 Processed Values")
                processed_df = pd.DataFrame([explanation["processed_values"]])
                st.dataframe(processed_df, use_container_width=True)
            
            # Additional metrics for cardio
            if risk_type == "cardio":
                col1, col2 = st.columns(2)
                with col1:
                    if "calculated_bmi" in explanation:
                        st.metric("BMI", f"{explanation['calculated_bmi']} kg/m²")
                with col2:
                    if "age_in_days" in explanation:
                        st.metric("Age (Days)", f"{explanation['age_in_days']:,}")
    
    # Feature importance visualization
    if "feature_importance" in result:
        with st.expander(f"📈 {title} Feature Importance", expanded=False):
            importance_data = result["feature_importance"]
            if isinstance(importance_data, dict):
                # Create DataFrame and sort by importance
                df_importance = pd.DataFrame(list(importance_data.items()), 
                                           columns=['Feature', 'Importance'])
                df_importance = df_importance.sort_values('Importance', ascending=True)
                
                # Display as horizontal bar chart
                st.bar_chart(df_importance.set_index('Feature'))
                
                # Display as table
                st.subheader("Feature Importance Values")
                df_importance_sorted = df_importance.sort_values('Importance', ascending=False)
                st.dataframe(df_importance_sorted, use_container_width=True)
    
    # Raw prediction data
    with st.expander(f"🔍 Raw {title} Prediction Data", expanded=False):
        st.json(result)

# Sidebar for prediction selection
st.sidebar.title("🎯 Prediction Type")
prediction_type = st.sidebar.selectbox(
    "Choose prediction type:",
    ["Both Predictions", "Cardiovascular Risk Only", "Diabetes Risk Only"]
)

# Main content area
col1, col2 = st.columns(2)

# Cardiovascular Risk Input
if prediction_type in ["Both Predictions", "Cardiovascular Risk Only"]:
    with col1:
        st.header("❤️ Cardiovascular Risk Assessment")
        
        with st.form("cardio_form"):
            st.subheader("Patient Demographics")
            cardio_age = st.number_input("Age (years)", min_value=18, max_value=120, value=50)
            cardio_gender = st.selectbox("Gender", [2, 1], format_func=lambda x: "Male" if x == 2 else "Female")
            cardio_height = st.number_input("Height (cm)", min_value=100, max_value=250, value=175)
            cardio_weight = st.number_input("Weight (kg)", min_value=30, max_value=300, value=80)
            
            st.subheader("Vital Signs")
            ap_hi = st.number_input("Systolic Blood Pressure", min_value=80, max_value=250, value=140)
            ap_lo = st.number_input("Diastolic Blood Pressure", min_value=40, max_value=150, value=90)
            
            st.subheader("Lab Results")
            cholesterol = st.selectbox("Cholesterol Level", 
                                     [1, 2, 3], 
                                     format_func=lambda x: ["Normal", "Above Normal", "Well Above Normal"][x-1])
            gluc = st.selectbox("Glucose Level",
                               [1, 2, 3],
                               format_func=lambda x: ["Normal", "Above Normal", "Well Above Normal"][x-1])
            
            st.subheader("Lifestyle Factors")
            smoke = st.selectbox("Smoking", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
            alco = st.selectbox("Alcohol Consumption", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
            active = st.selectbox("Physical Activity", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
            
            cardio_submit = st.form_submit_button("🔍 Predict Cardiovascular Risk", use_container_width=True)

# Diabetes Risk Input
if prediction_type in ["Both Predictions", "Diabetes Risk Only"]:
    with col2:
        st.header("🩺 Diabetes Risk Assessment")
        
        with st.form("diabetes_form"):
            st.subheader("Patient Demographics")
            diabetes_age = st.number_input("Age (years) ", min_value=18, max_value=120, value=45)
            diabetes_gender = st.selectbox("Gender ", ["Male", "Female", "Other"])
            bmi = st.number_input("BMI", min_value=10.0, max_value=60.0, value=28.5, step=0.1)
            
            st.subheader("Medical History")
            hypertension = st.selectbox("Hypertension", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
            heart_disease = st.selectbox("Heart Disease", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
            smoking_history = st.selectbox("Smoking History", 
                                         ["never", "No Info", "current", "former", "ever", "not current"])
            
            st.subheader("Lab Values")
            hba1c_level = st.number_input("HbA1c Level (%)", min_value=3.0, max_value=15.0, value=6.2, step=0.1)
            blood_glucose_level = st.number_input("Blood Glucose Level (mg/dL)", 
                                                 min_value=50, max_value=500, value=140)
            
            diabetes_submit = st.form_submit_button("🔍 Predict Diabetes Risk", use_container_width=True)

# Handle form submissions and display results
if prediction_type in ["Both Predictions", "Cardiovascular Risk Only"]:
    if cardio_submit:
        cardio_data = {
            "age": cardio_age,
            "gender": cardio_gender,
            "height": cardio_height,
            "weight": cardio_weight,
            "ap_hi": ap_hi,
            "ap_lo": ap_lo,
            "cholesterol": cholesterol,
            "gluc": gluc,
            "smoke": smoke,
            "alco": alco,
            "active": active
        }
        
        with st.spinner("🔄 Analyzing cardiovascular risk..."):
            cardio_result = predict_cardio_risk(cardio_data)
        
        st.header("📊 Cardiovascular Risk Results")
        display_prediction_result("Cardiovascular", cardio_result, "cardio")

if prediction_type in ["Both Predictions", "Diabetes Risk Only"]:
    if diabetes_submit:
        diabetes_data = {
            "age": diabetes_age,
            "gender": diabetes_gender,
            "hypertension": hypertension,
            "heart_disease": heart_disease,
            "smoking_history": smoking_history,
            "bmi": bmi,
            "HbA1c_level": hba1c_level,
            "blood_glucose_level": blood_glucose_level
        }
        
        with st.spinner("🔄 Analyzing diabetes risk..."):
            diabetes_result = predict_diabetes_risk(diabetes_data)
        
        st.header("📊 Diabetes Risk Results")
        display_prediction_result("Diabetes", diabetes_result, "diabetes")

# Information section
st.markdown("---")
with st.expander("ℹ️ About This Dashboard"):
    st.markdown("""
    ### MediMax AI Prediction Dashboard
    
    This dashboard uses advanced machine learning models loaded natively for real-time health risk assessment:
    
    **🫀 Cardiovascular Risk Assessment:**
    - Uses XGBoost machine learning model loaded directly
    - Analyzes demographics, vital signs, lab results, and lifestyle factors
    - Provides instant risk probability calculations
    
    **🩺 Diabetes Risk Assessment:**
    - Uses trained diabetes prediction model with label encoders
    - Considers medical history, BMI, and lab values
    - Provides comprehensive risk analysis
    
    **⚡ Performance Features:**
    - Models loaded natively in Streamlit (no API calls required)
    - Cached model loading for fast subsequent predictions
    - Real-time predictions with instant results
    
    **⚠️ Important Notes:**
    - This tool is for educational/research purposes only
    - Not a substitute for professional medical advice
    - Always consult healthcare professionals for medical decisions
    - Models trained on specific datasets and may have limitations
    
    **🔧 Technical Details:**
    - Direct model inference using joblib and pickle
    - XGBoost models with preprocessing pipelines
    - Built with Streamlit for interactive web interface
    - Cached model loading using @st.cache_resource
    """)

# Model status information
st.markdown("---")
st.subheader("🔧 Model Status")
col1, col2 = st.columns(2)

with col1:
    if cardio_model is not None:
        st.success("✅ Cardiovascular Model: Loaded")
    else:
        st.error("❌ Cardiovascular Model: Failed to Load")

with col2:
    if diabetes_model is not None:
        st.success("✅ Diabetes Model: Loaded")
    else:
        st.error("❌ Diabetes Model: Failed to Load")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🏥 MediMax AI Health Prediction Dashboard | Built with ❤️ using Streamlit</p>
    <p>Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)