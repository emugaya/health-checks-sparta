from django.db import models

class Blog(models.Model):
    title = models.CharField(max_length=200)
    category = models.TextField()
    story = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    user = models.TextField()

    def get_date(self):
        # Return only date without time
        return self.date_added.split(' ')[0]

    def __str__(self):
        return self.title