# example/views.py
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Note, Conversation, CVAnalysis
from .serializers import NoteSerializer, ConversationSerializer, CVAnalysisSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiTypes

from django.http import HttpResponse
import os
from PIL import Image
import io
import PyPDF2
import pytesseract
from openai import OpenAI
from rest_framework.parsers import MultiPartParser
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()

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

class PDFAnalysisView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def extract_text_from_pdf(self, pdf_file):
        # Read PDF file
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        # Extract text from each page
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text

    def analyze_text_with_openai(self, text):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes resumes and CVs. When analyzing, provide a clean summary without any special characters or formatting artifacts. Focus on professional experience, skills, education, dates of employment and study, and achievements. Use clear, professional language."},
                {"role": "user", "content": f"Please analyze this CV and provide a clear summary and key points. Remove any special characters or formatting artifacts from the text:\n\n{text}"}
            ],
            max_tokens=500
        )
        # Remove newlines from the summary and replace multiple spaces with single space
        summary = response.choices[0].message.content.replace('\n', ' ').replace('  ', ' ')
        return summary

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {'type': 'string', 'format': 'binary'},
                    'user_id': {'type': 'string'}
                },
                'required': ['file', 'user_id']
            }
        },
        responses={201: CVAnalysisSerializer},
        description='Analyze a PDF file and use OpenAI to provide analysis',
        examples=[
            OpenApiExample(
                'Successful Response',
                value={
                    'id': 1,
                    'user_id': 'string'
                }
            )
        ]
    )
    def post(self, request):
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if 'user_id' not in request.data:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.data['user_id']
        pdf_file = request.FILES['file']
        
        if not pdf_file.name.endswith('.pdf'):
            return Response(
                {'error': 'File must be a PDF'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            extracted_text = self.extract_text_from_pdf(pdf_file)
            
            if not extracted_text.strip():
                return Response(
                    {'error': 'Could not extract text from PDF'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            analysis = self.analyze_text_with_openai(extracted_text)

            # Save to database
            cv_analysis = CVAnalysis.objects.create(
                user_id=user_id,
                summary=analysis,
                text=extracted_text
            )

            # Return only id and user_id
            return Response({
                'id': cv_analysis.id,
                'user_id': cv_analysis.user_id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            if hasattr(e, 'response'):
                return Response(
                    {'error': e.response.json()}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )