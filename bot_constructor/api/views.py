from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.exceptions import (
    ValidationError,
    PermissionDenied,
    NotFound
)
from rest_framework.permissions import (
    BasePermission,
    SAFE_METHODS
)
from rest_framework import status

from . import bots
from .models import ApiUser, ChatBot, Scenario
from .serializers import (
    ApiUserSerializer,
    ChatBotSerializer,
    ScenarioSerializer,
    StepSerializer
)


class IsAuthorOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class IsUserOrRegisterRead(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user


class IsScenarioAuthorOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        scenario = get_object_or_404(
            Scenario,
            pk=view.kwargs.get('scenario_id')
        )
        return scenario.author == request.user


class ApiUserModelViewSet(ModelViewSet):
    queryset = ApiUser.objects.all()
    serializer_class = ApiUserSerializer
    permission_classes = (IsUserOrRegisterRead,)


class ChatBotModelViewSet(ModelViewSet):
    queryset = ChatBot.objects.all()
    serializer_class = ChatBotSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ScenarioModelViewSet(ModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class StepModelViewSet(ModelViewSet):
    serializer_class = StepSerializer
    permission_classes = (IsScenarioAuthorOrReadOnly,)

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


class BotRunView(APIView):
    def get(self, request, bot_id):
        if not request.user.is_authenticated:
            raise PermissionDenied
        chat_bot = get_object_or_404(ChatBot, pk=bot_id)
        try:
            data = bots.run_bots(request.user, chat_bot, 'start')
        except bots.BotNotRunnableError:
            raise ValidationError('Bot is not runnable')
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, bot_id):
        chat_bot = get_object_or_404(ChatBot, pk=bot_id)
        move = request.data.get('next')
        if move is None:
            raise ValidationError('Field "next" is required')
        detail = request.data.get('message')
        try:
            data = bots.run_bots(request.user, chat_bot, move, detail)
        except bots.BotNotExistsError:
            raise NotFound('Active chatbot not found')
        except bots.MoveNotValidError as e:
            raise ValidationError(f'Incorrect move. {e}')
        return Response(data, status=status.HTTP_200_OK)
