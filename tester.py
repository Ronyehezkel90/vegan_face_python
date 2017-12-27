import json

from conf import POSTS_WITHOUT_RANK_QUERY, IRRELEVANT_RANK
from db_handler import DB_Handler
from facebook_handler import FacebookHandler
import unittest

from pre_processor import PreProcessor
from utils import get_day_range_unix_time
from ranker import Ranker


class Tester(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Tester, self).__init__(*args, **kwargs)
        self.db_handler = DB_Handler()
        self.ranker = Ranker(self.db_handler)

    def test_get_posts_from_facebook(self):
        fb_handler = FacebookHandler()
        posts_from_facebook = fb_handler.get_posts_from_facebook(2)
        self.assertTrue(posts_from_facebook)

    def test_get_posts_from_mongo(self):
        posts = self.db_handler.get_posts_from_mongo()
        self.assertTrue(posts)

    def test_get_unranked_post_from_mongo(self):
        post = self.db_handler.get_unranked_post()
        self.assertTrue(post)

    def test_rank_post_request_test(self):
        post_as_string = self.db_handler.get_unranked_post()
        post_as_json = json.loads(post_as_string)
        result = self.ranker.rank_post_request(post_as_json['post_id'], '0')
        self.assertTrue(result)

    def test_get_posts_with_attr_from_mongo(self):
        posts = self.db_handler.get_posts_from_mongo()
        # chosen_posts = [x for x in posts if 'message' in x and '?' in x['message']]
        for post in posts:
            pic = 'yes' if ('attachments' in post and post[u'attachments'][u'data'][0][u'media'][u'image']) else 'no'
            place = 'yes' if 'place' in post else 'no'
            print 'picture: ' + pic + ' - place: ' + place
            print post['message']
            raw_input()
        self.assertTrue(posts)

    def test_rank_posts(self):
        self.ranker.rank_post_manually()

    def test_build_machine_learning_model(self):
        pre_processor = PreProcessor()
        pre_processor.pre_process_recs()

    def test_rank_post_automatically(self):
        self.ranker = Ranker(self.db_handler)
        sign = '?'
        rank = IRRELEVANT_RANK
        posts = self.db_handler.get_posts_from_mongo(POSTS_WITHOUT_RANK_QUERY)
        for post in posts:
            if 'message' in post and sign in post['message']:
                self.db_handler.posts_collection.update_one({'_id': post['_id']}, {"$set": {'rank': rank}})

    def test_update_restaurants(self):
        self.db_handler.update_restaurants(self.db_handler.get_posts_from_mongo())

    def test_clear_restaurants(self):
        self.db_handler.clear_restaurants()

    def test_count_recommendations(self):
        total_recommendations = self.db_handler.count_recs()
        self.assertTrue(total_recommendations)
        return total_recommendations

    def test_remove_post_by_id(self):
        self.db_handler.remove_post_by_id('619669744790558_1496029353821255')

    def test_get_unrelated_posts(self):
        self.db_handler.get_related_posts()

    def test_print_restaurants_data(self):
        self.db_handler.print_restaurants_data()

    def test_get_top_ten_json(self):
        top_ten_json = self.db_handler.get_top_ten_json(10)
        self.assertTrue(top_ten_json)

    def test_get_rest_images_test(self):
        images = self.db_handler.get_restaurant_images('FOUR ONE SIX')
        self.assertTrue(images)

    def test_restaurant_name_in_message(self):
        separator = '******************************'
        related_posts = self.db_handler.get_related_posts()
        for post in self.db_handler.get_posts_from_mongo({}):
            if post['id'] in related_posts and 'message' in post:
                # self.data_handler.restaurant_name_in_message(post)
                print separator + '\n' + post['message'] + '\n' + separator
                raw_input()

    def test_get_current_unix_time(self):
        unixtime_range = get_day_range_unix_time(2)
        self.assertTrue(unixtime_range)


if __name__ == '__main__':
    unittest.main()
