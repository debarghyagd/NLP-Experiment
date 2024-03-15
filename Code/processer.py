import nltk
from nltk import sent_tokenize,RegexpTokenizer
from nltk.corpus import stopwords
import syllapy as sp #for processing syllables
import os

nltk.download('stopwords')
nltk.download('punkt')
print()

pw_all = ["i", "you", "he", "she", "it", "we", "they", "them", "us", "him", "her", "his", "hers", "its", "theirs", "our", "your"]

def tokenize(text, verbose=False): #tokenizes the text snippet into sentences and then further into lists of words without punctuations
	tokenized_text = []
	tokenized_sents = sent_tokenize(text)
	sent_count, word_count = len(tokenized_sents), 0
	for i in tokenized_sents:
		tokens = RegexpTokenizer(r'\w+').tokenize(i)
		word_count += len(tokens)
		tokenized_text.append(tokens)

	if verbose:
		print('Tokenized-Text:\n', tokenized_text)
		print()
		print('Sentences: ', sent_count)
		print()
		print('Words: ', word_count)
		print()
		print()

	return tokenized_text




def filter(tokenized_text, verbose=False, ignore=None, sw_path='../StopWords'): # Filters stop-words from the tokenized text data passed.
	if ignore == None:
			ignore = []

	sw_all = []
	for FILE in os.listdir(sw_path): #read and accounts for all the stop-word lists(files) present.
		with open(os.path.join(sw_path,FILE), 'r') as F:
				sw_all += [i.split('|')[0].strip().lower() for i in F.readlines()]
    
	if 'nltkStopWords' not in ignore: # Accounting for nltk corpus stop words is left optional, but default.
            
		sw_nltk = stopwords.words('english')
		sw_all += sw_nltk
	
	if 'pronouns' not in ignore: # Excluding personal-pronouns stop words is left optional, but default.
		sw_all = set(sw_all).difference(set(pw_all))

	if type(sw_all)=='list':
		sw_all = set(sw_all)

	sw_filtered_text = []
	word_count = 0
	for i in tokenized_text: #removes the stop-words.
		sw_filtered_sent = []
		for j in i:
				if j == 'US':
						sw_filtered_sent.append(j)
						word_count += 1
						continue
				if j.lower() not in sw_all:
						sw_filtered_sent.append(j)
						word_count += 1
		sw_filtered_text.append(sw_filtered_sent)
  
	if verbose:
		print('Stop-Words:\n', sw_all, '(',len(sw_all),')')
		print()
		print('Personal-Pronouns: ', pw_all, '(',len(pw_all),')')
		print()
		print('Filtered-Text:\n', sw_filtered_text, '\n\tSentences: ',len(sw_filtered_text), '\n\tWords: ',word_count)
		print()
		print()

	return sw_filtered_text



def sentiment(sw_filtered_text, verbose=False, dic_path='../MasterDictionary'): #counts positive, negative, & complex-words as well as total sentences, words, syllables, & letters.
	for i in os.listdir(dic_path): #reads and accounts for all the positive and negative words .
		if 'pos' in i.lower():
			with open(os.path.join(dic_path,i),'r') as positive_words_txt:
				positive_words = [i.strip('\n') for i in positive_words_txt.readlines()]
		if 'neg' in i.lower():
			with open(os.path.join(dic_path,i),'r') as negative_words_txt:
				negative_words = [i.strip('\n') for i in negative_words_txt.readlines()]

	sentiment_words = {'positive':[], 'negative': []}
	sent_count, word_count, char_count, pron_count, syll_count, comp_count = 0, 0, 0, 0, 0, 0
	for sent in sw_filtered_text:
		sent_count += 1
		for word in sent:
			word_count += 1
			char_count += len(word)
			syll_count += sp.count(word) #counting syllables
			if word.lower() in positive_words:
				sentiment_words['positive'].append(word) #add to dictionary if it's a postive non-stop-word
			if word.lower() in negative_words:
				sentiment_words['negative'].append(word) #add to dictionary if it's a negative non-stop-word
			if word.lower() in pw_all:
				pron_count += 1 #counting pronouns
			if sp.count(word) > 2:
				comp_count += 1 #counting complex words (more than 2 syllables present)

	result={	'Sentences': sent_count,
				'Words': word_count,
				'Positive': {   'tokens':sentiment_words['positive'], 
								'count':len(sentiment_words['positive'])
							}, 
				'Negative': {   'tokens':sentiment_words['negative'], 
								'count':len(sentiment_words['negative'])
							},
				'Complex-words': comp_count,
				'Personal-Pronouns': pron_count,
				'Syllables': syll_count,
				'Letters': char_count,
			}

	if verbose:
		print(result['Positive'])
		print()
		print(result['Negative'])
		print()
		print()

	return result


def process(text, sw_path='../StopWords', dic_path='../MasterDictionary', verbosity = [], ignore = []): #pipelines the tokenization, filtering, and semantic-analysis step
	tokenized_text = tokenize(text, verbose=('tokenize' in verbosity))
	sw_filtered_text = filter(tokenized_text, verbose=('filter' in verbosity), ignore=ignore, sw_path=sw_path)
	processed_data = sentiment(sw_filtered_text, verbose=('sentiment' in verbosity), dic_path='../MasterDictionary')

	scores = dict() #creating a dictionary to store various scorrs
	scores['POSITIVE SCORE'] = processed_data['Positive']['count']
	scores['NEGATIVE SCORE'] = processed_data['Negative']['count']
	scores['POLARITY SCORE'] = (scores['POSITIVE SCORE'] - scores['NEGATIVE SCORE'])/ ((scores['POSITIVE SCORE'] + scores['NEGATIVE SCORE']) + 0.000001)
	scores['SUBJECTIVITY SCORE'] = (scores['POSITIVE SCORE'] + scores['NEGATIVE SCORE'])/ ((processed_data['Words']) + 0.000001)
	scores['AVG SENTENCE LENGTH'] = processed_data['Words'] / processed_data['Sentences']
	scores['PERCENTAGE OF COMPLEX WORDS'] = processed_data['Complex-words'] / processed_data['Words']
	scores['FOG INDEX'] = 0.4 * (scores['AVG SENTENCE LENGTH'] + scores['PERCENTAGE OF COMPLEX WORDS'])
	scores['AVG NUMBER OF WORDS PER SENTENCE'] = scores['AVG SENTENCE LENGTH']
	scores['COMPLEX WORD COUNT'] = processed_data['Complex-words']
	scores['WORD COUNT'] = processed_data['Words']
	scores['SYLLABLE PER WORD'] = processed_data['Syllables'] / processed_data['Words']
	scores['PERSONAL PRONOUNS'] = processed_data['Personal-Pronouns']
	scores['AVG WORD LENGTH'] = processed_data['Letters'] / processed_data['Words']

	if 'process' in verbosity:
		for i in scores.items():
			print(f'{i[0]}: {i[-1]}')
		print()
		print()

	return scores