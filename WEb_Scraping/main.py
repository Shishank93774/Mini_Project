#importing required libraries:
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np

#initializing lists to store data:
movie_name = []
year = []
time = []
rating = []
metascore = []
votes = []
genre = []
gross = []
list(gross)
description = []

for index in range(1, 1000, 50):              #for loop to run over pages
    url = 'https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,desc&start=' + str(index) + '&ref_=adv_nxt'

    response = requests.get(url)                                #getting response when requested
    soup = BeautifulSoup(response.content, 'html.parser')       #using utility to parse the response as html content

    movie_data = soup.find_all('div', attrs={'class': 'lister-item mode-advanced'})

    for data in movie_data:
        name = data.h3.a.text
        movie_name.append(name)

        year_of_release = data.h3.find(
            'span', class_='lister-item-year text-muted unbold').text.replace('(', '').replace(')', '')
        year.append(year_of_release)
    
        duration = data.p.find('span', class_='runtime').text.replace('min', '')
        duration = int(duration)
        hr = duration//60
        min = duration % 60
        duration = str(hr) + 'hr ' + str(min) + 'min(s)'
        time.append(duration)
    
        genre_of_movie = data.p.find('span', class_='genre').text.replace('\n', '').replace(" ", "")
        genre.append(genre_of_movie)
    
        rating_of_movie = data.find(
            'div', class_='inline-block ratings-imdb-rating').text.replace('\n', '')
        rating.append(rating_of_movie)
    
        meta = data.find('span', class_='metascore').text.replace(' ', '') if data.find('span', class_='metascore') else '-NA-'
        metascore.append(meta)
    
        value = data.find_all('span', attrs={'name': 'nv'})
        vote = value[0].text
        votes.append(vote)
        profit = value[1].text if(len(value)) > 1 else '*NA*'
        if("#" in profit):
            profit = '*NA*'
        gross.append(profit)


movie_DataFrame = pd.DataFrame({'Name of Movie: ': movie_name, 'Year of Release: ': year, 'Duration ': time, 'Genre ': genre, 'Metascore ': metascore, 'No. of Votes ': votes, 'Gross Production ': gross})
movie_DataFrame.head(15)
movie_DataFrame.size

movie_DataFrame.to_excel("Top1000MoviesOfAllTime.xlsx")
