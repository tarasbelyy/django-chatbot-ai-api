from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS
)

from .bots import run_bots
from .models import ApiUser, ChatBot, Scenario
from .serializers import (
    ApiUserSerializer,
    ChatBotSerializer,
    ScenarioSerializer,
    StepSerializer
)


class IsAuthorOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
    

class IsUserOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user  


class ApiUserModelViewSet(ModelViewSet):
    queryset = ApiUser.objects.all()
    serializer_class = ApiUserSerializer
    permission_classes = [IsUserOrReadOnly]


class ChatBotModelViewSet(ModelViewSet):
    queryset = ChatBot.objects.all()
    serializer_class = ChatBotSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ScenarioModelViewSet(ModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)


class StepModelViewSet(ModelViewSet):
    serializer_class = StepSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)

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
        if scenario.author != self.request.user:
            raise PermissionDenied
        serializer.save(author=self.request.user, scenario=scenario)


class BotRunView(APIView):
    def get(self, request):
        return Response()
    
    def post(self, request):
        return Response()
    