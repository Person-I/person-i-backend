from rest_framework import serializers

class HelloWorldSerializer(serializers.Serializer):
    message = serializers.CharField()
    status = serializers.CharField() 