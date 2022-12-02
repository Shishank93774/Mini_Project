import json
import streamlit as st
import requests
import ast
import pickle as pkl

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from nltk.stem.snowball import SnowballStemmer
import warnings; warnings.simplefilter('ignore')

def fetch_poster(movie_id):
    response = requests.get("https://api.themoviedb.org/3/movie/{}?api_key=0ed778e3b6b725cd4eeeccf42e6de65e&language=en-US".format(movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

def get_posters(df, start = 0, length = 5):
    posters = []
    for i in range(start, start + length):
        movie_id = df.iloc[i]['id']
        # print(movie_id)
        posters.append(fetch_poster(movie_id = movie_id))
    return posters

def weigthed_rating(obj):
    v = obj['vote_count']
    R = obj['vote_average']
    return (v/(v+m)*R) + (m/(v+m)*C)

def build_chart(genre, length = 5, percentile=0.85):
    df = gen_md[gen_md['genre'] == genre]
    vote_counts = df[df['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = df[df['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()
    m = vote_counts.quantile(percentile)

    qfd = df[(df['vote_count'] >= m) & (df['vote_count'].notnull()) & (df['vote_average'].notnull())][
        ['id', 'title', 'year', 'vote_count', 'vote_average', 'popularity']]
    qfd['vote_count'] = qfd['vote_count'].astype('int')
    qfd['vote_average'] = qfd['vote_average'].astype('int')

    qfd['wr'] = qfd.apply(
        lambda x: (x['vote_count'] / (x['vote_count'] + m) * x['vote_average']) + (m / (m + x['vote_count']) * C),
        axis=1)
    qfd = qfd.sort_values('wr', ascending=False).head(10)

    return qfd

def improved_recommendations(title, length = 5):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:26]
    movie_indices = [i[0] for i in sim_scores]

    movies = smd.iloc[movie_indices][['id', 'title', 'vote_count', 'vote_average', 'year']]
    vote_counts = movies[movies['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = movies[movies['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()
    m = vote_counts.quantile(0.60)
    qfd = movies[
        (movies['vote_count'] >= m) & (movies['vote_count'].notnull()) & (movies['vote_average'].notnull())]
    qfd['vote_count'] = qfd['vote_count'].astype('int')
    qfd['vote_average'] = qfd['vote_average'].astype('int')
    qfd['wr'] = qfd.apply(
        lambda x: (x['vote_count'] / (x['vote_count'] + m) * x['vote_average']) + (m / (m + x['vote_count']) * C),
        axis=1)
    qfd = qfd.sort_values('wr', ascending=False).head(length)
    return qfd.drop(columns=['vote_count', 'vote_average'])


md = pkl.load(open("allMovies.pkl", 'rb'))
qualified = pkl.load(open("topMovies.pkl", 'rb'))
smd = pkl.load(open("allModifiedMovies.pkl", 'rb'))

vote_counts = md[md['vote_count'].notnull()]['vote_count'].astype('int')
vote_average = md[md['vote_average'].notnull()]['vote_average'].astype('int')
C = round(vote_average.mean())
m = vote_counts.quantile(0.85)

s = md.apply(lambda x: pd.Series(x['genres']),axis=1).stack().reset_index(level=1, drop=True)
s.name = 'genre'
gen_md = md.drop('genres', axis=1).join(s)

count = CountVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
count_matrix = count.fit_transform(smd['soup'])

cosine_sim = cosine_similarity(count_matrix, count_matrix)

smd = smd.reset_index()
titles = smd['title']
indices = pd.Series(smd.index, index=smd['title'])

st.title('Movie Recommender System')

# https://api.themoviedb.org/3/movie/{movie_id}?api_key=<<api_key>>&language=en-US
# 0ed778e3b6b725cd4eeeccf42e6de65e
# https://image.tmdb.org/t/p/w500/


st.markdown(
    "### Our Global Top 10 Movies List:"
)
cols = st.columns(5)
for i in range(5):
    posters = get_posters(qualified, 0, 5)
    with cols[i]:
        st.text(qualified.iloc[i]['title'])
        st.image(posters[i])

st.markdown("""---""")

cols = st.columns(5)
for i in range(5):
    posters = get_posters(qualified, 5, 5)
    with cols[i]:
        st.text(qualified.iloc[5+i]['title'])
        st.image(posters[i])

top_genres = ['romance', 'sports', 'based on novel or book', 'horror', 'zombie', 'murder', 'biography', 'superhero', 'heist', 'based on true story', 'psychopath', 'time travel']

selectedGenre = st.selectbox(
    'Select a genre:',
    (top_genres)
)

if st.button('Recommend From Genre'):
    for i in range(len(top_genres)):
        if selectedGenre == top_genres[i]:
            chart = build_chart(top_genres[i], length=10)
            posters = get_posters(chart, length= 10)
            cols = st.columns(5)
            for j in range(5):
                with cols[j]:
                    st.text(chart.iloc[j]['title'])
                    st.image(posters[j])
            st.markdown("""---""")
            cols = st.columns(5)
            for j in range(5):
                with cols[j]:
                    st.text(chart.iloc[j+5]['title'])
                    st.image(posters[j+5])

st.markdown(
    "### Still didn't liked the movies?"
)

selectedMovie = st.selectbox(
    'Enter a Movie Name you recently watched and liked',
    (qualified['title'])
)

if st.button('Recommend based on this movie:'):
    st.write('Try out these:')

    recommendations_frame = improved_recommendations(selectedMovie, length=15)
    sz = min(len(recommendations_frame), 15)
    posters = get_posters(recommendations_frame, start= 0, length=sz)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(recommendations_frame.iloc[i]['title'])
            st.image(posters[i])
    st.write("""---""")
    if sz >= 10:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(recommendations_frame.iloc[i+5]['title'])
                st.image(posters[i+5])
        st.write("""---""")
    if sz >= 15:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(recommendations_frame.iloc[i+10]['title'])
                st.image(posters[i+10])
st.markdown(
    '#### We really hope you like the recommendations. :)'
)