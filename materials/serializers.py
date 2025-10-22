# ФАЙЛ: materials/serializers.py

from rest_framework import serializers
from materials.models import Course, Lesson, Subscription
from materials.validators import YouTubeURLValidator
from drf_spectacular.utils import extend_schema_field


class LessonSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True, help_text="ID владельца урока")
    video_url = serializers.URLField(
        validators=[YouTubeURLValidator()],
        help_text="Ссылка на видео-урок (должна быть ссылкой на YouTube)"
    )
    title = serializers.CharField(help_text="Название урока")
    description = serializers.CharField(help_text="Описание урока")
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(),
                                                help_text="ID курса, к которому относится урок")
    preview = serializers.ImageField(required=False, help_text="Превью/изображение урока")

    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True, help_text="ID владельца курса")
    lesson_count = serializers.SerializerMethodField(help_text="Количество уроков в курсе")
    lessons = LessonSerializer(many=True, read_only=True,
                               help_text="Список уроков, принадлежащих этому курсу (для просмотра)")
    is_subscribed = serializers.SerializerMethodField(help_text="Признак подписки текущего пользователя на этот курс")
    title = serializers.CharField(help_text="Название курса")
    description = serializers.CharField(help_text="Краткое описание курса")
    preview = serializers.ImageField(required=False, help_text="Превью/изображение курса")
    price = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Цена курса (в рублях)")

    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'preview', 'owner',
                  'price', 'lesson_count', 'lessons', 'is_subscribed')


    @extend_schema_field(serializers.BooleanField())
    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, course=obj).exists()


    @extend_schema_field(serializers.IntegerField())
    def get_lesson_count(self, obj):
        return obj.lessons.count()