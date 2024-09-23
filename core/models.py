import requests
from django.core.files import File
from io import BytesIO
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from users.models import TimeStampedModel, User
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError


# Create your models here.
def category_images_dir(instance, filename):
    return f'Category/Image/{instance.id}_{filename}'


class Category(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    name_ru = models.CharField(max_length=100, unique=True, null=True, blank=True)
    icon = models.ImageField(upload_to=category_images_dir, blank=True, null=True)


def sub_category_images_dir(instance, filename):
    return f'SubCategory/Image/{instance.id}_{filename}'


class SubCategory(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    name_ru = models.CharField(max_length=100, unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, related_name='sub_categories', on_delete=models.CASCADE)
    icon = models.ImageField(upload_to=sub_category_images_dir, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['category']),
        ]


# class RestaurantType:
#     CAFE = 'cafe'
#     RESTAURANT = 'restaurant'
#     CHOICES = (
#         (CAFE, _("cafe")),
#         (RESTAURANT, _("restaurant"))
#     )


def restaurant_profile_pic_dir(instance, filename):
    return f'Restaurant/{instance.id}_{filename}'


class Cuisines(TimeStampedModel):
    cuisines = models.CharField(max_length=100, unique=True)
    cuisines_ru = models.CharField(max_length=100, unique=True)


class BusinessType(TimeStampedModel):
    type = models.TextField(unique=True)
    type_ru = models.TextField()


class City(TimeStampedModel):
    city = models.TextField(unique=True)
    city_ru = models.TextField()


class State(TimeStampedModel):
    state = models.TextField(unique=True)
    state_ru = models.TextField()


class Restaurant(TimeStampedModel):
    name = models.CharField(max_length=100, blank=True, null=True)
    owner = models.ForeignKey(User, blank=True, null=True, related_name='restaurants', on_delete=models.SET_NULL)
    manager = models.OneToOneField(User, blank=True, null=True, related_name='manager_restaurant', on_delete=models.SET_NULL)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    phone_number_2 = models.CharField(max_length=20, blank=True, null=True)
    business_whatsapp = models.CharField(max_length=20, blank=True, null=True)
    business_instagram = models.TextField(blank=True, null=True)
    business_2gis = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    address_ru = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    location_point = models.PointField(blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, related_name='city_restaurants', on_delete=models.SET_NULL)
    state = models.ForeignKey(State, blank=True, null=True, related_name='state_restaurants', on_delete=models.SET_NULL)
    zipcode = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    profile_image = models.ImageField(blank=True, null=True, upload_to=restaurant_profile_pic_dir)
    business_description = models.TextField(blank=True, null=True)
    # cuisines = models.ForeignKey(Cuisines, blank=True, null=True, related_name='cuisines_restaurants', on_delete=models.SET_NULL)
    type = models.ForeignKey(BusinessType, blank=True, null=True, on_delete=models.SET_NULL)
    known_for = models.TextField(blank=True, null=True)
    must_order = models.TextField(blank=True, null=True)
    year_of_established = models.IntegerField(blank=True, null=True)
    average_bill = models.IntegerField(blank=True, null=True)
    business_capacity = models.IntegerField(blank=True, null=True)
    business_email = models.EmailField(blank=True, null=True)
    business_website = models.TextField(blank=True, null=True)
    is_disabled = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['name']),
            models.Index(fields=['type']),
        ]

    def save(self, *args, **kwargs):
        self.location_point = Point(self.longitude, self.latitude)
        super(Restaurant, self).save(*args, **kwargs)

    def __str__(self):
        return self.name if self.name else " "

    @property
    def average_rating(self):
        ratings = self.restaurant_reviews.all()
        if not ratings:
            return 0
        total_ratings = sum([rating.rating for rating in ratings])
        return total_ratings / len(ratings)

    @property
    def rating_count(self):
        return self.restaurant_reviews.all().count()

    @property
    def category_count(self):
        return self.restaurant_categories.all().count()

    @property
    def menu_item_count(self):
        return self.menu_items.all().count()


class RestaurantCuisines(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant, related_name='cuisines', on_delete=models.CASCADE)
    cuisine = models.ForeignKey(Cuisines, related_name='restaurants', on_delete=models.CASCADE)

    def clean(self):
        if self.restaurant.cuisines.count() >= 5:
            raise ValidationError("Cannot add more than 5 cuisines to a restaurant.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate before saving
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (('restaurant', 'cuisine'),)
        indexes = [
            models.Index(fields=['restaurant']),
        ]


class ClamRequest(TimeStampedModel):
    request_by = models.ForeignKey(User, related_name='clam_requests', on_delete=models.SET_NULL, null=True, blank=True)
    request_for = models.ForeignKey(Restaurant, related_name='clam_requests', on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_approved:
            self.request_for.owner = self.request_by
            self.request_for.save()

        super().save(*args, **kwargs)


class ModeOfPayment(TimeStampedModel):
    payment_name = models.TextField(unique=True)
    payment_name_ru = models.TextField()


class RestaurantAcceptedPayment(TimeStampedModel):
    payment = models.ForeignKey(ModeOfPayment, related_name='accepted_by_restaurants', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, related_name='restaurant_payment_modes', db_index=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('payment', 'restaurant'),)
        indexes = [
            models.Index(fields=['restaurant']),
        ]


class Service(TimeStampedModel):
    service_name = models.CharField(unique=True, max_length=255)
    service_name_ru = models.CharField(max_length=255, unique=True, blank=True, null=True)

    def __str__(self):
        return self.service_name


class RestaurantService(TimeStampedModel):
    service = models.ForeignKey(Service, related_name='service_restaurnats', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, related_name='restaurant_services', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('service', 'restaurant'),)
        indexes = [
            models.Index(fields=['restaurant']),
        ]


class Favorite(TimeStampedModel):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, related_name='liked_by', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'restaurant'),)
        indexes = [
            models.Index(fields=['restaurant']),
            models.Index(fields=['user']),
        ]


def restaurant_pic_dir(instance, filename):
    return f'Restaurant/{instance.restaurant.id}_{filename}'


class RestaurantImages(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant, related_name='restaurant_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=restaurant_pic_dir)

    class Meta:
        indexes = [
            models.Index(fields=['restaurant']),
        ]


class MenuType(TimeStampedModel):
    type = models.CharField(max_length=255, unique=True)
    type_ru = models.CharField(max_length=255)


def meny_item_cover_pic_dir(instance, filename):
    return f'MenuItem/CoverImage/{instance.restaurant.id}_{filename}'


class MenuItem(TimeStampedModel):
    Item_name = models.TextField(blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, blank=True, null=True, on_delete=models.CASCADE, related_name="menu_items")
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(blank=True, null=True, upload_to=meny_item_cover_pic_dir)
    sub_category = models.ForeignKey(SubCategory, blank=True, null=True, on_delete=models.CASCADE, related_name="sub_category_items")
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_veg = models.BooleanField(blank=True, null=True)
    menu_type = models.ForeignKey(MenuType, blank=True, null=True, on_delete=models.SET_NULL, related_name='items')

    class Meta:
        indexes = [
            models.Index(fields=['restaurant']),
        ]

    def __str__(self):
        return self.Item_name if self.Item_name else " "

    def save_image_from_url(self, image_url):
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                # Open the image file using BytesIO
                image_data = BytesIO(response.content)

                # Save the image to the ImageField
                self.cover_image.save(f"image.jpg", File(image_data), save=True)
        except Exception as e:
            print(f"Error downloading image from URL: {e}")


class ItemIngredient(TimeStampedModel):
    item = models.ForeignKey(MenuItem, related_name="item_ingredients", on_delete=models.CASCADE)
    ingredients = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['item']),
        ]


def menu_item_images_dir(instance, filename):
    return f'MenuItem/Images/{instance.menu_item.id}_{filename}'


class MenuItemImages(TimeStampedModel):
    menu_item = models.ForeignKey(MenuItem, related_name='menu_item_images', on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, upload_to=menu_item_images_dir)

    def image_save_from_url(self, image_url):
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                # Open the image file using BytesIO
                image_data = BytesIO(response.content)

                # Save the image to the ImageField
                self.image.save(f"image.jpg", File(image_data), save=True)
        except Exception as e:
            print(f"Error downloading image from URL: {e}")


def banner_images_dir(instance, filename):
    return f'banners/{instance.id}_{filename}'


class RestaurantCategory(TimeStampedModel):
    category = models.ForeignKey(Category, related_name='category_restaurants', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, related_name='restaurant_categories', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('category', 'restaurant'),)
        indexes = [
            models.Index(fields=['restaurant']),
        ]


class AdsBanner(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant, related_name='restaurant_ads_banner', on_delete=models.CASCADE, blank=True, null=True)
    cover_img = models.ImageField(blank=True, null=True, upload_to=banner_images_dir)
    priority = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)


class Review(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='restaurant_reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True, null=True)
    reported = models.BooleanField(default=False)
    report_rejected = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_by_user')

    class Meta:
        indexes = [
            models.Index(fields=['restaurant']),
        ]


class ReviewReply(TimeStampedModel):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='review_replays')
    replay = models.TextField(blank=True, null=True)


WEEKDAYS = [
    ('Sunday', 'Sunday'),
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
]


class RestaurantTimings(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='restaurants_timings')
    weekday = models.CharField(
        choices=WEEKDAYS,
    )
    from_hour = models.TimeField(blank=True, null=True)
    to_hour = models.TimeField(blank=True, null=True)

    class Meta:
        unique_together = (('weekday', 'restaurant'),)
        indexes = [
            models.Index(fields=['restaurant']),
        ]
        ordering = ['id']


class QA(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='restaurant_q_a')
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['restaurant']),
        ]


class RequestDetailsUpdate(TimeStampedModel):
    request_by = models.ForeignKey(User, related_name='request_details', on_delete=models.CASCADE, blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, related_name='restaurant_details_update', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    address = models.TextField(blank=True, null=True)
    address_ru = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, related_name='city_restaurants_update', on_delete=models.SET_NULL)
    state = models.ForeignKey(State, blank=True, null=True, related_name='state_restaurants_update', on_delete=models.SET_NULL)
    zipcode = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_approved:
            if self.name is not None:
                self.restaurant.name = self.name
            if self.address is not None:
                self.restaurant.address = self.address
            if self.address_ru is not None:
                self.restaurant.address_ru = self.address_ru
            if self.location is not None:
                self.restaurant.location = self.location
            if self.latitude is not None:
                self.restaurant.latitude = self.latitude
            if self.longitude is not None:
                self.restaurant.longitude = self.longitude
            if self.city is not None:
                self.restaurant.city = self.city
            if self.state is not None:
                self.restaurant.state = self.state
            if self.zipcode is not None:
                self.restaurant.zipcode = self.zipcode
            self.restaurant.save()
        super(RequestDetailsUpdate, self).save(*args, **kwargs)
