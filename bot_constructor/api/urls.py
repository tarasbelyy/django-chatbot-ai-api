from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('users', views.ApiUserModelViewSet, basename='apiuser')
router.register('bots', views.ChatBotModelViewSet, basename='chatbot')
router.register('scenarios', views.ScenarioModelViewSet, basename='scenario')
router.register(
    r'scenarios/(?P<scenario_id>\d+)/steps',
    views.StepModelViewSet,
    basename='step'
)


urlpatterns = [
    path(r'bots/(?P<bot_id>\d+)/run', views.BotRunView.as_view())
]

urlpatterns.extend(router.urls)
