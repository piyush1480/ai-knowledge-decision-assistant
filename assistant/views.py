from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from core.models import Organization
from knowledge.services import retrieve_chunks
from .decision_engine import run_decision_models
from .llm import generate_answer
from .models import QuestionLog
class AskAssistantView(APIView):
 permission_classes=[AllowAny]
 authentication_classes=[]
 def post(self,request):
  token=request.data.get('token','').strip(); question=request.data.get('question','').strip()
  if not token: return Response({'error':'Assistant token is required.'},status=400)
  if not question: return Response({'error':'Question cannot be empty.'},status=400)
  try: org=Organization.objects.get(assistant_token=token)
  except Organization.DoesNotExist: return Response({'error':'Invalid assistant token.'},status=404)
  chunks=retrieve_chunks(org,question)
  decisions=run_decision_models(question,chunks)
  answer=generate_answer(question,chunks,decisions)
  refs=[{'document':c.document.original_name,'page':c.page_number} for c in chunks]
  log=QuestionLog.objects.create(organization=org,question=question,answered=bool(chunks),decision_data=decisions)
  return Response({'answer':answer,'references':refs,'decisions':decisions,'answered':log.answered})
class AssistantConfigView(APIView):
 permission_classes=[IsAuthenticated]
 def get(self,request):
  org=request.user.organization
  return Response({'assistant_url':request.build_absolute_uri(f'/assistant/{org.assistant_token}/'),'token':org.assistant_token,'embed_code':f'<iframe src="{request.build_absolute_uri(f"/assistant/{org.assistant_token}/")}" width="400" height="600"></iframe>'})
 def post(self,request):
  org=request.user.organization; org.regenerate_token()
  return Response({'token':org.assistant_token,'assistant_url':request.build_absolute_uri(f'/assistant/{org.assistant_token}/')})
class UsageView(APIView):
 permission_classes=[IsAuthenticated]
 def get(self,request):
  qs=request.user.organization.questions.all()
  return Response({'questions_total':qs.count(),'answered':qs.filter(answered=True).count(),'unanswered':qs.filter(answered=False).count()})
