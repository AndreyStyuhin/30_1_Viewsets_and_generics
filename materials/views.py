from rest_framework import viewsets, generics, permissions, status
from materials.models import Course, Lesson, Subscription
from materials.paginators import MaterialsPagination
from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModer, IsOwner
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = MaterialsPagination

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
    serializer_class = LessonSerializer
    pagination_class = MaterialsPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.groups.filter(name='moderators').exists():
            return Lesson.objects.all().order_by('id')  # Упорядочиваем по id
        return Lesson.objects.filter(owner=self.request.user).order_by('id')

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


class SubscriptionToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({'error': 'course_id required'}, status=status.HTTP_400_BAD_REQUEST)
        course = get_object_or_404(Course, id=course_id)
        sub = Subscription.objects.filter(user=user, course=course)
        if sub.exists():
            sub.delete()
            message = 'подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course)
            message = 'подписка добавлена'
        return Response({'message': message}, status=status.HTTP_200_OK)