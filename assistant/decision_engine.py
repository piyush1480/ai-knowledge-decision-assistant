"""Deterministic System-1 style decision models; no LLM is used for these calculations."""
import re

def classify_question(question):
 q=question.lower()
 if any(x in q for x in ['eligible','qualify','can i get','should i receive']): return 'eligibility'
 if any(x in q for x in ['compare','difference','versus',' vs ']): return 'comparison'
 if any(x in q for x in ['how do i','process','steps','procedure']): return 'procedure'
 return 'information'

def choice_decision(question, evidence):
 text=' '.join(evidence).lower()
 q=question.lower()
 labels=['merit scholarship','sports scholarship','need-based scholarship','academic policy','admission policy']
 hits=[label for label in labels if label in q or label in text]
 return {'type':'choice','selected':hits[0] if hits else 'not_determined','candidates':hits}

def boolean_eligibility_decisions(question, evidence):
 """Example scholarship checks. A rule is evaluated only when evidence explicitly contains its threshold."""
 text=' '.join(evidence).lower(); q=question.lower()
 decisions=[]
 gpa_match=re.search(r'(?:minimum|min\.?|at least)\s*(?:gpa\s*)?([0-4](?:\.\d+)?)',text)
 user_gpa=re.search(r'gpa\s*(?:of|:|=)?\s*([0-4](?:\.\d+)?)',q)
 if gpa_match and user_gpa:
  threshold=float(gpa_match.group(1)); actual=float(user_gpa.group(1))
  decisions.append({'type':'boolean','rule':'minimum_gpa','passed':actual>=threshold,'actual':actual,'required':threshold})
 year_match=re.search(r'(?:only|must be|eligible students are)\s*(?:in\s*)?(first|second|third|fourth|1st|2nd|3rd|4th)\s*year',text)
 year_user=re.search(r'(first|second|third|fourth|1st|2nd|3rd|4th)\s*year',q)
 if year_match and year_user:
  decisions.append({'type':'boolean','rule':'study_year','passed':year_user.group(1)==year_match.group(1)})
 # Explicit exclusion can be checked deterministically.
 if 'cannot hold' in text or 'not eligible if' in text:
  decisions.append({'type':'boolean','rule':'exclusion_check','passed':not any(x in q for x in ['already receiving','existing sports scholarship'])})
 return decisions

def score_decision(evidence, decisions):
 if not evidence: return {'type':'score','score':0,'label':'no_evidence'}
 score=min(1.0, len(evidence)/3 * 0.6 + (sum(1 for d in decisions if d.get('passed'))/max(len(decisions),1))*0.4)
 return {'type':'score','score':round(score,2),'label':'strong' if score>=0.7 else 'moderate' if score>=0.35 else 'weak'}

def run_decision_models(question, chunks):
 evidence=[c.content for c in chunks]
 category=classify_question(question)
 choice=choice_decision(question,evidence)
 booleans=boolean_eligibility_decisions(question,evidence) if category=='eligibility' else []
 score=score_decision(evidence,booleans)
 overall='insufficient_evidence'
 if booleans: overall='eligible' if all(d['passed'] for d in booleans) else 'not_eligible'
 return {'classification':category,'choice':choice,'boolean_checks':booleans,'score':score,'overall_decision':overall}
