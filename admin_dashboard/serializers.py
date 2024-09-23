from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import StringRelatedField
from admin_dashboard.models import AdminNotification, UserDisputeResolution
from core.models import Category, SubCategory, ClamRequest, Restaurant, AdsBanner, Review, RestaurantTimings, RestaurantImages, RestaurantService, Service, RequestDetailsUpdate, Cuisines, MenuType, \
    BusinessType, City, State, RestaurantCuisines
from owner_dashboard.serializers import RestaurantCuisineSerializer, RestaurantPaymentMethodSerializer
from users.models import User, Collaborator
from users.serializers import get_object_or_none


class AdminEmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def _validate_email(self, email):
        user = get_object_or_none(User, email__exact=email)
        if user and user.is_superuser:
            return user
        else:
            msg = 'Admin account not found with this email!'
            raise ValidationError(msg, code=400)

    def validate(self, attrs):
        email = attrs.get("email")

        if email:
            user = self._validate_email(email)
        else:
            msg = 'Must include "email" .'
            raise ValidationError(msg, code=400)

        if not user or not user.is_superuser:
            msg = 'Admin account not found!'
            raise ValidationError(msg, code=400)

        attrs["user"] = user
        return attrs


class AdminMobileLoginSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(required=True)

    def _validate_number(self, mobile_number):
        user = get_object_or_none(User, mobile_number__exact=mobile_number)
        if user and user.is_superuser:
            return user
        else:
            msg = 'Admin account not found with this email!'
            raise ValidationError(msg, code=400)

    def validate(self, attrs):
        mobile_number = attrs.get("mobile_number")

        if mobile_number:
            user = self._validate_number(mobile_number)
        else:
            msg = 'Must include "mobile number" .'
            raise ValidationError(msg, code=400)

        if not user or not user.is_superuser:
            msg = 'Admin account not found!'
            raise ValidationError(msg, code=400)

        attrs["user"] = user
        return attrs


class CollaboratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collaborator
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class AllBusinessTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = SubCategory
        fields = '__all__'


class AddSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'


class RequestBySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'mobile_number', 'first_name', 'last_name', 'profile_image', ]


class CuisinesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisines
        fields = '__all__'


class RequestForSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    type = AllBusinessTypesSerializer(read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'address', 'location', 'latitude', 'longitude', 'city', 'state', 'type', 'zipcode', 'profile_image', 'phone_number', 'business_whatsapp']


class ClaimRequestSerializer(serializers.ModelSerializer):
    request_by = RequestBySerializer(read_only=True)
    request_for = RequestForSerializer(read_only=True)

    class Meta:
        model = ClamRequest
        fields = '__all__'
        read_only_fields = ['request_by', 'request_for', 'created_at', 'modified_at']


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'mobile_number', 'profile_image', 'is_visitor', 'is_cafe_owner', 'is_cafe_manager', 'created_at', 'modified_at'
        ]


class UserRestaurantSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    type = AllBusinessTypesSerializer(read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'phone_number', 'address', 'address_ru', 'location', 'latitude', 'longitude', 'city', 'state', 'zipcode',
            'profile_image', 'business_description', 'type', 'average_rating', 'is_disabled', 'is_approved',
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    restaurants = UserRestaurantSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'auth_provider', 'username', 'first_name', 'last_name', 'email', 'mobile_number', 'profile_image', 'date_of_birth', 'is_visitor', 'is_cafe_owner', 'is_cafe_manager', 'restaurants'
        ]
        read_only_fields = [
            'id', 'auth_provider', 'username', 'restaurants', 'email', 'mobile_number',
        ]


class RestaurantSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    # state = StateSerializer(read_only=True)
    type = AllBusinessTypesSerializer(read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'phone_number', 'year_of_established', 'city', 'profile_image', 'type', 'is_approved', 'average_rating', 'is_disabled', 'created_at', 'modified_at'
        ]


class RestaurantUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'mobile_number', 'profile_image', 'is_cafe_owner', 'is_cafe_manager'
        ]


class RestaurantImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantImages
        fields = ['image', 'id']


class RestaurantDetailsServiceSerializer(serializers.ModelSerializer):
    service = StringRelatedField()

    class Meta:
        model = RestaurantService
        fields = ['service', ]


class RestaurantTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantTimings
        fields = [
            'id', 'weekday', 'from_hour', 'to_hour'
        ]
        read_only_fields = ['id', 'weekday']


class RestaurantDetailSerializer(serializers.ModelSerializer):
    owner = RestaurantUserSerializer(read_only=True)
    manager = RestaurantUserSerializer(read_only=True)
    restaurant_images = RestaurantImagesSerializer(many=True, read_only=True)
    restaurant_services = RestaurantDetailsServiceSerializer(many=True, read_only=True)
    restaurants_timings = RestaurantTimeSerializer(many=True, read_only=True)
    cuisines = RestaurantCuisineSerializer(read_only=True, many=True)
    restaurant_payment_modes = RestaurantPaymentMethodSerializer(read_only=True, many=True)
    type = AllBusinessTypesSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    state = StateSerializer(read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'owner', 'manager', 'phone_number', 'phone_number_2', 'business_whatsapp', 'address', 'address_ru', 'location', 'latitude', 'longitude', 'location_point',
            'city', 'state', 'zipcode', 'is_approved', 'profile_image', 'business_description', 'cuisines', 'type', 'known_for', 'must_order', 'year_of_established',
            'is_disabled', 'average_rating', 'rating_count', 'restaurant_services', 'restaurants_timings', 'restaurant_images', 'restaurant_payment_modes', 'business_instagram', 'average_bill',
            'business_capacity', 'business_email', 'business_website',
        ]


class RestaurantDetailUpdateSerializer(serializers.ModelSerializer):
    owner = RestaurantUserSerializer(read_only=True)
    manager = RestaurantUserSerializer(read_only=True)

    # restaurant_images = RestaurantImagesSerializer(many=True, read_only=True)
    # restaurant_services = RestaurantDetailsServiceSerializer(many=True, read_only=True)
    # restaurants_timings = RestaurantTimeSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'owner', 'manager', 'phone_number', 'phone_number_2', 'business_whatsapp', 'address', 'address_ru', 'location', 'latitude', 'longitude', 'location_point',
            'city', 'state', 'zipcode', 'is_approved', 'profile_image', 'business_description', 'type', 'known_for', 'must_order', 'year_of_established',
            'is_disabled', 'average_rating', 'rating_count', 'business_instagram', 'average_bill', 'business_capacity', 'business_email', 'business_website'
        ]


class AdsSerializer(serializers.ModelSerializer):
    restaurant = UserRestaurantSerializer(read_only=True)

    class Meta:
        model = AdsBanner
        fields = [
            'id', 'restaurant', 'cover_img', 'priority', 'description', 'is_active', 'created_at', 'modified_at'
        ]
        read_only_fields = [
            'id', 'restaurant', 'created_at', 'modified_at'
        ]


class AdminNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminNotification
        fields = '__all__'


class UserDisputeResolutionSerializer(serializers.ModelSerializer):
    query_by = RestaurantUserSerializer(read_only=True)

    class Meta:
        model = UserDisputeResolution
        fields = '__all__'
        read_only_fields = [
            'id', 'query_by', 'query'
        ]


class ReviewRestaurantSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    state = StateSerializer(read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'location', 'city', 'state', 'zipcode', 'profile_image', 'phone_number', 'business_whatsapp']


class ReviewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'mobile_number', 'profile_image', ]


class ReportedReviewSerializer(serializers.ModelSerializer):
    restaurant = ReviewRestaurantSerializer(read_only=True)
    user = ReviewUserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['id', 'restaurant', 'rating', 'comment', 'reported', 'report_rejected', 'user', 'created_at', 'modified_at']


class AllServiceSerializer(serializers.ModelSerializer):
    is_already_added = SerializerMethodField('get_is_already_added', read_only=True)

    def get_is_already_added(self, data):
        restaurant = self.context['restaurant']
        if restaurant:
            try:
                RestaurantService.objects.get(service=data, restaurant=restaurant)
                return True
            except RestaurantService.DoesNotExist:
                return False
        return False

    class Meta:
        model = Service
        fields = ['id', 'service_name', 'service_name_ru', 'is_already_added']


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'service_name', 'service_name_ru']


class RestaurantServiceSerializer(serializers.ModelSerializer):
    service = ServiceSerializer()

    class Meta:
        model = RestaurantService
        fields = '__all__'


class AddServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantService
        fields = ['service', ]


class DetailsUpdateRequestSerializer(serializers.ModelSerializer):
    request_by = RequestBySerializer(read_only=True)
    restaurant = RequestForSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    state = StateSerializer(read_only=True)

    class Meta:
        model = RequestDetailsUpdate
        fields = '__all__'


class MenuTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuType
        fields = '__all__'
