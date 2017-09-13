from django.db import models
from django.utils import timezone

class Blog(models.Model):
    title = models.CharField(max_length=200)
    category = models.TextField()
    story = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    user = models.TextField()

    def get_date(self):
        # Return only date without time
        return str(self.date_added).split(' ')[0]

    def __str__(self):
        return self.title

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
