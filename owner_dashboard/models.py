from django.db import models
from core.models import Restaurant, MenuItem, WEEKDAYS
from users.models import TimeStampedModel, User


# Create your models here.
class RestaurantNotification(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant, related_name='notifications', on_delete=models.CASCADE)
    title = models.TextField(default='')
    message = models.TextField(default='')
    is_read = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['restaurant']),
        ]


class PublicQuery(TimeStampedModel):
    raise_by = models.ForeignKey(User, related_name='user_queries', on_delete=models.CASCADE, blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, related_name='restaurant_queries', on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    is_answered = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['restaurant']),
        ]


OFFERS = [
    ('percentage', 'percentage'),
    ('fixed_amount', 'fixed_amount'),
    ('bogo', 'bogo'),

]


class Promotion(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='promotions')
    title = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to='promotion_images')
    apply_on_everyday = models.BooleanField(default=False)
    offer_start_time = models.TimeField(null=True, blank=True)
    offer_end_time = models.TimeField(null=True, blank=True)
    term_and_condition = models.TextField(blank=True, null=True)
    offer_type = models.CharField(max_length=20, choices=OFFERS)
    discount = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=False)


class PromotionWeekDay(TimeStampedModel):
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='week_days')
    day = models.CharField(choices=WEEKDAYS, max_length=10,)

    class Meta:
        indexes = [
            models.Index(fields=['promotion']),
        ]
        unique_together = (('promotion', 'day'),)


class PromotionOnItem(TimeStampedModel):
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='applicable_on')
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='offers')

    class Meta:
        indexes = [
            models.Index(fields=['promotion']),
        ]
        unique_together = (('promotion', 'item'),)
