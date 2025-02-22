# example/views.py
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import HelloWorldSerializer

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

class HelloWorldView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        data = {
            'message': 'Hello World!',
            'status': 'success'
        }
        serializer = HelloWorldSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)