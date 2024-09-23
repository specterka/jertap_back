from celery import shared_task
import pandas as pd
from core.models import Restaurant, MenuItem, SubCategory, ItemIngredient, MenuType


@shared_task()
def create_menu_items(restaurant_id, df_json):
    df = pd.read_json(df_json)
    restaurant = Restaurant.objects.get(id=restaurant_id)

    for index, row in df.iterrows():
        try:
            item = MenuItem(restaurant=restaurant, Item_name=row['Item_name'].strip(), description=row['description'].strip(), is_veg=True if row['is_veg'].strip() == 'Y' else False)
            try:
                item.price = row['price']
            except:
                item.price = None
            try:
                item.sub_category = SubCategory.objects.get(name=row['sub_category'].strip())
            except:
                item.sub_category = None
            try:
                item.menu_type = MenuType.objects.get(name=row['menu_type'].strip())
            except:
                item.menu_type = None
            try:
                item.save_image_from_url(row['cover_image'])
            except:
                pass

            item.save()
            ingredient_list = row['item_ingredients'].split(',') if row['item_ingredients'] else []
            for ingredient in ingredient_list:
                try:
                    ItemIngredient(item=item, ingredients=ingredient).save()
                except Exception as e:
                    print(e)

        except Exception as e:
            print(e)
