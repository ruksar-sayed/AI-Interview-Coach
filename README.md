# AI Interview Coach 🎯

An AI-powered web application that helps users analyze their resumes against a job description and prepare for interviews.

## 📌 Project Overview

AI Interview Coach helps job seekers understand how well their resumes match a target job role. It uses Google's Gemini AI to analyze resume content and generate useful career preparation insights.

## ✨ Features

- **Resume Upload:** Upload a resume in PDF format.
- **Resume Analysis:** Analyze resume content using AI.
- **Job Description Matching:** Compare resume details with a target job description.
- **AI-Powered Insights:** Generate analysis and recommendations using Google Gemini.
- **Interview Preparation:** Help users identify areas to improve before applying for a job.

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- Google Gen AI SDK
- PyPDF
- Python-dotenv

## 📂 Project Structure

```text
AI-Interview-Coach/
├── app.py
├── coach.py
├── llm.py
├── test_llm.py
├── text_summarizer.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/ruksar-sayed/AI-Interview-Coach.git
cd AI-Interview-Coach
```

### 2. Create a virtual environment

```bash
python -m venv coach_env
```

Activate it on Linux or GitHub Codespaces:

```bash
source coach_env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

Get your API key from [Google AI Studio](https://aistudio.google.com/apikey).

**Security:** Never commit your `.env` file or expose your API key publicly.

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal to use the application.

## 🎯 Objective

To simplify resume evaluation and job preparation through AI-powered resume analysis and personalized recommendations.

## 👩‍💻 Author

**Ruksar Sayed**

GitHub: [@ruksar-sayed](https://github.com/ruksar-sayed)

## 🚀 Future Enhancements

- More detailed resume scoring and skill-gap analysis
- Personalized interview questions
- Improved job-role recommendations
- Downloadable resume analysis reports