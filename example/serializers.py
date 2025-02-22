from rest_framework import serializers
from .models import Note, Conversation

class NoteSerializer(serializers.ModelSerializer):
    content = serializers.CharField(trim_whitespace=False)  # This will preserve exact string format
    
    class Meta:
        model = Note
        fields = ['id', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ConversationSerializer(serializers.ModelSerializer):
    content = serializers.CharField(trim_whitespace=False)  # Change to CharField to handle plain text
    
    class Meta:
        model = Conversation
        fields = ['id', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def to_internal_value(self, data):
        # If content is passed as string, strip any quotes
        if isinstance(data.get('content'), str):
            data = data.copy()
            data['content'] = data['content'].strip('"')
        return super().to_internal_value(data) 