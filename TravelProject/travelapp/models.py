from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from django.conf import settings
import datetime


class User(AbstractUser):
    avatar = models.ImageField(null=True, upload_to='users/%Y/%m')


def upload_to(instance, filename):
    return 'posts/{filename}'.format(filename=filename)


class ModelBase(models.Model):
    name = models.CharField(max_length=255, null=True,default='thong tin')
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    email = models.EmailField(max_length=254, null=False)
    phone = models.CharField(max_length=255, null=False)
    address = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


# model nhân viên
class Staff(ModelBase):
    class Meta:
        unique_together = ('email', 'phone', 'avatar')

    avatar = models.ImageField(upload_to='images/avatars/%Y/%m', null=True, default=None)

    def __str__(self):
        return self.name


class TourGuide(ModelBase):
    name_tourguide = models.TextField()
    address = models.TextField()
    phone = models.TextField
    imageTourGuide = models.ImageField(null=True, blank=True, upload_to='imageTourGuide/%Y/%m')

    def __str__(self):
        return self.name_tourguide


class Tour(ModelBase):
    name_tour = models.CharField(max_length=255, null=False)
    plan_tour = RichTextField(default=None, null=True)
    description = RichTextField(default=None, null=True)
    banner = models.ImageField(upload_to='imageBanner/%Y/%m', default=None)
    slot = models.IntegerField(default=0, null=True)

    departure = models.CharField(max_length=255, null=True)
    depart_date = models.DateField(null=True, blank=True)
    duration = models.CharField(max_length=50, null=True)

    price_of_tour = models.FloatField(null=False, blank=False)
    price_of_tour_child = models.FloatField(null=False, default=0)
    price_of_room = models.FloatField(null=False, blank=False)

    rating = models.FloatField(null=True, blank=True)

    imageTour = models.ImageField(null=True, blank=True, upload_to='imageTour/%Y/%m')

    tourguide = models.ForeignKey(TourGuide, related_name="Tour", null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey('Category', related_name='tours', null=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('name_tour', 'category')
        ordering = ["-id"]

    def __str__(self):
        return self.name_tour


class Category(models.Model):
    name = models.CharField(max_length=50, null=False, unique=True)

    def __str__(self):
        return self.name


class Artical(models.Model):
    class Meta:
        ordering = ["-id"]

    active = models.BooleanField(default=True)
    title = models.CharField(max_length=255, null=False, unique=True)
    image = models.ImageField(upload_to='images/artical/%Y/%m', null=True)
    author = models.CharField(max_length=100, null=True, default=None)
    content = RichTextField()
    likes = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - Ngày tạo: %s" % (self.title, self.created_date.strftime("%Y-%m-%d"))


# comment cho bài viết và tour
class Comment(models.Model):
    class Meta:
        ordering = ["-id"]

    active = models.BooleanField(default=True)
    content = RichTextField()
    created_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE, null=True)
    artical = models.ForeignKey(Artical, related_name="comments", on_delete=models.CASCADE, null=True)
    tour = models.ForeignKey(Tour, related_name="comments", on_delete=models.CASCADE, null=True)


# action, like, rating, view
class ActionBase(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Rating(ActionBase):
    rate = models.PositiveSmallIntegerField(default=0)
    tour = models.ForeignKey(Tour, related_name="ratings", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("tour", "user")
        ordering = ["-id"]


class Action(ActionBase):
    LIKE, NOT_LIKE = range(2)
    ACTIONS = [
        (LIKE, 'Like'),
        (NOT_LIKE, 'Not like'),
    ]
    type = models.PositiveSmallIntegerField(choices=ACTIONS, default=LIKE)
    artical = models.ForeignKey(Artical, related_name="actions", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("artical", "user")


# Thông tin khách hàng
class Customer(ModelBase):
    class Meta:
        ordering = ["-id"]

    ADULT, CHILD = range(2)
    AGES = [
        (ADULT, 'adult'),
        (CHILD, 'child')
    ]
    avatar = models.ImageField(upload_to='customerAvatar/%Y/%m', null=True, default=None)
    age = models.PositiveSmallIntegerField(choices=AGES, default=ADULT)
    payer = models.ForeignKey('Payer', related_name='customers', on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=20, null=False,default='')

    def __str__(self):
        return self.name_customer


# Thanh toán online
class Payer(models.Model):
    class Meta:
        ordering = ["-id"]

    name = models.CharField(max_length=255, null=False)
    email = models.EmailField(max_length=254, null=False)
    phone = models.CharField(max_length=255, null=False)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    class Meta:
        ordering = ["-id"]

    WAITING, COMPLETED = range(2)
    STATUS_PAYMENT = [
        (WAITING, 'waiting'),
        (COMPLETED, 'completed')
    ]
    total_amount = models.FloatField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True, blank=True)
    status_payment = models.PositiveSmallIntegerField(choices=STATUS_PAYMENT, default=WAITING)
    tour = models.ForeignKey('Tour', related_name='invoices', null=True, on_delete=models.SET_NULL)
    payer = models.ForeignKey('Payer', related_name='invoices', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "Mã hóa đơn %s - Ngày tạo: %s" % (str(self.id), self.created_date.strftime("%Y-%m-%d"))