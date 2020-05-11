
import csv
import time
import re
from string import punctuation
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import twitter
# IMPORTANT : package to be installed is python-twitter and to be imported i twitter


twitter_api = twitter.Api(consumer_key='Your_Consumer_Key',
                        consumer_secret='Your_Consumer_Secret',
                        access_token_key='Your_Access_Token_Key',
                        access_token_secret='Your_Access_Token_Secret')

twitter_api.VerifyCredentials()


def SearchTweets(keyword):
    tweets_fetched=twitter_api.GetSearch(keyword,count=100)
    # print("Fetched"+len(tweets)+" tweets for "+keyword)
    return [{"text":status.text, "label":None} for status in tweets_fetched]

testDS=SearchTweets("football")

def TrainingSet(corpusFile, trainingFile):
    import csv
    import time
    
    corpus = []
    
    with open(corpusFile,'r') as csvfile:
        lineReader = csv.reader(csvfile,delimiter=',', quotechar="\"")
        for row in lineReader:
            corpus.append({"tweet_id":row[2], "label":row[1], "topic":row[0]})
            
    rate = 180
    sleep_time = 5


    training=[]

    for tweet in corpus:
        try:
            status=twitter_api.GetStatus(tweet["tweet_id"])
            tweet["text"]=status.text
            training.append(tweet)
            time.sleep(sleep_time)
        except:
            continue


        with open(trainingFile,'w') as csvfile:
            linewriter = csv.writer(csvfile,delimiter=',',quotechar="\"")
            for tweet in training:
                try:
                    linewriter.writerow([tweet["tweet_id"], tweet["text"], tweet["label"], tweet["topic"]])
                except Exception as e:
                    print(e)
    return training



corpusfile="/home/vikrant/Desktop/Projects/TwitterSentimentAnalysis/env/corpus.csv"
trainingfile="/home/vikrant/Desktop/Projects/TwitterSentimentAnalysis/env/training.csv"
trainingDS=TrainingSet(corpusfile,trainingfile)

def PreProcess(dataset):
    total_stopwords = set(stopwords.words("english")+list(punctuation)+["AT_USER","URL"])
    for tweet in dataset:
        text1=tweet["text"]
        text1=text1.lower()
        text1 = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', text1) # remove URLs
        text1 = re.sub('@[^\s]+', 'AT_USER', text1) # remove usernames
        text1 = re.sub(r'#([^\s]+)', r'\1', text1) # remove the # in #hashtag
        text1 = word_tokenize(text1) # remove repeated characters (helloooooooo into hello)
        finaltext=""
        processedTweet=[]
        for word in text1:
            if word not in stopwrods:
                finaltext= finaltext + word
        processedTweet.append(finaltext,tweet["label"])


proTrainDS=PreProcess(trainingDS)
proTestDS=PreProcess(testDS)

      
def Vocab(proTrainDS):
    words_list=[]
    for (words,sentiment) in proTrainDS:
        words_list.extends(words)

    wordFreq=nltk.FreqDist(words_list)
    word_features=wordFreq.keys()
    return word_features


def ExtractFeatures(tweet,word_features):
    tweet_set=set(tweet)
    features={}
    for word in word_feature:
        features["contain(%s)"%word]=(word in tweet_set)
    return features

word_features=Vocab(proTrainDS)
trainingFeatures=nltk.classify.apply_features(ExtractFeatures, proTrainDS)
NBayesClassifier = nltk.NaiveBayesClassifier.train(trainingFeatures)

for tweet in proTestDS:
    NBResultLabels = NBayesClassifier.classify(ExtractFeatures(tweet[0]))
    if NBResultLabels.count('positive') > NBResultLabels.count('negative'):
        print("Overall Positive Sentiment")
        print("Positive Sentiment Percentage = " + str(100*NBResultLabels.count('positive')/len(NBResultLabels)) + "%")
    else: 
        print("Overall Negative Sentiment")
        print("Negative Sentiment Percentage = " + str(100*NBResultLabels.count('negative')/len(NBResultLabels)) + "%")
