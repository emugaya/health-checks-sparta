from django.db import models
from django.utils import timezone

class FAQnAnswers(models.Model):
    """ Model for FAQs """
    question = models.CharField(max_length=200)
    answer = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def add_question(self):
        """ Admin uses this to add more QnAs """
        self.save()

    def __str__(self):
        return self.question

