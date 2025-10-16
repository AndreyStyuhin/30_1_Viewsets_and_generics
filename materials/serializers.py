from rest_framework import serializers
from materials.models import Course, Lesson, Subscription
from materials.validators import validate_video_url


class LessonSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    video_url = serializers.URLField(validators=[validate_video_url])  # Привязываем валидатор к полю

    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, course=obj).exists()

    def get_lesson_count(self, obj):
        return obj.lessons.count()