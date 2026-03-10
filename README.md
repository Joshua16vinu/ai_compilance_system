# Secure AI Policy Compliance & Gap Analysis System

A comprehensive, privacy-first solution for analyzing organizational policies against NIST SP 800-53 standards using a local AI architecture.

---

## Project Overview

This system provides an offline, secure environment for auditing cybersecurity policies. It uses a local Large Language Model (Mistral-7B) and vector embeddings to autonomously partition policy documents, map them to NIST controls, detect compliance gaps, and generate actionable remediation roadmaps.

**Key Capabilities:**
- **Offline Inference:** Zero data leakage; all processing happens locally.
- **Semantic Mapping:** Uses vector embeddings for precise control alignment.
- **Automated Partitioning:** Intelligently segments huge PDFs into security domains.
- **RAG-Based Remediation:** Generates specific policy revisions based on retrieved NIST standards.

---

## Technology Stack

### **Backend (Python)**
*Core logic, AI inference, and API handling.*

| Component | Library/Tool | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Framework** | **Flask** | Latest | Lightweight WSGI web application framework for the REST API. |
| **CORS** | **Flask-CORS** | Latest | Handles Cross-Origin Resource Sharing for frontend communication. |
| **LLM Inference** | **llama-cpp-python** | `0.2.82` | Runs quantized GGUF models (Mistral-7B) efficiently on CPU. |
| **Embeddings** | **Sentence-Transformers** | `5.2.2` | Generates 384-dimensional embeddings using `all-MiniLM-L6-v2`. |
| **Vector Database** | **ChromaDB** | `1.4.1` | Local vector store for indexing and retrieving NIST SP 800-53 controls. |
| **PDF Processing** | **PyPDF2** | Latest | Extracts text from standard PDF documents. |
| **OCR Handling** | **pdf2image** | `1.16.3` | Converts PDF pages to images for OCR when text extraction fails. |
| **OCR Engine** | **pytesseract** | `0.3.13` | Python wrapper for Google's Tesseract-OCR Engine. |
| **Data Handling** | **NumPy** | `2.4.2` | Efficient numerical operations for vector handling. |
| **ML Framework** | **PyTorch** | `2.10.0` | Underlying tensor library for transformer models. |
| **Utilities** | **python-dotenv** | `1.2.1` | Manages environment variables and configuration. |
| **Progress Bars** | **tqdm** | `4.67.3` | Displays progress for long-running batch operations. |

### **Frontend (TypeScript)**
*Interactive dashboard and user interface.*

| Component | Library/Tool | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Framework** | **Next.js** | `16.1.6` | React framework for server-side rendering and static site generation. |
| **Library** | **React** | `19.2.3` | Core library for building composable user interfaces. |
| **Styling** | **Tailwind CSS** | `4.0` | Utility-first CSS framework for rapid UI development. |
| **Icons** | **Lucide React** | `0.563.0` | Consistent, lightweight icon set. |
| **Animations** | **Framer Motion** | `12.33.0` | Production-ready motion library for React. |
| **HTTP Client** | **Axios** | `1.13.5` | Promise-based HTTP client for API requests. |
| **PDF Generation** | **jspdf** / **jspdf-autotable** | Latest | Generates downloadable PDF reports directly in the browser. |
| **Utilities** | **clsx** | `2.1.1` | Utility for constructing `className` strings conditionally. |
| **Utilities** | **tailwind-merge** | `3.4.0` | Merges Tailwind CSS classes without style conflicts. |
| **Linting** | **ESLint** | `9.0` | Pluggable linting utility for JavaScript and TypeScript. |

### **Infrastructure & Models**

| Component | Details |
| :--- | :--- |
| **LLM Model** | **Mistral-7B-Instruct-v0.3-Q5_K_M** (Quantized GGUF format for local inference) |
| **Embedding Model** | **sentence-transformers/all-MiniLM-L6-v2** (384 dimensions) |
| **Database** | **ChromaDB** (Persistent local parquet/sqlite storage) |
| **OCR Binary** | **Tesseract-OCR** (Must be installed on the host system) |

---

## Prerequisites

*   **Python:** 3.11+
*   **Node.js:** 18+ & npm
*   **Hardware:** Minimum 8GB RAM (16GB recommended for smooth LLM inference) on CPU. No GPU required.
*   **System Tools:** Tesseract-OCR installed and added to system PATH.

## Quick Start

### 1. Backend Setup

1.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### 2. Model Setup

Download the quantized LLM (Mistral-7B) to the `models/` directory:

```bash
python scripts/download_model.py
```

### 3. Database Initialization

Ingest the NIST SP 800-53 controls into the local ChromaDB vector store:

```bash
python backend/ingest/nist_ingest.py
```

### 4. Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  Start the development server:
    ```bash
    npm run dev
    ```
    *App runs at `http://localhost:3000`*

### 5. Backend Start

1.  Start the backend API (ensure venv is active):
    ```bash
    python backend/app.py
    ```
    *Server runs at `http://localhost:5000`*

## Verification & Testing

To verify the pipeline without the frontend, use the provided test scripts:

### Test Gap Analysis Pipeline
Runs the full PDF processing and gap analysis flow on a sample policy:
```bash
python scripts/test_gap_analysis.py
```
*Note: Ensure a valid PDF exists at `policies/policy1.pdf` or update the script path.*

### Quick System Check
Verifies that all modules (LLM, ChromaDB, Embeddings) are loading correctly:
```bash
python scripts/check_db.py
```

---

## Workflow

1.  **Upload:** User uploads a policy PDF via the frontend.
2.  **Partitioning (Backend):** 
    *   `PyPDF2` (or `pytesseract`) extracts raw text.
    *   Local LLM partitions text into domains (ISMS, Risk, etc.) & subdomains.
3.  **Selection (Frontend):** 
    *   Extracted domains are cached in `localStorage` for quick access.
    *   User selects a specific domain to analyze.
4.  **Analysis (Backend):**
    *   Text is converted to embeddings via `Sentence-Transformers`.
    *   `ChromaDB` retrieves relevant NIST controls.
    *   Local LLM compares policy vs. NIST controls to find gaps.
5.  **Results (Frontend):** Dashboard displays compliance score, gaps, and roadmap.
6.  **Report:** User downloads a detailed PDF report of the findings.

---

## The "Double Engine" Architecture

The core of our solution relies on a dual-process architecture (the "Double Engine"): **Autonomous Domain Partitioning** followed by **Semantic Control Mapping**.

### 1. Generating the NIST/CIS Knowledge Base

We transformed the raw NIST SP 800-53 and CIS implementation guidelines into a structured, machine-searchable JSON format (`backend/data/cis_policy_chunks_clean.json`).

**The Data Structure:**
Each entry in the JSON represents a specific policy chunk mapped to our 4-domain taxonomy:
```json
{
  "id": "uuid-v4-string",
  "text": "Full extracted text of the policy control...",
  "domain": "Data Privacy & Security",
  "subdomain": "Access-Control-Policy",
  "source_file": "CISecurity"
}
```

**The Mapping Strategy:**
We manually and algorithmically mapped thousands of controls into **4 Primary Domains** and **Unique Subdomains**:
1.  **ISMS (Information Security Management System)**
    *   *Subdomains:* Security Awareness, Incident Response, Personnel Security, etc.
2.  **Data Privacy & Security**
    *   *Subdomains:* Access Control, Encryption, Media Protection, Data Retention, etc.
3.  **Risk Management**
    *   *Subdomains:* Risk Assessment, Vulnerability Scanning, Audit Logging, etc.
4.  **Patch Management**
    *   *Subdomains:* Vulnerability Scanning, Secure Configuration, System Updates, etc.

This JSON acts as the "Ground Truth" for the RAG system.

### 2. Semantic Embedding & Storage (ChromaDB)

Once the JSON structure was finalized, we ingested it into **ChromaDB** using **Sentence-Transformers**.

*   **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2`
*   **Dimensionality:** 384-dimensional dense vectors.

**The Process:**
1.  **Ingestion Script:** `backend/ingest/nist_ingest.py` reads the JSON.
2.  **Vectorization:** Each `text` block is passed through the model to create a vector.
    *   *Example:* "Ensure users have unique IDs" → `[0.12, -0.45, 0.88, ...]`
3.  **Storage:** The vector + original metadata (domain, subdomain) is stored in the local ChromaDB instance (`backend/db/chroma`).

### 3. The "Double Engine" Execution Flow

When a user uploads a PDF, the system executes two distinct AI processes:

**Engine 1: Domain Partitioning (The Structure)**
*   **Input:** Raw unstructured text from the PDF.
*   **Action:** The local **Mistral-7B LLM** reads the text and logically segments it into the 4 primary domains.
*   **Output:** Structured JSON separating the user's messy policy into clean buckets (e.g., "This paragraph belongs to Risk Management").

**Engine 2: Semantic Retrieval & Traceability (The Analysis)**
*   **Input:** The "Risk Management" chunk from Engine 1.
*   **Action:**
    1.  The chunk is converted into a vector query.
    2.  **ChromaDB** searches its 384-dimensional space to find the *closest* NIST controls (stored in Step 2).
    3.  A "Similarity Score" (0 to 1) determines relevance.
*   **Output:** The LLM receives the user's policy segment + the *exact* matching NIST controls and performs the Gap Analysis.

This "Double Engine" ensures we don't just "chat" with the PDF—we structurally analyze it against a hard-coded regulatory framework.

### 4. Visual Execution Flow

```mermaid
graph TD
    subgraph "User Input"
        PDF[Upload Policy PDF]
    end

    subgraph "Engine 1: Domain Partitioning"
        PDF -->|Text Extraction| RAW[Raw Text]
        RAW -->|LLM Inference| PART[Mistral-7B Partitioning]
        PART -->|JSON| DOMAINS[Structured Domains]
        
        DOMAINS -->|Cache| LOCAL[(LocalStorage)]
        
        DOMAINS -- "ISMS" --> D1[Domain 1]
        DOMAINS -- "Data Privacy" --> D2[Domain 2]
        DOMAINS -- "Risk Mgmt" --> D3[Domain 3]
        DOMAINS -- "Patch Mgmt" --> D4[Domain 4]
    end

    subgraph "Engine 2: Iterative Gap Analysis (RAG)"
        LOCAL -->|Select| D2
        D2 -->|Vectorize| EMB[Embedding Model]
        
        DB[(ChromaDB NIST Store)] -.->|Retrieve Top-K| REL[Relevant NIST Controls]
        EMB -.->|Semantic Search| DB
        
        REL -->|Context| GAP[Gap Analysis LLM]
        D2 -->|Policy Query| GAP
        
        GAP -->|Analyze| CHECK{Gaps Found?}
        CHECK -- Yes --> REVISE[Generate Revised Policy]
        REVISE -->|Iterate| GAP
        CHECK -- No --> REPORT[Final Compliance Report]
    end

    subgraph "Output"
        REPORT -->|Display| UI[Frontend Dashboard]
        UI -->|Click| DL[Download PDF Report]
        UI -->|View| ROADMAP[Implementation Roadmap]
    end

    style PDF fill:#f9f,stroke:#333,stroke-width:2px,color:#000
    style PART fill:#bbf,stroke:#333,stroke-width:2px,color:#000
    style LOCAL fill:#f9f,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5,color:#000
    style GAP fill:#bbf,stroke:#333,stroke-width:2px,color:#000
    style DB fill:#bfb,stroke:#333,stroke-width:2px,color:#000
    style DL fill:#ffdfba,stroke:#333,stroke-width:2px,color:#000
    style CHECK fill:#ffecb3,stroke:#333,stroke-width:2px,color:#000
    style REVISE fill:#ffecb3,stroke:#333,stroke-width:2px,color:#000
```