# ANUVAAD Backend

## Overview

ANUVAAD is a reusable multilingual translation backend designed for Indian languages. It provides Translation-as-a-Service (TaaS) capabilities through a unified API layer and supports automatic language detection, transliteration, code-mixed input handling, intelligent model routing, caching, and secure API access.

The backend was developed during an internship at CDAC Pune with the objective of creating a scalable multilingual translation platform that can be integrated with browser extensions, mobile applications, and future NLP services.

---

## Key Features

### Language Detection

The system automatically detects the source language using IndicLID models.

Supported detection models:

- IndicLID-FTN (Native Script Detection)
- IndicLID-FTR (Romanized Language Detection)
- IndicLID-BERT (Fallback Detection Model)

Examples:

| Input | Detected Language |
|---------|---------|
| আমি বাড়ি যাচ্ছি | Bengali |
| मैं घर जा रहा हूँ | Hindi |
| mein ghar ja raha hun | Hindi (Romanized) |

---

### Transliteration Support

Romanized Indian language text is automatically converted into native script before translation.

Example:

**Input**

```text
mein ghar ja raha hun
```

**Transliterated Output**

```text
मैं ghar जा रहा हूँ
```

**Translated Output**

```text
I am going home
```

---

### Code-Mixed Input Detection

The backend detects inputs containing both Latin and native Indic scripts.

Example:

```text
This project bahut acha hai
```

Such inputs are identified and routed through the appropriate processing pipeline before translation.

---

### Intelligent Model Routing

ANUVAAD supports multiple translation engines through a centralized routing layer.

Current translation engines:

- Sarvam AI
- IndicTrans2

Routing decisions are based on:

- Input type
- Translation requirements
- Model availability
- Fallback conditions

---

### Authentication

API access is secured using JWT (JSON Web Tokens).

Features:

- User authentication
- Token verification
- Protected API endpoints

---

### Redis-Based Caching

Translation responses are cached to improve performance.

Benefits:

- Faster repeated translations
- Reduced external API calls
- Lower latency
- Improved scalability

---

## Workflow

```text
Translation Request
        ↓
JWT Authentication
        ↓
Language Detection
        ↓
Romanized / Code-Mixed Detection
        ↓
Input Preprocessing
        ↓
Cache Lookup (Redis)
        ↓
Model Router
        ↓
Sarvam AI / IndicTrans2
        ↓
Store Result in Cache
        ↓
Translation Response
```

---

## Project Structure

```text
ANUVAAD/
│
├── benchmark/
│   ├── datasets/
│   ├── benchmark_runner.py
│   ├── language_detection_test.py
│   └── routing_test.py
│
├── models/
│   ├── base_adapter.py
│   ├── indictrans_adapter.py
│   └── llm_adapter.py
│
├── routers/
│   ├── detect.py
│   └── translate.py
│
├── services/
│   ├── analytics_service.py
│   ├── error_logger.py
│   ├── indic_lid_detector.py
│   ├── language_detector.py
│   ├── logger.py
│   ├── model_router.py
│   ├── summarizer.py
│   └── transliterator.py
│
├── auth.py
├── main.py
├── requirements.txt
└── README.md
```

---

## Technology Stack

| Component | Technology |
|------------|------------|
| Backend Framework | FastAPI |
| Programming Language | Python |
| Authentication | JWT |
| Caching | Redis |
| Translation Engines | Sarvam AI, IndicTrans2 |
| Language Detection | IndicLID |
| Deep Learning Framework | PyTorch |
| Romanized Language Detection | FastText |

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/trishaya/ANUVAAD.git
cd ANUVAAD
```

### 2. Create Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Environment File

Create a file named `.env`

Example:

```env
SARVAM_API_KEY=your_api_key
```

### 5. Install Redis

Verify installation:

```bash
redis-server
```

### 6. Download Language Detection Models

Create the following directory structure:

```text
models/
├── indiclid-bert/
├── indiclid-ftn/
└── indiclid-ftr/
```

### 7. Start the Application

```bash
uvicorn main:app --reload
```

Backend URL:

```text
http://localhost:8000
```

Swagger Documentation:

```text
http://localhost:8000/docs
```

---

## Required Models

The repository does not include large model files.

The following models must be downloaded separately.

### IndicLID-FTN

Used for native script language detection.

Directory:

```text
models/indiclid-ftn/
```

Expected file:

```text
model_baseline_roman.bin
```

---

### IndicLID-FTR

Used for romanized language detection.

Directory:

```text
models/indiclid-ftr/
```

Expected file:

```text
model_baseline_roman.bin
```

---

### IndicLID-BERT

Used as a fallback language detection model.

Directory:

```text
models/indiclid-bert/
```

Expected file:

```text
basline_nn_simple.pt
```

---

### Model Source

Download the required IndicLID models from:

https://github.com/AI4Bharat/IndicLID

After downloading, place the files in their respective directories as shown above.

---

## API Endpoints

| Method | Endpoint | Description |
|----------|----------|-------------|
| POST | /login | User Authentication |
| POST | /translate | Translation Service |
| POST | /summarize-meeting | Meeting Summarization |
| GET | /analytics/stats | Analytics Statistics |
| GET | /analytics/languages | Language Usage Statistics |
| GET | /analytics/models | Model Usage Statistics |
| GET | /analytics/daily | Daily Analytics |
| GET | /analytics/success | Success Metrics |
| GET | /errors | Error Logs |

---

## Future Scope

- Cloud deployment and scaling
- Additional Indian language support
- Speech-to-text integration
- Text-to-speech integration
- Automated Minutes of Meeting (MoM) generation
- Multilingual meeting summarization
- Additional NLP services
- Enhanced analytics dashboard

---

## Contributors

**Trisha Das**  
MCA, Tezpur University

Developed as part of the CDAC Pune Internship Project.
