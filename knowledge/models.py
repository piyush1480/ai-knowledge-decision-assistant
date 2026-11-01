from django.db import models
from core.models import Organization
class KnowledgeDocument(models.Model):
 organization=models.ForeignKey(Organization,on_delete=models.CASCADE,related_name='documents')
 file=models.FileField(upload_to='private_pdfs/')
 original_name=models.CharField(max_length=255)
 page_count=models.PositiveIntegerField(default=0)
 uploaded_at=models.DateTimeField(auto_now_add=True)
 def __str__(self): return self.original_name
class DocumentChunk(models.Model):
 organization=models.ForeignKey(Organization,on_delete=models.CASCADE,related_name='chunks')
 document=models.ForeignKey(KnowledgeDocument,on_delete=models.CASCADE,related_name='chunks')
 page_number=models.PositiveIntegerField()
 content=models.TextField()
 created_at=models.DateTimeField(auto_now_add=True)
 class Meta: indexes=[models.Index(fields=['organization','document'])]
