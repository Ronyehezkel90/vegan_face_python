from db_handler import DB_Handler

db_handler = DB_Handler()
for i in range(1, 2):
    try:
        posts_from_facebook = db_handler.fb_handler.get_posts_from_facebook(i)
        added_posts = db_handler.insert_posts_to_mongo(posts_from_facebook)
        print 'Posts from: {} days ago has been added'.format(str(i))
        db_handler.update_restaurants(added_posts)
    except:
        print 'Posts from: {} days ago has been FAILED'.format(str(i))
