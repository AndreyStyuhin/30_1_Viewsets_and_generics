from django.contrib import admin
from materials.models import Course, Lesson, Subscription


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'video_url')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course')