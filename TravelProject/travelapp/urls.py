from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(prefix='users', viewset=views.UserViewSet, basename='user')
router.register("categories", views.CategoryViewSet, 'category')
router.register(prefix='tours', viewset=views.TourViewSet, basename='tour')
router.register("comments", views.CommentViewSet, 'comment')
router.register(prefix='tourguides', viewset=views.TourguideViewSet, basename='tourguide')
# router.register(prefix='AdminStatTourView', viewset=views.AdminStatTourView, basename='adminstattour')
router.register(prefix='articals', viewset=views.ArticalViewset, basename='artical')
router.register(prefix='customers', viewset=views.CustomerViewSet, basename='customer')
router.register(prefix='payers', viewset=views.PayerViewSet, basename='payer')

urlpatterns = [
    path('', include(router.urls)),
    path('oauth2-info/', views.AuthInfo.as_view()),
]
