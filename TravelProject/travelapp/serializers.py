from rest_framework import serializers
from .models import *
from rest_framework.serializers import ModelSerializer, SerializerMethodField, DateTimeField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'avatar',
                  'last_name', 'email', 'date_joined', 'id', 'is_superuser', 'is_staff']
        extra_kwargs = {
            'password': {'write_only': 'true'}
        }

    def create(self, validated_data):
        data = validated_data.copy()

        u = User(**data)
        u.set_password(u.password)
        u.save()

        return u


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class TourguideSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourGuide
        fields = ['id', 'name_tourguide', 'imageTourGuide']


class CustomerSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class PayerSerializer(ModelSerializer):
    class Meta:
        model = Payer
        fields = '__all__'


class InvoiceSerializer(ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'


class TourSerializer(serializers.ModelSerializer):
    # transports = TransportSerializer(many=True)
    # hotels = HotelSerializer(many=True)
    # image = SerializerMethodField()
    # banner = SerializerMethodField()
    # rate = SerializerMethodField()

    def get_image(self, tours):
        request = self.context['request']
        name = tours.image.name
        if name.startswith('static/'):
            path = '/%s' % name
        else:
            path = '/static/%s' % name

        return request.build_absolute_uri(path)

    class Meta:
        model = Tour
        fields = '__all__'


class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = ["id", "rate", "created_date"]


class ActionSerializer(ModelSerializer):
    class Meta:
        model = Action
        fields = ["id", "type", "created_date"]


# serializer cho bai viet
class ArticalSerializer(serializers.ModelSerializer):
    created_date = DateTimeField(read_only=True, format="%Y-%m-%d")
    image = SerializerMethodField()

    # type = SerializerMethodField()
    # content = SerializerMethodField()

    def get_image(self, tours):
        request = self.context['request']
        name = tours.image.name
        path = '/%s' % name

        return request.build_absolute_uri(path)

    class Meta:
        model = Artical
        fields = ['id', 'title', 'image', 'author', 'content', 'likes', 'created_date']


class CommentSerializer(ModelSerializer):
    user = SerializerMethodField()

    def get_user(self, comment):
        return UserSerializer(comment.user, context={"request": self.context.get('request')}).data

    class Meta:
        model = Comment
        fields = '__all__'

# serializer cho thong ke
# class AdminStatTour(ModelSerializer):
#     class Meta:
#         model = Tour
#         fields = "__all__"