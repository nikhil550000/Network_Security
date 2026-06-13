# 🛡️ Network Security — Phishing Website Detection

An **end-to-end MLOps pipeline** for detecting phishing websites using machine learning. The system ingests network-level URL features from MongoDB, trains an **XGBoost** classifier, tracks experiments with **MLflow**, orchestrates retraining via **Apache Airflow**, and deploys through a fully automated **CI/CD pipeline** to **AWS (ECR + EC2)** using **GitHub Actions** and **Docker**.

---

## 📌 Table of Contents

- [Problem Statement](#-problem-statement)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Dataset](#-dataset)
- [ML Pipeline Stages](#-ml-pipeline-stages)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Docker](#-docker)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Airflow DAGs](#-airflow-dags)
- [MLflow Experiment Tracking](#-mlflow-experiment-tracking)
- [Screenshots](#-screenshots)
- [Future Improvements](#-future-improvements)
- [License](#-license)
- [Author](#-author)

---

## 🎯 Problem Statement

Phishing websites are a major cybersecurity threat, responsible for stealing personal information, credentials, and financial data from unsuspecting users. Traditional blacklist-based approaches fail to detect new (zero-day) phishing URLs.

This project builds a **machine learning system** that classifies URLs as **legitimate** or **phishing** based on 30 extracted network and URL-level features — providing a proactive, intelligent defense against phishing attacks.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          TRAINING PIPELINE                              │
│                                                                         │
│  MongoDB ──► Data Ingestion ──► Data Validation ──► Data Transformation │
│                                      │                      │           │
│                                Drift Report            KNN Imputer      │
│                                                             │           │
│              Model Pusher ◄── Model Evaluation ◄── Model Trainer        │
│                   │                  │                  (XGBoost)        │
│                   │             MLflow Tracking                         │
│                   ▼                                                     │
│              saved_models/                                              │
└────────────────────┬────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        PREDICTION SERVICE                               │
│                                                                         │
│           FastAPI ──► Upload CSV ──► Preprocessor + Model ──► Results   │
└─────────────────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DEPLOYMENT                                     │
│                                                                         │
│  GitHub Actions ──► Docker Build ──► AWS ECR ──► EC2 (Self-Hosted)      │
│                                                                         │
│  Airflow DAGs ──► Scheduled Retraining ──► S3 Artifact Sync             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.10 |
| **ML Model** | XGBoost (XGBClassifier) |
| **Data Processing** | Pandas, NumPy, Scikit-learn |
| **Imputation** | KNN Imputer (Scikit-learn Pipeline) |
| **Drift Detection** | Kolmogorov–Smirnov Test (SciPy) |
| **Experiment Tracking** | MLflow |
| **API Framework** | FastAPI + Uvicorn |
| **Database** | MongoDB Atlas |
| **Cloud Storage** | AWS S3 |
| **Orchestration** | Apache Airflow |
| **Containerization** | Docker + Docker Compose |
| **CI/CD** | GitHub Actions |
| **Deployment** | AWS ECR + EC2 (Self-Hosted Runner) |
| **Version Control** | DVC (Data Version Control) |
| **Serialization** | Pickle / dill |

---

## 📊 Dataset

The project uses the **UCI Phishing Websites Dataset** containing **11,055 URL instances** with **30 numerical features** and 1 target column.

### Features (30)

| Category | Features |
|---|---|
| **Address Bar** | `having_IP_Address`, `URL_Length`, `Shortining_Service`, `having_At_Symbol`, `double_slash_redirecting`, `Prefix_Suffix`, `having_Sub_Domain` |
| **SSL / Domain** | `SSLfinal_State`, `Domain_registeration_length`, `Favicon`, `port`, `HTTPS_token` |
| **Content** | `Request_URL`, `URL_of_Anchor`, `Links_in_tags`, `SFH`, `Submitting_to_email`, `Abnormal_URL`, `Redirect`, `on_mouseover`, `RightClick`, `popUpWidnow`, `Iframe` |
| **Domain** | `age_of_domain`, `DNSRecord`, `web_traffic`, `Page_Rank`, `Google_Index`, `Links_pointing_to_page`, `Statistical_report` |
| **Target** | `Result` — {1: Legitimate, -1: Phishing} |

> Feature values are encoded as `{-1, 0, 1}` representing {Phishing, Suspicious, Legitimate} for each attribute.

### 📚 Citation

> Tan, Choon Lin (2018), "Phishing Dataset for Machine Learning: Feature Evaluation", Mendeley Data, V1, doi: [10.17632/h3cgnj8hft.1](https://doi.org/10.17632/h3cgnj8hft.1)

---

## ⚙️ ML Pipeline Stages

The training pipeline is modular, with each stage producing versioned artifacts:

### 1️⃣ Data Ingestion
- Connects to **MongoDB Atlas** and exports the phishing data collection as a DataFrame.
- Handles missing value replacement (`"na"` → `NaN`).
- Splits data into **train (80%)** and **test (20%)** sets.
- Saves feature store and split files to the timestamped artifact directory.

### 2️⃣ Data Validation
- Validates the **number of columns** against a predefined YAML schema (`data_schema/schema.yaml`).
- Verifies all expected **numerical columns** are present.
- Performs **dataset drift detection** using the **Kolmogorov–Smirnov (KS) test** between train and test distributions.
- Generates a **drift report** (`report.yaml`) for each feature with p-values and drift status.

### 3️⃣ Data Transformation
- Applies **KNN Imputation** (K=3, uniform weights) via a Scikit-learn Pipeline to handle missing values.
- Converts target labels from `{-1, 1}` to `{0, 1}` for binary classification.
- Saves transformed numpy arrays (`.npy`) and the fitted preprocessor object (`.pkl`).

### 4️⃣ Model Training
- Trains an **XGBClassifier** on the transformed training data.
- Evaluates using **F1 Score**, **Precision**, and **Recall** on both train and test sets.
- Validates against a minimum expected accuracy threshold (`F1 ≥ 0.6`).
- Detects **overfitting/underfitting** by checking if the F1 score difference between train and test exceeds `0.05`.
- Bundles the preprocessor and model into a single `NetworkModel` object for seamless inference.

### 5️⃣ Model Evaluation
- Compares the newly trained model against the **best existing model** in `saved_models/`.
- Accepts the new model only if it improves F1 score by at least `0.02`.
- Logs metrics (**F1, Precision, Recall**) and the model artifact to **MLflow**.
- Generates an evaluation report saved as YAML.

### 6️⃣ Model Pusher
- Copies the accepted model to the `saved_models/` directory with a timestamp.
- Syncs artifacts and saved models to **AWS S3** for persistence.

---

## 🌐 API Endpoints

The prediction service is built with **FastAPI**:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Redirects to the Swagger UI (`/docs`) |
| `GET` | `/train` | Triggers the full training pipeline |
| `POST` | `/predict` | Upload a CSV file and get phishing predictions |

### Prediction Flow
1. Upload a CSV file containing the 30 URL features.
2. The API loads the latest model from `saved_models/`.
3. The preprocessor transforms the input, and the model predicts each URL.
4. Results are rendered as an HTML table with a `predicted_column` (0 = Legitimate, 1 = Phishing).

---

## 📁 Project Structure

```
Network_Security/
│
├── .github/
│   └── workflows/
│       └── main.yaml                 # CI/CD pipeline (GitHub Actions)
│
├── airflow/
│   └── dags/
│       ├── training_pipeline.py      # Scheduled retraining DAG
│       └── batch_prediction.py       # Batch prediction DAG
│
├── data_schema/
│   └── schema.yaml                   # Feature schema for validation
│
├── Network_Data/
│   └── NetworkData.csv               # Raw dataset (11,055 records × 31 cols)
│
├── networksecurity/                  # Main Python package
│   ├── cloud/
│   │   └── s3_synchronizer.py        # AWS S3 sync utility
│   ├── components/
│   │   ├── data_ingestion.py         # Stage 1: MongoDB → DataFrame → Train/Test
│   │   ├── data_validation.py        # Stage 2: Schema + Drift validation
│   │   ├── data_transformation.py    # Stage 3: KNN Imputation + Preprocessing
│   │   ├── model_trainer.py          # Stage 4: XGBoost training + evaluation
│   │   ├── model_evaluation.py       # Stage 5: Model comparison + MLflow
│   │   └── model_pusher.py           # Stage 6: Model deployment to saved_models
│   ├── constant/
│   │   └── training_pipeline/
│   │       └── __init__.py           # All pipeline constants & hyperparameters
│   ├── entity/
│   │   ├── config_entity.py          # Configuration dataclasses for each stage
│   │   └── artifact_entity.py        # Artifact dataclasses for each stage
│   ├── exception/
│   │   └── exception.py              # Custom exception with file & line tracking
│   ├── logger/
│   │   └── logger.py                 # Timestamped logging configuration
│   ├── pipeline/
│   │   └── training_pipeline.py      # Orchestrates all 6 stages end-to-end
│   ├── utils/
│   │   ├── main_utils/
│   │   │   └── utils.py              # YAML, NumPy, Pickle I/O utilities
│   │   └── ml_utils/
│   │       ├── metric/
│   │       │   └── classification_metric.py  # F1, Precision, Recall computation
│   │       └── model/
│   │           └── estimator.py      # NetworkModel wrapper + ModelResolver
│   ├── main.py                       # FastAPI application (Train + Predict)
│   └── Dockerfile                    # Docker image definition
│
├── docker-compose.yaml               # Container orchestration
├── get_data.py                       # Script to push CSV data to MongoDB
├── start_training.py                 # Standalone training pipeline trigger
├── start.sh                          # Airflow scheduler + webserver launcher
├── requirements.txt                  # Python dependencies
├── setup.py                          # Package configuration
├── .gitignore                        # Git ignore rules
└── README.md                         # You are here
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MongoDB Atlas account (or local MongoDB instance)
- AWS account (for S3, ECR, EC2)
- Docker & Docker Compose (optional, for containerized deployment)

### 1. Clone the Repository

```bash
git clone https://github.com/nikhil550000/Network_Security.git
cd Network_Security
```

### 2. Create a Virtual Environment

```bash
python -m venv nenv
source nenv/bin/activate        # Linux / macOS
nenv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
MONGO_DB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>
AWS_DEFAULT_REGION=us-east-1
BUCKET_NAME=<your-s3-bucket-name>
```

### 5. Push Data to MongoDB

```bash
python get_data.py
```

This reads `Network_Data/NetworkData.csv`, converts it to JSON records, and inserts them into the `phishing_data` collection in the `network_security_db` database on MongoDB Atlas.

### 6. Run the Training Pipeline

```bash
python start_training.py
```

This executes all 6 pipeline stages sequentially and saves the trained model to `saved_models/`.

### 7. Start the FastAPI Server

```bash
cd networksecurity
python main.py
```

The API will be available at **http://localhost:8000**. Visit **http://localhost:8000/docs** for the interactive Swagger UI.

---

## 🔐 Environment Variables

| Variable | Description |
|---|---|
| `MONGO_DB_URL` | MongoDB Atlas connection string |
| `AWS_ACCESS_KEY_ID` | AWS IAM access key for S3 and ECR |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |
| `AWS_DEFAULT_REGION` | AWS region (default: `us-east-1`) |
| `BUCKET_NAME` | S3 bucket for artifact and model storage |

> ⚠️ **Never commit `.env` to version control.** The `.gitignore` is configured to exclude it.

---

## 🐳 Docker

### Build the Docker Image

```bash
docker build -t network-security -f networksecurity/Dockerfile .
```

### Run with Docker Compose

```bash
docker-compose up -d
```

The application starts on **port 8080** with Airflow scheduler and webserver running inside the container.

### Docker Compose Configuration

```yaml
services:
  application:
    image: ${IMAGE_NAME}
    container_name: sensor
    ports:
      - "8080:8080"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
      - MONGO_DB_URL=${MONGO_DB_URL}
      - BUCKET_NAME=${BUCKET_NAME}
```

---

## 🔄 CI/CD Pipeline

The project uses **GitHub Actions** for a complete CI/CD workflow triggered on every push to the `master` branch.

### Pipeline Stages

```
Push to master
    │
    ▼
┌──────────────────────┐
│  Continuous           │
│  Integration          │
│  • Checkout code      │
│  • Lint repository    │
│  • Run unit tests     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Continuous           │
│  Delivery             │
│  • Configure AWS      │
│  • Login to ECR       │
│  • Build Docker image │
│  • Push to ECR        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Continuous           │
│  Deployment           │
│  • Pull latest image  │
│  • Stop old container │
│  • Run new container  │
│  • Image cleanup      │
└──────────────────────┘
```

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |
| `AWS_REGION` | AWS region |
| `AWS_ECR_LOGIN_URI` | ECR registry URI |
| `ECR_REPOSITORY_NAME` | ECR repository name |
| `MONGO_DB_URL` | MongoDB connection string |

---

## 🌬️ Airflow DAGs

Two Airflow DAGs automate the ML workflow:

### 1. Training Pipeline DAG (`network_training`)

- **Schedule**: Weekly (`@weekly`)
- **Tasks**:
  1. `train_pipeline` — Runs the full training pipeline
  2. `sync_data_to_s3` — Syncs artifacts and saved models to S3

### 2. Batch Prediction DAG (`network_prediction`)

- **Schedule**: Weekly (`@weekly`)
- **Tasks**:
  1. `download_file` — Downloads input files from S3
  2. `prediction` — Runs batch prediction on all input files
  3. `upload_prediction_files` — Uploads prediction results to S3

---

## 📈 MLflow Experiment Tracking

The model evaluation stage integrates with **MLflow** to track:

- **Metrics**: F1 Score, Precision, Recall
- **Artifacts**: Trained model (logged via `mlflow.sklearn.log_model`)

To view the MLflow UI locally:

```bash
mlflow ui
```

Navigate to **http://localhost:5000** to explore experiments, compare runs, and analyze model performance.

---

## 📸 Screenshots

> *Screenshots of the running application can be added here:*
>
> - Swagger UI (FastAPI `/docs`)
> - Prediction results table
> - MLflow experiment dashboard
> - Airflow DAG view
> - GitHub Actions workflow runs

---

## 🔮 Future Improvements

- [ ] Add hyperparameter tuning with GridSearchCV / Optuna
- [ ] Implement model monitoring for production drift detection
- [ ] Add unit and integration tests with pytest
- [ ] Set up Grafana + Prometheus for real-time monitoring
- [ ] Deploy to AWS ECS / EKS for auto-scaling
- [ ] Build a frontend dashboard for real-time URL analysis
- [ ] Add additional models (Random Forest, LightGBM) for ensemble predictions
- [ ] Implement feature importance visualization

---

## 📄 License

This project is open source and available under the [MIT License](LICENCE).

---

## 👤 Author

**Nikhil Sai**

- 📧 Email: [nikhilsai550000@gmail.com](mailto:nikhilsai550000@gmail.com)
- 🐙 GitHub: [@nikhil550000](https://github.com/nikhil550000)

---

<div align="center">

⭐ **If you found this project useful, please give it a star!** ⭐

</div>
