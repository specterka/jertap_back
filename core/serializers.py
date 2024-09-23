from rest_framework.fields import SerializerMethodField
from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer
from admin_dashboard.models import UserDisputeResolution
from core.models import Restaurant, Category, SubCategory, Review, AdsBanner, Favorite, RestaurantTimings, RestaurantService, RestaurantImages, Cuisines, Service, MenuItem, ItemIngredient, \
    ReviewReply, QA, BusinessType, City, State, ModeOfPayment, RestaurantAcceptedPayment, RestaurantCuisines, MenuType
from owner_dashboard.models import PublicQuery
from users.models import User


class AllBusinessTypesSerializer(ModelSerializer):
    class Meta:
        model = BusinessType
        fields = '__all__'


class CitySerializer(ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class StateSerializer(ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class SubCategorySerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'


class HomeCategoriesSerializer(ModelSerializer):
    sub_categories = SubCategorySerializer(many=True)

    class Meta:
        model = Category
        fields = '__all__'


class ReviewUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'email', 'profile_image']


class ReviewRestaurantSerializer(ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'profile_image']


class HomeRecentReviewSerializer(ModelSerializer):
    restaurant = ReviewRestaurantSerializer(read_only=True)
    user = ReviewUserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'


class SearchRestaurantUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class RestaurantSearchSerializer(ModelSerializer):
    owner = SearchRestaurantUserSerializer(read_only=True)
    manager = SearchRestaurantUserSerializer(read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'profile_image', 'business_description', 'average_rating', 'owner', 'manager'
        ]


class AdsBannerSerializer(ModelSerializer):
    class Meta:
        model = AdsBanner
        fields = '__all__'


class NearByRestaurantSerializer(ModelSerializer):
    class Meta:
        model = Restaurant
        fields = [
            'name', 'id', 'profile_image', 'business_description', 'average_rating',
        ]


class RestaurantListSerializer(ModelSerializer):
    city = CitySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    is_favorite = SerializerMethodField('get_is_favorite', read_only=True)

    def get_is_favorite(self, data):
        user = self.context['user']
        if user is None:
            return False
        else:
            if Favorite.objects.filter(user=user, restaurant=data).exists():
                return True
            else:
                return False

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'profile_image', 'average_rating', 'rating_count', 'business_description', 'is_disabled', 'phone_number', 'address', 'address_ru', 'latitude', 'longitude', 'city', 'state', 'is_favorite'
        ]


class FavoriteSerializer(ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ['id', 'user', 'restaurant', 'created_at', 'updated_at', 'user', ]


class RestaurantUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'mobile_number', 'profile_image', 'is_cafe_owner', 'is_cafe_manager'
        ]


class RestaurantImagesSerializer(ModelSerializer):
    class Meta:
        model = RestaurantImages
        fields = ['image', 'id']


class ServiceSerializer(ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'service_name', 'service_name_ru']


class RestaurantDetailsServiceSerializer(ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = RestaurantService
        fields = ['service', ]


class RestaurantTimeSerializer(ModelSerializer):
    class Meta:
        model = RestaurantTimings
        fields = [
            'id', 'weekday', 'from_hour', 'to_hour'
        ]
        read_only_fields = ['id', 'weekday']


class CuisinesDropdownSerializer(ModelSerializer):
    class Meta:
        model = Cuisines
        fields = '__all__'


class CuisinesSerializer(ModelSerializer):
    class Meta:
        model = Cuisines
        fields = '__all__'


class RestaurantCuisinesSerializer(ModelSerializer):
    cuisine = CuisinesSerializer(read_only=True)

    class Meta:
        model = RestaurantCuisines
        fields = [
            'cuisine'
        ]


class ReviewPartialSerializer(ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment']


class PaymentModeDetailSerializer(ModelSerializer):
    class Meta:
        model = ModeOfPayment
        fields = '__all__'


class RestaurantPaymentMethodSerializer(ModelSerializer):
    payment = PaymentModeDetailSerializer()

    class Meta:
        model = RestaurantAcceptedPayment
        fields = ['payment', 'id']


class RestaurantDetailSerializer(ModelSerializer):
    owner = RestaurantUserSerializer(read_only=True)
    manager = RestaurantUserSerializer(read_only=True)
    restaurant_images = RestaurantImagesSerializer(many=True, read_only=True)
    restaurant_services = RestaurantDetailsServiceSerializer(many=True, read_only=True)
    restaurants_timings = RestaurantTimeSerializer(many=True, read_only=True)
    cuisines = RestaurantCuisinesSerializer(read_only=True, many=True)
    is_favorite = SerializerMethodField('get_is_favorite', read_only=True)
    your_review = SerializerMethodField('get_your_review', read_only=True)
    city = CitySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    type = AllBusinessTypesSerializer(read_only=True)
    restaurant_payment_modes = RestaurantPaymentMethodSerializer(read_only=True, many=True)

    def get_is_favorite(self, data):

        user = self.context['user']
        if user is None:
            return False
        else:
            if Favorite.objects.filter(user=user, restaurant=data).exists():
                return True
            else:
                return False

    def get_your_review(self, data):
        user = self.context['user']
        restaurant = self.context['restaurant']
        if user is not None and restaurant is not None:
            try:
                review = Review.objects.get(user=user, restaurant=restaurant)
                review = ReviewPartialSerializer(instance=review).data
            except Exception as e:
                review = None
            return review

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'owner', 'manager', 'phone_number', 'phone_number_2', 'business_whatsapp', 'business_instagram', 'business_2gis', 'address', 'address_ru', 'location', 'latitude',
            'longitude', 'location_point', 'city', 'state', 'zipcode', 'is_approved', 'profile_image', 'business_description', 'cuisines', 'type', 'known_for', 'must_order', 'year_of_established',
            'average_bill', 'business_capacity', 'business_email', 'is_disabled', 'average_rating', 'rating_count', 'restaurant_services', 'restaurants_timings', 'restaurant_images', 'is_favorite',
            'your_review', 'business_website', 'restaurant_payment_modes'
        ]


class MenuTypeSerializer(ModelSerializer):
    class Meta:
        model = MenuType
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = ItemIngredient
        fields = [
            'id', 'ingredients'
        ]


class RestaurantMenuSerializer(ModelSerializer):
    item_ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            'id', 'Item_name', 'description', 'cover_image', 'price', 'is_veg', 'item_ingredients',
        ]


class MenuItemDetailsSerializer(ModelSerializer):
    sub_category = SubCategorySerializer(read_only=True)
    item_ingredients = IngredientSerializer(many=True, read_only=True)
    menu_type = MenuTypeSerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            'id', 'Item_name', 'description', 'cover_image', 'price', 'is_veg', 'sub_category', 'item_ingredients', 'menu_type'
        ]


class ReviewReplaySerializer(ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = ['replay', ]


class RestaurantReviewSerializer(ModelSerializer):
    review_replays = ReviewReplaySerializer(read_only=True, many=True)
    user = ReviewUserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'rating', 'comment', 'user', 'review_replays'
        ]
        read_only_fields = [
            'id', 'user', 'review_replays'
        ]


class FavoriteListSerializer(ModelSerializer):
    restaurant = RestaurantListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = [
            'restaurant'
        ]


class RestaurantQASerializer(ModelSerializer):
    class Meta:
        model = QA
        fields = ['id', 'question', 'answer']


class PublicQuerySerializer(ModelSerializer):
    class Meta:
        model = PublicQuery
        fields = ['question', ]


class UserDisputeResolutionSerializer(ModelSerializer):
    class Meta:
        model = UserDisputeResolution
        fields = ['query', ]


class AllServiceSerializer(ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'service_name', 'service_name_ru', ]


class AllCuisinesListSerializer(ModelSerializer):
    class Meta:
        model = Cuisines
        fields = ['id', 'cuisines', 'cuisines_ru', ]
