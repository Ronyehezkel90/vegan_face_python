from pymongo import MongoClient
import pandas as pd
import json

from conf import BAD_CHARACTERS, POSTS_WITHOUT_RANK_QUERY


class DB_Handler:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        db = client.veganDB
        self.posts_collection = db.posts
        self.restaurants_collection = db.restaurants
        self.restaurants_data_collection = db.restaurants_data
        self.restaurants_doc_id_obj = list(self.restaurants_collection.find())[0]['_id']
        self.all_restaurants = list(self.restaurants_collection.find())[0]['restaurants_names']

    def insert_posts_to_mongo(self, posts):
        all_posts = list(self.posts_collection.find())
        all_posts_ids = [post['id'] for post in all_posts]
        for post in posts:
            if post['id'] not in all_posts_ids and 'message' in post and all(
                            char not in post['message'] for char in BAD_CHARACTERS):
                self.posts_collection.insert_one(post)

    def get_posts_from_mongo(self, query={}):
        return list(self.posts_collection.findOne(query))

    def get_unranked_post(self):
        post = {}
        posts_iterator = self.posts_collection.find(POSTS_WITHOUT_RANK_QUERY)
        while 'message' not in post:
            post = posts_iterator.next()
        json_response = json.dumps({'post_id': post['id'], 'message': post['message']})
        return json_response

    def get_related_posts(self):
        all_related_posts_lists = [res['recs'].keys() for res in self.restaurants_data_collection.find()]
        all_related_posts = []
        for res_ids_list in all_related_posts_lists:
            for res_id in res_ids_list:
                all_related_posts.append(res_id)
        return all_related_posts

    def add_new_place(self, post, place_name, place_dict):
        self.all_restaurants.append(place_name)
        self.restaurants_collection.update_one({'_id': self.restaurants_doc_id_obj},
                                               {"$set": {'restaurants_names': self.all_restaurants}})
        place_dict['recs'] = {post['id']: 0}
        self.restaurants_data_collection.insert_one(place_dict)

    def add_existing_place(self, post, place_name):
        recs_posts_ids = list(self.restaurants_data_collection.find({'name': place_name}))[0]['recs']
        if post['id'] not in [id for id in recs_posts_ids]:
            recs_posts_ids[post['id']] = 0
            self.restaurants_data_collection.update_one({'name': place_name},
                                                        {"$set": {'recs': recs_posts_ids}})

    def add_place_recommendation(self, post):
        place_name = post['place']['name']
        place_dict = post['place']
        self.add_new_place(post, place_name, place_dict) if place_name not in self.all_restaurants \
            else self.add_existing_place(post, place_name)

    def update_restaurants(self, posts):
        tagged_posts = []
        counter = []
        counter_two = []
        for post in posts:
            if '1531688776921979' in post[u'id']:
                ron = 2
            mentioned_restaurants = [restaurant for restaurant in self.all_restaurants if
                                     restaurant in post['message']] if 'message' in post else []
            try:
                place_name = post[u'attachments'][u'data'][0][u'description_tags'][0][u'name']
                tagged_posts.append((place_name, post))
            except KeyError:
                if 'place' in post:
                    self.add_place_recommendation(post)
                elif len(mentioned_restaurants) == 1:
                    counter.append((post, mentioned_restaurants))
                elif len(mentioned_restaurants) > 1:
                    counter_two.append((post, mentioned_restaurants))
        for (place_name, post) in tagged_posts:
            if place_name in self.all_restaurants:
                self.add_existing_place(post, place_name)

    def count_recs(self):
        restaurants = list(self.restaurants_data_collection.find())
        return sum([len(x['recs']) for x in restaurants])

    def clear_restaurants(self):
        self.restaurants_collection.update_one({'_id': self.restaurants_doc_id_obj},
                                               {"$set": {'restaurants_names': []}})
        self.restaurants_data_collection.remove()

    def remove_post_by_id(self, p_id):
        self.posts_collection.remove({'id': p_id})

    def print_restaurants_data(self):
        all_restaurants_data = list(self.restaurants_data_collection.find())
        data = [(res['name'], len(res['recs'])) for res in all_restaurants_data]
        df = pd.DataFrame(data, columns=['name', 'recs']).sort_values('recs', ascending=False)
        df.to_excel('restaurants.xlsx')
        print df

    def get_top_ten_json(self, count):
        top_restaurants_data = list(self.restaurants_data_collection.find())
        data = [(res['name'], len(res['recs'])) for res in top_restaurants_data]
        df = pd.DataFrame(data, columns=['name', 'recs']).sort_values('recs', ascending=False).set_index('name')
        top_ten_json = df[:count].to_json()
        return top_ten_json

    def get_restaurant_posts(self, rest_name):
        posts_ids = list(self.restaurants_data_collection.find({'name': rest_name}))[0]['recs'].keys()
        posts = {'posts': []}
        for post_id in posts_ids:
            rest_data = self.posts_collection.find({'id': post_id})[0]
            if 'message' in rest_data:
                posts['posts'].append({'id': post_id, 'text': rest_data['message'][:40]})
        posts_json = pd.DataFrame(posts['posts']).set_index('id')[:10].to_json()
        return posts_json
