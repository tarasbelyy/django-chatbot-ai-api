from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router_1 = DefaultRouter()
router_1.register('users', views.ApiUserModelViewSet, basename='apiuser')
router_1.register('bots', views.ChatBotModelViewSet, basename='chatbot')
router_1.register('scenarios', views.ScenarioModelViewSet, basename='scenario')
router_1.register(
    r'scenarios/(?P<scenario_id>\d+)/steps',
    views.StepModelViewSet,
    basename='step'
)


urlpatterns = [
    path(r'v1/bots/<int:bot_id>/run/', views.BotRunView.as_view()),
    path('v1/', include(router_1.urls))
]
