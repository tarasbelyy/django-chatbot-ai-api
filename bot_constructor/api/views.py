from django.shortcuts import get_object_or_404
from rest_framework import viewsets


from .models import ApiUser, ChatBot, Scenario
from .serializers import (
    ApiUserSerializer,
    ChatBotSerializer,
    ScenarioSerializer,
    StepSerializer
)


class ApiUserModelViewSet(viewsets.ModelViewSet):
    queryset = ApiUser.objects.all()
    serializer_class = ApiUserSerializer


class ChatBotModelViewSet(viewsets.ModelViewSet):
    queryset = ChatBot.objects.all()
    serializer_class = ChatBotSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ScenarioModelViewSet(viewsets.ModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer


class StepModelViewSet(viewsets.ModelViewSet):
    serializer_class = StepSerializer

    def get_queryset(self):
        scenario = get_object_or_404(
            Scenario,
            pk=self.kwargs.get('scenario_id')
        )
        return scenario.steps.all()
    
    def perform_create(self, serializer):
        scenario = get_object_or_404(
            Scenario,
            pk=self.kwargs.get('scenario_id')
        )
        serializer.save(author=self.request.user, scenario=scenario)
