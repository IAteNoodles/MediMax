from fastmcp import FastMCP
import requests
import mariadb
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Get DB details
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3306))

mcp = FastMCP("Hospital")

@mcp.tool("Hello")
def hello(name: str) -> str:
    """
    A simple hello world function.
    
    Args:
        name (str): The name to greet.

    Returns:
        str: A greeting message.
    """
    return f"Hello, Bro {name}!"

@mcp.tool("Predict_Cardiovascular_Risk_With_Explanation")
def predict_cardiovascular_risk_with_explanation(
    age: float,
    gender: int,
    height: float,
    weight: float,
    ap_hi: int,
    ap_lo: int,
    cholesterol: int,
    gluc: int,
    smoke: int,
    alco: int,
    active: int
) -> dict:
    """
    Send patient data to local prediction service and return the JSON response.

    Expected input fields:
      - age: Age in years (numeric)
      - gender: 1 = Female, 2 = Male
      - height: Height in centimeters
      - weight: Weight in kilograms
      - ap_hi: Systolic blood pressure
      - ap_lo: Diastolic blood pressure
      - cholesterol: 1 = Normal, 2 = Above normal, 3 = Well above normal
      - gluc: Glucose level (1 = Normal, 2 = Above normal, 3 = Well above normal)
      - smoke: 0 = No, 1 = Yes
      - alco: Alcohol consumption (0 = No, 1 = Yes)
      - active: Physical activity (0 = No, 1 = Yes)
    """

    payload = {
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "ap_hi": ap_hi,
        "ap_lo": ap_lo,
        "cholesterol": cholesterol,
        "gluc": gluc,
        "smoke": smoke,
        "alco": alco,
        "active": active
    }

    try:
        resp = requests.post(
            "http://localhost:5002/predict",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": "request_failed", "details": str(e)}

@mcp.tool("Predict_Diabetes_Risk_With_Explanation")
def predict_diabetes_risk_with_explanation(
        age: float,
        gender: str,
        hypertension: int,
        heart_disease: int,
        smoking_history: str,
        bmi: float,
        HbA1c_level: float,
        blood_glucose_level: float
        ) -> dict:
        """
        Send diabetes-related patient data to local prediction service and return the JSON response.

        Expected input fields:
          - age: Age in years (numeric)
          - gender: "Female", "Male", or "Other"
          - hypertension: 0 = No, 1 = Yes
          - heart_disease: 0 = No, 1 = Yes
          - smoking_history: "never", "No Info", "current", "former", "ever", "not current"
          - bmi: Body Mass Index (numeric)
          - HbA1c_level: Hemoglobin A1c level (numeric)
          - blood_glucose_level: Blood glucose level in mg/dL (numeric)
        """
        payload = {
            "age": age,
            "gender": gender,
            "hypertension": hypertension,
            "heart_disease": heart_disease,
            "smoking_history": smoking_history,
            "bmi": bmi,
            "HbA1c_level": HbA1c_level,
            "blood_glucose_level": blood_glucose_level
        }

        try:
            resp = requests.post(
            "http://localhost:5003/predict",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": "request_failed", "details": str(e)}
mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8005,
        log_level="debug"
    )