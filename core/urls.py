from django.urls import path

from core.views import HomeCategoryList, HomeRecentReviewApi, \
    RestaurantSearchApi, AdsBannerApi, NearByRestaurantApi, RestaurantListAPI, AddToFavorite, RemoveFavorite, RestaurantDetail, RestaurantMenu, ItemDetail, RestaurantReview, AddRestaurantReview, \
    UpdateReview, FavoriteRestaurant, RestaurantQAList, AskPublicQuery, MenuTypeList, AddUserDispute, CityList, AllServices, AllCuisinesList

app_name = 'core'
core_api_v1_urlpatterns = [
    path('all-city/', CityList.as_view(), name='city list'),
    path('all-category-list/', HomeCategoryList.as_view(), name='restaurant all category list'),
    path('all-service-list/', AllServices.as_view(), name='all service list'),
    path('all-cuisine-list/', AllCuisinesList.as_view(), name='all cuisine list'),
    path('home-review-list/', HomeRecentReviewApi.as_view(), name='home review listing'),
    path('home-restaurant-search/', RestaurantSearchApi.as_view(), name='Home Restaurant search'),
    path('home-ads-banners/', AdsBannerApi.as_view(), name='Home Ads banner list'),
    path('home-nearby_restaurant/', NearByRestaurantApi.as_view(), name='Home nearby restaurant list'),
    path('restaurants/', RestaurantListAPI.as_view(), name='Restaurants list and filters'),

    path('add-to-favorite/<int:restaurant_id>/', AddToFavorite.as_view(), name='Add Restaurant to Favorite'),
    path('remove-favorite/<int:restaurant_id>/', RemoveFavorite.as_view(), name='Remove Restaurant from Favorite'),

    path('restaurant/<int:id>/', RestaurantDetail.as_view(), name='Restaurant Detail'),
    path('menu-types/', MenuTypeList.as_view(), name='Menu Type List'),
    path('menu/<int:restaurant_id>/', RestaurantMenu.as_view(), name='Restaurant Menu'),
    path('menu-item/<int:id>/', ItemDetail.as_view(), name='Menu Item details'),
    path('reviews/<int:restaurant_id>/', RestaurantReview.as_view(), name='Restaurant reviews'),
    path('add-review/<int:restaurant_id>/', AddRestaurantReview.as_view(), name='Add Restaurant reviews'),
    path('update-review/<int:id>/', UpdateReview.as_view(), name='Update Restaurant reviews'),

    path('favorite-restaurants/', FavoriteRestaurant.as_view(), name='Favorite Restaurant List'),

    path('restaurant-qa/<int:restaurant_id>/', RestaurantQAList.as_view(), name='restaurant default Q&A list'),
    path('add-query/<int:restaurant_id>/', AskPublicQuery.as_view(), name='Ask query to particular restaurant'),

    path('add-user-dispute/', AddUserDispute.as_view(), name='Ask query to admin'),

]
