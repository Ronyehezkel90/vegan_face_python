import sys

from conf import POSTS_PER_REQUEST
from db_handler import DB_Handler
from filter import Filter
from ranker import Ranker


def get_full_last_arg(last_param_index):
    full_arg = ''
    for idx in range(last_param_index, len(sys.argv)):
        full_arg += sys.argv[idx] + ' ' if idx != len(sys.argv) - 1 else sys.argv[idx]
    return full_arg


script_name = sys.argv[1]
db_handler = DB_Handler()
ranker = Ranker(db_handler)
filterer = Filter(db_handler)
if script_name == 'get_top_rests':
    page = sys.argv[2]
    filter_by_prop = get_full_last_arg(3)
    count = int(page) * 10
    if filter_by_prop == 'all':
        top_restaurants_json = db_handler.get_top_restaurants_as_json(count, count + 10)
    else:
        top_restaurants_json = filterer.filter_rests_by_property(filter_by_prop, count, count + 10)
    print top_restaurants_json
elif script_name == 'get_rest_data':
    rest_name = get_full_last_arg(3)
    print db_handler.get_restaurant_data_by_field_as_json(get_full_last_arg(3), sys.argv[2])
elif script_name == 'get_posts':
    page = sys.argv[2]
    count = int(page) * POSTS_PER_REQUEST
    rest_name = get_full_last_arg(3)
    rest_posts = db_handler.get_restaurant_posts(rest_name, count, count + POSTS_PER_REQUEST)
    print rest_posts
elif script_name == 'get_images':
    page = sys.argv[2]
    count = int(page) * 20
    rest_name = get_full_last_arg(3)
    rest_posts = db_handler.get_restaurant_images(rest_name, count, count + 10)
    print rest_posts
elif script_name == 'train_machine':
    print db_handler.get_unranked_post()
elif script_name == 'rank_post':
    print ranker.rank_post_request(sys.argv[2], sys.argv[3])
else:
    print '2'
