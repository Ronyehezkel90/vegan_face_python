import sys

from db_handler import DB_Handler
from ranker import Ranker


def get_rest_name(last_param_index):
    rest_name = ''
    for idx in range(last_param_index, len(sys.argv)):
        rest_name += sys.argv[idx] + ' ' if idx != len(sys.argv) - 1 else sys.argv[idx]
    return rest_name


script_name = sys.argv[1]
db_handler = DB_Handler()
ranker = Ranker(db_handler)

if script_name == 'get_top_rests':
    page = sys.argv[2]
    count = int(page) * 10
    top_restaurants_json = db_handler.get_top_restaurants_as_json(count, count + 10)
    print top_restaurants_json
elif script_name == 'get_rest_data':
    rest_name = get_rest_name(3)
    print db_handler.get_restaurant_data_by_field_as_json(get_rest_name(3), sys.argv[2])
elif script_name == 'get_posts':
    page = sys.argv[2]
    count = int(page) * 10
    rest_name = get_rest_name(3)
    rest_posts = db_handler.get_restaurant_posts(rest_name, count, count + 10)
    print rest_posts
elif script_name == 'get_images':
    page = sys.argv[2]
    count = int(page) * 20
    rest_name = get_rest_name(3)
    rest_posts = db_handler.get_restaurant_images(rest_name, count, count + 20)
    print rest_posts
elif script_name == 'train_machine':
    print db_handler.get_unranked_post()
elif script_name == 'rank_post':
    print ranker.rank_post_request(sys.argv[2], sys.argv[3])
else:
    print '2'
