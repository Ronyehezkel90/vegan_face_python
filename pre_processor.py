import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.tree import DecisionTreeClassifier

from conf import CHARS_TO_REMOVE, GOOD_RANK, IRRELEVANT_RANK, BAD_RANK
from db_handler import DB_Handler
from emoji import UNICODE_EMOJI


class PreProcessor:
    def __init__(self):
        self.data_handler = DB_Handler()
        self.restaurnts_words = re.sub(CHARS_TO_REMOVE, ' ',
                                       ' '.join(self.data_handler.all_restaurants_names).encode('utf-8')).split()
        with open('heb_stopwords.txt', 'r') as f:
            stopwords_list = [line.strip() for line in f]
            self.stopwords = set(stopwords_list)

    def is_res_name(self, word):
        return True if (word[2:] in self.restaurnts_words) or word in self.restaurnts_words else False

    def emoji_handler(self, s):
        for emoji in UNICODE_EMOJI:
            if emoji in s:
                s = s.replace(emoji, ' ' + emoji + ' ')
        return s

    def prediction(self, classifier, X_train, X_test, y_train, y_test):
        classifier.fit(X_train.astype(int), y_train.astype(int))
        y_pred = classifier.predict(X_test)
        cm = confusion_matrix(y_test.astype(int), y_pred)
        print accuracy_score(y_test.astype(int), y_pred)
        print cm

    def pre_process_recs(self):
        posts = self.data_handler.get_posts_from_mongo()
        recs_df = pd.DataFrame(posts)
        recs_df = recs_df[pd.notnull(recs_df['rank'])]
        recs_df.dropna(subset=['message'], inplace=True)
        words_bag = []
        for rec in recs_df['message']:
            clean_rec = self.emoji_handler(rec)
            clean_rec = re.sub(CHARS_TO_REMOVE, ' ', clean_rec.encode('utf-8')).split()
            # todo -  Here I should stemming the words or using LEMA by HebMorph - Java library for Lema
            # remove restaurants names from posts.
            clean_rec = [word for word in clean_rec if word not in self.stopwords and not self.is_res_name(word)]
            clean_rec = ' '.join(clean_rec)
            words_bag.append(clean_rec)
        cv = CountVectorizer(max_features=1500)
        X = cv.fit_transform(raw_documents=words_bag).toarray()
        ranks = recs_df['rank'].values
        ranks[ranks == BAD_RANK] = 0
        ranks[ranks == GOOD_RANK] = 1
        ranks[ranks == IRRELEVANT_RANK] = 2
        y = ranks
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
        classifier = GaussianNB()
        self.prediction(classifier, X_train, X_test, y_train, y_test)
        classifier = DecisionTreeClassifier(criterion='entropy', random_state=0)
        self.prediction(classifier, X_train, X_test, y_train, y_test)
