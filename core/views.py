import django_filters
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Q
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, ListAPIView, DestroyAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from admin_dashboard.models import UserDisputeResolution
from core.models import Restaurant, Category, Review, AdsBanner, RestaurantTimings, Favorite, MenuItem, QA, MenuType, City, Cuisines, Service
from core.serializers import HomeCategoriesSerializer, HomeRecentReviewSerializer, \
    RestaurantSearchSerializer, AdsBannerSerializer, NearByRestaurantSerializer, RestaurantListSerializer, FavoriteSerializer, RestaurantDetailSerializer, RestaurantMenuSerializer, \
    MenuItemDetailsSerializer, RestaurantReviewSerializer, FavoriteListSerializer, RestaurantQASerializer, PublicQuerySerializer, MenuTypeSerializer, UserDisputeResolutionSerializer, CitySerializer, \
    AllServiceSerializer, AllCuisinesListSerializer
from owner_dashboard.models import PublicQuery
from owner_dashboard.views import CustomPagination
from users.permissions import IsVisitor


# Create your views here.


class HomeCategoryList(ListAPIView):
    serializer_class = HomeCategoriesSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        return Category.objects.all().order_by('name')


class HomeRecentReviewApi(ListAPIView):
    serializer_class = HomeRecentReviewSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        return Review.objects.all().order_by('-id')[:9]


class RestaurantSearchApi(ListAPIView):
    serializer_class = RestaurantSearchSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        queryset = Restaurant.objects.filter(is_approved=True, is_disabled=False)

        search = self.request.query_params.get('search')
        lat = self.request.query_params.get('lat', None)
        long = self.request.query_params.get('long', None)
        city = self.request.query_params.get('city', None)

        if city is not None:
            try:
                city_id = int(city)
                queryset = queryset.filter(city__id=city_id)
            except Exception as e:
                print(e)
                pass

        if search is not None:
            queryset = queryset.filter(Q(name__icontains=search) | Q(restaurant_categories__category__name__icontains=search) | Q(cuisines__cuisine__cuisines__icontains=search))

        if lat and long:
            try:
                user_location = Point(float(long), float(lat))
                queryset = queryset.filter(location_point__distance_lte=(user_location, D(km=10)))
            except Exception as e:
                print(e)

        return queryset.distinct()[:10]


class AdsBannerApi(ListAPIView):
    serializer_class = AdsBannerSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        return AdsBanner.objects.filter(is_active=True).order_by('priority')


class NearByRestaurantApi(ListAPIView):
    serializer_class = NearByRestaurantSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        lat = self.request.query_params.get('lat', None)
        long = self.request.query_params.get('long', None)
        if lat and long:
            try:
                user_location = Point(float(long), float(lat))
            except Exception as e:
                print(e)
                return Restaurant.objects.none()
            return Restaurant.objects.filter(is_approved=True, is_disabled=False, location_point__distance_lte=(user_location, D(km=10)))[:10]
        else:
            return Restaurant.objects.none()


class CafeFilterSet(django_filters.FilterSet):
    average_bill_lt = django_filters.CharFilter(method='get_average_bill_lt')
    average_bill_gt = django_filters.CharFilter(method='get_average_bill_gt')

    def get_average_bill_lt(self, queryset, name, value):
        return queryset.filter(average_bill__lte=value)

    def get_average_bill_gt(self, queryset, name, value):
        return queryset.filter(average_bill__gte=value)

    class Meta:
        model = Restaurant
        fields = ['average_bill_lt', 'average_bill_gt', ]


class RestaurantListAPI(ListAPIView):
    serializer_class = RestaurantListSerializer
    permission_classes = [AllowAny, ]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CafeFilterSet
    ordering_fields = ['name', ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user if self.request.user.is_authenticated else None
        context.update({"user": user, })
        return context

    def get_queryset(self):
        queryset = Restaurant.objects.filter(is_approved=True).order_by('name')
        category = self.request.query_params.get('category')
        type = self.request.query_params.get('type')
        cuisine = self.request.query_params.get('cuisine')
        amenity = self.request.query_params.get('amenity')
        rating = self.request.query_params.get('rating')
        lat = self.request.query_params.get('lat', None)
        long = self.request.query_params.get('long', None)
        city = self.request.query_params.get('city', None)
        is_disabled = self.request.query_params.get('is_disabled', None)

        filter_conditions = Q()

        if city is not None:
            try:
                city_id = int(city)
                filter_conditions &= Q(city__id=city_id)
            except Exception as e:
                print(e)
                pass

        if lat and long:
            try:
                user_location = Point(float(long), float(lat))
                filter_conditions &= Q(location_point__distance_lte=(user_location, D(km=10)))
            except Exception as e:
                print(e)

        if is_disabled is not None and is_disabled in ['True', 'False']:
            filter_conditions &= Q(is_disabled=is_disabled)

        if type:
            filter_conditions &= Q(type__id=type)
        if category:
            filter_conditions &= Q(restaurant_categories__category__id=category)
        # if sub_category:
        #     filter_conditions &= Q(restaurant_categories__category__sub_categories__id=sub_category)
        if cuisine:
            filter_conditions &= Q(cuisines__cuisine__id=cuisine)
        if amenity:
            filter_conditions &= Q(restaurant_services__service__id=amenity)

        queryset = queryset.filter(filter_conditions)
        if rating:
            return [q for q in queryset if q.average_rating >= float(rating)]

        return queryset.distinct()


class AddToFavorite(CreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsVisitor, ]

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return Response({'details': 'restaurant does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Favorite.objects.get(restaurant=restaurant, user=self.request.user)
            return Response({'details': 'restaurant already in your favorite list'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            Favorite(user=self.request.user, restaurant=restaurant).save()
            return Response({'details': 'Added to favorite'}, status=status.HTTP_200_OK)


class RemoveFavorite(GenericAPIView):
    permission_classes = [IsVisitor, ]

    # def get_queryset(self):
    #     return Favorite.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return Response({'details': 'restaurant does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Favorite.objects.get(restaurant=restaurant, user=self.request.user).delete()
            return Response({'details': 'Removed from favorite'}, status=status.HTTP_200_OK)
        except:
            return Response({'details': 'Favourite not fount'}, status=status.HTTP_400_BAD_REQUEST)


class RestaurantDetail(RetrieveAPIView):
    serializer_class = RestaurantDetailSerializer
    lookup_field = 'id'
    queryset = Restaurant.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user if self.request.user.is_authenticated else None
        try:
            restaurant = Restaurant.objects.get(id=self.kwargs.get('id'))
        except Exception as e:
            restaurant = None
        context.update({"user": user, 'restaurant': restaurant})
        return context


class MenuTypeList(ListAPIView):
    serializer_class = MenuTypeSerializer
    queryset = MenuType.objects.all().order_by('id')


class MenuFilterSet(django_filters.FilterSet):
    search = django_filters.CharFilter(method='custom_search')
    price_lt = django_filters.CharFilter(method='get_price_lt')
    price_gt = django_filters.CharFilter(method='get_price_gt')
    menu_type = django_filters.NumberFilter(field_name='menu_type')

    def custom_search(self, queryset, name, value):
        return queryset.filter(Q(Item_name__icontains=value) | Q(description__icontains=value))

    def get_price_lt(self, queryset, name, value):
        return queryset.filter(price__lte=value)

    def get_price_gt(self, queryset, name, value):
        return queryset.filter(price__gte=value)

    class Meta:
        model = MenuItem
        fields = ['search', 'price_lt', 'price_gt', 'menu_type']


class RestaurantMenu(ListAPIView):
    serializer_class = RestaurantMenuSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MenuFilterSet
    ordering_fields = ['id', 'created_at', 'updated_at', 'Item_name', 'price']

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return MenuItem.objects.none()
        queryset = MenuItem.objects.filter(restaurant=restaurant).order_by('Item_name')
        is_veg = self.request.query_params.get('is_veg')

        if is_veg is not None and is_veg in ['True', 'False']:
            queryset = queryset.filter(is_veg=is_veg)

        return queryset


class ItemDetail(RetrieveAPIView):
    serializer_class = MenuItemDetailsSerializer
    queryset = MenuItem.objects.all()
    lookup_field = 'id'


class RestaurantReview(ListAPIView):
    serializer_class = RestaurantReviewSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return Review.objects.none()
        queryset = Review.objects.filter(restaurant=restaurant).order_by('-id')

        return queryset


class AddRestaurantReview(CreateAPIView):
    serializer_class = RestaurantReviewSerializer
    permission_classes = [IsVisitor]

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return Response({'details': 'Restaurant not found'}, status=status.HTTP_400_BAD_REQUEST)
        user = self.request.user
        try:
            Review.objects.get(user=user, restaurant=restaurant)
            return Response({'details': 'Review already added'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            rating = serializer.validated_data['rating']
            comment = serializer.validated_data['comment']
            Review(restaurant=restaurant, rating=rating, comment=comment, user=user).save()
            return Response({'details': 'Review added'}, status=status.HTTP_201_CREATED)


class UpdateReview(UpdateAPIView):
    serializer_class = RestaurantReviewSerializer
    permission_classes = [IsVisitor]
    lookup_field = 'id'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def put(self, request, *args, **kwargs):
        return Response({'details': 'method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class FavoriteRestaurant(ListAPIView):
    serializer_class = FavoriteListSerializer
    permission_classes = [IsVisitor]
    pagination_class = CustomPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user if self.request.user.is_authenticated else None
        context.update({"user": user, })
        return context

    def get_queryset(self):
        queryset = Favorite.objects.filter(user=self.request.user).order_by('-id')
        return queryset


class RestaurantQAList(ListAPIView):
    serializer_class = RestaurantQASerializer

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return QA.objects.none()

        return QA.objects.filter(restaurant=restaurant).order_by('-id')


class AskPublicQuery(CreateAPIView):
    serializer_class = PublicQuerySerializer
    permission_classes = [IsVisitor]

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except:
            return Response({'details': 'Restaurant not found'}, status=status.HTTP_400_BAD_REQUEST)
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data['question']
        PublicQuery(restaurant=restaurant, question=question, raise_by=user).save()
        return Response({'details': 'Question asked to restaurant'}, status=status.HTTP_201_CREATED)


class AddUserDispute(CreateAPIView):
    serializer_class = UserDisputeResolutionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data['query']
        UserDisputeResolution(query=query, query_by=user).save()
        return Response({'details': 'Query added successfully'}, status=status.HTTP_201_CREATED)


class CityList(ListAPIView):
    serializer_class = CitySerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = City.objects.all().order_by('city')
        city = self.request.query_params.get('city')
        if city is not None:
            queryset = queryset.filter(Q(city__icontains=city) | Q(city_ru__icontains=city))

        return queryset


class AllServices(ListAPIView):
    serializer_class = AllServiceSerializer
    permission_classes = [AllowAny]
    queryset = Service.objects.all().order_by('service_name')


class AllCuisinesList(ListAPIView):
    serializer_class = AllCuisinesListSerializer
    permission_classes = [AllowAny]
    queryset = Cuisines.objects.all().order_by('cuisines')
