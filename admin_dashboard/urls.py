from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from admin_dashboard.views import AdminLoginWithEmailApi, AdminLoginWithMobileNumberApi, DashboardApi, CollaboratorList, AddCollaborator, CollaboratorDetails, CategoryList, AddCategory, \
    CategoryDetails, \
    SubCategoryList, AddSubCategory, SubCategoryDetails, ClaimRequests, ClaimDetails, UserList, UserDetails, RestaurantList, RestaurantDetails, AdsList, AdsDetails, CategoryForDropdown, \
    AdminNotifications, AdminNotificationsMarkAsRead, UserDisputeResolutionList, UserDisputeDetail, ReportedReviews, RespondReportedReview, CreateRestaurant, RestaurantTimeList, UpdateRestaurantTime, \
    RestaurantImageUpload, DeleteRestaurantImage, AllServices, RestaurantServiceList, RemoveRestaurantService, AddRestaurantService, AddService, ServiceDetails, DetailsUpdateRequestList, \
    DetailsUpdateRequestDetails, CuisinesList, AddCuisines, CuisinesDetails, AddMenuType, MenuTypeList, DeleteMenuType, AllCuisinesList, AllPaymentModes, RestaurantCuisineList, \
    RestaurantPaymentMethodList, AddRestaurantCuisines, AddRestaurantAcceptedPaymentMethod, RemoveRestaurantCuisine, RemovePaymentMethod, AdminRestaurantMenuItemList, AdminUploadMenuCsvApi, \
    AdminMenuItemDetail, AdminCreateMenuItem, AdminUpdateMenuItem, AdminDeleteIngredients, AdminRemoveMenuItem, AdminRestaurantSubCategoryList
from owner_dashboard.views import AllBusinessTypes, AllCitys, AllStates
from users.views import VerifyLoginOTP

app_name = 'admin_dashboard'
admin_dashboard_api_v1_urlpatterns = [
    path('login-with-email/', AdminLoginWithEmailApi.as_view(), name='Owner Login With Email'),
    path('login-with-mobile-number/', AdminLoginWithMobileNumberApi.as_view(), name='Owner Login With mobile number'),
    path('verify-login-otp/', VerifyLoginOTP.as_view(), name='Verify login otp for admin'),
    path('token-refresh/', TokenRefreshView.as_view(), name='refresh jwt auth token'),

    path('dashboard-data/', DashboardApi.as_view(), name='Dashboard data'),

    path('collaborator-list/', CollaboratorList.as_view(), name='Collaborator List'),
    path('add-collaborator/', AddCollaborator.as_view(), name='Add new collaborator'),
    path('collaborator/<int:id>/', CollaboratorDetails.as_view(), name='edit or delete collaborator'),

    path('category-list/', CategoryList.as_view(), name='Category List'),
    path('add-category/', AddCategory.as_view(), name='Add new Category'),
    path('category/<int:id>/', CategoryDetails.as_view(), name='edit or delete Category'),

    path('sub-category-list/', SubCategoryList.as_view(), name='Subcategory List'),
    path('category-dropdown/', CategoryForDropdown.as_view(), name='Categories for dropdown'),
    path('add-sub-category/', AddSubCategory.as_view(), name='Add new Subcategory'),
    path('sub-category/<int:id>/', SubCategoryDetails.as_view(), name='edit or delete Subcategory'),

    path('claim-list/', ClaimRequests.as_view(), name='Restaurant claim List'),
    path('claim/<int:id>/', ClaimDetails.as_view(), name='edit or delete Claim Request'),

    path('user-list/', UserList.as_view(), name='All user list'),
    path('user/<int:id>/', UserDetails.as_view(), name='User details, edit, delete'),

    path('cuisines-list/', CuisinesList.as_view(), name='Cuisines List'),
    path('add-cuisines/', AddCuisines.as_view(), name='Add new Cuisines'),
    path('cuisines/<int:id>/', CuisinesDetails.as_view(), name='edit or delete cuisines'),

    path('restaurant-list/', RestaurantList.as_view(), name='All restaurant list'),

    path('restaurant-create/', CreateRestaurant.as_view(), name='Add restaurant'),
    path('restaurant/<int:id>/', RestaurantDetails.as_view(), name='Restaurant details, edit, delete'),

    path('restaurant-images-upload/<int:restaurant_id>/', RestaurantImageUpload.as_view(), name='Restaurant images upload'),
    path('restaurant-image-delete/<int:restaurant_id>/<int:id>/', DeleteRestaurantImage.as_view(), name='Restaurant images delete'),

    path('all-business-types/', AllBusinessTypes.as_view(), name='all business types'),
    path('all-cities/', AllCitys.as_view(), name='all Cities'),
    path('all-states/', AllStates.as_view(), name='all states'),

    path('all-services/<int:restaurant_id>/', AllServices.as_view(), name='All services'),
    path('all-cuisines/<int:restaurant_id>/', AllCuisinesList.as_view(), name='all cuisines'),
    path('all-payment-modes/<int:restaurant_id>/', AllPaymentModes.as_view(), name='all payment modes'),

    path('restaurant-services/<int:restaurant_id>/', RestaurantServiceList.as_view(), name='Restaurant services'),
    path('restaurant-cuisine/<int:restaurant_id>/', RestaurantCuisineList.as_view(), name='Restaurant cuisine'),
    path('restaurant-payment-methods/<int:restaurant_id>/', RestaurantPaymentMethodList.as_view(), name='Restaurant payment methods'),

    path('add-services/<int:restaurant_id>/', AddRestaurantService.as_view(), name='Add Restaurant services'),
    path('add-cuisine/<int:restaurant_id>/', AddRestaurantCuisines.as_view(), name='Add Restaurant cuisine'),
    path('add-payment-method/<int:restaurant_id>/', AddRestaurantAcceptedPaymentMethod.as_view(), name='Add Restaurant Payment Method'),

    path('remove-services/<int:restaurant_id>/<int:id>/', RemoveRestaurantService.as_view(), name='Remove Restaurant services'),
    path('remove-cuisine/<int:restaurant_id>/<int:id>/', RemoveRestaurantCuisine.as_view(), name='Remove Restaurant cuisine'),
    path('remove-payment-method/<int:restaurant_id>/<int:id>/', RemovePaymentMethod.as_view(), name='Remove Restaurant Payment Method'),

    path('restaurant-timings/<int:restaurant_id>/', RestaurantTimeList.as_view(), name='Restaurant timings'),
    path('restaurant-time-update/<int:restaurant_id>/<int:id>/', UpdateRestaurantTime.as_view(), name='Restaurant timings update'),

    path('service/', AddService.as_view(), name='Add new service'),
    path('service/<int:id>/', ServiceDetails.as_view(), name='Edit or delete service'),

    path('ads/', AdsList.as_view(), name='ADS list and create'),
    path('ads-detail/<int:id>/', AdsDetails.as_view(), name='ADS edit and delete'),

    path('admin-notifications/', AdminNotifications.as_view(), name='Admin notifications'),
    path('admin-notifications/mark-as_read/<int:id>/', AdminNotificationsMarkAsRead.as_view(), name='Admin notifications mark as read'),

    path('user-dispute-list/', UserDisputeResolutionList.as_view(), name='User displacement list'),
    path('user-dispute/<int:id>/', UserDisputeDetail.as_view(), name='User displacement edit, delete'),

    path('reported-reviews/', ReportedReviews.as_view(), name='list of reported reviews'),
    path('reported-reviews-action/<int:id>/', RespondReportedReview.as_view(), name='delete or update status of reported reviews'),

    path('restaurant-details-change-requests/', DetailsUpdateRequestList.as_view(), name='list of restaurant details update request'),
    path('restaurant-details-change-request/<int:id>/', DetailsUpdateRequestDetails.as_view(), name='delete or approve restaurant details update request'),

    path('menu-type-list/', MenuTypeList.as_view(), name='Menu type List'),
    path('add-menu-type/', AddMenuType.as_view(), name='Add new Menu type'),
    path('menu-type/<int:id>/', DeleteMenuType.as_view(), name='delete Menu type'),

    path('restaurant-menu/<int:restaurant_id>/', AdminRestaurantMenuItemList.as_view(), name='menu item list for restaurant'),
    path('restaurant-menu-item/<int:restaurant_id>/<int:id>/', AdminMenuItemDetail.as_view(), name='Restaurant menu item details'),
    path('restaurant-upload-menu-csv/<int:restaurant_id>/', AdminUploadMenuCsvApi.as_view(), name='Bulk upload menu items'),
    path('restaurant-add-menu-item/<int:restaurant_id>/', AdminCreateMenuItem.as_view(), name='Restaurant menu item create'),
    path('restaurant-update-menu-item/<int:restaurant_id>/<int:id>/', AdminUpdateMenuItem.as_view(), name='Restaurant menu item update'),
    path('restaurant-delete-menu-item-ingredient/<int:restaurant_id>/<int:id>/', AdminDeleteIngredients.as_view(), name='Delete menu item ingredients'),
    path('restaurant-menu-item/delete/<int:restaurant_id>/<int:id>/', AdminRemoveMenuItem.as_view(), name='Delete menu item'),
    path('restaurant-sub-categories/<int:restaurant_id>/', AdminRestaurantSubCategoryList.as_view(), name='Sub category list for menu items'),

]
