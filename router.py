import sys

from db_handler import DB_Handler
from ranker import Ranker

script_name = sys.argv[1]
db_handler = DB_Handler()
ranker = Ranker(db_handler)

if script_name == 'get_top_rests':
    page = sys.argv[2]
    count = int(page) * 10
    top_restaurants_json = db_handler.get_top_ten_json(count, count + 10)
    print top_restaurants_json
elif script_name == 'get_posts':
    page = sys.argv[2]
    count = int(page) * 10
    rest_name = ''
    for idx in range(3, len(sys.argv)):
        rest_name += sys.argv[idx] + ' ' if idx != len(sys.argv) - 1 else sys.argv[idx]
    rest_posts = db_handler.get_restaurant_posts(rest_name, count, count + 10)
    print rest_posts
elif script_name == 'get_images':
    page = sys.argv[2]
    count = int(page) * 20
    rest_name = ''
    for idx in range(3, len(sys.argv)):
        rest_name += sys.argv[idx] + ' ' if idx != len(sys.argv) - 1 else sys.argv[idx]
    rest_posts = db_handler.get_restaurant_images(rest_name, count, count + 20)
    print rest_posts
elif script_name == 'train_machine':
    print db_handler.get_unranked_post()
elif script_name == 'rank_post':
    print ranker.rank_post_request(sys.argv[2], sys.argv[3])
else:
    print '2'
