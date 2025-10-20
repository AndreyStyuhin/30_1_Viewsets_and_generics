from rest_framework import serializers
from materials.models import Course, Lesson, Subscription
from materials.validators import YouTubeURLValidator
from rest_framework.fields import SerializerMethodField


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

    # lesson_count: количество уроков в курсе
    lesson_count = serializers.SerializerMethodField(help_text="Количество уроков в курсе")

    # lessons: вложенный сериализатор для отображения списка уроков
    lessons = LessonSerializer(many=True, read_only=True,
                               help_text="Список уроков, принадлежащих этому курсу (для просмотра)")

    # is_subscribed: признак подписки текущего пользователя
    is_subscribed = serializers.SerializerMethodField(help_text="Признак подписки текущего пользователя на этот курс")

    # Предполагается, что поля модели Course включают title, description, preview
    title = serializers.CharField(help_text="Название курса")
    description = serializers.CharField(help_text="Краткое описание курса")
    preview = serializers.ImageField(required=False, help_text="Превью/изображение курса")

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