from rest_framework import viewsets, generics, permissions
from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModer, IsOwner

class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        else:
            return Course.objects.filter(owner=user)

    def get_permissions(self):
        # Регулярные пользователи: видеть список/создавать свои объекты
        if self.action in ['list', 'create']:
            return [permissions.IsAuthenticated()]
        if self.action in ['retrieve', 'update', 'partial_update']:
            # Модераторы могут просматривать/редактировать любые; владельцы — свои
            return [permissions.IsAuthenticated(), IsModer() | IsOwner()]
        if self.action == 'destroy':
            # Только владелец может удалить
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# Generic-классы для уроков
class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        else:
            return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in ('GET',):
            # Для просмотра: модератор или владелец
            return [permissions.IsAuthenticated(), IsModer() | IsOwner()]
        if self.request.method in ('PUT', 'PATCH'):
            return [permissions.IsAuthenticated(), IsModer() | IsOwner()]
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]