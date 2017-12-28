from db_handler import DB_Handler
from facebook_handler import FacebookHandler

fb_handler = FacebookHandler()
db_handler = DB_Handler()
# for i in range(1, 20):
#     try:
#         posts_from_facebook = fb_handler.get_posts_from_facebook(i)
#         db_handler.insert_posts_to_mongo(posts_from_facebook)
#         print 'Posts from: {} days ago has been added'.format(str(i))
#     except:
#         print 'Posts from: {} days ago has been FAILED'.format(str(i))

all_posts = db_handler.get_posts_from_mongo()
db_handler.update_restaurants(all_posts)
db_handler.print_restaurants_data()

ron = 2
