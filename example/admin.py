from django.contrib import admin
from .models import Note, Conversation

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
