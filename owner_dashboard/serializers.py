from rest_framework.fields import SerializerMethodField, ListField
from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from core.models import Restaurant, Category, RestaurantCategory, MenuItem, Review, ReviewReply, QA, RestaurantTimings, RestaurantImages, SubCategory, ItemIngredient, MenuItemImages, ClamRequest, \
    Service, RestaurantService, RequestDetailsUpdate, Cuisines, MenuType, RestaurantCuisines, BusinessType, City, State, RestaurantAcceptedPayment, ModeOfPayment, AdsBanner
from owner_dashboard.models import RestaurantNotification, PublicQuery, Promotion, PromotionWeekDay, PromotionOnItem
from users.models import User, Collaborator
from social.models import Event


class CategoryCountSerializer(ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['category_count', 'menu_item_count', 'average_rating', 'is_disabled']


class AllCategoryListSerializer(ModelSerializer):
    is_added = SerializerMethodField('get_is_added', read_only=True)

    def get_is_added(self, data):
        restaurant = self.context['restaurant']
        if restaurant:
            try:
                RestaurantCategory.objects.get(category=data, restaurant=restaurant)
                return True
            except:
                return False
        return False

    class Meta:
        model = Category
        fields = '__all__'


class AllCuisinesListSerializer(serializers.ModelSerializer):
    is_added = SerializerMethodField('get_is_added', read_only=True)

    def get_is_added(self, data):
        restaurant = self.context['restaurant']
        if restaurant:
            try:
                RestaurantCuisines.objects.get(cuisine=data, restaurant=restaurant)
                return True
            except:
                return False
        return False

    class Meta:
        model = Cuisines
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


class PaymentModeSerializer(ModelSerializer):
    is_added = SerializerMethodField('get_is_added', read_only=True)

    def get_is_added(self, data):
        restaurant = self.context['restaurant']
        if restaurant:
            try:
                RestaurantAcceptedPayment.objects.get(payment=data, restaurant=restaurant)
                return True
            except:
                return False
        return False

    class Meta:
        model = ModeOfPayment
        fields = '__all__'


class AddRestaurantCategorySerializer(ModelSerializer):
    class Meta:
        model = RestaurantCategory
        fields = ['category', 'restaurant', ]


class RatingUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'profile_image']


class UserReviewListSerializer(ModelSerializer):
    user = RatingUserSerializer()

    class Meta:
        model = Review
        fields = [
            'id', 'rating', 'comment', 'user'
        ]


class ReplayReviewSerializer(ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = '__all__'


class ReviewDetailSerializer(ModelSerializer):
    user = RatingUserSerializer()
    review_replays = ReplayReviewSerializer(many=True)

    class Meta:
        model = Review
        fields = [
            'id', 'rating', 'comment', 'user', 'review_replays', 'reported'
        ]

        read_only_fields = ['id', 'rating', 'comment', 'user', 'review_replays', 'reported', ]


class AddReviewReplaySerializer(ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = [
            'replay', 'review',
        ]


class RestaurantNotificationSerializer(ModelSerializer):
    class Meta:
        model = RestaurantNotification
        fields = '__all__'


class CollaboratorListSerializer(ModelSerializer):
    class Meta:
        model = Collaborator
        fields = '__all__'


class QASerializer(ModelSerializer):
    class Meta:
        model = QA
        fields = '__all__'
        read_only_fields = ['restaurant', ]


class CuisinesSerializer(ModelSerializer):
    class Meta:
        model = Cuisines
        fields = '__all__'


class RestaurantAddressSerializer(ModelSerializer):
    city = CitySerializer(read_only=True)
    state = StateSerializer(read_only=True)

    class Meta:
        model = Restaurant
        fields = ['address', 'address_ru', 'location', 'latitude', 'longitude', 'city', 'state', 'zipcode']
        # read_only_fields = ['address', 'location', 'latitude', 'longitude', 'city', 'state', 'zipcode']


class AddressUpdateRequestSerializer(ModelSerializer):
    class Meta:
        model = RequestDetailsUpdate
        fields = ['address', 'address_ru', 'location', 'latitude', 'longitude', 'city', 'state', 'zipcode', 'restaurant', 'request_by']


class RestaurantTimeSerializer(ModelSerializer):
    class Meta:
        model = RestaurantTimings
        fields = [
            'id', 'weekday', 'from_hour', 'to_hour'
        ]
        read_only_fields = ['id', 'weekday']


class RestaurantImagesSerializer(ModelSerializer):
    class Meta:
        model = RestaurantImages
        fields = ['image', 'id']


class RestaurantBasicDetailSerializer(ModelSerializer):
    restaurant_images = RestaurantImagesSerializer(many=True, read_only=True)
    type = AllBusinessTypesSerializer(read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'name', 'business_description', 'phone_number', 'phone_number_2', 'business_whatsapp', 'business_instagram', 'business_2gis', 'average_bill', 'business_capacity',
            'profile_image', 'restaurant_images', 'year_of_established', 'must_order', 'known_for', 'type', 'is_disabled', 'is_approved', 'business_email', 'business_website',
        ]
        read_only_fields = ['is_approved', ]

    # def update(self, instance, validated_data):
    #     print(validated_data)
    #     images = validated_data.pop('restaurant_images', [])  # Extract restaurant_images data
    #
    #     # Update restaurant fields
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.business_description = validated_data.get('business_description', instance.business_description)
    #     instance.phone_number = validated_data.get('phone_number', instance.phone_number)
    #     instance.business_whatsapp = validated_data.get('business_whatsapp', instance.business_whatsapp)
    #     instance.profile_image = validated_data.get('profile_image', instance.profile_image)
    #     instance.save()
    #
    #     # Update or create image instances
    #     print(images)
    #     for image in images:
    #         RestaurantImages.objects.create(restaurant=instance, **image)
    #
    #     return instance


class RestaurantBasicDetailUpdateSerializer(ModelSerializer):
    restaurant_images = RestaurantImagesSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'name', 'business_description', 'phone_number', 'phone_number_2', 'business_whatsapp', 'business_instagram', 'business_2gis', 'average_bill', 'business_capacity',
            'profile_image', 'restaurant_images', 'year_of_established', 'must_order', 'known_for', 'type', 'is_disabled', 'is_approved', 'business_email', 'business_website'
        ]
        read_only_fields = ['is_approved', ]

    # def update(self, instance, validated_data):
    #     print(validated_data)
    #     images = validated_data.pop('restaurant_images', [])  # Extract restaurant_images data
    #
    #     # Update restaurant fields
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.business_description = validated_data.get('business_description', instance.business_description)
    #     instance.phone_number = validated_data.get('phone_number', instance.phone_number)
    #     instance.business_whatsapp = validated_data.get('business_whatsapp', instance.business_whatsapp)
    #     instance.profile_image = validated_data.get('profile_image', instance.profile_image)
    #     instance.save()
    #
    #     # Update or create image instances
    #     print(images)
    #     for image in images:
    #         RestaurantImages.objects.create(restaurant=instance, **image)
    #
    #     return instance


class ItemSubCategorySerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = [
            'id', 'name', 'icon'
        ]


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = ItemIngredient
        fields = [
            'id', 'ingredients'
        ]


class MenuTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuType
        fields = '__all__'


class ItemImageSerializer(ModelSerializer):
    class Meta:
        model = MenuItemImages
        fields = [
            'id', 'image'
        ]


class MenuItemDetailSerializer(ModelSerializer):
    item_ingredients = IngredientSerializer(many=True, required=False, read_only=True)
    ingredients = ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = MenuItem
        fields = ['id', 'Item_name', 'restaurant', 'description', 'cover_image', 'sub_category', 'price', 'is_veg', 'menu_type', 'item_ingredients', 'ingredients']
        read_only_fields = ['restaurant', 'item_ingredients', ]
        # write_only_fields = ['ingredients', 'images']

    def create(self, validated_data):
        restaurant = self.context['restaurant']
        # print(validated_data)
        # item_ingredients_data = validated_data.pop('item_ingredients', [])
        item_ingredients_data = validated_data.pop('ingredients', [])
        menu_instance = MenuItem.objects.create(restaurant=restaurant, **validated_data)
        for ingredient in item_ingredients_data:
            try:
                # ItemIngredient.objects.create(item=menu_instance, **ingredient)
                ItemIngredient.objects.create(item=menu_instance, ingredients=ingredient)
            except:
                pass

        return menu_instance

    def update(self, instance, validated_data):
        instance.Item_name = validated_data.get('Item_name', instance.Item_name)
        instance.description = validated_data.get('description', instance.description)
        instance.sub_category = validated_data.get('sub_category', instance.sub_category)
        instance.price = validated_data.get('price', instance.price)
        instance.is_veg = validated_data.get('is_veg', instance.is_veg)
        instance.cover_image = validated_data.get('cover_image', instance.cover_image)
        instance.menu_type = validated_data.get('menu_type', instance.menu_type)

        # item_ingredients_data = validated_data.pop('item_ingredients', [])
        item_ingredients_data = validated_data.pop('ingredients', [])
        for ingredient in item_ingredients_data:
            try:
                # ItemIngredient.objects.create(item=menu_instance, **ingredient)
                ItemIngredient.objects.create(item=instance, ingredients=ingredient)
            except:
                pass

        instance.save()
        return instance

        """
        # Update or create item ingredients
        item_ingredients_data = validated_data.get('item_ingredients', [])
        existing_ingredient_ids = [ingredient.id for ingredient in instance.item_ingredients.all()]
        for ingredient_data in item_ingredients_data:
            ingredient_id = ingredient_data.get('id')
            print(ingredient_id)
            if ingredient_id in existing_ingredient_ids:
                ingredient_instance = ItemIngredient.objects.get(id=ingredient_id)
                ingredient_instance.ingredients = ingredient_data.get('ingredients', ingredient_instance.ingredients)
                ingredient_instance.save()
            else:
                ItemIngredient.objects.create(item=instance, **ingredient_data)

        # Update or create menu item images
        menu_item_images_data = validated_data.get('menu_item_images', [])
        existing_image_ids = [img.id for img in instance.menu_item_images.all()]

        for image_data in menu_item_images_data:
            image_id = image_data.get('id')
            if image_id in existing_image_ids:
                image_instance = MenuItemImages.objects.get(id=image_id)
                image_instance.image = image_data.get('image', image_instance.image)
                image_instance.save()
            else:
                MenuItemImages.objects.create(menu_item=instance, **image_data)

        instance.save()
        return instance
        """


class MenuItemListSerializer(ModelSerializer):
    sub_category = ItemSubCategorySerializer(read_only=True)
    item_ingredients = IngredientSerializer(many=True, required=False)
    menu_type = MenuTypeSerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = '__all__'
        read_only_fields = ['restaurant', ]


class RestaurantSubCategorySerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'icon']


def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.csv', ]
    if not ext.lower() in valid_extensions:
        raise ValidationError('Only csv file can allow to upload')


class MenuUploadCsvSerializer(Serializer):
    data_file = serializers.FileField(validators=[validate_file_extension], required=True)


class UnclaimedRestaurantSerializer(ModelSerializer):
    city = CitySerializer(read_only=True)
    state = StateSerializer(read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'phone_number', 'address', 'location', 'latitude', 'longitude', 'city', 'state', 'zipcode',
            'profile_image', 'business_description',
        ]


class MakeClaimRequestSerializer(ModelSerializer):
    class Meta:
        model = ClamRequest
        fields = ['request_for', ]

    def create(self, validated_data):
        request_by = self.context['request'].user
        menu_instance = ClamRequest.objects.create(request_by=request_by, **validated_data)
        return menu_instance


class OwnerRestaurantListSerializer(ModelSerializer):
    city = CitySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    type = AllBusinessTypesSerializer(read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'phone_number', 'phone_number_2', 'address', 'address_ru', 'location', 'latitude', 'longitude', 'city', 'state', 'zipcode',
            'profile_image', 'business_description', 'is_disabled', 'is_approved', 'type',
        ]


class RestaurantCreateSerializer(ModelSerializer):
    class Meta:
        model = Restaurant
        fields = [
            'name', 'phone_number', 'phone_number_2', 'year_of_established', 'type', 'address', 'address_ru', 'location', 'city', 'state', 'zipcode',
            'latitude', 'longitude', 'profile_image', 'business_description', 'known_for', 'must_order'
        ]


class RaiseBySerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'mobile_number', 'profile_image']


class PublicQuerySerializer(ModelSerializer):
    raise_by = RaiseBySerializer(read_only=True)

    class Meta:
        model = PublicQuery
        fields = '__all__'
        read_only_fields = [
            'id', 'raise_by', 'restaurant', 'question', 'is_answered'
        ]


class ManagerUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'profile_image', 'mobile_number']


class RestaurantManagerSerializer(ModelSerializer):
    manager = ManagerUserSerializer(read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'manager']
        read_only_fields = fields


class SetManagerSerializer(ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['manager', ]


class ManagerCreateSerializer(Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    mobile_number = serializers.CharField(required=True)


class AllServiceSerializer(ModelSerializer):
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


class ServiceSerializer(ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'service_name', 'service_name_ru']


class RestaurantServiceSerializer(ModelSerializer):
    service = ServiceSerializer()

    class Meta:
        model = RestaurantService
        fields = '__all__'


class RestaurantCuisineSerializer(ModelSerializer):
    cuisine = CuisinesSerializer()

    class Meta:
        model = RestaurantCuisines
        fields = '__all__'


class AddServiceSerializer(ModelSerializer):
    class Meta:
        model = RestaurantService
        fields = ['service', ]


class AddCuisinesSerializer(ModelSerializer):
    class Meta:
        model = RestaurantCuisines
        fields = ['cuisine', ]


class AddPaymentModeSerializer(ModelSerializer):
    class Meta:
        model = RestaurantAcceptedPayment
        fields = ['payment', ]


class PaymentModeDetailSerializer(ModelSerializer):
    class Meta:
        model = ModeOfPayment
        fields = '__all__'


class RestaurantPaymentMethodSerializer(ModelSerializer):
    payment = PaymentModeDetailSerializer()

    class Meta:
        model = RestaurantAcceptedPayment
        fields = ['payment', 'id']


class PromotionListSerializer(ModelSerializer):
    class Meta:
        model = Promotion
        fields = [
            'id', 'created_at', 'modified_at', 'title', 'apply_on_everyday', 'offer_type', 'discount', 'is_active'
        ]


class PromotionWeekDaySerializer(ModelSerializer):
    class Meta:
        model = PromotionWeekDay
        fields = [
            'id', 'day'
        ]


class MenuItemDropdownSerializer(ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ('id', 'Item_name')


class PromotionOnItemSerializer(ModelSerializer):
    item = MenuItemDropdownSerializer(read_only=True)

    class Meta:
        model = PromotionOnItem
        fields = [
            'id', 'item'
        ]


class PromotionDetailSerializer(ModelSerializer):
    week_days = PromotionWeekDaySerializer(read_only=True, many=True)
    applicable_on = PromotionOnItemSerializer(read_only=True, many=True)
    days = ListField(child=serializers.CharField(), write_only=True, required=False)
    items = ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = Promotion
        fields = [
            'id', 'created_at', 'modified_at', 'title', 'image', 'apply_on_everyday', 'offer_start_time', 'offer_end_time', 'term_and_condition', 'offer_type', 'discount', 'is_active', 'week_days',
            'applicable_on', 'restaurant', 'days', 'items'
        ]
        read_only_fields = [
            'id', 'created_at', 'modified_at', 'restaurant', 'week_days', 'applicable_on'
        ]

    def create(self, validated_data):
        restaurant = self.context['restaurant']

        days_data = validated_data.pop('days', [])
        items_data = validated_data.pop('items', [])
        promotion_instance = Promotion.objects.create(restaurant=restaurant, **validated_data)
        for day in days_data:
            try:
                PromotionWeekDay.objects.create(promotion=promotion_instance, day=day)
            except Exception as e:
                print(e)
        for item_id in items_data:
            try:
                item = MenuItem.objects.get(id=item_id)
                PromotionOnItem.objects.create(promotion=promotion_instance, item=item)
            except Exception as e:
                print(e)
        return promotion_instance

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.image = validated_data.get('image', instance.image)
        instance.apply_on_everyday = validated_data.get('apply_on_everyday', instance.apply_on_everyday)
        instance.offer_start_time = validated_data.get('offer_start_time', instance.offer_start_time)
        instance.offer_end_time = validated_data.get('offer_end_time', instance.offer_end_time)
        instance.term_and_condition = validated_data.get('term_and_condition', instance.term_and_condition)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.offer_type = validated_data.get('offer_type', instance.offer_type)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        days_data = validated_data.pop('days', [])
        items_data = validated_data.pop('items', [])
        for day in days_data:
            try:
                PromotionWeekDay.objects.create(promotion=instance, day=day)
            except Exception as e:
                print(e)
        for item_id in items_data:
            try:
                item = MenuItem.objects.get(id=item_id)
                PromotionOnItem.objects.create(promotion=instance, item=item)
            except Exception as e:
                print(e)

        instance.save()
        return instance


class CreatedBySerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'mobile_number', 'profile_image']


class EventSerializer(ModelSerializer):
    created_by = CreatedBySerializer()

    class Meta:
        model = Event
        fields = ['id', 'created_by', 'restaurant', 'name', 'description', 'event_image', 'date_time', 'is_approved_by_restaurant']
        read_only_fields = ['id', 'created_by', 'restaurant']


class AddEventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ['name', 'description', 'event_image', 'date_time', ]

    def create(self, validated_data):
        created_by = self.context.get('request').user
        restaurant = self.context.get('restaurant')
        event = Event(created_by=created_by, restaurant=restaurant, is_approved_by_restaurant=True, **validated_data)
        event.save()
        return event


class CreateAdsSerializer(ModelSerializer):
    class Meta:
        model = AdsBanner
        fields = [
            'cover_img', 'description'
        ]

    def create(self, validated_data):
        restaurant = self.context.get('restaurant')
        ads = AdsBanner(restaurant=restaurant, **validated_data)
        ads.save()
        return ads
