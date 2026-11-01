from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import KnowledgeDocument, DocumentChunk
from .services import validate_pdf_upload,process_pdf
from .serializers import DocumentSerializer
class DocumentListUploadView(APIView):
 permission_classes=[IsAuthenticated]
 def get(self,request): return Response(DocumentSerializer(KnowledgeDocument.objects.filter(organization=request.user.organization),many=True).data)
 def post(self,request):
  try:
   upload=request.FILES.get('file')
   if not upload: return Response({'error':'Choose a PDF file.'},status=400)
   validate_pdf_upload(request.user.organization,upload)
   doc=KnowledgeDocument.objects.create(organization=request.user.organization,file=upload,original_name=upload.name)
   process_pdf(doc)
   return Response(DocumentSerializer(doc).data,status=201)
  except ValueError as e: return Response({'error':str(e)},status=400)
  except Exception as e: return Response({'error':'PDF processing failed. Check that the PDF contains readable text.','detail':str(e)},status=400)
class DocumentDeleteView(APIView):
 permission_classes=[IsAuthenticated]
 def delete(self,request,pk):
  try: doc=KnowledgeDocument.objects.get(pk=pk,organization=request.user.organization)
  except KnowledgeDocument.DoesNotExist: return Response({'error':'Document not found.'},status=404)
  doc.file.delete(save=False); doc.delete(); return Response(status=204)
