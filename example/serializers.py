from rest_framework import serializers
from .models import Note, Conversation

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at'] 