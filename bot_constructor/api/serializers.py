from rest_framework import serializers, validators

from .models import ApiUser, ChatBot, Scenario, Step


class ApiUserSerializer(serializers.Serializer):
    username = serializers.SlugField(max_length=128, validators=[
        validators.UniqueValidator(ApiUser.objects.all())
    ])
    password = serializers.CharField(
        min_length=6,
        max_length=20,
        write_only=True
    )
    self_description = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        if self_description := validated_data.get('self_description'):
            instance.self_description = self_description
            instance.save(update_fields=['self_description'])

        if password := validated_data.get('password'):
            instance.set_password(password)
            instance.save(update_fields=['password'])
        return instance

    def create(self, validated_data):
        user = ApiUser.objects.create(
            self_description=validated_data['self_description'],
            username=validated_data['username'],
        )

        user.set_password(validated_data['password'])
        user.save(update_fields=['password'])
        return user


class ChatBotSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = ChatBot
        fields = '__all__'


class StepSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Step
        fields = '__all__'
        read_only_fields = ('scenario',)


class ScenarioSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    steps = StepSerializer(many=True, required=False)

    class Meta:
        model = Scenario
        fields = '__all__'
    
    def create(self, validated_data):
        steps_data = validated_data.pop('steps', None)
        author = self.context['request'].user
        scenario = Scenario.objects.create(author=author, **validated_data)
        if steps_data:
            for step_data in steps_data:
                Step.objects.create(
                    author=author,
                    scenario=scenario,
                    **step_data
                )
        return scenario
