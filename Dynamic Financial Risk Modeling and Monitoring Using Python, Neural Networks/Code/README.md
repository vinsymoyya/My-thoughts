# Dynamic Financial Risk Modeling and Monitoring System

## Overview
This project implements a machine learning-based financial risk assessment and loan approval prediction system. It uses advanced algorithms to evaluate loan applications based on multiple factors and provides real-time risk scoring and loan approval predictions through a modern web interface.

## Project Structure
```
├── app.py                 # FastAPI application main file
├── requirements.txt       # Project dependencies
├── clf_model.pkl         # Trained classification model
├── reg_model.pkl         # Trained regression model
├── scaler.pkl           # Fitted StandardScaler object
├── Loan.csv             # Dataset file
├── final-model.ipynb    # Model training notebook
├── static/              # Static files for web interface
│   ├── css/
│   │   └── styles.css   # Custom CSS styles
│   └── js/
│       └── script.js    # Client-side JavaScript
└── templates/           # HTML templates
    ├── index.html      # Main form page
    └── result.html     # Results display page
```

## Features
- Risk score prediction using LightGBM Regressor
- Loan approval prediction using Random Forest Classifier
- Real-time data validation and processing
- Interactive web interface with modern UI
- Visual representation of risk assessment
- Dynamic recommendations based on risk factors
- Responsive design for all devices

## Technical Implementation

### Data Processing Pipeline
1. Data Loading and Selection
   - Load loan application data
   - Select relevant features based on EDA
   - Handle categorical variables through ordinal encoding

2. Data Preprocessing
   - Handle skewness using log transformation
   - Remove outliers using IQR method
   - Standardize numeric features using StandardScaler

3. Feature Engineering
   - Transform continuous numeric columns
   - Apply log transformation to amount-related features
   - Scale numeric features for model consistency

### Model Architecture

#### Risk Score Prediction (Regression)
- Model: LightGBM Regressor
- Features: 13 preprocessed inputs
- Target: Risk Score (0-100)
- Purpose: Predicts the risk level associated with a loan application

#### Loan Approval Prediction (Classification)
- Model: Random Forest Classifier
- Feature: Predicted Risk Score
- Target: Loan Approval Status (0/1)
- Purpose: Determines loan approval based on calculated risk score

### Web Application

#### Backend (FastAPI)
- RESTful API endpoints for predictions
- Data validation and preprocessing
- Model inference pipeline
- Result generation and formatting

#### Frontend
- Modern, responsive UI
- Real-time form validation
- Interactive visualizations
- Dynamic recommendations
- Mobile-friendly design

## Input Features
1. Age
2. Credit Score
3. Employment Status (Unemployed/Self-Employed/Employed)
4. Education Level (High School/Associate/Bachelor/Master/Doctorate)
5. Loan Amount
6. Loan Duration
7. Credit Card Utilization Rate
8. Bankruptcy History
9. Previous Loan Defaults
10. Length of Credit History
11. Monthly Income
12. Net Worth
13. Interest Rate

## Model Outputs
1. Risk Score (0-100)
2. Loan Approval Status (Approved/Not Approved)
3. Approval Probability
4. Custom Recommendations

## Setup and Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn app:app --reload   
```

3. Access the application:
```
http://localhost:8000
```

## Model Training Process

1. Data Preparation
   - Load and clean the dataset
   - Select relevant features
   - Handle categorical variables
   - Transform skewed features
   - Remove outliers
   - Scale numeric features

2. Risk Score Model Training
   - Split data into training and testing sets
   - Train LightGBM Regressor
   - Evaluate model performance using R2 score
   - Save trained model

3. Loan Approval Model Training
   - Use predicted risk scores as input
   - Train Random Forest Classifier
   - Evaluate classification performance
   - Save trained model

## Usage
1. Fill in the loan application form with required details
2. Submit the form for assessment
3. View comprehensive risk assessment results including:
   - Risk score visualization
   - Loan approval status
   - Approval probability
   - Custom recommendations

## Development Process
1. Data Analysis and Preprocessing
2. Model Development and Training
3. FastAPI Backend Implementation
4. Frontend UI/UX Design
5. Integration and Testing
6. Deployment and Optimization

## Future Enhancements
- Additional model features
- Enhanced visualization options
- API documentation
- User authentication
- Historical data tracking
- Batch processing capabilities
- Model retraining pipeline
- Extended recommendation system
