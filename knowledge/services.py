import fitz, re
from django.conf import settings
from .models import KnowledgeDocument, DocumentChunk
MAX_BYTES=10*1024*1024
MAX_PAGES=20
MAX_DOCS=10

def process_pdf(document):
 path=document.file.path
 pdf=fitz.open(path)
 if pdf.page_count > MAX_PAGES: raise ValueError('A PDF can contain at most 20 pages.')
 document.page_count=pdf.page_count; document.save(update_fields=['page_count'])
 chunks=[]
 for idx,page in enumerate(pdf):
  text=re.sub(r'\s+',' ',page.get_text()).strip()
  if not text: continue
  # Keep page metadata intact; split long pages into overlapping text windows.
  size=900; overlap=120; start=0
  while start < len(text):
   part=text[start:start+size]
   if part: chunks.append(DocumentChunk(organization=document.organization,document=document,page_number=idx+1,content=part))
   start += size-overlap
 DocumentChunk.objects.bulk_create(chunks)
 return len(chunks)

def validate_pdf_upload(org, uploaded):
 if uploaded.size > MAX_BYTES: raise ValueError('PDF size must not exceed 10 MB.')
 if uploaded.content_type not in ('application/pdf','application/x-pdf') and not uploaded.name.lower().endswith('.pdf'):
  raise ValueError('Only PDF files are allowed.')
 if org.documents.count() >= MAX_DOCS: raise ValueError('Maximum 10 PDFs are allowed per organization.')
 try:
  uploaded.seek(0); doc=fitz.open(stream=uploaded.read(),filetype='pdf'); uploaded.seek(0)
 except Exception: raise ValueError('The uploaded file is not a valid PDF.')
 if doc.page_count > MAX_PAGES: raise ValueError('A PDF can contain at most 20 pages.')
 return doc.page_count

def retrieve_chunks(org, question, limit=5):
 # Tenant filter is applied in the database query before relevance scoring.
 terms={t.lower() for t in re.findall(r'[a-zA-Z0-9]{3,}',question)}
 scored=[]
 for chunk in DocumentChunk.objects.filter(organization=org).select_related('document'):
  words=set(t.lower() for t in re.findall(r'[a-zA-Z0-9]{3,}',chunk.content))
  score=len(terms & words)/max(len(terms),1)
  if score: scored.append((score,chunk))
 scored.sort(key=lambda x:x[0],reverse=True)
 return [c for _,c in scored[:limit]]
