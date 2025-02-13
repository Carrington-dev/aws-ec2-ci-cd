from django.db import models
length  = 256

class Post(models.Model):
    title = models.CharField(max_length=length,)
    author = models.CharField(max_length=length,)
    content = models.TextField()
    date_updated = models.DateTimeField(auto_now=True)
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"

    def __unicode__(self):
        return f"{self.title}"
