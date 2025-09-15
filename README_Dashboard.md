# MediMax AI Prediction Dashboard

A comprehensive Streamlit dashboard for cardiovascular and diabetes risk assessment using machine learning models.

## Features

- 🫀 **Cardiovascular Risk Assessment**: Predicts heart disease risk using patient demographics, vital signs, lab results, and lifestyle factors
- 🩺 **Diabetes Risk Assessment**: Evaluates diabetes risk based on medical history, BMI, and lab values
- 📊 **Interactive Interface**: User-friendly forms with real-time predictions
- 📈 **Detailed Analysis**: Feature importance and prediction explanations
- 🎯 **Flexible Prediction**: Choose to run single or both predictions

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r dashboard_requirements.txt
```

### 2. Start the AI Model Services

First, ensure the AI model APIs are running:

**Cardiovascular API (Port 5002):**
```bash
cd AI_Models/cardio
python cardiovascular_api.py
```

**Diabetes API (Port 5003):**
```bash
cd AI_Models/diabetes
python diabetes_api.py
```

### 3. Launch the Dashboard

```bash
streamlit run prediction_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Usage

### Cardiovascular Risk Assessment
1. Fill in patient demographics (age, gender, height, weight)
2. Enter vital signs (blood pressure readings)
3. Input lab results (cholesterol and glucose levels)
4. Specify lifestyle factors (smoking, alcohol, physical activity)
5. Click "Predict Cardiovascular Risk"

### Diabetes Risk Assessment
1. Enter patient demographics (age, gender, BMI)
2. Provide medical history (hypertension, heart disease, smoking history)
3. Input lab values (HbA1c level, blood glucose)
4. Click "Predict Diabetes Risk"

## Input Parameters

### Cardiovascular Model
- **Age**: 18-120 years
- **Gender**: Male (2) or Female (1)
- **Height**: 100-250 cm
- **Weight**: 30-300 kg
- **Systolic BP**: 80-250 mmHg
- **Diastolic BP**: 40-150 mmHg
- **Cholesterol**: Normal (1), Above Normal (2), Well Above Normal (3)
- **Glucose**: Normal (1), Above Normal (2), Well Above Normal (3)
- **Smoking**: Yes (1) or No (0)
- **Alcohol**: Yes (1) or No (0)
- **Physical Activity**: Yes (1) or No (0)

### Diabetes Model
- **Age**: 18-120 years
- **Gender**: Male, Female, Other
- **BMI**: 10.0-60.0
- **Hypertension**: Yes (1) or No (0)
- **Heart Disease**: Yes (1) or No (0)
- **Smoking History**: never, No Info, current, former, ever, not current
- **HbA1c Level**: 3.0-15.0%
- **Blood Glucose**: 50-500 mg/dL

## API Endpoints

- **Cardiovascular**: `POST http://localhost:5002/predict`
- **Diabetes**: `POST http://localhost:5003/predict`

## Important Notes

⚠️ **Medical Disclaimer**: This tool is for educational and research purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for medical decisions.

## Troubleshooting

### Common Issues

1. **API Connection Error**: Ensure both AI model services are running on the correct ports
2. **Missing Dependencies**: Install all requirements using `pip install -r dashboard_requirements.txt`
3. **Port Conflicts**: Check that ports 5002, 5003, and 8501 are available

### Model Loading Issues

If the AI models fail to load:
1. Check that all model files are present in their respective directories
2. Ensure all required ML libraries are installed (xgboost, scikit-learn, etc.)
3. Verify the model pickle files are not corrupted

## File Structure

```
MediMax/
├── prediction_dashboard.py          # Main Streamlit dashboard
├── dashboard_requirements.txt       # Dashboard dependencies
├── AI_Models/
│   ├── cardio/
│   │   ├── cardiovascular_api.py   # Cardio prediction API
│   │   └── xgboost_model.pkl       # Trained cardio model
│   └── diabetes/
│       ├── diabetes_api.py         # Diabetes prediction API
│       └── diabetes_xgboost_model.pkl # Trained diabetes model
└── README_Dashboard.md             # This file
```

## Features in Detail

### Real-time Predictions
- Instant API calls to ML models
- Loading spinners for user feedback
- Error handling for failed requests

### Visual Results
- Color-coded risk levels (Red for high risk, Green for low risk)
- Risk probability percentages
- Expandable detailed analysis sections

### User Experience
- Responsive design that works on different screen sizes
- Form validation and sensible default values
- Clear instructions and parameter explanations

## Contributing

To enhance the dashboard:
1. Add new prediction models by creating additional API endpoints
2. Improve the UI with additional Streamlit components
3. Add data visualization features for trend analysis
4. Implement patient data storage and history tracking