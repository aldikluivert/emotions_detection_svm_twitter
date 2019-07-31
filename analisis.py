import tweepy
from nltk.corpus import stopwords
import re, string, pickle, joblib
from nltk import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import numpy as np
from wordcloud import WordCloud

list_stopwords = set(stopwords.words('indonesian'))
a = ['rt', 'amp', 'si', 'jae', 'pa', 'aja', 'dgn', 'via', 'to', 'yg', 'sdh', 'rr', 'sih']
stopwords = list_stopwords.union(a)

hasil_preprocess = []

class analisis():

    def processing(self, keyword, jumlah):

        # list of raw tweets
        tweets = []
        # number
        count = []

        postag_file = []

        counter = 0

        # authenticating
        consumerKey = '1snOJJobHYSineKS2NllqhCuv'
        consumerSecret = 'TOWiJdAval9Bpe01wRjr1HNaovVv1KDlOAdZZMWD6F4CrLrzl1'
        accessToken = '782325524-NMBUD40C6sBjHElBpamHqGhPEQaUOWy4y5fozlLm'
        accessTokenSecret = 'PT1kupQZSbsyaKVKIa6YyFAZEZofqw774Ci59yzwrQigS'

        auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
        auth.set_access_token(accessToken, accessTokenSecret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        for tweet in tweepy.Cursor(api.search, q=keyword).items(jumlah):

            # counter of data
            counter += 1

            count.append(counter)

            # extract twitter tweet only
            tweet = tweet.text

            # append raw tweet to tweet list
            tweets.append(tweet)

            # case folding
            hasil = tweet.lower()

            # remove web URL
            hasil = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', hasil)

            # remove username
            hasil = re.sub('@[^\s]+', '', hasil)

            # remove #
            hasil = re.sub('#[^\s]+', '', hasil)

            # remove number
            hasil = re.sub(r'\d+', '', hasil)

            # remove punctuation
            hasil = hasil.translate(str.maketrans('', '', string.punctuation))

            # remove emoji or ascii character
            hasil = hasil.encode('ascii', 'ignore').decode('ascii')

            # remove multiple letters
            hasil = re.sub(r'(.)\1+', r'\1\1', hasil)

            # remove single letter
            hasil = re.sub(r'\b[a-zA-Z]\b', '', hasil)

            # load pickle POS Tag File
            file = open('indonesian_ngram_pos_tag.pickle', 'rb')
            ngram_tagger = pickle.load(file)

            # POS Tag process
            hasil_ = ngram_tagger.tag(word_tokenize(hasil))

            # append each pos tag result to an array
            for item in hasil_:
                postag_file.append(item)

            # word tokenize
            tokens = word_tokenize(hasil)

            # stopwords removal
            stopped_words = [word for word in tokens if word not in stopwords]
            hasil = ' '.join(stopped_words)

            # stemming
            factory_stem = StemmerFactory()
            stemmer = factory_stem.create_stemmer()
            hasil = stemmer.stem(hasil)

            hasil_preprocess.append(hasil)

            file.close()

        load_vector = joblib.load(open('vectorizer_joblib.pkl', 'rb'))
        tfidf_test = load_vector.transform(hasil_preprocess)

        load_model = joblib.load(open('model_svm_joblib2.sav', 'rb'))
        hasil_svm = load_model.predict(tfidf_test)

        persen = []
        marah = np.sum( hasil_svm == 'marah')
        marah = round((marah / hasil_svm.size) * 100)
        persen.append(marah)
        sedih = np.sum(hasil_svm == 'sedih')
        sedih = round((sedih / hasil_svm.size) * 100)
        persen.append(sedih)
        senang = np.sum(hasil_svm == 'senang')
        senang = round((senang / hasil_svm.size) * 100)
        persen.append(senang)
        terkejut = np.sum(hasil_svm == 'terkejut')
        terkejut = round((terkejut / hasil_svm.size) * 100)
        persen.append(terkejut)

        # zip 2 lists into 1 list
        clf_result = zip(count, tweets, hasil_svm)

        # open out file
        out_file = open('postag_n_file.txt', 'w', encoding='utf-8')

        postag_n = []

        # select certain labels
        for i in range(0, len(postag_file)):
            if postag_file[i][1] == 'NN':
                postag_file.append(postag_file[i][0])
                out_file.write(postag_file[i][0])
                out_file.write('\n')
                counter += 1
            elif postag_file[i][1] == 'NNP':
                postag_n.append(postag_file[i][0])
                out_file.write(postag_file[i][0])
                out_file.write('\n')
                counter += 1
            elif postag_file[i][1] == 'NND':
                postag_n.append(postag_file[i][0])
                out_file.write(postag_file[i][0])
                out_file.write('\n')
                counter += 1

        # close out_file access to program
        out_file.close()

        in_file = open('postag_n_file.txt', encoding='utf-8')
        texts = in_file.read()

        wcc = WordCloud(stopwords=stopwords, background_color='white')
        wcc.generate(texts)
        wcc.to_file('static/wc.png')
        # in_file.close()

        return clf_result, persen, count
