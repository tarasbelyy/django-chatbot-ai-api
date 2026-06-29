from django.contrib import admin

from .models import ApiUser, ChatBot, Scenario, Step


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'author', 'display_steps')
    list_select_related = ('author',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('steps')

    @admin.display(description='Steps')
    def display_steps(self, obj):
        return list(obj.steps.values_list('id', flat=True))


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'message', 'scenario__id', 'transitions')
    list_select_related = ('scenario',)


@admin.register(ChatBot)
class ChatBotAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'author', 'scenario__id')
    list_select_related = ('author', 'scenario')


@admin.register(ApiUser)
class ApiUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'self_description')
