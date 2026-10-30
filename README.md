# Krishika AI — Intelligent Crop Disease Detection & Agricultural Advisory System

**Academic Submission for CSE494: Intelligent NoSQL Databases (MongoDB)**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0%2B-47A248.svg)](https://www.mongodb.com/)
[![Vite+React](https://img.shields.io/badge/Frontend-Vite%20%2B%20React-61DAFB.svg)](https://vitejs.dev/)

---

## 1. Project Overview & Real-World Problem

In Indian agriculture, over 60% of rural livelihoods depend directly on crop yields. However, smallholder farmers lose 20% to 40% of their annual harvest to plant diseases caused by fungal, bacterial, and viral pathogens. Diagnosing plant diseases in remote fields typically requires traveling to a Krishi Vigyan Kendra (KVK) or relying on chemical shop vendors who frequently recommend inappropriate or expensive agrochemicals.

**Krishika AI** bridges this gap:
1. **Instant AI Diagnostics**: Leverages Deep Transfer Learning (VGG19 feature extraction + crop-specific Support Vector Machines) to diagnose diseases across **17 major Indian crops** from a smartphone photo.
2. **Actionable Remedies & Impact Profiles**: Provides specific, licensed chemical treatments, organic cultural controls, and economic risk assessments.
3. **NoSQL MongoDB Core**: Built from the ground up on MongoDB to handle semi-structured agricultural data, embedded sub-documents, dynamic schema validation, and multi-faceted aggregation analytics.

---

## 2. Project Independence & Protection of Original Work

> [!IMPORTANT]
> **This project is an independent submission located entirely within `crop_desies_detection/`.**
> - The original project files, trained models, scripts, and port configurations (Port 8000) remain 100% untouched.
> - This version uses its own independent database: `krishika_cse494` (preventing collision with `krishika_ai`).
> - The backend runs on Port `8001`, and the Vite React frontend runs on Port `5173`.

---

## 3. Technology Stack & Architecture

### 3.1 Machine Learning Pipeline (Reused & Isolated)
- **Feature Extractor**: VGG19 Convolutional Neural Network pretrained on ImageNet (extracts 25,088 high-dimensional visual features from $224 \times 224 \times 3$ leaf images).
- **Classifiers**: Crop-specialized Support Vector Machines (SVM) trained with RBF / Linear kernels for 17 crop categories.
- **Decision Engine**: Automated confidence scoring; predictions below $60\%$ confidence or on lower-accuracy crops (e.g. Brinjal) automatically trigger an agronomist verification advisory.

### 3.2 Backend
- **FastAPI** (Python async framework)
- **PyMongo & Motor** (MongoDB NoSQL driver connection pool)
- **Pydantic v2** (Strict schema validation and serialization)
- **JWT + Bcrypt** (Secure farmer authentication)

### 3.3 Frontend
- **React 19 + Vite 8**
- **Modern Agricultural Theme**: Dark slate background with emerald/mint glassmorphism, glowing badges, live leaf scanner animation, and an interactive **MongoDB BSON / Aggregation Inspector**.

---

## 4. MongoDB Database Design (CSE494 Focus)

The database `krishika_cse494` implements four core collections demonstrating key NoSQL patterns:

```
krishika_cse494
├── farmers       (Profiles, authentication, unique phone index, embedded stats)
├── detections    (Diagnosis records, compound indexes, embedded diagnosis sub-doc)
├── crops         (17 species, embedded growing_information sub-doc)
└── diseases      (Pathogen records, cross-collection $lookup join with crops)
```

### 4.1 Schema Strategy Rationale

| Pattern | Implemented In | Academic Rationale |
| :--- | :--- | :--- |
| **Embedded Sub-Document** | `detections.diagnosis` | **Zero-Join Read Performance & Immutability**: Stores symptoms, remedy, and severity in the same document. Ensures the exact advice given on a date is permanently preserved even if master disease remedies are updated later. |
| **Embedded Sub-Document** | `crops.growing_information` | **Tight Domain Cohesion**: Soil type, rainfall, and temperatures belong strictly to that crop species. |
| **Referenced Collection** | `crops` ↔ `diseases` | **Normalization & Many-to-Many**: Shared pathogen profiles referenced by `crop_id` and queried via `$lookup`. |
| **Referenced Collection** | `farmers` ↔ `detections` | **Prevents 16MB Limit Violation**: Avoids unbounded array anti-pattern by linking through `farmer_id`. |

### 4.2 Schema Validation (`$jsonSchema`)
Every collection is configured with strict MongoDB `$jsonSchema` rules enforcing types (`string`, `double`, `date`, `object`, `array`) and required fields.

### 4.3 Aggregation Pipelines Used
- **`$facet`**: Executes multi-pipeline aggregations in a single database pass (calculating total scans, average confidence, high-severity ratios, and top affected crops).
- **`$group` + `$dateToString`**: Aggregates temporal trends by year-month to detect seasonal disease outbreaks.
- **`$lookup`**: Performs dynamic left-outer joins between `crops` and `diseases` collections.

Detailed database documentation and query listings are in [`docs/mongodb_architecture.md`](file:///c:/Users/arjun/OneDrive/Desktop/Crop/crop_desies_detection/docs/mongodb_architecture.md) and [`docs/collection_relationships.md`](file:///c:/Users/arjun/OneDrive/Desktop/Crop/crop_desies_detection/docs/collection_relationships.md).

---

## 5. Installation & Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher & npm
- MongoDB Community Server or MongoDB Atlas cluster running on `localhost:27017`

### 5.1 Environment Configuration
In `crop_desies_detection/`, copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default configuration:
```ini
APP_NAME=Krishika AI — CSE494
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=krishika_cse494
CONFIDENCE_THRESHOLD=0.60
```

### 5.2 Backend Setup
```bash
# Navigate to project directory
cd crop_desies_detection

# Install Python requirements
pip install -r backend/requirements.txt

# Seed MongoDB with the 17 crops and complete disease catalog
python scripts/seed_db.py
```

### 5.3 Frontend Setup
```bash
cd frontend/krishika-frontend
npm install
```

---

## 6. How to Run the Application

### Step 1: Start MongoDB
Ensure MongoDB service is running locally (`mongod` or through MongoDB Compass / Windows Service).

### Step 2: Start the FastAPI Backend
```bash
# From crop_desies_detection directory:
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```
API Documentation will be available at: [http://localhost:8001/api/docs](http://localhost:8001/api/docs)

### Step 3: Start the Vite React Frontend
```bash
# In a separate terminal:
cd frontend/krishika-frontend
npm run dev
```
Open your browser at: [http://localhost:5173](http://localhost:5173)

---

## 7. Automated Testing & Verification

The project includes an automated test suite across ML inference, authentication, and MongoDB CRUD operations:

```bash
# Run all unit tests
pytest tests/ -v
```

### Test Suite Summary:
- `tests/test_auth.py`: Bcrypt password hashing, JWT token generation, and expiry validation.
- `tests/test_ml_pipeline.py`: VGG19 feature extraction dimensions ($25,088$), class mappings, and SVM predictor validation.
- `tests/test_db_operations.py`: MongoDB collection validation, compound index queries, `$group`, `$facet`, and `$lookup` aggregations.
- `tests/test_api.py`: FastAPI endpoints for registration, disease diagnosis, paginated scan history, and system health checks.

---

## 8. Directory Structure

```
crop_desies_detection/
├── .env.example                      # Configuration template (db: krishika_cse494)
├── .gitignore                         # Git exclusion rules
├── README.md                          # Academic submission documentation
├── backend/                           # FastAPI Backend
│   ├── main.py                        # Entry point (port 8001)
│   ├── config.py                      # Pydantic settings
│   ├── database.py                    # PyMongo / Motor database connection pool
│   ├── models/                        # MongoDB document data models
│   ├── schemas/                       # Pydantic request/response schemas
│   ├── services/                      # Auth, ML inference, and aggregation services
│   ├── routes/                        # API route handlers (/auth, /detect, /dashboard, etc.)
│   └── utils/                         # Image processing and validation helpers
├── docs/                              # Academic Architecture & DB Documentation
│   ├── mongodb_architecture.md        # Schema design, validation rules & pipelines
│   ├── architecture_diagram.md        # Full-stack Mermaid architecture diagrams
│   └── collection_relationships.md    # ERD and BSON document examples
├── frontend/krishika-frontend/        # Vite + React Modern Web Application
│   ├── src/
│   │   ├── api.js                     # API client with JWT handling
│   │   ├── index.css                  # Modern agricultural design system
│   │   ├── App.jsx                    # Root view manager
│   │   └── components/                # Diagnose, History, Dashboard, Encyclopedia, Inspector
│   └── package.json
├── ml/                                # Isolated Machine Learning Predictor
│   ├── predictor.py                   # VGG19 singleton + cached SVM inference
│   ├── class_mappings.py              # 17 crop disease classes
│   └── disease_db.py                  # Agronomic remedy definitions
├── scripts/
│   └── seed_db.py                     # MongoDB seeder with embedded growing data
├── tests/                             # Pytest test suite
├── trained_models/                    # Copy of SVM model weights (original preserved)
└── uploads/                           # Uploaded leaf images storage
```
