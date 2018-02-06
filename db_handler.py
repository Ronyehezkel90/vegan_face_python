import re

from pymongo import MongoClient
import pandas as pd
import json

from conf import BAD_CHARACTERS, POSTS_WITHOUT_RANK_QUERY, ATTACHMENTS, DATA, DESC_TAG, NAME, NO_REST_IN_POST, \
    CHARS_TO_REMOVE, PLACE_FIELDS
from facebook_handler import FacebookHandler


class DB_Handler:
    def __init__(self):
        self.fb_handler = FacebookHandler()
        client = MongoClient('localhost', 27017)
        self.db = client.veganDBA
        self.initialize_db()

    def initialize_db(self):
        self.posts_collection = self.db.posts
        self.restaurants_collection = self.db.restaurants
        self.restaurants_data_collection = self.db.restaurants_data
        self.all_restaurants = list(self.restaurants_data_collection.find())
        if not list(self.restaurants_collection.find()):
            self.restaurants_collection.insert_one({'restaurants_names': []})
        self.restaurants_doc_id_obj = list(self.restaurants_collection.find())[0]['_id']
        self.all_restaurants_names = list(self.restaurants_collection.find())[0]['restaurants_names']

    def insert_posts_to_mongo(self, posts):
        all_posts = list(self.posts_collection.find())
        posts = [post for post in posts if post['id'] not in self.get_irrelevant_posts(posts)]
        all_posts_ids = [post['id'] for post in all_posts]
        added_posts = []
        for post in posts:
            if post['id'] in all_posts_ids:
                self.posts_collection.update_one({'id': post['id']}, {"$set": {'reactions': post['reactions']}})
            elif 'message' in post and all(char not in post['message'] for char in BAD_CHARACTERS):
                self.posts_collection.insert_one(post)
                added_posts.append(post)
        return added_posts

    def get_irrelevant_posts(self, posts):
        with open('irrelevant_words') as f:
            words = f.readlines()
            words = [w.decode('utf-8').replace('\n', '') for w in words]
        irrelevant_posts = []
        for p in posts:
            irrelevant_post = False
            if 'message' in p:
                for word in words:
                    if word in p['message']:
                        irrelevant_post = True
            if irrelevant_post:
                irrelevant_posts.append(p['id'])
        return irrelevant_posts

    def get_posts_from_mongo(self, query={}):
        return list(self.posts_collection.find(query))

    def get_unranked_post(self):
        post = {}
        posts_iterator = self.posts_collection.find(POSTS_WITHOUT_RANK_QUERY)
        while 'message' not in post:
            post = posts_iterator.next()
        json_response = json.dumps({'post_id': post['id'], 'message': post['message'][:500]})
        return json_response

    def get_related_posts(self):
        all_related_posts_lists = [res['recs'].keys() for res in self.restaurants_data_collection.find()]
        all_related_posts = []
        for res_ids_list in all_related_posts_lists:
            for res_id in res_ids_list:
                all_related_posts.append(res_id)
        return all_related_posts

    def add_new_place(self, post, place_name, place_dict):
        self.all_restaurants_names.append(place_name)
        self.restaurants_collection.update_one({'_id': self.restaurants_doc_id_obj},
                                               {"$set": {'restaurants_names': self.all_restaurants_names}})
        place_dict['recs'] = {post['id']: 0}
        self.restaurants_data_collection.insert_one(place_dict)

    def add_existing_place(self, post, place_name):
        recs_posts_ids = [rest['recs'] for rest in self.all_restaurants if rest['name'] == place_name][0]
        if post['id'] not in recs_posts_ids:
            recs_posts_ids[post['id']] = 0
            self.restaurants_data_collection.update_one({'name': place_name},
                                                        {"$set": {'recs': recs_posts_ids}})

    def add_place_recommendation(self, post):
        place_name = post['place']['name']
        place_dict = post['place']
        if place_name not in self.all_restaurants_names:
            try:
                place_data = self.fb_handler.graph.get_object(post['place']['id'] + PLACE_FIELDS)
                place_dict.update(place_data)
            except Exception as e:
                print place_dict['name'] + ' -- >' + e.message
            self.add_new_place(post, place_name, place_dict)
        else:
            self.add_existing_place(post, place_name)

    def get_restaurant_tag_in_post(self, post):
        if ATTACHMENTS in post and DATA in post[ATTACHMENTS] and DESC_TAG in post[ATTACHMENTS][DATA][0] and \
                        NAME in post[ATTACHMENTS][DATA][0][DESC_TAG][0]:
            return post[ATTACHMENTS][DATA][0][DESC_TAG][0][NAME]
        else:
            return NO_REST_IN_POST

    def get_rest_from_post_message(self, post):
        if 'message' in post:
            for idx, row in self.synonyms_df.iterrows():
                clear_post = re.sub(CHARS_TO_REMOVE, ' ', post['message'])
                if row['synonyms'] + ' ' in clear_post and 'place' not in post:
                    return row['name']
        return NO_REST_IN_POST

    def get_synonyms(self, rest_name):
        rest_df = self.synonyms_df[self.synonyms_df['name'] == rest_name]
        synonyms = list(rest_df['synonyms'])[0] if not pd.isnull(rest_df['synonyms']).bool() else None
        if synonyms:
            synonyms = synonyms.split(',')
        return synonyms

    def update_restaurants(self, posts):
        self.synonyms_df = pd.read_excel('synonyms.xlsx').dropna()
        tagged_posts = []
        for post in posts:
            place_name = self.get_restaurant_tag_in_post(post)
            if place_name != NO_REST_IN_POST:
                tagged_posts.append((place_name, post))
            elif 'place' in post:
                self.add_place_recommendation(post)
            # else:
            #     place_name = self.get_rest_from_post_message(post)
            #     if place_name != NO_REST_IN_POST:
            #         tagged_posts.append((place_name, post))
        for (place_name, post) in tagged_posts:
            if place_name in self.all_restaurants_names:
                self.add_existing_place(post, place_name)

    def count_recs(self):
        restaurants = list(self.restaurants_data_collection.find())
        return sum([len(x['recs']) for x in restaurants])

    def print_restaurants_data(self):
        all_restaurants_data = list(self.restaurants_data_collection.find())
        data = [(res['name'], len(res['recs'])) for res in all_restaurants_data]
        df = pd.DataFrame(data, columns=['name', 'recs']).sort_values('recs', ascending=False)
        df.to_excel('restaurants.xlsx')
        print df

    def get_top_restaurants_as_json(self, count_from, count_to):
        data = {}
        top_restaurants_data = list(self.restaurants_data_collection.find())
        for res in top_restaurants_data:
            data[res['id']] = {'name': res['name'], 'recs': len(res['recs']), 'loc': res['location']}
            data[res['id']]['about'] = res['about'][0:100] if 'about' in res else 'no about'
        df = pd.DataFrame(data).T.sort_values(by=['recs'], ascending=False)
        top_ten_json = df[count_from:count_to].to_json()
        return top_ten_json

    def get_restaurant_data_by_field_as_json(self, rest_name, rest_field):
        rest_data_as_json = list(self.restaurants_data_collection.find({'name': rest_name}))[0]
        data_field = rest_data_as_json[rest_field] if rest_field in rest_data_as_json else 'NO FIELD'
        if rest_field == 'about':
            data_field = {'about': data_field}
        posts_json = json.dumps(data_field)
        return posts_json

    def get_restaurant_posts(self, rest_name, count_from, count_to):
        posts_ids = list(self.restaurants_data_collection.find({'name': rest_name}))[0]['recs'].keys()
        posts = {'posts': []}
        for post_id in posts_ids:
            if posts['posts'] > count_to:
                break
            rest_data = self.posts_collection.find({'id': post_id})[0]
            if 'message' in rest_data:
                posts['posts'].append({'id': post_id, 'text': rest_data['message'][:100]})
        posts_json = pd.DataFrame(posts['posts']).set_index('id')[count_from:count_to].to_json()
        return posts_json

    def get_restaurant_images(self, rest_name, count_from, count_to):
        posts_ids = list(self.restaurants_data_collection.find({'name': rest_name}))[0]['recs'].keys()
        posts = {'urls': []}
        for post_id in posts_ids:
            if len(posts['urls']) > count_to:
                break
            rest_data = self.posts_collection.find({'id': post_id})[0]
            if 'attachments' in rest_data:
                for attachment in rest_data['attachments']['data']:
                    if 'media' in attachment and 'image' in attachment['media']:
                        posts['urls'].append({'url': attachment['media']['image']['src'], 'id': post_id})
                    elif 'subattachments' in attachment:
                        for subattachment in attachment['subattachments']['data']:
                            if 'media' in subattachment and 'image' in subattachment['media']:
                                posts['urls'].append({'url': subattachment['media']['image']['src'], 'id': post_id})
        urls_json = pd.DataFrame(posts['urls'])[count_from:count_to].to_json()
        return urls_json

    def set_rests_synonym(self):
        rests = json.loads(self.get_top_restaurants_as_json(0, 100))['recs'].keys()
        for idx, rest_name in enumerate(rests):
            print str(idx) + '. ' + rest_name
            rest = list(self.restaurants_data_collection.find({'name': rest_name}))[0]
            if 'synonyms' not in rest:
                print rest['name'] + '\n*****************'
                user_input = raw_input()
                synonyms = user_input.split(' ') if user_input else []
                synonyms = [synonym.replace('-', ' ') for synonym in synonyms]
                if synonyms:
                    self.restaurants_data_collection.update_one({'_id': rest['_id']},
                                                                {"$set": {'synonyms': synonyms}})
