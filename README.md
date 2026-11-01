# AI Knowledge & Decision Assistant

A multi-tenant Django MVP. Each organization has a private PDF knowledge base and a public assistant token. PDFs are limited to 10 per organization, 20 pages each, and 10 MB each. PDF text is split into page-aware chunks. Retrieval is tenant-scoped before relevance ranking. Gemini is used for grounded natural-language answer generation; deterministic Python decision models provide question classification, choice, boolean eligibility checks, and evidence scoring.

## Requirements
- Python 3.10+
- pip
- Optional Google Gemini API key
- SQLite is used by default. PostgreSQL can be configured with `.env`.

## Setup (Windows PowerShell)
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Add GEMINI_API_KEY to .env (optional; fallback mode works without it)
python manage.py makemigrations core knowledge assistant
python manage.py migrate
python manage.py runserver
```
Open http://127.0.0.1:8000/register/ and create an organization.

## Setup (macOS/Linux)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations core knowledge assistant
python manage.py migrate
python manage.py runserver
```

## Main flow
1. Register an organization and sign in.
2. Upload searchable PDFs from the dashboard.
3. The server validates size, page count, and document count, extracts text with PyMuPDF, and stores page-aware chunks.
4. The dashboard shows the unique public assistant URL and iframe snippet.
5. Visitors can ask questions without an account.
6. The API validates the assistant token, identifies the organization, retrieves only that organization's chunks, runs structured decisions, then generates a grounded answer and references.

## Architecture
```text
Visitor / iframe
      | POST /api/ask/ (assistant token + question)
      v
Token validation -> Organization resolution
      |
      v
Tenant-scoped retrieval (organization_id filter)
      |
      +--> Question classifier (System 1)
      +--> Choice decision
      +--> Boolean eligibility rules
      +--> Evidence score
      |
      v
Decision combination + retrieved page evidence
      |
      v
Gemini grounded response (or local fallback)
      |
      v
Answer + source document/page references + usage log
```

## API endpoints
- `POST /register/`, `POST /login/`, `GET /` dashboard, `GET /logout/`
- `GET /api/documents/` list own PDFs (authenticated)
- `POST /api/documents/` upload own PDF (authenticated; multipart field `file`)
- `DELETE /api/documents/<id>/` delete own PDF (authenticated)
- `GET /api/assistant-config/` get assistant URL and iframe code (authenticated)
- `POST /api/assistant-config/` regenerate public token (authenticated)
- `GET /api/usage/` usage counts (authenticated)
- `POST /api/ask/` public visitor question (`{"token":"...","question":"..."}`)

## Decision model design
- Classification: information, procedure, comparison, eligibility.
- Choice: identifies a relevant policy category from the question and retrieved evidence.
- Boolean: evaluates a GPA/year/exclusion rule only when both the rule and user value are explicitly present.
- Score: deterministic evidence-support score.
- Combination: eligibility is positive only when all evaluated checks pass; missing rules remain unevaluated rather than guessed.

## Security notes
- Admin APIs require a logged-in user.
- Every document list, delete, and retrieval query is scoped to the authenticated or token-resolved organization.
- Public tokens are random URL-safe values and can be regenerated.
- PDF files are not exposed through a public download route.
- The public assistant route does not grant dashboard access.
- Add HTTPS, rate limiting, malware scanning, secure private object storage, and stricter token rotation/audit controls before production.

## Tests
```bash
python manage.py test tests
```
The tenant isolation test ensures retrieval for Organization A never returns Organization B's chunks. Create at least two organizations and upload different PDFs for the assignment demo.

## Limitations / next improvements
- Retrieval uses lexical overlap, not vector embeddings. This keeps local setup lightweight; add pgvector or a managed vector database for semantic retrieval.
- The included eligibility rules are generic examples. For a real policy, implement explicit configurable rules from the uploaded policy content and add tests for each policy.
- Scanned PDFs require OCR, which is not included.
- For production, move processing to Celery, add quotas/rate limits, logging/monitoring, CSRF-safe frontend handling, and private cloud file storage.
