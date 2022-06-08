from typing import Union
from django.shortcuts import render, get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, generics, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.generic import View
from .paginators import *
from django.db.models import Q
from .models import *
from .serializers import *

from .perms import CommentOwnerPerms
from django.db.models import F
from django.http import Http404
from django.conf import settings


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, ]

    def get_permissions(self):
        if self.action == 'get_current_user':
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path='current-user')
    def get_current_user(self, request):
        return Response(self.serializer_class(request.user).data,
                        status=status.HTTP_200_OK)

    # API thay đổi mật khẩu
    @action(methods=['post'], detail=False, url_path="change-password")
    def change_password(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        account = request.user

        if old_password is not None and new_password is not None and old_password != new_password:
            if not account.check_password(old_password):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            account.set_password(new_password)
            account.save()
            response = {
                'status': 'success',
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response, status=status.HTTP_200_OK)

        return Response({"Message": ["Errors."]}, status=status.HTTP_400_BAD_REQUEST)


class AuthInfo(APIView):
    def get(self, request):
        return Response(settings.OAUTH2_INFO, status=status.HTTP_200_OK)


class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.filter(active=True)
    serializer_class = TourSerializer
    pagination_class = TourPagination

    def get_permissions(self):
        if self.action in ['add_comment', 'take_action', 'rate']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['post'], detail=True, url_path='update-slots')
    def update_quantity(self, request, pk):
        try:
            count = int(request.data['count'])
        except IndexError | ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            slot = int(Tour.objects.get(pk=pk).slot) - count
            if slot > -1:
                Tour.objects.filter(pk=pk).update(slot=slot)

            return Response({"message": "update success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='rating')
    def rate(self, request, pk):
        try:
            rating = int(request.data['rating'])
        except IndexError | ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            r = Rating.objects.update_or_create(user=request.user,
                                                tour=self.get_object(),
                                                defaults={"rate": rating})

            return Response(RatingSerializer(r).data,
                            status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path="add-comment")
    def add_comment(self, request, pk):
        content = request.data.get('content')
        if content:
            c = Comment.objects.create(content=content,
                                       tour=self.get_object(),
                                       user=request.user)

            return Response(CommentSerializer(c, context={"request": request}).data,
                            status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], url_path='comments', detail=True)
    def get_comments(self, request, pk):
        tour = self.get_object()
        comments = tour.comments.select_related('user').filter(active=True)

        return Response(CommentSerializer(comments, many=True).data,
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description='Get the comments of a tour',
        responses={
            status.HTTP_200_OK: CommentSerializer()
        }
    )
    @action(methods=['post'], detail=True, url_path='like')
    def take_action(self, request, pk):
        try:
            action_type = int(request.data['type'])
        except IndexError | ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            action = Action.objects.create(type=action_type,
                                           user=request.user,
                                           tour=self.get_object())

            return Response(ActionSerializer(action).data,
                            status=status.HTTP_200_OK)

    def get_queryset(self):
        tours = Tour.objects.filter(active=True)

        q = self.request.query_params.get('q')
        if q is not None:
            if q == '1':
                tours = tours.order_by('name_tour')
            elif q == '2':
                tours = tours.order_by('price_of_tour')
            elif q == '3':
                tours = tours.order_by('-price_of_tour')
            elif q == '4':
                tours = tours.order_by('-rating')
        else:
            pass

        # tìm kiếm theo tên tour
        q = self.request.query_params.get('q')
        if q is not None:
            tours = tours.filter(name_tour__icontains=q)

        # tìm kiếm theo category
        cate_id = self.request.query_params.get('category_id')
        if cate_id is not None:
            tours = tours.filter(category_id=cate_id)

        # lọc theo giá tour
        max_price = self.request.query_params.get('max')
        min_price = self.request.query_params.get('min')
        if max_price is not None:
            tours = tours.filter(price_of_tour__lte=max_price)
        if min_price is not None:
            tours = tours.filter(price_of_tour__gte=min_price)
        # lọc thời gian
        depart_date = self.request.query_params.get('date')
        if depart_date is not None:
            tours = tours.filter(depart_date=depart_date)

        min_d = self.request.query_params.get('min_d')
        max_d = self.request.query_params.get('max_d')
        if min_d is not None and max_d is not None:
            tours = tours.filter(Q(duration__startswith=min_d) | Q(duration__startswith=max_d))

        #lọc theo rate
        rate = self.request.query_params.get('rate')
        if rate is not None:
            tours = tours.filter(rating=rate)

        depart_date = self.request.query_params.get('depart_date')
        if depart_date is not None:
            tours = tours.filter(depart_date=depart_date)

        return tours


class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TourguideViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = TourGuide.objects.all()
    serializer_class = TourguideSerializer

    def get_queryset(self):
        query = self.queryset

        kw = self.request.query_params.get('kw')
        if kw:
            query = query.filter(name__icontains=kw)

        return query


class CustomerViewSet(viewsets.ViewSet, generics.ListAPIView,
                      generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class InvoiceViewSet(viewsets.ViewSet, generics.ListAPIView):
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()


class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView,
                     generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        if request.user == self.get_object().user:
            return super().destroy(request, *args, **kwargs)

        return Response(status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        if request.user == self.get_object().user:
            return super().partial_update(request, *args, **kwargs)

        return Response(status=status.HTTP_403_FORBIDDEN)


class ArticalViewset(viewsets.ViewSet, generics.ListAPIView, generics.DestroyAPIView,
                     generics.RetrieveAPIView, generics.RetrieveUpdateAPIView, generics.CreateAPIView):
    queryset = Artical.objects.all()
    serializer_class = ArticalSerializer
    pagination_class = ArticalPagination

    def get_permissions(self):
        if self.action in ['add_comment', 'take_action', 'rate']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], url_path='comments', detail=True)
    def get_comments(self, request, pk):
        tour = self.get_object()
        comments = tour.comments.select_related('user').filter(active=True)

        return Response(CommentSerializer(comments, many=True).data,
                        status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='like')
    def take_action(self, request, pk):
        try:
            action_type = int(request.data['type'])
        except IndexError | ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            action = Action.objects.create(type=action_type,
                                           user=request.user,
                                           artical=self.get_object())

            return Response(ActionSerializer(action).data,
                            status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path="add-comment")
    def add_comment(self, request, pk):
        content = request.data.get('content')
        if content:
            c = Comment.objects.create(content=content,
                                       artical=self.get_object(),
                                       user=request.user)

            return Response(CommentSerializer(c, context={"request": request}).data,
                            status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    # tim kiem theo topic bai viet
    def get_queryset(self):
        list_artical = Artical.objects.filter(active=True)

        q = self.request.query_params.get('q')
        if q is not None:
            list_artical = list_artical.filter(title__icontains=q)

        return list_artical


class PayerViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView):
    serializer_class = PayerSerializer
    queryset = Payer.objects.all()

    @action(methods=['post'], detail=True, url_path="add-customer")
    def add_customer(self, request, pk):
        name = request.data.get('name')
        age = request.data.get('age')
        gender = request.data.get('gender')
        email = request.data.get('email')
        phone = request.data.get('phone')
        address = request.data.get('address')
        age_type = 0

        if name and age and gender and phone and address and email:
            if age == 'Trẻ em':
                age_type = 1
            c = Customer.objects.create(name=name, age=age_type, gender=gender, address=address,
                                        phone=phone, email=email, payer=self.get_object())

            return Response(CustomerSerializer(c).data,
                            status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path="add-invoice")
    def add_invoice(self, request, pk):
        total_amount = request.data.get('total_amount')
        tour_id = request.data.get('tour_id')
        tour = Tour.objects.get(pk=tour_id)
        note = request.data.get('note')
        status_payer = request.data.get('status_payer')

        if total_amount:
            inv = Invoice.objects.create(total_amount=total_amount, note=note, status_payment=status_payer,
                                         payer=self.get_object(), tour=tour)

            return Response(InvoiceSerializer(inv).data,
                            status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

# API thong ke
# class AdminStatTourView(viewsets.ViewSet, generics.ListAPIView):
#     queryset = Tour.objects.count()
#     serializer_class = AdminStatTour