from rest_framework import serializers
from .models import KnowledgeDocument
class DocumentSerializer(serializers.ModelSerializer):
 class Meta:
  model=KnowledgeDocument; fields=['id','original_name','page_count','uploaded_at']
