from datetime import datetime

from conf import SEPERATOR
from db_handler import DB_Handler

db_handler = DB_Handler()
for i in range(0, 1200):
    try:
        posts_from_facebook = db_handler.fb_handler.get_posts_from_facebook(i)
        added_posts = db_handler.insert_posts_to_mongo(posts_from_facebook)
        print 'Posts from: {} days ago has been added'.format(str(i))
        db_handler.update_restaurants(added_posts)
    except Exception as e:
        log_error = '{}\nPosts from: {} days ago has been FAILED\n'.format(datetime.utcnow().now(), str(i)) + str(
            e) + SEPERATOR
        with open('log.txt', 'a') as log_file:
            log_file.write(log_error + '\n')
        print log_error
