from django.contrib.auth.models import AbstractUser
from django.db import models


class ApiUser(AbstractUser):
    self_description = models.TextField(blank=True)


class Scenario(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    author = models.ForeignKey(
        ApiUser,
        related_name='scenarios',
        on_delete=models.CASCADE
    )


class Step(models.Model):
    name = models.CharField(max_length=128)
    author = models.ForeignKey(
        ApiUser,
        related_name='steps',
        on_delete=models.CASCADE
    )
    message = models.TextField()
    scenario = models.ForeignKey(
        Scenario,
        related_name='steps',
        on_delete=models.CASCADE
    )
    transitions = models.JSONField(default=dict, blank=True)


class ChatBot(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    author = models.ForeignKey(
        ApiUser,
        related_name='chat_bots',
        on_delete=models.CASCADE
    )
    scenario = models.ForeignKey(
        Scenario,
        related_name='chat_bots',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
