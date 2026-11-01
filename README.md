# AI Knowledge & Decision Assistant

A multi-tenant AI-powered knowledge and decision assistant built with **Python, Django, Django REST Framework, and Google Gemini**. Organizations can register, upload PDF documents to a private knowledge base, and provide visitors with a public assistant that answers questions using organization-specific document content.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [AI and Decision-Making Architecture](#ai-and-decision-making-architecture)
- [Tenant Isolation and Security](#tenant-isolation-and-security)
- [Project Structure](#project-structure)
- [PDF Processing and Retrieval](#pdf-processing-and-retrieval)
- [API Endpoints](#api-endpoints)
- [Installation and Setup](#installation-and-setup)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [Sample Questions for Testing](#sample-questions-for-testing)
- [Current Limitations](#current-limitations)
- [Future Improvements](#future-improvements)

## Overview

The AI Knowledge & Decision Assistant enables organizations to create their own AI-powered assistants using their internal PDF documents.

Each organization has an isolated knowledge base and a unique public assistant token. Visitors can interact with the assistant without creating an account. The system retrieves relevant information from the organization's uploaded documents, evaluates applicable decision checks, and generates a response with document and page references.

The application is designed around three principles:

1. **Multi-tenancy:** Each organization can access only its own documents and knowledge.
2. **Grounded responses:** Answers are based on retrieved document content rather than unsupported assumptions.
3. **Structured decision-making:** Deterministic Python logic handles supported decision checks separately from natural-language response generation.

## Key Features

### Organization Management
- Organization registration and login.
- Organization-specific dashboard.
- Unique public assistant token for each organization.
- Ability to regenerate the assistant token.

### PDF Knowledge Management
- Upload PDF documents through the dashboard.
- Maximum 10 documents per organization.
- Maximum 20 pages per PDF.
- Maximum file size of 10 MB per PDF.
- Extract PDF text using PyMuPDF.
- Store extracted text as page-aware chunks.
- Keep document and organization relationships for tenant-scoped retrieval.

### Public AI Assistant
- Public assistant URL for visitors.
- Visitors can ask questions without logging in.
- Assistant token validation.
- Organization-specific knowledge retrieval.
- Answers generated using Google Gemini when configured.
- Local fallback response generation when Gemini is unavailable.
- Source document and page references in responses.

### Decision Engine
The Python decision engine supports structured checks such as:
- Question classification.
- Choice/category identification.
- Boolean eligibility checks.
- Evidence-support scoring.
- Combining evaluated decision results.

### Usage Tracking
- Record visitor questions.
- Associate question logs with the relevant organization.
- Store answer status and decision information.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Django |
| API | Django REST Framework |
| Database | SQLite by default |
| Optional database configuration | PostgreSQL |
| PDF processing | PyMuPDF |
| AI response generation | Google Gemini API |
| Decision logic | Python |
| Frontend | Django Templates, HTML, CSS, JavaScript |
| Version control | Git and GitHub |

## System Architecture

The application follows a tenant-aware request and retrieval flow.

```text
             Organization
                  |
          Register / Login
                  |
                  v
          Organization Dashboard
                  |
             Upload PDFs
                  |
                  v
          PDF Text Extraction
                  |
             Text Chunking
                  |
                  v
          Organization Knowledge Base
                  |
                  |
        Public Assistant URL / Token
                  |
                  v
             Visitor Question
                  |
                  v
           Assistant Token Check
                  |
                  v
        Resolve Organization Context
                  |
                  v
       Tenant-Scoped Knowledge Retrieval
                  |
          +-------+--------+
          |                |
          v                v
    Question Analysis   Relevant Chunks
          |                |
          v                v
     Python Decision Engine
          |
          v
   Decision Result Combination
          |
          v
    Gemini / Fallback Generator
          |
          v
   Answer + Source References
```

## AI and Decision-Making Architecture

The application separates structured decision logic from natural-language answer generation.

### 1. Question Analysis

The incoming question is analyzed and classified into supported categories, such as:

- Information
- Procedure
- Comparison
- Eligibility

### 2. Knowledge Retrieval

The system retrieves relevant text chunks belonging to the organization identified by the assistant token.

The current implementation uses lexical keyword-overlap matching to rank relevant chunks.

### 3. Structured Decision Engine

The decision engine performs supported checks using Python logic:

| Decision type | Purpose |
|---|---|
| Classification | Categorizes the visitor's question |
| Choice | Identifies a relevant category from the question and retrieved evidence |
| Boolean | Evaluates supported eligibility conditions when the required values and rules are present |
| Score | Calculates an evidence-support score |

The decision results are combined before the final response is generated.

### 4. Natural-Language Answer Generation

Google Gemini is used to generate a readable answer using the retrieved document evidence and decision results.

If Gemini is not configured or unavailable, the application can use its local fallback behavior.

### 5. Grounding and References

The assistant uses retrieved document content as its evidence and includes available source document and page references.

If the knowledge base does not contain relevant information, the assistant should avoid presenting unsupported information as fact.

## Tenant Isolation and Security

Tenant isolation is a core part of the application.

The following measures are implemented:

- Each organization is associated with an authenticated owner.
- Each organization receives a unique, randomly generated assistant token.
- Public assistant requests validate the token before resolving the organization.
- Document listing and deletion are scoped to the authenticated organization's data.
- Knowledge retrieval is filtered by organization.
- Question logs are associated with the organization.
- Public assistant access does not provide dashboard access.
- PDF files are not exposed through a public document-download API.

### Security Considerations Before Production

For production deployment, additional controls should be added:

- HTTPS and secure cookie configuration.
- API rate limiting and request throttling.
- Malware scanning for uploaded documents.
- Secure private object storage.
- Audit logging and monitoring.
- Stronger token rotation and revocation controls.
- Production-ready secret management.
- Appropriate cross-origin and iframe security configuration.

## Project Structure

```text
ai_knowledge_assistant/
│
├── assistant/
│   ├── admin.py
│   ├── decision_engine.py
│   ├── llm.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py
│
├── core/
│   ├── static/
│   ├── templates/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── knowledge/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── urls.py
│   └── views.py
│
├── tests/
│   ├── __init__.py
│   └── test_tenant_isolation.py
│
├── .env.example
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

## PDF Processing and Retrieval

The document processing flow is:

1. A logged-in organization uploads a PDF.
2. The backend validates the file type, file size, page count, and organization document limit.
3. PyMuPDF extracts text from the PDF.
4. Extracted text is divided into page-aware chunks.
5. Each chunk is stored with its document and organization relationship.
6. When a visitor asks a question, retrieval searches only the organization associated with the validated assistant token.
7. Relevant chunks are passed to the decision engine and response generator.

**Retrieval implementation:** The current version uses keyword-overlap retrieval. It does not currently implement vector embeddings or semantic vector search.

## API Endpoints

All API paths below are relative to the local application base URL.

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| GET, POST | `/register/` | Organization registration | Public |
| GET, POST | `/login/` | User login | Public |
| GET | `/` | Organization dashboard | Authenticated |
| GET | `/logout/` | Logout | Authenticated |
| GET | `/assistant/<token>/` | Public assistant page | Public |
| GET | `/api/documents/` | List organization documents | Authenticated |
| POST | `/api/documents/` | Upload a PDF | Authenticated |
| DELETE | `/api/documents/<id>/` | Delete a document | Authenticated |
| GET | `/api/assistant-config/` | Retrieve assistant configuration | Authenticated |
| POST | `/api/assistant-config/` | Regenerate assistant token | Authenticated |
| GET | `/api/usage/` | Retrieve usage counts | Authenticated |
| POST | `/api/ask/` | Submit a visitor question | Public token required |

### Public Question API

**Endpoint:** `POST /api/ask/`

Example request:

```json
{
  "token": "YOUR_PUBLIC_ASSISTANT_TOKEN",
  "question": "What is the eligibility criteria?"
}
```

The request is associated with the organization identified by the supplied token.

The response structure should be checked against the current API implementation before using it as an integration contract.

### PDF Upload API

**Endpoint:** `POST /api/documents/`

Send a multipart/form-data request with the PDF in the `file` field.

### Document Deletion API

**Endpoint:** `DELETE /api/documents/<id>/`

The document is deleted only within the authenticated organization's scope.

## Installation and Setup

### Prerequisites

- Python 3.10 or higher.
- pip.
- Git.
- VS Code or another Python IDE.
- Google Gemini API key (optional for local fallback mode).

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-knowledge-decision-assistant.git
cd ai-knowledge-decision-assistant
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a Virtual Environment

**Windows PowerShell:**

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

Update `.env` with your local configuration.

### 5. Configure Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create an Administrator Account (Optional)

```bash
python manage.py createsuperuser
```

### 7. Start the Development Server

```bash
python manage.py runserver
```

Open the application:

- Registration: http://127.0.0.1:8000/register/
- Login: http://127.0.0.1:8000/login/
- Dashboard: http://127.0.0.1:8000/
- Django Admin: http://127.0.0.1:8000/admin/

## Environment Variables

The application reads configuration from a local `.env` file.

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Enables or disables Django debug mode |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames |
| `GEMINI_API_KEY` | Optional Google Gemini API key |
| `GEMINI_MODEL` | Gemini model name |
| `DB_NAME` | Optional PostgreSQL database name |
| `DB_USER` | Optional PostgreSQL username |
| `DB_PASSWORD` | Optional PostgreSQL password |
| `DB_HOST` | Optional PostgreSQL host |
| `DB_PORT` | Optional PostgreSQL port |

The default local database is SQLite. PostgreSQL configuration is available in the settings, but you must install a compatible PostgreSQL driver before using it.

**Never commit your actual `.env` file, API keys, passwords, or Django production secret key to GitHub.**

## Running Tests

Run the tenant-isolation test:

```bash
python manage.py test tests
```

The included test checks that retrieval for one organization does not return chunks belonging to another organization.

Additional tests should be added for:

- Invalid PDF uploads.
- File-size and page-count limits.
- Organization document limits.
- Invalid assistant tokens.
- Empty questions.
- Questions with no relevant document evidence.
- Gemini API failures.
- Decision engine behavior.
- Unauthorized document deletion.

## Sample Questions for Testing

Use questions based on the actual content of your uploaded PDFs.

Examples:

1. What is the main purpose of this policy?
2. What documents are required for application?
3. What is the eligibility criteria?
4. What is the minimum required score?
5. What is the application deadline?
6. What is the procedure for submitting an application?
7. What happens if an applicant does not meet the eligibility criteria?
8. What are the key differences between the two options?
9. Can an applicant satisfy both condition A and condition B?
10. Is there any information about this topic in the uploaded documents?

For a multi-tenant test, create two organizations and upload different documents to each. Ask each assistant questions about both knowledge bases and verify that it cannot retrieve another organization's private information.

## Current Limitations

This is an MVP intended for local demonstration and further development.

- Retrieval is based on lexical keyword overlap rather than vector embeddings.
- Scanned PDFs requiring OCR are not supported.
- The included decision rules are generic examples and need to be configured for real organization policies.
- Background document processing and distributed task queues are not included.
- Production-grade rate limiting, malware scanning, and monitoring need to be added.
- PostgreSQL requires a compatible database driver and database configuration.

## Future Improvements

- Semantic retrieval using embeddings and pgvector.
- Hybrid retrieval combining keyword and vector search.
- OCR support for scanned PDF documents.
- Configurable decision rules for each organization.
- Background PDF processing using Celery and Redis.
- API rate limiting and usage quotas.
- Improved observability and audit logging.
- Cloud deployment using AWS.
- Automated integration and security testing.

## Author

**Your Name**

GitHub: https://github.com/piyush1480

---

## License

This project was developed as a technical assignment and demonstration of a multi-tenant AI knowledge and decision assistant.