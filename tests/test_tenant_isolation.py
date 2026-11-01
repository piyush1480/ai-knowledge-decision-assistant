from django.test import TestCase,Client
from django.contrib.auth.models import User
from core.models import Organization
from knowledge.models import KnowledgeDocument,DocumentChunk
class TenantIsolationTests(TestCase):
 def test_retrieval_is_scoped_to_organization(self):
  from knowledge.services import retrieve_chunks
  a=Organization.objects.create(name='Org A',owner=User.objects.create_user('a'))
  b=Organization.objects.create(name='Org B',owner=User.objects.create_user('b'))
  da=KnowledgeDocument.objects.create(organization=a,original_name='a.pdf')
  db=KnowledgeDocument.objects.create(organization=b,original_name='b.pdf')
  DocumentChunk.objects.create(organization=a,document=da,page_number=1,content='Unique phrase for tenant alpha')
  DocumentChunk.objects.create(organization=b,document=db,page_number=1,content='Unique phrase for tenant beta')
  results=retrieve_chunks(a,'Unique phrase tenant beta')
  self.assertTrue(all(x.organization_id==a.id for x in results))
 def test_invalid_assistant_token_rejected(self):
  response=Client().post('/api/ask/',data={'token':'not-a-real-token','question':'hello'},content_type='application/json')
  self.assertEqual(response.status_code,404)
