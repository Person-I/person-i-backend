# example/views.py
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Note, Conversation
from .serializers import NoteSerializer, ConversationSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiTypes
from rest_framework.parsers import MultiPartParser, FormParser
from .services.fal_service import FalService
import base64
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings
from urllib.parse import urljoin

from django.http import HttpResponse

def index(request):
    now = datetime.now()
    html = f'''
    <html>
        <body>
            <h1>Hello from Vercel!</h1>
            <p>The current time is { now }.</p>
        </body>
    </html>
    '''
    return HttpResponse(html)

class NotesView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='user_id', description='ID of the user', required=True, type=str)
        ],
        responses={200: NoteSerializer(many=True)},
        description='Get all notes for a specific user'
    )
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        notes = Note.objects.filter(user_id=user_id)
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=NoteSerializer,
        responses={201: NoteSerializer},
        description='Create a new note for a user'
    )
    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=user_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NoteDetailView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk, user_id):
        try:
            return Note.objects.get(pk=pk, user_id=user_id)
        except Note.DoesNotExist:
            return None

    def get(self, request, pk):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        note = self.get_object(pk, user_id)
        if not note:
            return Response({'error': 'Note not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = NoteSerializer(note)
        return Response(serializer.data)

    def put(self, request, pk):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        note = self.get_object(pk, user_id)
        if not note:
            return Response({'error': 'Note not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = NoteSerializer(note, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        note = self.get_object(pk, user_id)
        if not note:
            return Response({'error': 'Note not found'}, status=status.HTTP_404_NOT_FOUND)
        
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ConversationsView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='user_id', description='ID of the user', required=True, type=str)
        ],
        responses={200: ConversationSerializer(many=True)},
        description='Get all conversations for a specific user'
    )
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        conversations = Conversation.objects.filter(user_id=user_id)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=ConversationSerializer,
        responses={201: ConversationSerializer},
        description='Create a new conversation for a user'
    )
    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ConversationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=user_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConversationDetailView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk, user_id):
        try:
            return Conversation.objects.get(pk=pk, user_id=user_id)
        except Conversation.DoesNotExist:
            return None

    def get(self, request, pk):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        conversation = self.get_object(pk, user_id)
        if not conversation:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)

    def put(self, request, pk):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        conversation = self.get_object(pk, user_id)
        if not conversation:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ConversationSerializer(conversation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        conversation = self.get_object(pk, user_id)
        if not conversation:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DocumentAnalysisView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Document Analysis'],
        operation_id='analyze_document',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary'
                    }
                },
                'required': ['file']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'raw_text': {'type': 'string', 'description': 'Extracted text from the image'},
                    'summary_prompt': {'type': 'string', 'description': 'Generated prompt for summarizing user information'}
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        description='Upload an image for OCR analysis and user information extraction. Supports common image formats (JPG, PNG, etc.)'
    )
    def post(self, request):
        try:
            if 'file' not in request.FILES:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

            file = request.FILES['file']
            
            # Create media directory if it doesn't exist
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'tmp'), exist_ok=True)
            
            # Save file temporarily
            path = default_storage.save(f'tmp/{file.name}', ContentFile(file.read()))
            
            # Generate full URL including domain
            domain = request.build_absolute_uri('/').rstrip('/')
            file_url = f"{domain}{settings.MEDIA_URL}{path}"
            
            # Initialize FAL service and process image
            fal_service = FalService()
            result = fal_service.extract_text_from_image(file_url)
            
            # Clean up temporary file
            default_storage.delete(path)
            
            if 'error' in result:
                return Response({'error': result['error']}, status=status.HTTP_400_BAD_REQUEST)
                
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)