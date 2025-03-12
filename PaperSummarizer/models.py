from django.db import models

class Summary(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    latex_format = models.TextField()

    def __str__(self):
        return f"Summary {self.id}"

class Label(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
class Paper(models.Model):
    title = models.CharField(max_length=255)
    key_words = models.JSONField(default=list)
    labels = models.ManyToManyField(Label, related_name='papers')  # Many-to-many relationship with Label
    summary = models.OneToOneField(Summary, on_delete=models.CASCADE)  # One-to-one relationship with Summary

    def __str__(self):
        return self.title