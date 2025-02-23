# example/views.py
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Note, Conversation, CVAnalysis, CalendarEvent, CalendarSubscription
from .serializers import NoteSerializer, ConversationSerializer, CVAnalysisSerializer, CVAnalysisDetailSerializer, CalendarSubscriptionSerializer, CalendarSyncResponseSerializer, CalendarEventDetailSerializer
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
import requests
from icalendar import Calendar
from django.utils import timezone
from django.db import models

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
        description='Get all notes for a specific user and default system notes (IDs: 14-18)'
    )
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get both user's notes and system notes (IDs: 14-18)
        notes = Note.objects.filter(
            models.Q(user_id=user_id) | 
            models.Q(id__in=[14, 15, 16, 17, 18])
        ).distinct().order_by('-created_at')
        
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

class CVAnalysisDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='user_id', description='ID of the user', required=True, type=str)
        ],
        responses={200: CVAnalysisDetailSerializer},
        description='Get CV analysis for a specific user'
    )
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the most recent analysis for this user
            analysis = CVAnalysis.objects.filter(user_id=user_id).latest('created_at')
            serializer = CVAnalysisDetailSerializer(analysis)
            return Response(serializer.data)
        except CVAnalysis.DoesNotExist:
            return Response(
                {'error': 'No CV analysis found for this user'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class CalendarSyncView(APIView):
    permission_classes = [AllowAny]

    def sync_calendar_events(self, user_id, webcal_url):
        https_url = webcal_url.replace('webcal://', 'https://')
        response = requests.get(https_url)
        cal = Calendar.from_ical(response.content)
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        
        events_added = 0
        
        for component in cal.walk('VEVENT'):
            event_start = component.get('dtstart').dt
            
            if event_start < start_date or event_start > end_date:
                continue
                
            event_id = str(component.get('uid'))
            
            # Extract attendees information
            attendees = []
            for attendee in component.get('attendee', []):
                attendee_params = dict(attendee.params)
                attendee_data = {
                    'email': str(attendee).replace('mailto:', ''),
                    'name': attendee_params.get('CN', ''),
                    'role': attendee_params.get('ROLE', ''),
                    'status': attendee_params.get('PARTSTAT', '')
                }
                attendees.append(attendee_data)

            # Extract location and meeting link
            location = str(component.get('location', ''))
            meeting_link = ''
            
            # Look for virtual meeting links in description or location
            description = str(component.get('description', ''))
            for line in description.split('\n'):
                if any(link in line.lower() for link in ['meet.google.com', 'teams.microsoft.com', 'zoom.us']):
                    meeting_link = line.strip()
                    break

            # Create or update event with extended information
            event, created = CalendarEvent.objects.update_or_create(
                user_id=user_id,
                event_id=event_id,
                defaults={
                    'summary': str(component.get('summary', '')),
                    'description': description,
                    'start_time': component.get('dtstart').dt,
                    'end_time': component.get('dtend').dt if component.get('dtend') else component.get('dtstart').dt,
                    'location': location,
                    'organizer': str(component.get('organizer', '')).replace('mailto:', ''),
                    'attendees': attendees,
                    'status': str(component.get('status', 'confirmed')).lower(),
                    'meeting_link': meeting_link,
                    'notes': str(component.get('x-alt-desc', ''))  # Some calendars use this for rich text notes
                }
            )
            
            if created:
                events_added += 1
        
        return events_added

    @extend_schema(
        request=CalendarSubscriptionSerializer,
        responses={201: CalendarSyncResponseSerializer},
        description='Sync calendar events from webcal URL'
    )
    def post(self, request):
        user_id = request.data.get('user_id')
        webcal_url = request.data.get('webcal_url')

        if not user_id or not webcal_url:
            return Response(
                {'error': 'Both user_id and webcal_url are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if not webcal_url.startswith('webcal://'):
            return Response(
                {'error': 'URL must be a webcal:// URL'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Save or update subscription
            subscription, _ = CalendarSubscription.objects.update_or_create(
                user_id=user_id,
                defaults={'webcal_url': webcal_url}
            )

            # Sync events
            events_added = self.sync_calendar_events(user_id, webcal_url)

            return Response({
                'status': 'success',
                'events_added': events_added
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserCalendarEventsView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='user_id', description='ID of the user', required=True, type=str),
            OpenApiParameter(
                name='start_date',
                description='Start date for filtering events (YYYY-MM-DD)',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='end_date',
                description='End date for filtering events (YYYY-MM-DD)',
                required=False,
                type=str
            )
        ],
        responses={200: CalendarEventDetailSerializer(many=True)},
        description='Get all calendar events for a specific user with optional date filtering'
    )
    def get(self, request):
        user_id = request.query_params.get('user_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Start with base query
        events = CalendarEvent.objects.filter(user_id=user_id)

        # Apply date filters if provided
        try:
            if start_date:
                events = events.filter(start_time__date__gte=start_date)
            if end_date:
                events = events.filter(end_time__date__lte=end_date)
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Order by start time
        events = events.order_by('start_time')
        
        serializer = CalendarEventDetailSerializer(events, many=True)
        return Response(serializer.data)