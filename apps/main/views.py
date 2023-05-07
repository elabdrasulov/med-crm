from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework import mixins, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .models import *
from .permissions import IsAdminOrReadOnly, IsAuthor
from .serializers import *
from .services import booked_up
from .tasks import create_an_appointment

class DoctorViewSet(ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['first_name']
    search_fields = ['categories__title', 'first_name', 'last_name']
    ordering_fields = ['first_name', 'last_name']

    @swagger_auto_schema(manual_parameters=[openapi.Parameter('first_name', openapi.IN_QUERY, 'search doctors by name', type=openapi.TYPE_STRING)])
    @action(methods=['GET'], detail=False)
    def search(self, request):
        first_name = request.query_params.get('first_name')
        queryset = self.get_queryset()
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        
        serializer = DoctorSerializer(queryset, many=True, context={'request':request})
        return Response(serializer.data, 200)

    @action(methods=["GET"], detail=False)
    def order_by_rating(self, request):
        queryset = self.get_queryset()

        queryset = sorted(queryset, key=lambda doctor: doctor.average_rating, reverse=True)
        serializer = DoctorSerializer(queryset, many=True, context={"request":request})
        return Response(serializer.data, 200)


class CategoryViewSet(mixins.CreateModelMixin, 
                    mixins.DestroyModelMixin, 
                    mixins.ListModelMixin, 
                    GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ServiceViewSet(mixins.CreateModelMixin, 
                    mixins.DestroyModelMixin, 
                    mixins.ListModelMixin, 
                    GenericViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]


class CommentViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthor, IsAuthenticatedOrReadOnly]

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def toggle_like(request, d_id):
    user = request.user
    doctor = get_object_or_404(Doctor, id=d_id)

    if Like.objects.filter(user=user, doctor=doctor).exists():
        Like.objects.filter(user=user, doctor=doctor).delete()
    else:
        Like.objects.create(user=user, doctor=doctor)

    return Response("Like toggled", 200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_rating(request, d_id):
    user = request.user
    doctor = get_object_or_404(Doctor, id=d_id)
    value = request.POST.get("value")

    if not value:
        raise ValueError("Value is required")

    if Rating.objects.filter(user=user, doctor=doctor, value=value).exists():
        rating = Rating.objects.get(user=user, doctor=doctor)
        rating.value = value
        rating.save()
    else:
        Rating.objects.create(user=user, doctor=doctor, value=value)

    return Response("Rating created", 201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def add_to_favorites(request, d_id):
    user = request.user
    doctor = get_object_or_404(Doctor, id=d_id)

    if Favorite.objects.filter(user=user, doctor=doctor).exists():
        Favorite.objects.filter(user=user, doctor=doctor).delete()
    else:
        Favorite.objects.create(user=user, doctor=doctor)
    return Response("Added to favorites", 200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_favorites(request):
    queryset = Favorite.objects.filter(user=request.user)
    serializer = FavoriteSerializer(queryset, many=True)
    return Response(serializer.data)


class AppointmentViewSet(ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor]

    
    def create(self, request, *args, **kwargs):

        book_date = request.data.get("date")
        book_time = request.data.get("time_list")
        doctor = request.data.get("doctor")

        if booked_up(book_date, book_time, doctor):
            return Response(
                """This time slot is already booked for this doctor.
                Please choose another time or day""", 400
            )

        super().create(request, *args, **kwargs)

        entry = Appointment.objects.get(
            date=book_date, time_list=book_time, doctor=doctor
        )
        create_an_appointment.delay(entry.id)
        return Response("Appointment created")


    def update(self, request, *args, **kwargs):
        book_date = request.data.get("date")
        book_time = request.data.get("time_list")
        doctor = request.data.get("doctor")

        if booked_up(book_date, book_time, doctor):
            return Response(
                """This time slot is already booked for this doctor.
                Please choose another time or day""", 400
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True

        instance = self.get_object()
        book_time = request.data.get('time_list')


        if book_time:
            if booked_up(instance.date, book_time, instance.doctor.id):
                return Response(
                    """This time slot is already booked for this doctor.
                    Please choose another time or day""", 400
                )
        else:
            return Response('You can update only booking time', 400)

        return super().update(request, *args, **kwargs)

@api_view(["GET"])
def show_similar_doctors(request, pk):

    doctor = get_object_or_404(Doctor, id=pk)
    relative_doctors = Doctor.objects.filter(categories__id__in=doctor.categories.all())
    serializer = DoctorSerializer(relative_doctors, many=True)
    return Response(serializer.data)