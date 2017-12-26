from conf import POSTS_WITHOUT_RANK_QUERY, BAD_RANK, GOOD_RANK, IRRELEVANT_RANK
from db_handler import DB_Handler


class Ranker:
    def __init__(self):
        self.db_handler = DB_Handler()

    def rank_post(self):
        posts = self.db_handler.get_posts_from_mongo(POSTS_WITHOUT_RANK_QUERY)
        for idx, post in enumerate(posts):
            print post['message'] + '\n*****************' + str(idx) if 'message' in post else 'Post without message'
            user_input, rank = raw_input(), IRRELEVANT_RANK
            if user_input == '1':
                rank = GOOD_RANK
            elif user_input == '2':
                rank = BAD_RANK
            self.db_handler.posts_collection.update_one({'_id': post['_id']}, {"$set": {'rank': rank}})
