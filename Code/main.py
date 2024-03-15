import pandas as pd
from tqdm import tqdm
import os
import pandas as pd
from crawler import crawl #for data extraction
from processer import process #for text analysis

INPUT_PATH = os.environ.get('INPUT_EXCEL','../Input.xlsx')
OUTFORM_PATH = os.environ.get('FORMAT_EXCEL','../Output Data Structure.xlsx')
OUTPUT_PATH = os.environ.get('OUTPUT_EXCEL','../Output.xlsx')
STOP_WORDS_PATH = os.environ.get('SW_PATH','../StopWords')
MASTER_DICT_PATH = os.environ.get('MD_PATH','../MasterDictionary')

df = crawl(INPUT_PATH,save_as='Dataframe.csv') #extracts the title and the content of the blogs from the links and store into a DataFrame
# print(df)

dfo = pd.read_excel(OUTFORM_PATH) #reads the desired output format

print()
err_url_id_new= []
for i in tqdm(range(df.shape[0]), desc='Processed: '):
	try:
		title = df.loc[i,'TITLE']
		content = df.loc[i,'CONTENT']
  
		if title == '.' and content == '.': #for handling errors occured during extraction step, such as HTTP 404
			err_url_id_new.append(df.iloc[i].URL_ID)
			for x in dfo.columns[2:]:
				dfo.loc[i,x] = None
			continue

		elif title[-1] == '.':
			text = title +' '+content
		else:
			text = title +'. '+content

		result = process(text, sw_path=STOP_WORDS_PATH, dic_path=MASTER_DICT_PATH) #returns the various scores/counts/indexes for the given text snippet

		for j in result.items():
			dfo.loc[i,j[0]] = j[-1]

	except Exception as e:
		err_url_id_new.append(df.iloc[i].URL_ID)
		print(f'Error: {e}, in URL: {df.iloc[i].URL} (ID: {df.iloc[i].URL_ID})')

# print(dfo)
dfo.to_excel(OUTPUT_PATH,index=False) #saves the text analysis output to desired path