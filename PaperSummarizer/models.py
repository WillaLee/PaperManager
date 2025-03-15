from django.db import models

class Summary(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    latex_format = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Summary {self.id}"
    
    def transform_to_latex(self):
        """
        Convert plain text to a basic LaTeX formatted document.
        """
        latex_content = "\\documentclass{article}\n\\begin{document}\n"
        latex_content += self.content
        latex_content += "\n\\end{document}"
        return latex_content

    def get_or_update_latex_format(self):
        """
        Return the LaTeX formatted summary. If it doesn't exist, generate it,
        update the instance, and then return the formatted text.
        """
        if self.latex_format:
            return self.latex_format
        self.latex_format = self.transform_to_latex()
        self.save(update_fields=['latex_format'])
        return self.latex_format

class Label(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
class Paper(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    key_words = models.JSONField(default=list, null=True, blank=True)
    file = models.FileField(upload_to='papers/', null=True, blank=True)
    labels = models.ManyToManyField(Label, related_name='papers', blank=True)  # Many-to-many relationship with Label
    summary = models.OneToOneField(Summary, on_delete=models.CASCADE, null=True, blank=True)  # One-to-one relationship with Summary

    def __str__(self):
        return self.title
    
    # function to update summary
    def update_summary(self, summary):
        if self.summary:
            self.summary.content = summary
        else:
            new_summary = Summary.objects.create(content=summary)
            self.summary = new_summary