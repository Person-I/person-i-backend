# example/urls.py
from django.urls import path
from .views import (
    NotesView, NoteDetailView, ConversationsView, ConversationDetailView,
    PDFAnalysisView, CVAnalysisDetailView, CalendarSyncView,
    UserCalendarEventsView
)

urlpatterns = [
    path('notes/', NotesView.as_view(), name='notes'),
    path('notes/<int:pk>/', NoteDetailView.as_view(), name='note-detail'),
    path('conversations/', ConversationsView.as_view(), name='conversations'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('analyze-pdf/', PDFAnalysisView.as_view(), name='analyze-pdf'),
    path('cv-analysis/', CVAnalysisDetailView.as_view(), name='cv-analysis'),
    path('calendar-sync/', CalendarSyncView.as_view(), name='calendar-sync'),
    path('calendar-events/', UserCalendarEventsView.as_view(), name='user-calendar-events'),
]