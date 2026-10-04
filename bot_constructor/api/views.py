import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
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


async def bot_run_view(request, bot_id):
    if request.method == 'GET':
        user = await request.auser()
        try:
            chat_bot = await ChatBot.objects.select_related(
                'scenario'
            ).prefetch_related('scenario__steps').aget(pk=bot_id)
        except ChatBot.DoesNotExist:
            return JsonResponse({'error': 'Bot not found'}, status=404)
        try:
            data = await bots.run_bots(user, chat_bot, 'start')
        except bots.BotNotRunnableError:
            return JsonResponse({'error': 'Bot not runnable'}, status=422)
        return JsonResponse(data, status=200)
    elif request.method == 'POST':
        user = await request.auser()
        try:
            chat_bot = await ChatBot.objects.select_related(
                'scenario'
            ).prefetch_related('scenario__steps').aget(pk=bot_id)
        except ChatBot.DoesNotExist:
            return JsonResponse({'error': 'Bot not found'}, status=404)
        request_data = json.loads(request.body)
        move = request_data.get('next')
        if move is None:
            return JsonResponse({'error': 'Field "next" is required'}, status=422)
        user_content = request_data.get('message')
        try:
            data = await bots.run_bots(user, chat_bot, move, user_content)
        except bots.BotNotExistsError:
            return JsonResponse({'error': 'Active bot not found'}, status=404)
        except bots.MoveNotValidError as e:
            return JsonResponse({'error': f'Incorrect move. {e}'}, status=400)
        return Response(data, status=200)
    return JsonResponse({'error': 'Request method not supported'}, status=405)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def custom_500_error_view(request):
    message = {'detail': 'Internal server error'}
    return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
