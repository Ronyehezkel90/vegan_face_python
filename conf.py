POSTS_COUNT = 200
APP_ID = '1705401553076241'
APP_SECRET_ID = '3594b7152674e912e843ef9209191c91'
TOKEN_FILE_NAME = 'token_file.txt'
UNIX_HOUR_REPRESENTATION = 3600
POST_FIELDS_LIST = 'created_time, message, place, attachments'
BASE_URL = '619669744790558/?fields=feed.limit({})'.format(str(POSTS_COUNT))
PLACE_URL = 'search?type=place&q={}&fields=name,id,location,hours,about'
DAY_RANGE = '.since({}).until({})'
GOOD_RANK = 'good'
BAD_RANK = 'bad'
IRRELEVANT_RANK = 'irrelevant'
POSTS_WITHOUT_RANK_QUERY = {'rank': {'$exists': 0}}
RESTAURANT_DATA = {
    'images': [],
    'recs': [],
    'dis_recs': [],
    'synonyms': []
}
CHARS_TO_REMOVE = '[,.~!-@#$%^&*(){}[;:<>\'"?/]'
ENGLISH_CHARS = '[a-zA-z0-9]'
BAD_CHARACTERS = ['?']
MEMORY_LIMIT = 20000
POSTS_PER_REQUEST = 3

ATTACHMENTS = 'attachments'
DATA = 'data'
DESC_TAG = 'description_tags'
NAME = 'name'
NO_TAG_IN_POST = 'no_tag_in_post'
