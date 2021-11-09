from nltk.tokenize.treebank import TreebankWordDetokenizer
from swanalytics_logger import get_sw_logger
swanalytics_logger = get_sw_logger()

from pyLDAvis import gensim as gensim_pyLDAvis
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from nltk.tokenize import TweetTokenizer
from textblob import TextBlob, Word
from nltk.corpus import stopwords
from gensim import corpora

import itertools
import pyLDAvis
import enchant  # vocabulary to process words stuck together
import gensim
import string
import spacy  # lemmatization
import json
import re


# define stop_words:
stop_words = stopwords.words('english')
stop_words.remove("down")
stop_words.remove("up")
stop_words.remove("against")
stop_words.extend(['from', 'subject', 're', 'edu', 'use', 'via', "tsla", "tesla",
                   "nos"])  # add Tesla because it doesnt add any value to the topic analysis.

# Initialize spacy 'en' model, keeping only tagger component (for efficiency)
nlp = spacy.load('en', disable=['parser', 'ner'])

# make a function to process words stuck together
list_exclude = ['sensor', 'amzn', 'edrive', 'etruck', 'suvs', 'elon', 'musk', 'ppl',
                'incl', 'excl', 'lol', 'lolza', 'wtf',
                'lmao', 'rofl', 'div', 'tlsa', 'dino', 'tesla', 'wuhan', 'corona',
                'covid', 'trump', 'donald', 'ooo', 'jb', 'straubel', 'nikolai',
                'nokia', 'usn', 'youtuber', 'deathtrap']

eng_dict = enchant.Dict("en_US")
for i in list_exclude:
    eng_dict.add(i)
eng_dict.add("electriic")


def remove_ends(text):
    for j, i in enumerate(reversed(text)):
        if i.startswith('#') or i.startswith('$') or i.startswith('&') or i in list(
                string.punctuation) or i in stop_words:
            continue
        elif j == 0:
            text = text
        else:
            text = text[:-j]
            break
    return text


def lemmatization(text, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    """https://spacy.io/api/annotation"""
    texts_out = []
    for sent in text:
        doc = nlp(" ".join(sent))
        texts_out.append(
            [token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out


def segment_string(chars, exclude=None):
    """
    Segment a string of chars using the pyenchant vocabulary.
    Keeps longest possible words that account for all characters,
    and returns list of segmented words.

    :param chars: (str) The character string to segment.
    :param exclude: (set) A set of string to exclude from consideration.

                    If an excluded word occurs later in the string, this
                    function will fail.
    """
    words = []

    if not chars.isalpha():  # don't check punctuation etc.; needs more work
        return [chars]

    if not exclude:
        exclude = set()

    working_chars = chars
    while working_chars:
        # iterate through segments of the chars starting with the longest segment possible
        for i in range(len(working_chars), 1, -1):
            segment = working_chars[:i]
            if eng_dict.check(segment) and segment not in exclude:
                words.append(segment)
                working_chars = working_chars[i:]
                break
        else:  # no matching segments were found
            if words:
                exclude.add(words[-1])
                return segment_string(chars, exclude=exclude)
            # let the user know a word was missing from the dictionary,
            # but keep the word
            return [chars]
    # return a list of words based on the segmentation
    return words


def get_dict_data(event):
    dict_df = {}  # a dict to store all the text-tweets across multiple keys(event dates)

    filename = event["start_date"] + "_" + event["end_date"]
    with open("tweets/results/" + filename + ".json", "r") as twitter_file:
        twitter_data = json.load(twitter_file)["tweets"]
        dict_df.update({filename: [sub['text'] for sub in twitter_data]})

    for key in dict_df.keys():
        dict_df.update(
            {key: [re.sub('\S*@\S*\s?', '', sent) for sent in dict_df[key]]})
        dict_df.update({key: [re.sub('\s+', ' ', sent) for sent in dict_df[key]]})
        dict_df.update(
            {key: [re.sub(r"http\S+", "", sent) for sent in dict_df[key]]})
        dict_df.update(
            {key: [TweetTokenizer().tokenize(sent) for sent in dict_df[key]]})
        dict_df.update({key: [remove_ends(sent) for sent in dict_df[key]]})
        dict_df.update({key: [remove_ends(sent) for sent in dict_df[
            key]]})  # twice, because of cases such as dict_df['2019-07-24'][3]
        dict_df.update({key: [[TreebankWordDetokenizer().detokenize(sent)] for sent
                              in dict_df[key]]})
        dict_df.update({key: [
            [word for word in simple_preprocess(str(sent), deacc=True) if
             word not in stop_words] for sent in
            dict_df[key]]})  # remove_stopwords and get back tokenized datar

    ## Lemmatization:  + taking care of words stuck together
    return dict_df


def get_topic_data(event):
    dict_df = get_dict_data(event)
    for key in dict_df.keys():
        dict_df[key] = [
            list(itertools.chain.from_iterable([list(*[segment_string(word)])
                                                for word in sent if
                                                word not in stop_words])) for sent
            in dict_df[key]]
        dict_df[key] = lemmatization(dict_df[key],
                                     allowed_postags=['NOUN', 'ADJ', 'VERB',
                                                      'ADV'])  # takes some time
        dict_df.update({key: [[str(TextBlob(word).correct()) for word in sent] for sent in dict_df[key]]})

    return dict_df


# MODEL :
def model_config(corpus, dictionary, num_topics=10, random_state=100):
    lda = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                          id2word=dictionary,
                                          num_topics=num_topics,
                                          random_state=random_state,
                                          update_every=1,
                                          chunksize=100,
                                          passes=10,
                                          alpha='auto',
                                          per_word_topics=True,
                                          eval_every=None)
    return lda


def get_model_out(dict_df, num_topics=None, limit=31, start=2, step=3,
                  show_num_topics=-1, word_map=False,
                  random_state=100):
    num_words = 6

    for key in dict_df.keys():
        # intermediary:
        c_v = []  # saves coherence scores
        model_list = []  # saves models
        topic_weights = []  # for extracting dominant topic
        tokenized_corpus = dict_df[key]
        id2word = corpora.Dictionary(tokenized_corpus)
        corpus = [id2word.doc2bow(text) for text in tokenized_corpus]
        # run model
        if num_topics:
            for topic in range(start, limit, step):
                model = model_config(corpus=corpus, dictionary=id2word,
                                        num_topics=topic,
                                        random_state=random_state)
                model_list.append(model)
                cm = CoherenceModel(model=model, texts=tokenized_corpus,
                                    dictionary=id2word, coherence='c_v')
                c_v.append(cm.get_coherence())

        else:
            model = model_config(corpus=corpus, dictionary=id2word,
                                    num_topics=num_topics,
                                    random_state=random_state)
            model_list.append(model)
            cm = CoherenceModel(model=model, texts=tokenized_corpus,
                                dictionary=id2word, coherence='c_v')
            c_v.append(cm.get_coherence())

        model = model_list[c_v.index(max(c_v))]
        model_topics = model.show_topics(num_words=num_words, formatted=False,
                                            num_topics=show_num_topics)
        topics = {}
        for j in [i[0] for i in model_topics]:
            topics[j] = dict(model_topics[j][1])
        # TSNE:

        for i, row_list in enumerate(model[corpus]):
            topic_weights.append([w for i, w in row_list[0]])

        panel = gensim_pyLDAvis.prepare(model, corpus, id2word, mds='tsne')  #
        pyLDAvis.save_html(panel, f'tweets/results/topic_analysis/pyLDAvis_{key}.html')


def read_events():
    with open("events.json", "r") as read_file:
        return json.load(read_file)


def topic_analysis():
    events = read_events()
    for event in events["events"]:
        swanalytics_logger.info(f"[{event['start_date']} to {event['end_date']}] {event['title']}")
        dict_df = get_topic_data(event)

        # change num_topics to some value (11) for a fast run, else None
        get_model_out(dict_df=dict_df, num_topics=11, limit=35, start=8, step=5,
                    show_num_topics=-1, word_map=False, random_state=100)


def main():
    swanalytics_logger.info("Started topic analysis")
    topic_analysis()


if __name__ == "__main__":
    main()
