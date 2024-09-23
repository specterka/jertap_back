from django.urls import path

from owner_dashboard.views import CategoryCount, AllCategoryList, AddRestaurantCategory, RestaurantMenuItemList, RemoveMenuItem, RestaurantReviewList, ReviewDetails, AddReviewReplay, \
    RestaurantNotificationList, MarkAsReadNotification, AvgMonthlyRating, CollaboratorList, QAList, CreateQA, UpdateQA, DeleteQA, RestaurantAddress, RestaurantTimeList, UpdateRestaurantTime, \
    RestaurantBasicDetails, RestaurantImageUpload, DeleteRestaurantImage, MenuItemDetail, CreateMenuItem, UpdateMenuItem, DeleteIngredients, DeleteItemImages, RestaurantSubCategoryList, \
    UploadMenuCsvApi, UnclaimedRestaurantList, MakeClaimRequest, OwnerRestaurantList, CreateRestaurantApi, PublicQueryList, ReplayPublicQuery, RestaurantManager, ExistingManagerList, SetManager, \
    CreateManager, AllServices, RestaurantServiceList, RemoveRestaurantService, AddRestaurantService, CuisinesList, MenuTypeList, AllCuisinesList, AllBusinessTypes, AllCitys, AllStates, \
    AllPaymentModes, AddRestaurantCuisines, RemoveRestaurantCuisine, RestaurantCuisineList, AddRestaurantAcceptedPaymentMethod, RemovePaymentMethod, RestaurantPaymentMethodList, PromotionList, \
    PromotionDetail, DeletePromotion, CreatePromotion, UpdatePromotion, RemovePromotionWeekDay, RemoveItemFromPromotion, MenuItemDropdown, CreateEvent, DeleteEvent, UpdateEvent, AllEvents, \
    CreateAdsBanner

app_name = 'owner_dashboard'
owner_dashboard_api_v1_urlpatterns = [

    path('cuisines-list/', CuisinesList.as_view(), name='Cuisines List'),
    path('create-restaurant/', CreateRestaurantApi.as_view(), name='Create restaurant'),
    path('collaborators/', CollaboratorList.as_view(), name='Collaborator list'),
    path('restaurants-unclaimed/', UnclaimedRestaurantList.as_view(), name='Unclaimed Restaurants list'),
    path('add-claim-request/', MakeClaimRequest.as_view(), name='Add Restaurants claim request'),
    path('owner-restaurants/', OwnerRestaurantList.as_view(), name="Owner's restaurant list"),
    path('dashboard-category-count/<int:id>/', CategoryCount.as_view(), name='restaurant category count'),
    path('all-category/<int:restaurant_id>/', AllCategoryList.as_view(), name='all category'),
    path('add-restaurant-category/', AddRestaurantCategory.as_view(), name='add category to restaurant'),
    path('restaurant-sub-categories/<int:restaurant_id>/', RestaurantSubCategoryList.as_view(), name='Sub category list for menu items'),
    path('restaurant-menu/<int:restaurant_id>/', RestaurantMenuItemList.as_view(), name='menu item list for restaurant'),
    path('restaurant-upload-menu-csv/<int:restaurant_id>/', UploadMenuCsvApi.as_view(), name='Bulk upload menu items'),
    path('monthly-rating/<int:restaurant_id>/', AvgMonthlyRating.as_view(), name='Avg Monthly Rating and count for past 12 months'),
    path('menu-types/', MenuTypeList.as_view(), name='Menu types'),
    path('restaurant-menu-item/<int:restaurant_id>/<int:id>/', MenuItemDetail.as_view(), name='Restaurant menu item details'),
    path('restaurant-add-menu-item/<int:restaurant_id>/', CreateMenuItem.as_view(), name='Restaurant menu item create'),
    path('restaurant-update-menu-item/<int:restaurant_id>/<int:id>/', UpdateMenuItem.as_view(), name='Restaurant menu item update'),
    path('restaurant-delete-menu-item-ingredient/<int:restaurant_id>/<int:id>/', DeleteIngredients.as_view(), name='Delete menu item ingredients'),
    path('restaurant-delete-menu-item-image/<int:restaurant_id>/<int:id>/', DeleteItemImages.as_view(), name='Delete menu item image'),
    path('restaurant-menu-item/delete/<int:restaurant_id>/<int:id>/', RemoveMenuItem.as_view(), name='Delete menu item'),
    path('restaurant-review-list/<int:restaurant_id>/', RestaurantReviewList.as_view(), name='Restaurant reviews'),
    path('restaurant-review-detail/<int:restaurant_id>/<int:id>/', ReviewDetails.as_view(), name='Restaurant reviews details and report review'),
    path('replay-to-restaurant-review/', AddReviewReplay.as_view(), name='Add Restaurant review replay'),
    path('restaurant-image-delete/<int:restaurant_id>/<int:id>/', DeleteRestaurantImage.as_view(), name='Restaurant images delete'),
    path('restaurant-upload-images/<int:restaurant_id>/', RestaurantImageUpload.as_view(), name='Restaurant images upload'),
    path('restaurant-timings/<int:restaurant_id>/', RestaurantTimeList.as_view(), name='Restaurant timings'),
    path('restaurant-time-update/<int:restaurant_id>/<int:id>/', UpdateRestaurantTime.as_view(), name='Restaurant timings update'),
    path('restaurant-address/<int:id>/', RestaurantAddress.as_view(), name='Restaurant address get and update'),
    path('restaurant-details/<int:id>/', RestaurantBasicDetails.as_view(), name='Restaurant basic details get and update'),
    path('notifications/<int:restaurant_id>/', RestaurantNotificationList.as_view(), name='Unread Notifications List'),
    path('mark-as-read/<int:restaurant_id>/<int:id>/', MarkAsReadNotification.as_view(), name='Notification mark as read'),

    path('manager/<int:id>/', RestaurantManager.as_view(), name='Manager details and remove'),
    path('existing-users', ExistingManagerList.as_view(), name='Existing users list'),
    path('set-manager/<int:id>/', SetManager.as_view(), name='Set existing user as manager'),
    path('create-manager/<int:restaurant_id>/', CreateManager.as_view(), name='Create new manager user'),

    path('all-business-types/', AllBusinessTypes.as_view(), name='all business types'),
    path('all-cities/', AllCitys.as_view(), name='all Cities'),
    path('all-states/', AllStates.as_view(), name='all states'),

    path('all-services/<int:restaurant_id>/', AllServices.as_view(), name='All services'),
    path('all-cuisines/<int:restaurant_id>/', AllCuisinesList.as_view(), name='all cuisines'),
    path('all-payment-modes/<int:restaurant_id>/', AllPaymentModes.as_view(), name='all payment modes'),
    path('restaurant-services/<int:restaurant_id>/', RestaurantServiceList.as_view(), name='Restaurant services'),
    path('restaurant-cuisine/<int:restaurant_id>/', RestaurantCuisineList.as_view(), name='Restaurant cuisine'),
    path('restaurant-payment-methods/<int:restaurant_id>/', RestaurantPaymentMethodList.as_view(), name='Restaurant payment methods'),
    path('remove-services/<int:restaurant_id>/<int:id>/', RemoveRestaurantService.as_view(), name='Remove Restaurant services'),
    path('remove-cuisine/<int:restaurant_id>/<int:id>/', RemoveRestaurantCuisine.as_view(), name='Remove Restaurant cuisine'),
    path('remove-payment-method/<int:restaurant_id>/<int:id>/', RemovePaymentMethod.as_view(), name='Remove Restaurant Payment Method'),
    path('add-services/<int:restaurant_id>/', AddRestaurantService.as_view(), name='Add Restaurant services'),
    path('add-cuisine/<int:restaurant_id>/', AddRestaurantCuisines.as_view(), name='Add Restaurant cuisine'),
    path('add-payment-method/<int:restaurant_id>/', AddRestaurantAcceptedPaymentMethod.as_view(), name='Add Restaurant Payment Method'),

    path('q&a-list/<int:restaurant_id>/', QAList.as_view(), name='Q&A list'),
    path('q&a-create/<int:restaurant_id>/', CreateQA.as_view(), name='Q&A create'),
    path('q&a-update/<int:restaurant_id>/<int:id>/', UpdateQA.as_view(), name='Q&A update'),
    path('q&a-delete/<int:restaurant_id>/<int:id>/', DeleteQA.as_view(), name='Q&A delete'),
    path('public-queries/<int:restaurant_id>/', PublicQueryList.as_view(), name='Not answered Public Query list'),
    path('answer-public-queries/<int:restaurant_id>/<int:id>/', ReplayPublicQuery.as_view(), name='Replay Public Query'),

    path('promotions/<int:restaurant_id>/', PromotionList.as_view(), name='Promotion List'),
    path('create-promotions/<int:restaurant_id>/', CreatePromotion.as_view(), name='Add Promotion'),
    path('promotions/<int:restaurant_id>/<int:id>/', PromotionDetail.as_view(), name='Promotion Details'),
    path('update-promotions/<int:restaurant_id>/<int:id>/', UpdatePromotion.as_view(), name='Update Promotion'),
    path('delete-promotions/<int:restaurant_id>/<int:id>/', DeletePromotion.as_view(), name='Delete Promotion'),
    path('delete-promotion-day/<int:restaurant_id>/<int:id>/', RemovePromotionWeekDay.as_view(), name='Delete Promotion day'),
    path('delete-promotion-item/<int:restaurant_id>/<int:id>/', RemoveItemFromPromotion.as_view(), name='Delete Promotion item'),
    path('menu-item-dropdown/<int:restaurant_id>/', MenuItemDropdown.as_view(), name='Menu Item Dropdown'),

    path('all-events/<int:restaurant_id>/', AllEvents.as_view(), name="All Events"),
    path('create-event/<int:restaurant_id>/', CreateEvent.as_view(), name="Add Event"),
    path('delete-event/<int:restaurant_id>/<int:id>/', DeleteEvent.as_view(), name="Delete Event"),
    path('update-event/<int:restaurant_id>/<int:id>/', UpdateEvent.as_view(), name="Update Event"),

    path('add-ads-banner-request/', CreateAdsBanner.as_view(), name="Create Ads Banner Request"),
]
