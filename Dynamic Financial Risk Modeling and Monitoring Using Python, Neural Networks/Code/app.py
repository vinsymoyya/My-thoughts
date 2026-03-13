from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import pickle
import numpy as np
import pandas as pd

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load the models and scaler
with open('reg_model.pkl', 'rb') as f:
    reg_model = pickle.load(f)

with open('clf_model.pkl', 'rb') as f:
    clf_model = pickle.load(f)

with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict( 
    request: Request,
    age: int = Form(...),
    credit_score: int = Form(...),
    employment_status: str = Form(...),
    education_level: str = Form(...),
    loan_amount: float = Form(...),
    loan_duration: int = Form(...),
    credit_utilization: float = Form(...),
    bankruptcy_history: int = Form(...),
    loan_defaults: int = Form(...),
    credit_history_length: int = Form(...),
    monthly_income: float = Form(...),
    net_worth: float = Form(...),
    interest_rate: float = Form(...),
):
    # Map categorical variables
    emp_status_map = {'Unemployed': 0, 'Self-Employed': 1, 'Employed': 2}
    edu_level_map = {'High School': 0, 'Associate': 1, 'Bachelor': 2, 'Master': 3, 'Doctorate': 4}
    
    features = [
        age, credit_score, emp_status_map[employment_status], edu_level_map[education_level],
        loan_amount, loan_duration, credit_utilization, bankruptcy_history,
        loan_defaults, credit_history_length, monthly_income, net_worth, interest_rate
    ]
    
    # Apply log transformation to specified features
    log_features = [4, 10, 11]  # indices for loan_amount, monthly_income, net_worth
    for idx in log_features:
        features[idx] = np.log1p(features[idx])
    
    # Scale numeric features
    numeric_features = [0, 1, 4, 5, 6, 9, 10, 11, 12]  # indices of numeric features
    scaled_numeric = scaler.transform(np.array([features[i] for i in numeric_features]).reshape(1, -1))
    
    for i, idx in enumerate(numeric_features):
        features[idx] = scaled_numeric[0][i]
      # Make predictions
    features_array = np.array(features).reshape(1, -1)
    risk_score = reg_model.predict(features_array)[0]
    # For classifier, we only use the risk score
    approval_prob = clf_model.predict_proba(np.array([[risk_score]]))[0][1]
    is_approved = clf_model.predict(np.array([[risk_score]]))[0]
    
    result = {
        "risk_score": float(risk_score),
        "approval_probability": float(approval_prob),
        "is_approved": bool(is_approved),
        "request": request
    }
    
    return templates.TemplateResponse("result.html", result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
