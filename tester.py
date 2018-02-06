import json

import pandas as pd

from conf import POSTS_WITHOUT_RANK_QUERY, IRRELEVANT_RANK
from db_handler import DB_Handler
from facebook_handler import FacebookHandler
import unittest

from filter import Filter
from pre_processor import PreProcessor
from utils import get_day_range_unix_time, get_hebrew_word_from_file
from ranker import Ranker


class Tester(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Tester, self).__init__(*args, **kwargs)
        self.db_handler = DB_Handler()
        self.ranker = Ranker(self.db_handler)

    def test_get_posts_from_facebook(self):
        fb_handler = FacebookHandler()
        posts_from_facebook = fb_handler.get_posts_from_facebook(10)
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
        chosen_posts = [x for x in posts if '619669744790558_1580944595329730' in x['id']]
        for post in chosen_posts:
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

    def test_update_restaurants_test(self):
        self.db_handler.get_rest_from_post_message(self.db_handler.get_posts_from_mongo())

    def test_count_recommendations(self):
        total_recommendations = self.db_handler.count_recs()
        self.assertTrue(total_recommendations)
        return total_recommendations

    def test_get_unrelated_posts(self):
        self.db_handler.get_related_posts()

    def test_print_restaurants_data(self):
        self.db_handler.print_restaurants_data()

    def test_get_top_ten_json(self):
        top_ten_json = self.db_handler.get_top_restaurants_as_json(0, 100)
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

    def test_update_place_info(self):
        fb_handler = FacebookHandler()
        rest_ids = [rest for rest in list(self.db_handler.restaurants_data_collection.find({}))]
        i = 0
        for rest in rest_ids:
            try:
                rest_data = fb_handler.graph.get_object(rest['id'] + "?fields=about,hours")
                if 'about' in rest_data:
                    self.db_handler.restaurants_data_collection.update_one({'id': rest['id']}, {"$set": rest_data})
                    i += 1
                    print str(i) + '. ' + rest['name']
            except Exception as e:
                ron = 2
        ron = 2

    def test_add_place(self):
        posts = [place_post for place_post in self.db_handler.get_posts_from_mongo() if 'place' in place_post]
        i = 40
        self.db_handler.add_place_recommendation(posts[i])

    def test_get_restaurnats_data(self):
        rest_name = get_hebrew_word_from_file()
        all_rests = list(self.db_handler.restaurants_data_collection.find())
        restaurant = [rest for rest in all_rests if rest_name in rest['name']][0]
        self.assertTrue(restaurant)

    def test_filter_posts_by_prop(self):
        with open('heb_word') as f:
            property = f.readline()
        f = Filter(self.db_handler)
        filtered_posts = f.filter_rests_by_property(property, 0, 100)
        self.assertTrue(filtered_posts)

    def test_remove_posts_with_word(self):
        self.db_handler.get_irrelevant_posts()

    def test_set_synonyms(self):
        self.db_handler.set_rests_synonym()

    def test_remove_all_recs(self):
        self.db_handler.restaurants_data_collection.update_many({},
                                                                {"$set": {'recs': {}}})

    def test_log_file_write(self):
        for i in range(0, 10):
            with open('log.txt', 'a') as the_file:
                the_file.write(str(i) + '\n')

    def test_recognize_new_post_with_topic(self):
        fb_handler = FacebookHandler()
        filterer = Filter(self.db_handler)
        posts_from_facebook = fb_handler.get_posts_from_facebook(1)
        new_posts_by_topic = filterer.recognize_new_post_with_topic(posts_from_facebook, get_hebrew_word_from_file())
        self.assertTrue(new_posts_by_topic)

    def test_put_comment(self):
        fb_handler = FacebookHandler()
        fb_handler.put_comment()
        ron = 2


if __name__ == '__main__':
    unittest.main()
