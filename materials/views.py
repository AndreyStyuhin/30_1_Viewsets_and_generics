from rest_framework import viewsets, generics, permissions
from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModer, IsOwner

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        # Регулярные пользователи: видеть список/создавать свои объекты
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        if self.action in ['create']:
            # Только авторизованные пользователи (создавать могут все авторизованные)
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update']:
            # Модераторы могут редактировать любые; владельцы — свои
            return [permissions.IsAuthenticated(), IsModer() | IsOwner()]
        if self.action == 'destroy':
            # Только владелец может удалить
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]


    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# Generic-классы для уроков
class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in ('GET',):
            return [permissions.IsAuthenticated()]
        if self.request.method in ('PUT', 'PATCH'):
            return [permissions.IsAuthenticated(), IsModer() | IsOwner()]
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]