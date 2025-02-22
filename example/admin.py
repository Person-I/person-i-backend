from django.contrib import admin
from .models import Note, Conversation, CVAnalysis, CalendarEvent

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'content', 'created_at', 'updated_at')
    list_filter = ('user_id', 'created_at')
    search_fields = ('user_id', 'content')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'created_at', 'updated_at')
    list_filter = ('user_id', 'created_at')
    search_fields = ('user_id', 'content')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(CVAnalysis)
class CVAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'created_at')
    list_filter = ('user_id', 'created_at')
    search_fields = ('user_id',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'event_id', 'summary', 'start_time', 'end_time', 'location', 'status', 'organizer', 'meeting_link', 'created_at')
    list_filter = ('user_id', 'status', 'created_at', 'start_time')
    search_fields = ('user_id', 'event_id', 'summary', 'description', 'location', 'organizer', 'meeting_link')
    readonly_fields = ('created_at',)
    ordering = ('-start_time',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('user_id', 'event_id', 'summary', 'description')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'created_at')
        }),
        ('Location', {
            'fields': ('location', 'meeting_link')
        }),
        ('Participants', {
            'fields': ('organizer', 'attendees')
        }),
        ('Additional Information', {
            'fields': ('status', 'notes')
        }),
    )