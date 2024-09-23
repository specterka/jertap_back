from django.contrib import admin
from core.models import Restaurant, Category, SubCategory, RestaurantImages, Review, MenuItem, ItemIngredient, MenuItemImages, ClamRequest, Service, RestaurantService, RequestDetailsUpdate, Cuisines, \
    MenuType

# Register your models here.
admin.site.register(Restaurant)
admin.site.register(Cuisines)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(RestaurantImages)
admin.site.register(Review)
admin.site.register(MenuItem)
admin.site.register(ItemIngredient)
admin.site.register(MenuItemImages)
admin.site.register(ClamRequest)
admin.site.register(Service)
admin.site.register(RestaurantService)
admin.site.register(RequestDetailsUpdate)
admin.site.register(MenuType)