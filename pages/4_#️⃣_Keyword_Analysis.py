import os
import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="#️⃣ Reddit Keyword Analysis", layout="wide")
st.title("#️⃣ Reddit Keyword Analysis")

base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(base_dir)
data_dir = os.path.join(project_root, "data")

@st.cache_data
def load_csv(file_name):
    return pd.read_csv(os.path.join(data_dir, file_name))

subreddit = st.selectbox('주제 선택', ['askrunningshoegeeks', 'handbags'])
default_brands = ['coach', 'louis vuitton'] if subreddit.lower() == 'handbags' else ['hoka', 'asics']

if subreddit.lower() == 'handbags':
    df_sub = load_csv('handbags_subreddit.csv')
    df_comm = load_csv('handbags_comments.csv')
    df_sub['text'] = df_sub['title'].fillna('') + ' ' + df_sub['selftext'].fillna('')
    df_comm['text'] = df_comm['comment_body'].fillna('')
    df_comm.rename(columns={'comment_time': 'time'}, inplace=True)
    df = pd.concat([df_sub, df_comm], ignore_index=True)
    brand_keywords = {
        'coach': ['coach', 'tabby', 'brooklyn', 'willow', 'swing zip', 'lana', 'juliet', 'cargo', 'kira'],
        'katespade': ['kate spade', 'deco chain', 'deco tweed', 'deco eyelet', 'deco crossbody', 'deco hobo', 'grace', 'tilly', 'nouveau', 'spade', 'liv', 'sam icon', 'manhattan', 'hudson', 'serena', 'suite', 'serena'],
        'gucci': ['gucci', 'bamboo', 'diana', '1955', 'gg emblem', 'ophidia', 'jackie', 'blondie', 'dionysus', 'marmont'],
        'louis vuitton': ['louis vuitton', 'louisvuition', 'lv', 'neverfull', 'speedy', 'alma', 'capucines', 'pochette', 'twist', 'go-14', 'go 14','twist', 'dauphine', 'coussin', 'onthego', 'neonoe', 'petit sac plat', 'locky', 'cluny'],
        'chanel': ['chanel', 'classic flap', 'flap', 'boy bag', '2.55', 'caviar', 'trendy cc', 'coco handle', 'gabrielle', '19', 'new mini'],
        'prada': ['prada', 're nylon', 'galleria', 'arque', 'cleo', 're-nylon', 'leather bucket', 're-edition'],
        'hermes': ['hermes', 'birkin', 'kelly', 'basket', 'garden party', 'constance', 'bolide', 'lindy', 'picotin', 'herbag', 'roulis', 'verrou', '2002', 'berline', 'cherche midi'],
        'fendi': ['fendi', 'peekaboo', 'baguette', 'monfriend', 'origami', "c'mon", 'cmon', 'mon tresor', 'by the way'],
        'burberry': ['burberry', 'check', 'banner', 'pocket', 'highlands', 'cotswolds', 'note', 'crochet', 'chainmail', 'hampshire', 'freya'],
        'mulberry': ['mulberry', 'bayswater', 'scarlett', 'amber', 'islington', 'lily', 'alexa', 'clovelly', 'lana', 'antony', 'iris'],
        'dior': ['christian', 'd-journey', 'lady dior', 'toujours', 'book tote', 'saddle', 'bobby', '30 montaigne', 'caro', 'dior groove', 'lady d-lite', 'lady d-joy', 'd joy', 'd-joy', 'd journey', 'book tote'],
        'goyard': ['goyard', 'saigon', 'vendome', 'boheme', 'anjou', 'artois', 'saint louis', 'st louis', 'voltaire', 'bellechasse', 'bohème', 'croisiere', 'majordome', 'comor', 'goyardine'],
        'celine': ['triomphe', 'victoire', 'ava', 'celine classic', 'nano belt', 'celine velt', '16', 'celine 16', 'celine'],
        'toryburch': ['romy', 'ella', 'fleming', 't monogram', 'lee', 'perry', 'tory burch'],
        'bottega veneta': ['bottega veneta', 'ciao ciao', 'cassette', 'jodie', 'arco', 'cabat', 'knot lock', 'pinacoteca', 'patti', 'andiamo', 'lauren', 'parachute'],
        'ysl': ['saint laurent', 'ysl', 'loulou', 'le 37', 'puffer', 'college', 'sac de jour', 'le 5 à 7', 'kaia', 'sunset', 'envelope', 'calypso', 'jamie', 'ysl y', 'icare'],
        'michael kors': ['michael kors', 'marilyn', 'jet set', 'nolita', 'harrison', 'laila', 'bryant', 'lillie', 'tribeca', 'hudson', 'chelsea', 'scarlett'],
        'miu miu': ['miu miu', 'miumiu', 'wander matelassé', 'leather beau', 'arcadie', 'aventure']
    }
else:
    df_sub = load_csv('askrunningshoegeeks_subreddit.csv')
    df_comm = load_csv('askrunningshoegeeks_comments.csv')
    df_sub['text'] = df_sub['title'].fillna('') + ' ' + df_sub['selftext'].fillna('')
    df_comm['text'] = df_comm['comment_body'].fillna('')
    df_comm.rename(columns={'comment_time': 'time'}, inplace=True)
    df = pd.concat([df_sub, df_comm], ignore_index=True)
    brand_keywords = {
        'hoka': ['hoka', 'bondi', 'bondi 9', 'bondi 8', 'clifton', 'clifton 9', 'speedgoat', 'arahi', 'stinson'],
        'nike': ['nike', 'air max', 'air force 1', 'pegasus', 'cortez', 'react', 'zoom', 'dunk', 'air jordan', 'jordan', 'vomero', 'shox', 'invincible', 'pegasus', 'alphafly', 'kiger', 'wildhorse', 'maxfly'],
        'adidas': ['adidas', 'ultraboost', 'yeezy', 'nmd', 'stan smith', 'superstar', 'adilette', 'gazelle', 'spezial', 'adizero', 'pureboost', 'supernova'],
        'newbalance': ['new balance', 'nb', '574', '990', '1080', 'minimus', '997', '9060', '530', '740', '1906', '1080', '990', '992', '2002', '993', 'fresh foam', 'fuelcell'],
        'asics': ['asics', 'gel nimbus', 'gel kayano', 'gel clydesdale', 'gel cumulust', 'gt-2000', 'gel lyte iii', 'superblast', 'novablast', 'gel quantum', 'gel-venture', 'gel-kayano', 'gel-lyte', 'gel-cumulus', 'gel-1130', 'metaspeed', 'noosa'],
        'reebok': ['reebok', 'classic', 'nano', 'pump', 'zig', 'instapump', 'energen'],
        'underarmour': ['under armour', 'ua', 'hovr', 'curry', 'charger', 'project rock', 'flow', 'phantom', 'charged assert', 'reign', 'speedform', 'slipspeed', 'surge', 'infinite'],
        'puma': ['puma', 'rs-x', 'suede', 'future', 'ignite', 'cell', 'future rider', 'clyde', 'deviate', 'cell thrill', 'rocket fuel', 'softride', 'neutron', 'contempt'],
        'brooks': ['brooks', 'ghost', 'adrenaline', 'levitate', 'launch', 'cascadia'],
        'saucony': ['saucony', 'kinvara', 'guide', 'pacer', 'endorphin', 'swift', 'predator'],
        'mizuno': ['mizuno', 'wave rider', 'wave inspire', 'wave culmination', 'wave prophecy', 'wave momentum', 'wave horizon', 'wave sky'],
        'altra': ['altra', 'escalante', 'torin', 'solstice', 'malone', 'superlor', 'mont blanc','timp', 'lone peak', 'torin', 'olympus', 'experience flow', 'experience form', 'experience wild'],
        'skechers': ['go walk 7', 'go walk joy', 'skechers', 'go walk 6', 'arch fit', 'summits', 'skech lite pro', 'skech-lite', 'glide step']
    }

df['time'] = pd.to_datetime(df['time'], errors='coerce')
aggregation_period = st.selectbox('집계 기준', ['Daily', 'Weekly'])
lower_text = df['text'].str.lower()


result_list = []
for brand, keywords in brand_keywords.items():
    parts = [re.sub(r'\s+', r'\\s*', re.escape(kw.lower())) for kw in keywords]
    pattern = '|'.join(parts)
    df_brand = df[lower_text.str.contains(pattern, regex=True)].copy()
    
    if aggregation_period == 'Daily':
        df_brand['period'] = df_brand['time'].dt.date
    else:
        df_brand['period'] = df_brand['time'].dt.to_period('W').apply(lambda r: r.start_time.date())
    
    freq = (
        df_brand
        .groupby('period')
        .size()
        .reset_index(name='count')
        .rename(columns={'period': 'time'})
    )
    freq['brand'] = brand
    result_list.append(freq)

if result_list:
    brand_ts = pd.concat(result_list, ignore_index=True)
    brand_ts = brand_ts.sort_values(['brand', 'time'])
    
    pivot_df_all = brand_ts.pivot(index='time', columns='brand', values='count').fillna(0)
    # st.write(f"### All Brands {aggregation_period} Counts", pivot_df_all)
    
    total_counts = pivot_df_all.sum(axis=1)
    pivot_portion = pivot_df_all.div(total_counts, axis=0) * 100
    
    selected_brands = st.multiselect(
        'Select brands',
        list(brand_keywords.keys()),
        default=default_brands
    )
    
    if selected_brands:
        pivot_df_sel = pivot_df_all[selected_brands]
        st.markdown("#### 📈 브랜드 등장 빈도 추이")
        st.line_chart(pivot_df_sel)

        pivot_por_sel = pivot_portion[selected_brands]
        pivot_por_sel = pivot_por_sel.round(2)
        st.markdown("#### 📈 브랜드 등장 비율 추이(%)")
        st.line_chart(pivot_por_sel)
    else:
        st.write("선택된 브랜드가 없습니다.")
else:
    st.write("데이터가 없습니다.")
