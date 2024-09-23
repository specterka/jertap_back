import numpy as np
import pandas as pd

from core.models import Category, Cuisines, BusinessType, City, State, ModeOfPayment, Service, Restaurant, RestaurantCategory, RestaurantCuisines, RestaurantService, RestaurantAcceptedPayment, \
    RestaurantTimings
from owner_dashboard.views import create_restaurant_times


def add_category():
    df = pd.read_csv("/home/ridhish/PycharmProjects/Jertap_other_details/csv_data/categories.csv", delimiter=";")
    print(df.keys())
    for index, row in df.iterrows():
        try:
            Category(name=row['category_en'], name_ru=row['category_ru']).save()
        except Exception as e:
            print(e)
            print(row['category_en'])


def add_cuisines():
    df = pd.read_csv("/home/ridhish/PycharmProjects/Jertap_other_details/csv_data/cuisines.csv", delimiter=";")
    print(df.keys())
    for index, row in df.iterrows():
        try:
            Cuisines(cuisines=row['cuisine_en'], cuisines_ru=row['cuisine_ru']).save()
        except Exception as e:
            print(e)
            print(row['cuisine_en'])


def add_business_type():
    df = pd.read_csv("/home/ridhish/PycharmProjects/Jertap_other_details/csv_data/types.csv", delimiter=";")
    print(df.keys())
    for index, row in df.iterrows():
        try:
            BusinessType(type=row['types_en'], type_ru=row['types_ru']).save()
        except Exception as e:
            print(e)
            print(row['types_en'])


def add_city():
    df = pd.read_csv("/home/ridhish/PycharmProjects/Jertap_other_details/csv_data/cities.csv", delimiter=";")
    print(df.keys())
    for index, row in df.iterrows():
        try:
            City(city=row['city_en'], city_ru=row['city_ru']).save()
        except Exception as e:
            print(e)
            print(row['city_en'])


def add_state():
    df = pd.read_csv("/home/ridhish/PycharmProjects/Jertap_other_details/csv_data/states.csv", delimiter=";")
    print(df.keys())
    for index, row in df.iterrows():
        try:
            State(state=row['state_en'], state_ru=row['state_ru']).save()
        except Exception as e:
            print(e)
            print(row['state_en'])


def add_mode_of_payment():
    df = pd.read_csv("/home/ridhish/PycharmProjects/Jertap_other_details/csv_data/payment_types.csv", delimiter=";")
    print(df.keys())
    for index, row in df.iterrows():
        try:
            ModeOfPayment(payment_name=row['payment_en'], payment_name_ru=row['payment_ru']).save()
        except Exception as e:
            print(e)
            print(row['payment_en'])


def add_services():
    df = pd.read_csv("/home/ridhish/PycharmProjects/Jertap_other_details/csv_data/business_services.csv", delimiter=";")
    print(df.keys())
    for index, row in df.iterrows():
        try:
            Service(service_name=row['service_en'], service_name_ru=row['service_ru']).save()
        except Exception as e:
            print(e)
            print(row['service_en'])


def get_full_day(data):
    choices = {
        'Mon': 'Monday',
        'Tue': 'Tuesday',
        'Wed': 'Wednesday',
        'Thu': 'Thursday',
        'Fr': 'Friday',
        'Sat': 'Saturday',
        'Sun': 'Sunday',
    }
    return choices.get(data, '')


def add_business():
    df = pd.read_csv("/home/ridhish/PycharmProjects/Jertap_other_details/csv_data/businesses.csv", delimiter=";")
    df = df.replace(np.nan, None)
    # for index, row in df.iloc[15000:].iterrows():
    for index, row in df.iterrows():
        try:
            typ = BusinessType.objects.get(type=row['type_en'])
        except Exception as e:
            print(e, row['type_en'])
            typ = None
        try:
            city = City.objects.get(city=row['city_en'])
        except Exception as e:
            print(e, row['city_en'])
            city = None
        try:
            state = State.objects.get(state=row['state_en'])
        except Exception as e:
            print(e, row['state_en'])
            state = None
        try:
            business_whatsapp = row['business_whatsapp'].split('/')[-1]
        except Exception as e:
            business_whatsapp = None
        try:
            average_bill = int(row['average_bill'])
        except:
            average_bill = None
        try:
            business_capacity = int(row['business_capacity'])
        except:
            business_capacity = None
        try:
            lat = float(row['business_latitude'].replace(',', '.').strip())
        except:
            lat = None
        try:
            long = float(row['business_longitude'].replace(',', '.').strip())
        except:
            long = None

        restaurant = Restaurant(name=row['business_name'], type=typ, average_bill=average_bill, business_capacity=business_capacity, address=row['address_en'], address_ru=row['address_ru'], city=city,
                                state=state, phone_number=row['business_number1'], phone_number_2=row['business_number2'], business_email=row['business_email'],
                                business_website=row['business_website'], business_instagram=row['business_instagram'], business_whatsapp=business_whatsapp,
                                latitude=lat, longitude=long, business_2gis=row['business_2gis'])
        restaurant.save()
        create_restaurant_times(restaurant)
        print(restaurant)

        try:
            categories = [item.strip() for item in row['category_en'].split(';')]
            if len(categories) > 0:
                for category in categories:
                    try:
                        RestaurantCategory(category=Category.objects.get(name=category), restaurant=restaurant).save()
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)

        try:
            cuisines = [item.strip() for item in row['cuisine_en'].split(';')]
            if len(cuisines) > 0:
                for cuisine in cuisines:
                    try:
                        RestaurantCuisines(cuisine=Cuisines.objects.get(cuisines=cuisine), restaurant=restaurant).save()
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)

        try:
            services = [item.strip() for item in row['service_en'].split(';')]
            if len(services) > 0:
                for service in services:
                    try:
                        RestaurantService(service=Service.objects.get(service_name=service), restaurant=restaurant).save()
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)

        """
        # restaurant timings
        try:
            if ',' in row['restaurantTiming_en']:
                pass
            else:
                try:
                    times = [item.strip() for item in row['restaurantTiming_en'].split(';')]
                    for t in times:
                        day, time_range = t.split(": ")
                        open_at, close_at = time_range.split("-")
                        try:
                            timing_obj = RestaurantTimings.objects.get(restaurant=restaurant, weekday=get_full_day(day))
                            timing_obj.from_hour = open_at
                            timing_obj.to_hour = close_at
                            timing_obj.save()
                            # print(get_full_day(day), open_at, close_at)
                        except Exception as e:
                            print(e)
                except Exception as e:
                    print(e)

        except Exception as e:
            print(e)
        """

        # try:
        #     payments = [item.strip() for item in row['payment_en'].split(';')]
        #     if len(payments) > 0:
        #         for payment in payments:
        #             try:
        #                 RestaurantAcceptedPayment(payment=ModeOfPayment.objects.get(payment_name=payment), restaurant=restaurant).save()
        #             except Exception as e:
        #                 print(e, payment)
        # except Exception as e:
        #     print(e)

# from admin_dashboard.data_upload_scripts import *
