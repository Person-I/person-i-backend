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

class CalendarEvent(models.Model):
    user_id = models.CharField(max_length=100)
    event_id = models.CharField(max_length=255)
    summary = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    organizer = models.CharField(max_length=255, null=True, blank=True)
    attendees = models.JSONField(default=list, blank=True)  # Store as JSON array of attendees
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)  # confirmed, tentative, cancelled
    meeting_link = models.URLField(max_length=500, null=True, blank=True)  # For virtual meetings

    class Meta:
        ordering = ['-start_time']
        unique_together = ['user_id', 'event_id']

class CalendarSubscription(models.Model):
    user_id = models.CharField(max_length=100)
    webcal_url = models.URLField(max_length=500)
    last_sync = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] 