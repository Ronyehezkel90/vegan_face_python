import copy
import facebook
import requests
from conf import POST_FIELDS_LIST, BASE_URL, POSTS_COUNT, DAY_RANGE, APP_SECRET_ID, APP_ID, TOKEN_FILE_NAME, \
    REACTIONS_DICT
from utils import get_day_range_unix_time, file_modified_in_last_hour
import json


class FacebookHandler:
    def __init__(self):
        self.graph = facebook.GraphAPI(access_token=self.get_facebook_token(), version='2.6')

    def get_facebook_token(self):
        if file_modified_in_last_hour(TOKEN_FILE_NAME):
            with open(TOKEN_FILE_NAME) as f:
                token = f.readline()
        else:
            payload = {'grant_type': 'client_credentials', 'client_id': APP_ID, 'client_secret': APP_SECRET_ID}
            response = requests.post('https://graph.facebook.com/oauth/access_token?', params=payload)
            token = json.loads(response.content)['access_token']
            with open(TOKEN_FILE_NAME, 'w') as token_file:
                token_file.write(token)
        return token

    def set_reactions(self, posts):
        for post in posts:
            reactions = copy.deepcopy(REACTIONS_DICT)
            if 'reactions' in post:
                current_post = post
                while 'paging' in current_post['reactions'] and 'next' in current_post['reactions']['paging']:
                    next_field = current_post[u'reactions'][u'paging'][u'next']
                    after_reaction_id = next_field[next_field.find('after=') + 6:].split('&')[0]
                    current_post = self.graph.get_objects(ids=[post['id']],
                                                          fields=POST_FIELDS_LIST + '.after({})'.format(
                                                              after_reaction_id)).values()[0]
                    post['reactions']['data'] += (current_post['reactions']['data'])
                for reaction in post['reactions']['data']:
                    reactions[reaction['type']] += 1
            post['reactions'] = reactions
        return posts

    def get_posts_from_facebook(self, before_days=None):
        base_url = BASE_URL
        if before_days:
            day_range_tuple = get_day_range_unix_time(before_days)
            base_url = BASE_URL + DAY_RANGE.format(day_range_tuple[0], day_range_tuple[1])
        group_data = self.graph.get_object(base_url)
        posts = group_data['feed']['data']
        post_ids = [post['id'] for post in posts]
        posts_data = []
        for counter in range(0, (POSTS_COUNT / 50) + 1):
            limited_post_ids = post_ids[counter * 50:(counter + 1) * 50]
            if limited_post_ids:
                posts_extra_data = self.graph.get_objects(ids=limited_post_ids, fields=POST_FIELDS_LIST).values()
                posts_extra_data = self.set_reactions(posts_extra_data)
                posts_data += posts_extra_data
        return posts_data
