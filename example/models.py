from django.db import models

class Note(models.Model):
    user_id = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class Conversation(models.Model):
    user_id = models.CharField(max_length=100)
    content = models.TextField()  # Changed from JSONField to TextField
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class CVAnalysis(models.Model):
    user_id = models.CharField(max_length=100)
    summary = models.TextField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] 