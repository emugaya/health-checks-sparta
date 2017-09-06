from django.db import models
from django.utils import timezone

# Create your models here.
class FAQnAnswers(models.Model):
    """ Model for FAQs """
    question = models.CharField(max_length=200)
    answer = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

