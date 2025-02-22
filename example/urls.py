# example/urls.py
from django.urls import path
from .views import NotesView, NoteDetailView, ConversationsView, ConversationDetailView, DocumentAnalysisView

urlpatterns = [
    path('notes/', NotesView.as_view(), name='notes'),
    path('notes/<int:pk>/', NoteDetailView.as_view(), name='note-detail'),
    path('conversations/', ConversationsView.as_view(), name='conversations'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('analyze-document/', DocumentAnalysisView.as_view(), name='analyze-document'),
]