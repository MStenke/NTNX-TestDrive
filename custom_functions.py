import pandas as pd
import streamlit as st
from datetime import datetime
import re
from urllib.parse import parse_qs, unquote, urlsplit

######################
# Custom Functions
######################

# Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        #st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        return f.read()

@st.cache(allow_output_mutation=True)
def verify_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # pass the regular expression
    # and the string into the fullmatch() method
    if(re.fullmatch(regex, email)):
        return True 
    else:
        return False

@st.cache(allow_output_mutation=True)
def convert_df(df):
    # format column names to match required csv format
    df_temp = df.rename(columns={'E-Mail Adresse': 'email', 'Vorname': 'first_name', 'Nachname': 'last_name'})
    # remove index and encode
    return df_temp.to_csv(index=False).encode('utf-8')

@st.cache(allow_output_mutation=True)
def url_to_df(urls, decode=True):
    if isinstance(urls, str):
        urls = [urls]
    decode = unquote if decode else lambda x: x
    split_list = []
    for url in urls:
        split = urlsplit(decode(url))
        port = split.port
        hostname = split.hostname if split.hostname != split.netloc else None
        split = split._asdict()
        if hostname:
            split['hostname'] = hostname
        if port:
            split['port'] = port
        parsed_query = parse_qs(split['query'])
        parsed_query = {'query_' + key: '@@'.join(val)
                        for key, val in parsed_query.items()}
        split.update(**parsed_query)
        split_list.append(split)
    df = pd.DataFrame(split_list)

    query_df = df.filter(regex='query_')
    if not query_df.empty:
        sorted_q_params = (query_df
                           .notna()
                           .mean()
                           .sort_values(ascending=False).index)
        query_df = query_df[sorted_q_params]
        df = df.drop(query_df.columns, axis=1)
    df = pd.concat([df, query_df], axis=1)
    df.insert(0, 'link', [decode(url) for url in urls])
    return df

@st.cache(allow_output_mutation=True)
def get_td_type_by_selection(selection):
    if selection == 1: # Kein fest vordefiniertes (frei wählbar von dem Interessenten)
        return ''
    elif selection == 2: # Nutanix Basis Test Drive (NCI, Prism, Calm)
        return '&target=td2'
    elif selection == 3: # Unified Storage Test Drive
        return '&target=tddata'
    elif selection == 4: # Xi Leap Test Drive
        return '&target=tdleap'
    elif selection == 5: # Era Test Drive
        return '&target=era'
    elif selection == 6: # Flow Test Drive
        return '&target=flow'
    elif selection == 7: # Clusters on AWS Test Drive
        return '&target=clusters'
    elif selection == 8: # Clusters on Azure Test Drive
        return '&target=clusters-azure'
    elif selection == 9: # Nutanix Mine with HYCU Test Drive
        return '&target=minehycu'
    elif selection == 10: # AOS Deep Dive
        return '&target=nx101'
    elif selection == 11: # Files Deep Dive
        return '&target=files'
    elif selection == 12: # Calm Deep Dive
        return '&target=calm'
    elif selection == 13: # One-Click Kubernetes Deep Dive
        return '&target=karbon'
    elif selection == 14: # Xi Leap Deep Dive
        return '&target=xileap'
