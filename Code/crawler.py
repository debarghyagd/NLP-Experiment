import requests as re
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import os
import time

print()
def crawl(input_path='../Input.xlsx', save_as='Dataframe.csv', verbose=False): #extracts text data from each blog-link
    if not (save_as in os.listdir('.')):
        df = pd.read_excel(input_path)
        err_url_id_new= [] #list of erroneos/bad pages
        titles, contents = [],[]
        for i in tqdm(range(df.shape[0]), desc='Crawled: '):
            try:
                resp = re.get(df.iloc[i].URL)
                if resp.status_code == 200: #parses HTML for title and and content tags if page is responsive/live
                    soup = BeautifulSoup(resp.text,'html.parser')
                    title, content = soup.find('h1', class_='entry-title'),soup.find('div', class_='td-post-content tagdiv-type')
                    if not (title and content):
                        title, content = soup.find('h1', class_='tdb-title-text'),soup.find('div', class_='td_block_wrap tdb_single_content tdi_130 td-pb-border-top td_block_template_1 td-post-content tagdiv-type').find('div', class_='tdb-block-inner td-fix-index')
                    title, content = title.get_text(), ' '.join(content.get_text().strip('\n').split('\n')[:-1])
                    titles.append(title)
                    contents.append(content)
                else:
                    titles.append('.') #default title text for bad pages
                    contents.append('.') #default title text for bad pages
            except Exception as e: #handles errors and lists bad pages
                err_url_id_new.append(df.iloc[i].URL_ID)
                print(f'Error: {e}, in URL: {df.iloc[i].URL} (ID: {df.iloc[i].URL_ID})') 

        df['TITLE'] = titles
        df['CONTENT'] = contents

        if save_as: #saves crawled data into a DataFrame
            df.to_csv(save_as,index=False)

        if verbose:
            print(df)

        return df

    else: #skip crawling if already crawled data present
        df = pd.read_csv(save_as)
        for i in tqdm(range(df.shape[0]), desc='Crawled: '):
            continue
        time.sleep(1)
        return df
    