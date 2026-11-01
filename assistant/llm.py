import os

def generate_answer(question, chunks, decisions):
 evidence='\n\n'.join(f"[{c.document.original_name} — Page {c.page_number}] {c.content}" for c in chunks)
 if not evidence:
  return 'I could not find relevant information in this organization’s knowledge base. Please contact the organization for confirmation.'
 api_key=os.getenv('GEMINI_API_KEY')
 if not api_key:
  # Useful local fallback so the full flow can be tested without an API key.
  return 'I found the following relevant information in your organization’s documents:\n\n' + '\n\n'.join(c.content[:500] for c in chunks[:3]) + '\n\nDecision summary: ' + decisions['overall_decision']
 try:
  import google.generativeai as genai
  genai.configure(api_key=api_key)
  model=genai.GenerativeModel(os.getenv('GEMINI_MODEL','gemini-2.0-flash'))
  prompt=f"""Answer the user's question using ONLY the evidence below. If evidence does not support an answer, say so. Never invent facts. Cite every material claim using [filename — Page N]. Explain the structured decision result without revealing private reasoning.
Question: {question}
Structured decision output: {decisions}
Evidence:
{evidence}
"""
  response=model.generate_content(prompt)
  return response.text
 except Exception:
  return 'The AI answer service is temporarily unavailable. Retrieved evidence: ' + '\n'.join(c.content[:300] for c in chunks[:2])
