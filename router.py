import sys

from db_handler import DB_Handler

script_name = sys.argv[1]
db_handler = DB_Handler()

if script_name == 'get_top_rests':
    top_restaurants_json = db_handler.get_top_ten_json(10)
    print top_restaurants_json
elif script_name == 'count_recs':
    print script_name
elif script_name == 'get_posts':
    rest_name = ''
    for idx in range(2, len(sys.argv)):
        rest_name += sys.argv[idx] + ' ' if idx != len(sys.argv) - 1 else sys.argv[idx]
    # with open('heb_rest') as f:
    #     rest_name = f.readline()
    rest_posts = db_handler.get_restaurant_posts(rest_name)
    print rest_posts
else:
    print '2'
