import django_filters
import pandas as pd
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView, ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_405_METHOD_NOT_ALLOWED, HTTP_400_BAD_REQUEST
from admin_dashboard.models import AdminNotification, UserDisputeResolution
from admin_dashboard.serializers import AdminEmailLoginSerializer, AdminMobileLoginSerializer, CollaboratorSerializer, CategorySerializer, SubCategorySerializer, ClaimRequestSerializer, \
    UserListSerializer, UserDetailSerializer, RestaurantSerializer, RestaurantDetailSerializer, AdsSerializer, AddSubCategorySerializer, AdminNotificationSerializer, UserDisputeResolutionSerializer, \
    ReportedReviewSerializer, RestaurantTimeSerializer, RestaurantImagesSerializer, AllServiceSerializer, RestaurantServiceSerializer, AddServiceSerializer, ServiceSerializer, \
    DetailsUpdateRequestSerializer, CuisinesSerializer, RestaurantDetailUpdateSerializer, MenuTypeSerializer
from core.models import Category, SubCategory, ClamRequest, Restaurant, AdsBanner, Review, RestaurantTimings, RestaurantImages, Service, RestaurantService, RequestDetailsUpdate, Cuisines, MenuType, \
    ModeOfPayment, RestaurantCuisines, RestaurantAcceptedPayment, BusinessType, MenuItem, ItemIngredient, RestaurantCategory
from owner_dashboard.models import RestaurantNotification
from owner_dashboard.serializers import AllCuisinesListSerializer, PaymentModeSerializer, RestaurantCuisineSerializer, RestaurantPaymentMethodSerializer, AddCuisinesSerializer, \
    AddPaymentModeSerializer
from owner_dashboard.views import CustomPagination, create_restaurant_times, RestaurantMenuItemList, UploadMenuCsvApi, MenuItemDetail, CreateMenuItem, UpdateMenuItem, DeleteIngredients, \
    RemoveMenuItem, RestaurantSubCategoryList
from users.email_and_sms import send_email, send_message
from users.models import TwoFactorVerificationOTP, Collaborator, User
from rest_framework.permissions import IsAdminUser
from owner_dashboard.tasks import create_menu_items


# Create your views here.

class AdminLoginWithEmailApi(GenericAPIView):
    serializer_class = AdminEmailLoginSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user', None)
        try:
            user.two_factor_otp.delete()
        except Exception as e:
            pass
        if user:
            otp_obj = TwoFactorVerificationOTP.objects.generate(user=user)
            # send an email with verification code
            send_email('Login Verification Code', f'<p><strong style="color: #336699;">{otp_obj.code}</strong> is your login verification code, It will valid for only 5 minutes</p>', [user.email, ])
            return Response({'details': 'otp sent successfully!'}, status=HTTP_200_OK)
        else:
            return Response({'details': 'User not found!'}, status=HTTP_200_OK)


class AdminLoginWithMobileNumberApi(GenericAPIView):
    serializer_class = AdminMobileLoginSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user', None)
        try:
            user.two_factor_otp.delete()
        except Exception as e:
            pass
        if user:
            otp_obj = TwoFactorVerificationOTP.objects.generate(user=user)
            # send sms with verification code
            send_message(phones=user.mobile_number, message=f'{otp_obj.code} is your login verification otp, It will valid for five minutes')

            return Response({'details': 'otp sent successfully!'}, status=HTTP_200_OK)
        else:
            return Response({'details': 'User not found!'}, status=HTTP_200_OK)


class DashboardApi(GenericAPIView):
    # permission_classes = [IsAdminUser, ]

    def get(self, request, *args, **kwargs):
        data = {
            'total_restaurant': Restaurant.objects.filter(is_approved=True).count(),
            'active_restaurant': Restaurant.objects.filter(is_approved=True, is_disabled=False).count(),
            'owner_count': User.objects.filter(is_cafe_owner=True).count(),
            'visitor_count': User.objects.filter(is_visitor=True).count(),
            'pending_claim_requests': ClamRequest.objects.filter(is_approved=False).count(),
            'pending_restaurant_approval': Restaurant.objects.filter(is_approved=False).count(),
            'pending_details_update_requests': RequestDetailsUpdate.objects.filter(is_approved=False).count(),
            'types': [],
        }

        for typ in BusinessType.objects.all():
            data['types'].append({
                'type': typ.type,
                'type_ru': typ.type_ru,
                'count': Restaurant.objects.filter(type=typ).count()
            })

        return Response(data, status=HTTP_200_OK)


class CollaboratorFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='custom_search')

    def custom_search(self, queryset, name, value):
        return queryset.filter(
            Q(full_name__icontains=value) |
            Q(youtube_channel_link__icontains=value) |
            Q(fb_profile_link__icontains=value) |
            Q(insta_profile_link__icontains=value) |
            Q(twitter_profile_link__icontains=value)
        )

    class Meta:
        model = Collaborator
        fields = ['search', ]


class CollaboratorList(ListAPIView):
    serializer_class = CollaboratorSerializer
    permission_classes = [IsAdminUser, ]
    pagination_class = CustomPagination
    queryset = Collaborator.objects.all().order_by('full_name')
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CollaboratorFilter
    ordering_fields = ['full_name', 'id', 'created_at', 'modified_at']


class AddCollaborator(CreateAPIView):
    serializer_class = CollaboratorSerializer
    permission_classes = [IsAdminUser, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'details': 'Collaborator created'}, status=HTTP_201_CREATED, headers=headers)


class CollaboratorDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = CollaboratorSerializer
    permission_classes = [IsAdminUser, ]
    lookup_field = 'id'
    queryset = Collaborator.objects.all()

    def put(self, request, *args, **kwargs):
        return Response({'details': 'method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'Collaborator deleted'}, status=HTTP_200_OK)


class CategoryFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='custom_search')

    def custom_search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)

    class Meta:
        model = Category
        fields = ['search', ]


class CategoryList(ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser, ]
    pagination_class = CustomPagination
    queryset = Category.objects.all().order_by('id')
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CategoryFilter
    ordering_fields = ['name', 'id', 'created_at', 'modified_at']


class CategoryForDropdown(ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser, ]
    queryset = Category.objects.all().order_by('name')


class AddCategory(CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'details': 'Category created'}, status=HTTP_201_CREATED, headers=headers)


class CategoryDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser, ]
    lookup_field = 'id'
    queryset = Category.objects.all()

    def put(self, request, *args, **kwargs):
        return Response({'details': 'method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'Category deleted'}, status=HTTP_200_OK)


class SubCategoryFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='custom_search')

    def custom_search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(category__name__icontains=value))

    class Meta:
        model = SubCategory
        fields = ['search', ]


class SubCategoryList(ListAPIView):
    serializer_class = SubCategorySerializer
    permission_classes = [IsAdminUser, ]
    pagination_class = CustomPagination
    queryset = SubCategory.objects.all().order_by('category')
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = SubCategoryFilter
    ordering_fields = ['id', 'name', 'category__name', 'created_at', 'modified_at']


class AddSubCategory(CreateAPIView):
    serializer_class = AddSubCategorySerializer
    permission_classes = [IsAdminUser, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'details': 'Subcategory created'}, status=HTTP_201_CREATED, headers=headers)


class SubCategoryDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = SubCategorySerializer
    permission_classes = [IsAdminUser, ]
    lookup_field = 'id'
    queryset = SubCategory.objects.all()

    def put(self, request, *args, **kwargs):
        return Response({'details': 'method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AddSubCategorySerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'Subcategory deleted'}, status=HTTP_200_OK)


class ClaimFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='custom_search')

    def custom_search(self, queryset, name, value):
        return queryset.filter(Q(request_for__name__icontains=value) | Q(request_by__email__icontains=value) | Q(request_by__username__icontains=value))

    class Meta:
        model = ClamRequest
        fields = ['search', ]


class ClaimRequests(ListAPIView):
    serializer_class = ClaimRequestSerializer
    permission_classes = [IsAdminUser, ]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ClaimFilter
    pagination_class = CustomPagination
    ordering_fields = ['is_approved', 'id', 'created_at', 'modified_at']

    def get_queryset(self):
        queryset = ClamRequest.objects.all().order_by('-id')
        is_approved = self.request.query_params.get('is_approved')
        if is_approved is not None and is_approved in ['True', 'False']:
            queryset = queryset.filter(is_approved=is_approved)
        return queryset


class ClaimDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = ClaimRequestSerializer
    permission_classes = [IsAdminUser, ]
    lookup_field = 'id'

    queryset = ClamRequest.objects.all()

    def put(self, request, *args, **kwargs):
        return Response({'details': 'method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'Subcategory deleted'}, status=HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        try:
            if instance.is_approved:
                # send claim approval mail
                send_email('Restaurant Claim Approved',
                           f'<p>Congratulations, Your restaurant claim request for <strong style="color: #336699;">{instance.request_for.name}</strong> was approved by Jertap. You can modify or add restaurant details, menu, timings and assign manager using your restaurant dashboard</p>',
                           [instance.request_by.email, ])

            if not instance.is_approved:
                # send claim rejection email
                send_email('Restaurant Claim Rejected',
                           f'<p>Your restaurant claim request for <strong style="color: #336699;">{instance.request_for.name}</strong> was not approved due by Jertap. You can contect Jertap support for further query</p>',
                           [instance.request_by.email, ])
        except Exception as e:
            print(e)

        return Response({'details': 'Claim request updated'}, status=HTTP_200_OK)


class UserSearchFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='custom_search')

    def custom_search(self, queryset, name, value):
        return queryset.filter(Q(username__icontains=value) | Q(email__icontains=value) | Q(mobile_number__icontains=value))

    class Meta:
        model = User
        fields = ['search', ]


class UserList(ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser, ]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = UserSearchFilter
    ordering_fields = ['id', 'username', 'email', 'first_name', 'last_name', 'created_at', 'modified_at']

    def get_queryset(self):
        queryset = User.objects.all().order_by('-id')
        is_visitor = self.request.query_params.get('is_visitor')
        is_cafe_owner = self.request.query_params.get('is_cafe_owner')
        is_cafe_manager = self.request.query_params.get('is_cafe_manager')

        if is_visitor is not None and is_visitor in ['True', 'False']:
            queryset = queryset.filter(is_visitor=is_visitor)
        if is_cafe_owner is not None and is_cafe_owner in ['True', 'False']:
            queryset = queryset.filter(is_cafe_owner=is_cafe_owner)
        if is_cafe_manager is not None and is_cafe_manager in ['True', 'False']:
            queryset = queryset.filter(is_cafe_manager=is_cafe_manager)

        return queryset


class UserDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    queryset = User.objects.all()

    def put(self, request, *args, **kwargs):
        return Response({'details': 'method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'User deleted'}, status=HTTP_200_OK)

    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response({'details': 'User details updated'}, status=HTTP_200_OK)


class RestaurantSearchFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='custom_search')

    def custom_search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(city__city__icontains=value))

    class Meta:
        model = Restaurant
        fields = ['search', ]


class RestaurantList(ListAPIView):
    serializer_class = RestaurantSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = RestaurantSearchFilter
    ordering_fields = ['name', 'id', 'city', 'created_at', 'modified_at']

    def get_queryset(self):
        queryset = Restaurant.objects.all().order_by('name')
        is_approved = self.request.query_params.get('is_approved')

        if is_approved is not None and is_approved in ['True', 'False']:
            queryset = queryset.filter(is_approved=is_approved)

        return queryset


class CreateRestaurant(CreateAPIView):
    serializer_class = RestaurantDetailUpdateSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        restaurant = serializer.save()
        create_restaurant_times(restaurant)

        return Response({'details': 'restaurant created!'}, status=HTTP_201_CREATED)


class RestaurantDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = RestaurantDetailSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    queryset = Restaurant.objects.all()

    def put(self, request, *args, **kwargs):
        return Response({'details': 'method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'Restaurant deleted'}, status=HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = RestaurantDetailUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response({'details': 'Restaurant details updated'}, status=HTTP_200_OK)


class RestaurantImageUpload(CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = RestaurantImagesSerializer

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return Response({'details': 'restaurant not found'}, status=HTTP_400_BAD_REQUEST)
        serializer = RestaurantImagesSerializer(data=request.data)

        if serializer.is_valid():
            RestaurantImages(image=request.data.get('image'), restaurant=restaurant).save()
            return Response({'details': 'image uploaded successfully'}, status=HTTP_201_CREATED)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class DeleteRestaurantImage(DestroyAPIView):
    permission_class = [IsAdminUser]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return RestaurantImages.objects.none()
        data = RestaurantImages.objects.filter(restaurant=restaurant)
        return data

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'details': 'Image deleted successfully'}, status=HTTP_200_OK)


class RestaurantTimeList(ListAPIView):
    serializer_class = RestaurantTimeSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return RestaurantTimings.objects.none()

        return RestaurantTimings.objects.filter(restaurant=restaurant).order_by('id')


class UpdateRestaurantTime(UpdateAPIView):
    serializer_class = RestaurantTimeSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return RestaurantTimings.objects.none()

        return RestaurantTimings.objects.filter(restaurant=restaurant).order_by('id')

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({'details': 'timings updated successfully'}, status=HTTP_200_OK)


# class AdsSearchFilter(django_filters.FilterSet):
#     search = django_filters.CharFilter(method='custom_search')
#
#     def custom_search(self, queryset, name, value):
#         return queryset.filter(description__icontains=value)
#
#     class Meta:
#         model = AdsBanner
#         fields = ['search', ]


class AddService(CreateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'details': 'New Service added'}, status=HTTP_201_CREATED)


class ServiceDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    queryset = Service.objects.all()

    def put(self, request, *args, **kwargs):
        return Response({'details': 'method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'Service deleted'}, status=HTTP_200_OK)


class AllServices(ListAPIView):
    serializer_class = AllServiceSerializer
    permission_classes = [IsAdminUser]
    queryset = Service.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            restaurant = None
        context.update({"restaurant": restaurant})
        return context


class AllCuisinesList(ListAPIView):
    serializer_class = AllCuisinesListSerializer
    permission_classes = [IsAdminUser]
    queryset = Cuisines.objects.all().order_by('id')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        restaurant_id = self.kwargs.get('restaurant_id')
        # context.update({"request": self.request})
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            restaurant = None
        context.update({"restaurant": restaurant})
        return context


class AllPaymentModes(ListAPIView):
    serializer_class = PaymentModeSerializer
    permission_classes = [IsAdminUser]
    queryset = ModeOfPayment.objects.all().order_by('id')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        restaurant_id = self.kwargs.get('restaurant_id')
        # context.update({"request": self.request})
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            restaurant = None
        context.update({"restaurant": restaurant})
        return context


class RestaurantServiceList(ListAPIView):
    serializer_class = RestaurantServiceSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
            return RestaurantService.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return RestaurantService.objects.none()


class RestaurantCuisineList(ListAPIView):
    serializer_class = RestaurantCuisineSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
            return RestaurantCuisines.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return RestaurantCuisines.objects.none()


class RestaurantPaymentMethodList(ListAPIView):
    serializer_class = RestaurantPaymentMethodSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
            return RestaurantAcceptedPayment.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return RestaurantAcceptedPayment.objects.none()


class RemoveRestaurantService(DestroyAPIView):
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
            return RestaurantService.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return RestaurantService.objects.none()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'details': 'Service removed'}, status=HTTP_200_OK)


class AddRestaurantService(GenericAPIView):
    serializer_class = AddServiceSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return Response({'details': 'Restaurant not found!'}, status=HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            service = Service.objects.get(id=serializer.data['service'])
        except:
            return Response({'details': 'Service not found!'}, status=HTTP_400_BAD_REQUEST)
        try:
            RestaurantService.objects.get(restaurant=restaurant, service=service)
            return Response({'details': 'Service already added!'}, status=HTTP_400_BAD_REQUEST)
        except:
            RestaurantService(restaurant=restaurant, service=service).save()
            return Response({'details': 'Service added successfully!'}, status=HTTP_201_CREATED)


class AddRestaurantCuisines(GenericAPIView):
    serializer_class = AddCuisinesSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return Response({'details': 'Restaurant not found!'}, status=HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            cuisine = Cuisines.objects.get(id=serializer.data['cuisine'])
        except:
            return Response({'details': 'Cuisines not found!'}, status=HTTP_400_BAD_REQUEST)
        try:
            RestaurantCuisines.objects.get(restaurant=restaurant, cuisine=cuisine)
            return Response({'details': 'Cuisine already added!'}, status=HTTP_400_BAD_REQUEST)
        except:
            RestaurantCuisines(restaurant=restaurant, cuisine=cuisine).save()
            return Response({'details': 'Cuisine added successfully!'}, status=HTTP_201_CREATED)


class RemoveRestaurantCuisine(DestroyAPIView):
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
            return RestaurantCuisines.objects.filter(restaurant=restaurant)
        except:
            return RestaurantService.objects.none()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'details': 'Cuisine removed'}, status=HTTP_200_OK)


class AddRestaurantAcceptedPaymentMethod(CreateAPIView):
    serializer_class = AddPaymentModeSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return Response({'details': 'Restaurant not found!'}, status=HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payment = ModeOfPayment.objects.get(id=serializer.data['payment'])
        except:
            return Response({'details': 'Payment method not found!'}, status=HTTP_400_BAD_REQUEST)
        try:
            RestaurantAcceptedPayment.objects.get(restaurant=restaurant, payment=payment)
            return Response({'details': 'Payment method already added!'}, status=HTTP_400_BAD_REQUEST)
        except:
            RestaurantAcceptedPayment(restaurant=restaurant, payment=payment).save()
            return Response({'details': 'Payment method added successfully!'}, status=HTTP_201_CREATED)


class RemovePaymentMethod(DestroyAPIView):
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
            return RestaurantAcceptedPayment.objects.filter(restaurant=restaurant)
        except:
            return RestaurantAcceptedPayment.objects.none()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'details': 'Payment method removed'}, status=HTTP_200_OK)


class AdsList(ListCreateAPIView):
    serializer_class = AdsSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['id', 'priority', 'created_at', 'modified_at']

    # filter_backends = [DjangoFilterBackend]
    # filterset_class = AdsSearchFilter

    def get_queryset(self):
        queryset = AdsBanner.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')

        if is_active is not None and is_active in ['True', 'False']:
            queryset = queryset.filter(is_active=is_active)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'details': 'Ads banner created!'}, status=HTTP_201_CREATED, )


class AdsDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = AdsSerializer
    permission_classes = [IsAdminUser]
    queryset = AdsBanner.objects.all()
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        return Response({'details': 'method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'Ads banner deleted'}, status=HTTP_200_OK)


class AdminNotifications(ListAPIView):
    serializer_class = AdminNotificationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return AdminNotification.objects.filter(is_read=False).order_by('-id')[:20]


class AdminNotificationsMarkAsRead(UpdateAPIView):
    serializer_class = AdminNotificationSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    queryset = AdminNotification.objects.all()

    def put(self, request, *args, **kwargs):
        return Response({'details': 'Method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_read = True
        instance.save()
        return Response({'details': 'Marked as read successfully'}, status=HTTP_200_OK)


class UserDisputeResolutionList(ListAPIView):
    serializer_class = UserDisputeResolutionSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['id', 'is_resolved', 'created_at', 'modified_at']

    def get_queryset(self):
        query_set = UserDisputeResolution.objects.all().order_by('id')
        is_resolved = self.request.query_params.get('is_resolved')
        if is_resolved and is_resolved in ['True', 'False']:
            query_set = query_set.filter(is_resolved=is_resolved)
        return query_set


class UserDisputeDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = UserDisputeResolutionSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    queryset = UserDisputeResolution.objects.all()

    def put(self, request, *args, **kwargs):
        return Response({'details': 'method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'User Dispute Detail deleted'}, status=HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance.save()
        # send query answer email
        send_email('Your query replay',
                   f"""
                           <p><strong style="color: #336699;">{instance.query}</strong></p>
                           <p style="color: #808080;">{instance.replay}</p>
                            """,
                   [instance.query_by.email, ])
        return Response({'details': 'Query answered successfully'}, status=HTTP_200_OK)


class ReportedReviews(ListAPIView):
    serializer_class = ReportedReviewSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['id', 'created_at', 'modified_at']

    def get_queryset(self):
        queryset = Review.objects.filter(reported=True, report_rejected=False).order_by('id')
        return queryset


class RespondReportedReview(RetrieveUpdateDestroyAPIView):
    serializer_class = ReportedReviewSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def get_queryset(self):
        queryset = Review.objects.filter(reported=True, report_rejected=False)
        return queryset

    def put(self, request, *args, **kwargs):
        return Response({'details': 'method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'Review deleted'}, status=HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.report_rejected = True
        instance.save()
        return Response({'details': 'Review report rejected'}, status=HTTP_200_OK)


class DetailsUpdateRequestList(ListAPIView):
    serializer_class = DetailsUpdateRequestSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['id', 'is_approved']

    def get_queryset(self):
        queryset = RequestDetailsUpdate.objects.all().order_by('id')
        is_approved = self.request.query_params.get('is_approved')
        if is_approved is not None and is_approved in ['True', 'False']:
            queryset = queryset.filter(is_approved=is_approved)
        return queryset


class DetailsUpdateRequestDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = DetailsUpdateRequestSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    queryset = RequestDetailsUpdate.objects.all()

    def put(self, request, *args, **kwargs):
        return Response({'details': 'method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'Details update request deleted'}, status=HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_approved = True
        instance.save()
        # send mail to requested user
        send_email('Restaurant details changes approved',
                   f'<p>your request for update restaurant details update was successfully approved by admin. You can review updated details from restaurant dashboard</p>',
                   [instance.request_by.email, ])
        # add restaurant notification
        try:
            RestaurantNotification(restaurant=instance.restaurant, title='Details updated', message='Your request for restaurant detail update has been approved by admin.').save()
        except Exception as e:
            print(e)

        return Response({'details': 'Restaurant details update request approved'}, status=HTTP_200_OK)


class CuisinesList(ListAPIView):
    serializer_class = CuisinesSerializer
    permission_classes = [IsAdminUser]
    queryset = Cuisines.objects.all().order_by('-id')
    filter_backends = [OrderingFilter]
    ordering_fields = ['cuisines', 'cuisines_ru']


class AddCuisines(CreateAPIView):
    serializer_class = CuisinesSerializer
    permission_classes = [IsAdminUser, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'details': 'Cuisines created'}, status=HTTP_201_CREATED, headers=headers)


class CuisinesDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = CuisinesSerializer
    permission_classes = [IsAdminUser, ]
    lookup_field = 'id'
    queryset = Cuisines.objects.all()

    def put(self, request, *args, **kwargs):
        return Response({'details': 'method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'Cuisines deleted'}, status=HTTP_200_OK)


class AddMenuType(CreateAPIView):
    serializer_class = MenuTypeSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'details': 'Menu Type added'}, status=HTTP_201_CREATED)


class MenuTypeList(ListAPIView):
    serializer_class = MenuTypeSerializer
    permission_classes = [IsAdminUser, ]
    queryset = MenuType.objects.all().order_by('id')


class DeleteMenuType(RetrieveUpdateDestroyAPIView):
    serializer_class = MenuTypeSerializer
    permission_classes = [IsAdminUser, ]
    queryset = MenuType.objects.all().order_by('id')
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        return Response({'details': 'method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'Menu type deleted'}, status=HTTP_200_OK)


class AdminRestaurantMenuItemList(RestaurantMenuItemList):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
            return MenuItem.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return MenuItem.objects.none()


class AdminUploadMenuCsvApi(UploadMenuCsvApi):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data_file = serializer.validated_data["data_file"]
        if data_file:
            df = pd.read_csv(data_file)
            # print(df.keys())
            if all(key in df.keys() for key in ["Item_name", "description", "cover_image", "sub_category", "price", "is_veg", 'item_ingredients', 'menu_type']):
                df_json = df.to_json()
                try:
                    restaurant = Restaurant.objects.get(id=restaurant_id)
                except:
                    return Response({'details': "You don't have a restaurant"}, status=HTTP_200_OK)
                # call celery function
                create_menu_items.delay(restaurant.id, df_json)
                return Response({'details': 'Data uploading started'}, status=HTTP_200_OK)
            else:
                return Response({'details': 'Invalid CSV file formate'}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({'details': 'CSV file required'}, status=HTTP_400_BAD_REQUEST)


class AdminMenuItemDetail(MenuItemDetail):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return MenuItem.objects.none()
        return MenuItem.objects.filter(restaurant=restaurant)


class AdminCreateMenuItem(CreateMenuItem):
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            restaurant = None
        context.update({"restaurant": restaurant})
        return context


class AdminUpdateMenuItem(UpdateMenuItem):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return MenuItem.objects.none()
        return MenuItem.objects.filter(restaurant=restaurant)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            restaurant = None
        context.update({"restaurant": restaurant})
        return context


class AdminDeleteIngredients(DeleteIngredients):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return ItemIngredient.objects.none()

        return ItemIngredient.objects.filter(item__restaurant=restaurant)


class AdminRemoveMenuItem(RemoveMenuItem):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
            return MenuItem.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return MenuItem.objects.none()


class AdminRestaurantSubCategoryList(RestaurantSubCategoryList):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return SubCategory.objects.none()

        restaurant_category_ids = RestaurantCategory.objects.filter(restaurant=restaurant).values_list('category__id', flat=True).distinct()
        data = SubCategory.objects.filter(category__id__in=restaurant_category_ids).order_by('category')
        return data