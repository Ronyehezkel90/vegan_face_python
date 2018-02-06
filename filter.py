import json
import operator

import pandas as pd


class Filter:
    def __init__(self, db_handler):
        self.db_handler = db_handler

    def get_posts_id_with_property(self, property, posts):
        # property = property.decode('utf-8')
        return [post['id'] for post in posts if 'message' in post and property in post['message']]

    def get_ranked_restaurants(self, filtered_posts_id):
        recs_dict = {}
        for rest in list(self.db_handler.restaurants_data_collection.find()):
            for post_rec in rest['recs']:
                recs_dict[post_rec] = rest['name']
        ranked_rests_dict = {}
        for rec in filtered_posts_id:
            if rec in recs_dict:
                ranked_rests_dict[recs_dict[rec]] = ranked_rests_dict[recs_dict[rec]] + 1 if recs_dict[
                                                                                                 rec] in ranked_rests_dict else 1
        return ranked_rests_dict

    def filter_rests_by_property(self, property, count_from, count_to):
        filtered_posts_id = self.get_posts_id_with_property(property, self.db_handler.get_posts_from_mongo())
        ranked_rests_dict = self.get_ranked_restaurants(filtered_posts_id)
        df = pd.DataFrame(sorted(ranked_rests_dict.items(), key=operator.itemgetter(1)),
                          columns=['name', 'recs']).sort_values('recs', ascending=False).set_index(
            'name')
        # df.to_excel('hamburger.xlsx')
        result_as_json = df[count_from:count_to].to_json()
        return result_as_json

    def recognize_new_post_with_topic(self, current_posts, topic):
        all_posts = list(self.db_handler.posts_collection.find())
        all_posts_ids = [post['id'] for post in all_posts]
        new_posts = []
        for post in current_posts:
            if post['id'] not in all_posts_ids:
                new_posts.append(post)
        self.get_posts_id_with_property(topic, new_posts)
        return new_posts
