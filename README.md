# OPINION.AI – AI-Powered Restaurant Review Analysis System

OPINION.AI is a Flask-based web application that allows restaurant customers to submit written reviews, then analyzes those reviews using machine learning to extract review categories and predict customer opinions.

The project is designed as a practical prototype that connects web development, databases, and applied machine learning in one system.

## Core Idea

Traditional review systems usually depend on star ratings and short comments. However, restaurant owners may not have enough time to read and analyze all written reviews manually.

OPINION.AI helps by:

- Collecting customer reviews
- Storing reviews in a SQLite database
- Analyzing review text using machine learning
- Classifying review categories such as food quality, cleanliness, staff behavior, and price
- Predicting the opinion as positive, neutral, or negative
- Displaying results in a simple dashboard for owner/admin users
- Exporting analysis results as a CSV file

## Features

- Public customer review submission page
- Star rating validation
- Review text validation
- Owner/Admin login system
- Password verification using hashed passwords
- Dashboard with review analysis summaries
- Category-based review analysis
- Opinion prediction for each detected category
- CSV export for analyzed review results
- SQLite database integration
- Scikit-learn model training and prediction

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Scikit-learn
- TF-IDF
- Logistic Regression
- One-vs-Rest Classification
- Joblib

## Machine Learning Approach

The machine learning part uses traditional NLP techniques:

- `TF-IDF` is used to convert review text into numerical features.
- `OneVsRestClassifier` with Logistic Regression is used for multi-label category classification.
- Logistic Regression is used to predict the opinion for each detected category.
- Joblib is used to save and load trained models.

The system predicts categories such as:

- Food Quality
- Cleanliness
- Staff Behavior
- Price

The opinion model predicts:

- Positive
- Neutral
- Negative

## Project Structure

```text
OPINION_AI/
├── app.py
├── db.py
├── ml_analysis.py
├── train_models.py
├── init_db.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── database/
│   └── schema.sql
│
├── models/
│   └── .gitkeep
│
├── templates/
│   ├── review.html
│   ├── login.html
│   └── dashboard.html
│
└── static/
    └── style.css
```

## How to Run

1. Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Train the machine learning models:

```bash
python train_models.py
```

4. Initialize the database:

```bash
python init_db.py
```

5. Run the Flask application:

```bash
python app.py
```

6. Open the application in your browser:

Customer Review Page:

```text
http://127.0.0.1:5000/
```

Login Page:

```text
http://127.0.0.1:5000/login
```

## Default Demo Users

These accounts are for local testing only:

| Role | Email | Password |
|---|---|---|
| Owner | owner@example.com | owner123 |
| Admin | admin@example.com | admin123 |

## Main Routes

| Route | Method | Description |
|---|---|---|
| `/` | GET | Customer review submission page |
| `/reviews` | POST | Submit a new customer review |
| `/login` | GET / POST | Owner/Admin login |
| `/logout` | POST | Logout |
| `/dashboard` | GET | Dashboard for analyzed reviews |
| `/analyze-queued` | POST | Analyze queued reviews |
| `/export` | GET | Export analysis results as CSV |

## Database Overview

The database contains four main tables:

- `users`: stores owner/admin login information
- `reviews`: stores submitted customer reviews
- `categories`: stores review category names
- `review_analysis`: stores machine learning analysis results for each review

The system uses foreign keys to connect reviews with their analysis results and categories.

> Note: Running `python init_db.py` resets the local database because the schema drops and recreates the tables.

## Limitations

This project is a learning-based prototype and is not production-ready.

Current limitations:

- The training dataset is small and controlled.
- The model mainly learns keyword-based patterns.
- The system does not fully understand complex natural language.
- The login system needs additional production security features such as CSRF protection and rate limiting.
- The ML analysis is performed directly during the request instead of using a background job.
- A larger real-world dataset is needed for reliable performance.

## Future Improvements

Possible future improvements include:

- Training the model on a larger real-world dataset
- Adding model evaluation metrics such as precision, recall, F1-score, and confusion matrix
- Improving the dashboard with charts and filtering
- Adding stronger role-based permissions for owner and admin users
- Adding CSRF protection and stronger session configuration
- Moving ML analysis to a background queue
- Using transformer-based NLP models for better language understanding

## Project Status

This project is a prototype built for learning and demonstration purposes. It shows how web development, databases, and machine learning can be integrated into a practical review analysis system.
