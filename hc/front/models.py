from django.db import models

class Blog(models.Model):
    title = models.CharField(max_length=200)
    category = models.TextField()
    story = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    user = models.TextField()


    def __str__(self):
        return self.title