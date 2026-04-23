# 🚀 Customer Review Intelligence Platform

A production-grade AI-powered text analytics system that converts thousands of unstructured customer reviews into actionable business insights in real time.

> ⚡ Converts 10,000+ reviews into meaningful insights in under 1 second.

---

## 📌 Problem Statement

Modern e-commerce platforms generate massive volumes of customer reviews, but extracting meaningful insights is challenging due to:

* Unstructured text data
* Spam and duplicate reviews
* Mixed language (English + Hindi/Hinglish)
* Lack of actionable insights from raw sentiment scores

---

## 💡 Solution

This system processes raw reviews through an **end-to-end intelligent pipeline** and generates:

* Feature-level sentiment analysis
* Spam & duplicate detection
* Trend detection using anomaly analysis
* Actionable insights for decision-making

---

## 🧠 Key Features

* 🔍 Sentiment Analysis (feature-level)
* 🚫 Spam & Duplicate Detection
* 🌐 Multi-language support (English + Hindi/Hinglish)
* 📈 Trend Detection using Z-score anomaly detection
* ⚡ Real-time processing (<500ms for 100 reviews)
* 📊 Interactive Dashboard (React + Streamlit)
* 📦 Supports CSV, JSON, and raw text inputs

---

## 🏗️ System Architecture

### 🔄 Processing Pipeline

```
Raw Reviews
   ↓
Cleaning & Normalization
   ↓
Language Detection & Translation
   ↓
Duplicate Detection (TF-IDF)
   ↓
Spam Detection
   ↓
Feature Extraction
   ↓
Sentiment Analysis
   ↓
Trend Detection
   ↓
Insight Generation
   ↓
API + Dashboard Output
```

---

## ⚙️ Tech Stack

### Backend

* Python
* FastAPI
* scikit-learn (TF-IDF)
* langdetect
* Pydantic

### Frontend

* React (Vite)

### Dashboard

* Streamlit

---

## 📂 Project Structure

```
customer_review_intelligence/
│
├── app/                # Core backend logic
├── frontend/           # React frontend
├── dashboard/          # Streamlit dashboard
├── sample_data/        # Sample datasets
├── tests/              # Test cases
│
├── run_server.py       # Backend entry point
├── demo_run.py         # Demo execution
├── requirements.txt    # Python dependencies
├── start_dev.bat       # Run full system
```

---

## ▶️ How to Run the Project

### 🔹 1. Clone Repository

```bash
git clone https://github.com/your-username/customer_review_intelligence.git
cd customer_review_intelligence
```

---

### 🔹 2. Setup Backend

```bash
pip install -r requirements.txt
python run_server.py
```

---

### 🔹 3. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

---

### 🔹 4. Run Dashboard (Optional)

```bash
cd dashboard
python app.py
```

---

### 🔹 5. Quick Start (Windows)

```bash
start_dev.bat
```

---

## 📊 Sample Output

* 🔴 **CRITICAL**: Battery complaints increased by 28%
* 🟠 **HIGH**: Display brightness issues rising
* 🟢 **POSITIVE**: Camera and build quality appreciated

---

## 📈 Use Cases

* 🛒 E-commerce product analysis
* 📱 Electronics defect detection
* 🏭 FMCG supply chain monitoring
* 📞 Customer service improvement

---

## ⚠️ Limitations

* Limited sentiment lexicon (can be expanded)
* Fixed feature categories (domain-specific)
* Basic sarcasm detection
* Limited multilingual support

---

## 🚀 Future Improvements

* Integration with LLMs (OpenAI, etc.)
* Database storage for historical trends
* Authentication & multi-user support
* Advanced NLP models (BERT, spaCy)

---

## 🏁 Conclusion

This is a **deployable, production-ready system** that transforms raw customer feedback into actionable insights using interpretable AI techniques.

> Designed for real-world use — fast, scalable, and practical.

---

## 👩‍💻 Author

Anvita Naik

---

## 📜 License

This project is for academic and demonstration purposes.
