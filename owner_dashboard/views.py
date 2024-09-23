import django_filters
from django.db.models import Avg, Q
from django.utils.timezone import make_aware
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateTimeFilter
from rest_framework.filters import OrderingFilter
from rest_framework.generics import RetrieveAPIView, ListAPIView, GenericAPIView, DestroyAPIView, CreateAPIView, UpdateAPIView, RetrieveUpdateAPIView, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_405_METHOD_NOT_ALLOWED
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from datetime import datetime, timedelta
from core.models import Restaurant, Category, RestaurantCategory, MenuItem, Review, QA, RestaurantTimings, RestaurantImages, ItemIngredient, MenuItemImages, SubCategory, Service, RestaurantService, \
    ClamRequest, RequestDetailsUpdate, Cuisines, MenuType, BusinessType, City, State, ModeOfPayment, RestaurantCuisines, RestaurantAcceptedPayment
from jertap_backend.settings import SOCIAL_SECRET
from owner_dashboard.models import RestaurantNotification, PublicQuery, Promotion, PromotionWeekDay, PromotionOnItem
from owner_dashboard.serializers import CategoryCountSerializer, AllCategoryListSerializer, AddRestaurantCategorySerializer, MenuItemListSerializer, UserReviewListSerializer, ReviewDetailSerializer, \
    AddReviewReplaySerializer, RestaurantNotificationSerializer, CollaboratorListSerializer, QASerializer, RestaurantAddressSerializer, RestaurantTimeSerializer, RestaurantBasicDetailSerializer, \
    RestaurantImagesSerializer, MenuItemDetailSerializer, RestaurantSubCategorySerializer, MenuUploadCsvSerializer, UnclaimedRestaurantSerializer, MakeClaimRequestSerializer, \
    OwnerRestaurantListSerializer, RestaurantCreateSerializer, PublicQuerySerializer, RestaurantManagerSerializer, ManagerUserSerializer, SetManagerSerializer, ManagerCreateSerializer, \
    AllServiceSerializer, RestaurantServiceSerializer, AddServiceSerializer, AddressUpdateRequestSerializer, CuisinesSerializer, RestaurantBasicDetailUpdateSerializer, MenuTypeSerializer, \
    AllCuisinesListSerializer, AllBusinessTypesSerializer, CitySerializer, StateSerializer, PaymentModeSerializer, AddCuisinesSerializer, RestaurantCuisineSerializer, AddPaymentModeSerializer, \
    RestaurantPaymentMethodSerializer, PromotionListSerializer, PromotionDetailSerializer, MenuItemDropdownSerializer, EventSerializer, AddEventSerializer, CreateAdsSerializer
from users.email_and_sms import send_email
from users.models import Collaborator, User
from users.permissions import IsRestaurantOwner, IsOwnerOrManager
from social.models import Event
import pandas as pd

from users.serializers import generate_username
from .tasks import create_menu_items


# Create your views here.
class CustomPagination(PageNumberPagination):
    page_size = 15


class CategoryCount(RetrieveAPIView):
    serializer_class = CategoryCountSerializer
    lookup_field = 'id'
    permission_classes = [IsOwnerOrManager]

    def get_queryset(self):
        return Restaurant.objects.filter(Q(owner=self.request.user) | Q(manager=self.request.user))


class AllCategoryList(ListAPIView):
    serializer_class = AllCategoryListSerializer
    permission_classes = [IsOwnerOrManager]
    queryset = Category.objects.all().order_by('name')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        restaurant_id = self.kwargs.get('restaurant_id')
        # context.update({"request": self.request})
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            restaurant = None
        context.update({"restaurant": restaurant})
        return context


class AddRestaurantCategory(GenericAPIView):
    serializer_class = AddRestaurantCategorySerializer
    permission_classes = [IsOwnerOrManager]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            category = Category.objects.get(id=serializer.data['category'])
        except Category.DoesNotExist:
            return Response({'details': 'Category does not exists'}, status=HTTP_400_BAD_REQUEST)
        try:
            restaurant_obj = Restaurant.objects.get(id=serializer.data['restaurant'])
            if self.request.user == restaurant_obj.owner or self.request.user == restaurant_obj.manager:
                restaurant = restaurant_obj
            else:
                return Response({'details': "You can't add category to other's restaurant"}, status=HTTP_400_BAD_REQUEST)
        except Restaurant.DoesNotExist:
            return Response({'details': 'Restaurant does not exists'}, status=HTTP_400_BAD_REQUEST)

        if RestaurantCategory.objects.filter(restaurant=restaurant, category=category).exists():
            return Response({'details': 'Category already exists'}, status=HTTP_400_BAD_REQUEST)
        else:
            res_cat = RestaurantCategory(restaurant=restaurant, category=category)
            res_cat.save()
            return Response({'details': 'Category created'}, status=HTTP_201_CREATED)


class MenuFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='custom_search')

    def custom_search(self, queryset, name, value):
        return queryset.filter(Item_name__icontains=value)

    class Meta:
        model = MenuItem
        fields = ['search', ]


class RestaurantMenuItemList(ListAPIView):
    serializer_class = MenuItemListSerializer
    permission_classes = [IsOwnerOrManager]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = MenuFilter

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
            return MenuItem.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return MenuItem.objects.none()


class RemoveMenuItem(DestroyAPIView):
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
            return MenuItem.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return MenuItem.objects.none()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'details': 'Menu Item deleted successfully'}, status=HTTP_200_OK)


class RestaurantReviewList(ListAPIView):
    serializer_class = UserReviewListSerializer
    permission_classes = [IsOwnerOrManager]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
            data = Review.objects.filter(restaurant=restaurant).order_by('modified_at')
            return data
        except:
            return Review.objects.none()


class ReviewDetails(RetrieveUpdateAPIView):
    serializer_class = ReviewDetailSerializer
    lookup_field = 'id'
    permission_classes = [IsOwnerOrManager]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
            data = Review.objects.filter(restaurant=restaurant).order_by('-id')
            return data
        except:
            return Review.objects.none()

    def put(self, request, *args, **kwargs):
        return Response({'details': 'Method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.reported = True
        instance.save()
        return Response({'details': 'Review reported!'}, status=HTTP_200_OK)


class AddReviewReplay(CreateAPIView):
    serializer_class = AddReviewReplaySerializer
    permission_classes = [IsOwnerOrManager]


class RestaurantNotificationList(ListAPIView):
    serializer_class = RestaurantNotificationSerializer
    permission_classes = [IsOwnerOrManager]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return RestaurantNotification.objects.none()
        return RestaurantNotification.objects.filter(restaurant=restaurant, is_read=False).order_by('-id')[:20]


class MarkAsReadNotification(UpdateAPIView):
    serializer_class = RestaurantNotificationSerializer
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return RestaurantNotification.objects.none()
        return RestaurantNotification.objects.filter(restaurant=restaurant).order_by('-id')

    def put(self, request, *args, **kwargs):
        return Response({'details': 'Method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_read = True
        instance.save()
        return Response({'details': 'Marked as read successfully'}, status=HTTP_200_OK)


def get_month_name(data):
    choices = {
        '1': 'Jan',
        '2': 'Feb',
        '3': 'Mar',
        '4': 'Apr',
        '5': 'May',
        '6': 'Jun',
        '7': 'Jul',
        '8': 'Aug',
        '9': 'Sep',
        '10': 'Oct',
        '11': 'Nov',
        '12': 'Dec',
    }
    return choices.get(data, '')


class AvgMonthlyRating(APIView):
    permission_classes = [IsOwnerOrManager, ]

    def get(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return Response({'details': 'Restaurant does not exist'}, status=HTTP_400_BAD_REQUEST)

        current_month = datetime.now().month
        current_year = datetime.now().year

        data = []
        for i in range(12):
            # Calculate the month and year for each iteration
            month = (current_month - i - 1) % 12 + 1
            if month == 12 and i > 0:
                current_year = current_year - 1
            year = current_year
            rating_count = Review.objects.filter(restaurant=restaurant, created_at__month=month, created_at__year=year).count()
            average = Review.objects.filter(restaurant=restaurant, created_at__month=month, created_at__year=year).aggregate(avg_rating=Avg('rating'))['avg_rating']
            avg_rating = average if average else 0
            data.append({'month': get_month_name(str(month)) + '/' + str(year), 'avg_rating': avg_rating, 'rating_count': rating_count})

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
    serializer_class = CollaboratorListSerializer
    permission_classes = [IsOwnerOrManager]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = CollaboratorFilter

    def get_queryset(self):
        data = Collaborator.objects.filter(is_active=True).order_by('full_name')
        return data


class QAList(ListAPIView):
    serializer_class = QASerializer
    permission_classes = [IsOwnerOrManager]
    pagination_class = CustomPagination

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return QA.objects.none()
        data = QA.objects.filter(restaurant=restaurant).order_by('-id')
        return data


class CreateQA(GenericAPIView):
    serializer_class = QASerializer
    permission_classes = [IsOwnerOrManager]

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return Response({'details': 'Restaurant not found!'}, status=HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        QA(restaurant=restaurant, question=serializer.data['question'], answer=serializer.data['answer']).save()
        return Response({'details': 'Q&A created successfully!'}, status=HTTP_201_CREATED)


class UpdateQA(UpdateAPIView):
    serializer_class = QASerializer
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return QA.objects.none()
        data = QA.objects.filter(restaurant=restaurant).order_by('-id')
        return data

    def put(self, request, *args, **kwargs):
        return Response({'details': 'Method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'details': 'Q&A updated successfully'}, status=HTTP_200_OK)


class DeleteQA(DestroyAPIView):
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return QA.objects.none()
        data = QA.objects.filter(restaurant=restaurant).order_by('-id')
        return data

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'details': 'Q&A deleted successfully'}, status=HTTP_200_OK)


class RestaurantAddress(RetrieveUpdateAPIView):
    serializer_class = RestaurantAddressSerializer
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    # def get_object(self):
    #     restaurant = get_object_or_404(Restaurant, owner=self.request.user)
    #     return restaurant

    def get_queryset(self):
        return Restaurant.objects.filter(Q(owner=self.request.user) | Q(manager=self.request.user))

    def put(self, request, *args, **kwargs):
        return Response({'details': 'Method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        request.data['restaurant'] = instance.id
        request.data['request_by'] = self.request.user.id
        serializer = AddressUpdateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        try:
            RestaurantNotification(restaurant=instance, title='Detail update requested',
                                   message='Your request for restaurant detail update has been submitted. You will receive and email once it will be approved').save()
        except Exception as e:
            print(e)
        return Response({'details': 'Address details update requested'}, status=HTTP_200_OK)


class RestaurantTimeList(ListAPIView):
    serializer_class = RestaurantTimeSerializer
    permission_classes = [IsOwnerOrManager]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return RestaurantTimings.objects.none()

        return RestaurantTimings.objects.filter(restaurant=restaurant).order_by('id')


class UpdateRestaurantTime(UpdateAPIView):
    serializer_class = RestaurantTimeSerializer
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
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


class RestaurantBasicDetails(RetrieveUpdateAPIView):
    serializer_class = RestaurantBasicDetailSerializer
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    # def get_object(self):
    #     restaurant = get_object_or_404(Restaurant, owner=self.request.user)
    #     return restaurant

    def get_queryset(self):
        return Restaurant.objects.filter(Q(owner=self.request.user) | Q(manager=self.request.user))

    def put(self, request, *args, **kwargs):
        return Response({'details': 'Method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        mutable_data = request.data.copy()
        if 'name' in request.data:
            name = mutable_data.pop('name', None)
            if isinstance(name, str):
                name_str = name
            else:
                name_str = name[0] if len(name) > 0 else name
            RequestDetailsUpdate(restaurant=instance, name=name_str, request_by=self.request.user).save()
            try:
                RestaurantNotification(restaurant=instance, title='Detail update requested',
                                       message='Your request for restaurant detail update has been submitted. You will receive and emali once it will be approved').save()
            except Exception as e:
                print(e)
        serializer = RestaurantBasicDetailUpdateSerializer(instance, data=mutable_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class RestaurantImageUpload(CreateAPIView):
    permission_classes = [IsOwnerOrManager]
    serializer_class = RestaurantImagesSerializer

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return Response({'details': 'restaurant not found'}, status=HTTP_400_BAD_REQUEST)
        serializer = RestaurantImagesSerializer(data=request.data)

        if serializer.is_valid():
            RestaurantImages(image=request.data.get('image'), restaurant=restaurant).save()
            return Response({'details': 'image uploaded successfully'}, status=HTTP_201_CREATED)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class DeleteRestaurantImage(DestroyAPIView):
    permission_class = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return RestaurantImages.objects.none()
        data = RestaurantImages.objects.filter(restaurant=restaurant)
        return data

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'details': 'Image deleted successfully'}, status=HTTP_200_OK)


class MenuItemDetail(RetrieveAPIView):
    serializer_class = MenuItemListSerializer
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return MenuItem.objects.none()
        return MenuItem.objects.filter(restaurant=restaurant)


class CreateMenuItem(CreateAPIView):
    serializer_class = MenuItemDetailSerializer
    permission_classes = [IsOwnerOrManager]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            restaurant = None
        context.update({"restaurant": restaurant})
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'details': 'Item created'}, status=HTTP_201_CREATED, headers=headers)


class UpdateMenuItem(UpdateAPIView):
    serializer_class = MenuItemDetailSerializer
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return MenuItem.objects.none()
        return MenuItem.objects.filter(restaurant=restaurant)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            restaurant = None
        context.update({"restaurant": restaurant})
        return context

    def put(self, request, *args, **kwargs):
        return Response({'details': 'Method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #
    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         instance._prefetched_objects_cache = {}
    #
    #     return Response({'details': 'Item updated'}, status=HTTP_200_OK)


class DeleteIngredients(DestroyAPIView):
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return ItemIngredient.objects.none()

        return ItemIngredient.objects.filter(item__restaurant=restaurant)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'details': 'Ingredient deleted '}, status=HTTP_200_OK)


class DeleteItemImages(DestroyAPIView):
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return MenuItemImages.objects.none()

        return MenuItemImages.objects.filter(menu_item__restaurant=restaurant)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'details': 'Image deleted '}, status=HTTP_200_OK)


class RestaurantSubCategoryList(ListAPIView):
    serializer_class = RestaurantSubCategorySerializer
    permission_classes = [IsOwnerOrManager]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return SubCategory.objects.none()

        restaurant_category_ids = RestaurantCategory.objects.filter(restaurant=restaurant).values_list('category__id', flat=True).distinct()
        data = SubCategory.objects.filter(category__id__in=restaurant_category_ids).order_by('category')
        return data


class UploadMenuCsvApi(GenericAPIView):
    serializer_class = MenuUploadCsvSerializer
    permission_classes = [IsOwnerOrManager]

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
                    restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
                except:
                    return Response({'details': "You don't have a restaurant"}, status=HTTP_200_OK)
                # call celery function
                create_menu_items.delay(restaurant.id, df_json)
                return Response({'details': 'Data uploading started'}, status=HTTP_200_OK)
            else:
                return Response({'details': 'Invalid CSV file formate'}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({'details': 'CSV file required'}, status=HTTP_400_BAD_REQUEST)


class UnclaimedRestaurantList(ListAPIView):
    serializer_class = UnclaimedRestaurantSerializer
    pagination_class = CustomPagination
    permission_classes = [IsRestaurantOwner]

    def get_queryset(self):
        data = Restaurant.objects.filter(owner=None).order_by('name')
        search = self.request.query_params.get('search')
        if search is not None:
            data = data.filter(Q(name__icontains=search) | Q(address__icontains=search) | Q(city__icontains=search)).distinct()

        return data


class MakeClaimRequest(CreateAPIView):
    serializer_class = MakeClaimRequestSerializer
    permission_classes = [IsRestaurantOwner]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        already_claimed = ClamRequest.objects.filter(request_by=self.request.user, request_for__id=request.data['request_for']).exists()
        if already_claimed:
            return Response({'details': "claim request already added"}, status=HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)

        # send email
        send_email('Restaurant Claim Requested',
                   f'<p>Your restaurant claim request for <strong style="color: #336699;">{instance.request_for.name}</strong> was submitted. You will received and email once admin approve your claim </p>',
                   [instance.request_by.email, ])

        return Response({'details': 'Claim request created'}, status=HTTP_201_CREATED, headers=headers)


class OwnerRestaurantList(ListAPIView):
    serializer_class = OwnerRestaurantListSerializer
    permission_classes = [IsOwnerOrManager]

    def get_queryset(self):
        return Restaurant.objects.filter(Q(Q(owner=self.request.user) | Q(manager=self.request.user))).order_by('-id')


def create_restaurant_times(restaurant):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for d in days:
        try:
            RestaurantTimings(restaurant=restaurant, weekday=d).save()
        except Exception as e:
            print(e)


class CreateRestaurantApi(CreateAPIView):
    serializer_class = RestaurantCreateSerializer
    permission_classes = [IsRestaurantOwner, ]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        restaurant = serializer.save()
        restaurant.owner = self.request.user
        restaurant.save()
        create_restaurant_times(restaurant)
        # Send mail to Super admin

        return Response({'details': 'restaurant created!'}, status=HTTP_201_CREATED)


class PublicQueryList(ListAPIView):
    serializer_class = PublicQuerySerializer
    pagination_class = CustomPagination
    permission_classes = [IsOwnerOrManager]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return PublicQuery.objects.none()

        return PublicQuery.objects.filter(restaurant=restaurant, is_answered=False).order_by('id')


class ReplayPublicQuery(UpdateAPIView):
    serializer_class = PublicQuerySerializer
    lookup_field = 'id'
    permission_classes = [IsOwnerOrManager]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return PublicQuery.objects.none()

        return PublicQuery.objects.filter(restaurant=restaurant, is_answered=False).order_by('id')

    def put(self, request, *args, **kwargs):
        return Response({'details': 'Method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance.is_answered = True
        instance.save()
        # send query answer email
        send_email('Your query replay',
                   f"""
                   <p><strong style="color: #336699;">{instance.question}</strong></p>
                   <p style="color: #808080;">{instance.answer}</p>
                    """,
                   [instance.raise_by.email, ])
        return Response({'details': 'Query answered successfully'}, status=HTTP_200_OK)


class RestaurantManager(RetrieveUpdateAPIView):
    serializer_class = RestaurantManagerSerializer
    permission_classes = [IsRestaurantOwner]
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Restaurant.objects.filter(owner=self.request.user)
        else:
            return Restaurant.objects.none()

    def put(self, request, *args, **kwargs):
        return Response({'details': 'Method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.manager = None
        instance.save()
        return Response({'details': 'Manager removed successfully'}, status=HTTP_200_OK)


class ExistingManagerList(ListAPIView):
    serializer_class = ManagerUserSerializer
    permission_classes = [IsRestaurantOwner]

    def get_queryset(self):
        data = User.objects.all().order_by('username')
        search = self.request.query_params.get('search')
        if search is not None:
            data = data.filter(Q(email__icontains=search) | Q(mobile_number__icontains=search)).distinct().order_by('email')[:10]
            return data
        else:
            return User.objects.none()


class SetManager(UpdateAPIView):
    serializer_class = SetManagerSerializer
    permission_classes = [IsRestaurantOwner]
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Restaurant.objects.filter(owner=self.request.user)
        else:
            return Restaurant.objects.none()

    def put(self, request, *args, **kwargs):
        return Response({'details': 'Method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.manager is not None:
            return Response({'details': 'Remove existing manager to set new'}, status=HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=request.data['manager'])
            if user.is_cafe_owner:
                return Response({'details': 'Owner account can not be manager'}, status=HTTP_400_BAD_REQUEST)
            user.is_cafe_manager = True
            user.save()
        except:
            return Response({'details': 'User not found '}, status=HTTP_400_BAD_REQUEST)
        try:
            restaurant = Restaurant.objects.get(manager=user)
            return Response({'details': 'User is already manager of another restaurant'}, status=HTTP_400_BAD_REQUEST)
        except:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'details': 'Manager set successfully'}, status=HTTP_200_OK)


class CreateManager(CreateAPIView):
    serializer_class = ManagerCreateSerializer
    permission_classes = [IsRestaurantOwner]

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id, owner=self.request.user)
        except:
            return Response({'details': 'Restaurant not found!'}, status=HTTP_400_BAD_REQUEST)

        if restaurant.manager is not None:
            return Response({'details': 'Remove existing manager to set new'}, status=HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        username = serializer.validated_data["username"]
        mobile_number = serializer.validated_data["mobile_number"]

        users_with_email = User.objects.filter(email__iexact=email)
        if users_with_email.exists():
            return Response({"details": "User already exist with this email"}, status=HTTP_400_BAD_REQUEST)
        users_with_mobile = User.objects.filter(mobile_number__iexact=mobile_number)
        if users_with_mobile.exists():
            return Response({"details": "User already exist with this mobile number"}, status=HTTP_400_BAD_REQUEST)

        user = User(email=email, username=generate_username(username), mobile_number=mobile_number, is_cafe_manager=True, password=SOCIAL_SECRET)
        user.save()
        restaurant.manager = user
        restaurant.save()
        return Response({'details': 'Manager created successfully!'}, status=HTTP_201_CREATED)


class AllServices(ListAPIView):
    serializer_class = AllServiceSerializer
    permission_classes = [IsOwnerOrManager]
    queryset = Service.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            restaurant = None
        context.update({"restaurant": restaurant})
        return context


class AllCuisinesList(ListAPIView):
    serializer_class = AllCuisinesListSerializer
    permission_classes = [IsOwnerOrManager]
    queryset = Cuisines.objects.all().order_by('id')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        restaurant_id = self.kwargs.get('restaurant_id')
        # context.update({"request": self.request})
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            restaurant = None
        context.update({"restaurant": restaurant})
        return context


class AllPaymentModes(ListAPIView):
    serializer_class = PaymentModeSerializer
    permission_classes = [IsOwnerOrManager]
    queryset = ModeOfPayment.objects.all().order_by('id')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        restaurant_id = self.kwargs.get('restaurant_id')
        # context.update({"request": self.request})
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            restaurant = None
        context.update({"restaurant": restaurant})
        return context


class RestaurantPaymentMethodList(ListAPIView):
    serializer_class = RestaurantPaymentMethodSerializer
    permission_classes = [IsOwnerOrManager]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
            return RestaurantAcceptedPayment.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return RestaurantAcceptedPayment.objects.none()


class AddRestaurantAcceptedPaymentMethod(CreateAPIView):
    serializer_class = AddPaymentModeSerializer
    permission_classes = [IsOwnerOrManager]

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
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
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
            return RestaurantAcceptedPayment.objects.filter(restaurant=restaurant)
        except:
            return RestaurantAcceptedPayment.objects.none()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'details': 'Payment method removed'}, status=HTTP_200_OK)


class AllBusinessTypes(ListAPIView):
    serializer_class = AllBusinessTypesSerializer
    # permission_classes = [IsOwnerOrManager]
    queryset = BusinessType.objects.all().order_by('id')


class AllCitys(ListAPIView):
    serializer_class = CitySerializer
    # permission_classes = [IsOwnerOrManager]
    queryset = City.objects.all().order_by('id')


class AllStates(ListAPIView):
    serializer_class = StateSerializer
    # permission_classes = [IsOwnerOrManager]
    queryset = State.objects.all().order_by('id')


class RestaurantServiceList(ListAPIView):
    serializer_class = RestaurantServiceSerializer
    permission_classes = [IsOwnerOrManager]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
            return RestaurantService.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return RestaurantService.objects.none()


class RemoveRestaurantService(DestroyAPIView):
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
            return RestaurantService.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return RestaurantService.objects.none()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'details': 'Service removed'}, status=HTTP_200_OK)


class AddRestaurantService(GenericAPIView):
    serializer_class = AddServiceSerializer
    permission_classes = [IsOwnerOrManager]

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
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


class RestaurantCuisineList(ListAPIView):
    serializer_class = RestaurantCuisineSerializer
    permission_classes = [IsOwnerOrManager]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
            return RestaurantCuisines.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return RestaurantCuisines.objects.none()


class AddRestaurantCuisines(GenericAPIView):
    serializer_class = AddCuisinesSerializer
    permission_classes = [IsOwnerOrManager]

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
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
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
            return RestaurantCuisines.objects.filter(restaurant=restaurant)
        except:
            return RestaurantService.objects.none()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'Cuisine removed'}, status=HTTP_200_OK)


class CuisinesList(ListAPIView):
    serializer_class = CuisinesSerializer
    permission_classes = [IsOwnerOrManager]
    queryset = Cuisines.objects.all().order_by('id')
    filter_backends = [OrderingFilter]
    ordering_fields = ['cuisines', 'cuisines_ru']


class MenuTypeList(ListAPIView):
    serializer_class = MenuTypeSerializer
    permission_classes = [IsOwnerOrManager, ]
    queryset = MenuType.objects.all().order_by('id')


class PromotionList(ListAPIView):
    serializer_class = PromotionListSerializer
    permission_classes = [IsOwnerOrManager]
    pagination_class = CustomPagination

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
            queryset = Promotion.objects.filter(restaurant=restaurant).order_by('-id')
            is_active = self.request.query_params.get('is_active')
            if is_active is not None and is_active in ['True', 'False']:
                queryset = queryset.filter(is_active=is_active)
            return queryset
        except:
            return Promotion.objects.none()


class PromotionDetail(RetrieveAPIView):
    serializer_class = PromotionDetailSerializer
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
            return Promotion.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return Promotion.objects.none()


class DeletePromotion(DestroyAPIView):
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
            return Promotion.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return Promotion.objects.none()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'Promotion Deleted'}, status=HTTP_200_OK)


class CreatePromotion(CreateAPIView):
    serializer_class = PromotionDetailSerializer
    permission_classes = [IsOwnerOrManager]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            restaurant = None
        context.update({"restaurant": restaurant})
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'details': 'Promotion created'}, status=HTTP_201_CREATED, headers=headers)


class UpdatePromotion(UpdateAPIView):
    serializer_class = PromotionDetailSerializer
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
            return Promotion.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return Promotion.objects.none()

    def put(self, request, *args, **kwargs):
        return Response({'details': 'Method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)


class RemovePromotionWeekDay(DestroyAPIView):
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return PromotionWeekDay.objects.none()
        return PromotionWeekDay.objects.filter(promotion__restaurant=restaurant)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'Day removed from promotion'}, status=HTTP_200_OK)


class RemoveItemFromPromotion(DestroyAPIView):
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return PromotionOnItem.objects.none()
        return PromotionOnItem.objects.filter(promotion__restaurant=restaurant)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'details': 'Item removed from promotion'}, status=HTTP_200_OK)


class MenuItemDropdown(ListAPIView):
    serializer_class = MenuItemDropdownSerializer
    permission_classes = [IsOwnerOrManager]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
            return MenuItem.objects.filter(restaurant=restaurant).order_by('-id')
        except:
            return MenuItem.objects.none()


class CreateEvent(CreateAPIView):
    serializer_class = AddEventSerializer
    permission_classes = [IsOwnerOrManager]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            restaurant = None
        context.update({"restaurant": restaurant})
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'details': 'Event created'}, status=HTTP_201_CREATED)


class DeleteEvent(DestroyAPIView):
    permission_classes = [IsOwnerOrManager]
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return Event.objects.none()
        return Event.objects.filter(restaurant=restaurant)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return Response({'details': 'Event deleted successfully.'}, status=HTTP_200_OK)


class UpdateEvent(UpdateAPIView):
    permission_classes = [IsOwnerOrManager]
    serializer_class = EventSerializer
    lookup_field = 'id'

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return Event.objects.none()
        return Event.objects.filter(restaurant=restaurant)

    def put(self, request, *args, **kwargs):
        return Response({'details': 'Method not allowed'}, status=HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'details': 'Event updated successfully'}, status=HTTP_200_OK)


class EventFilter(FilterSet):
    start = DateTimeFilter(field_name='date_time', lookup_expr='gte')
    end = DateTimeFilter(field_name='date_time', method='filter_end_date')
    search = django_filters.CharFilter(method='custom_search')

    def custom_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )

    def filter_end_date(self, queryset, name, value):
        end_datetime = make_aware(datetime.combine(value, datetime.max.time()))
        return queryset.filter(date_time__lte=end_datetime)

    class Meta:
        model = Event
        fields = ['start', 'end', 'search']


class AllEvents(ListAPIView):
    permission_classes = [IsOwnerOrManager]
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = EventFilter
    ordering_fields = ['date_time']
    pagination_class = CustomPagination

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            return Event.objects.none()

        queryset = Event.objects.filter(restaurant=restaurant).order_by('-id')
        return queryset


class CreateAdsBanner(CreateAPIView):
    serializer_class = CreateAdsSerializer
    permission_classes = [IsOwnerOrManager]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(Q(id=restaurant_id) & Q(Q(owner=self.request.user) | Q(manager=self.request.user)))
        except:
            restaurant = None
        context.update({"restaurant": restaurant})
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'details': 'Ads banner request created'}, status=HTTP_201_CREATED)