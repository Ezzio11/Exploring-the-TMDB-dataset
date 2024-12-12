#Importing necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

#Importing and exploring data
tmdb = pd.read_csv('Downloads/tmdb-movies.csv')
#tmdb.head()
#tmdb.describe()
#tmdb.isna().sum()

#Data Preprocessing
#columns to drop (not needed in the analysis): [homepage, tagline, overview, imdb_id, revenue, budget, id]
tmdb_clean = tmdb.drop(['homepage','tagline', 'overview', 'imdb_id', 'id','revenue', 'budget'], axis=1)

#Checking the percentage of budget and revenue that = 0
missing_tmdb_clean_percentages = []

for i in tmdb_clean[['budget_adj', 'revenue_adj', 'runtime']]:
    missing_tmdb_clean = tmdb_clean[tmdb_clean[i] == 0].shape[0]/tmdb_clean.shape[0]*100
    missing_tmdb_clean_percentages.append(missing_tmdb_clean)
    #print("Percentage of missing monetary tmdb_clean is: " + str(missing_tmdb_clean_percentages))

#More than half of our budegt and revenue data is missing! we can't omit more than 5% of missing data, otherwise the statistics become biased.
#Replacing zeroes with NaN, since dropping them would alter the results too much.
for col in tmdb_clean[['budget_adj', 'revenue_adj']]:
    tmdb_clean[col] = tmdb_clean[col].replace(0, np.NaN)
    
#However, the percentage of zeroes in the runtime, cast, genres and director columns are insignficant (<5%), so it's safe to drop the missing values.
na_drop = ['cast', 'genres', 'director']
tmdb_clean = tmdb_clean.dropna(subset = na_drop, how = 'any')
tmdb_clean = tmdb_clean[tmdb_clean['runtime'] != 0]

#Creating an adjusted profit column
tmdb_clean['profit_adj'] = tmdb_clean['revenue_adj'] - tmdb_clean['budget_adj']

#Extracting the main production company from production_companies
tmdb_clean['production_company'] = tmdb_clean['production_companies'].str.split('|').str[0]
tmdb_clean = tmdb_clean.drop('production_companies', axis=1)

#Creating a decade column
tmdb_clean['decade'] = (tmdb_clean['release_year'] // 10) * 10

#Splitting the genres column
movies_genres = tmdb_clean['genres'].str.split('|', expand=True)
genres_combined = movies_genres.stack().droplevel(1).rename('genres')
tmdb_clean.drop(['genres'], axis=1, inplace=True)
tmdb_clean = pd.merge(tmdb_clean, genres_combined, left_index=True, right_index=True)

#Dropping duplicates
tmdb_clean=tmdb_clean.drop_duplicates()

#Data Analysis and Visualization
#What are the most profitable movies from 1960 to 2015?
successful_movies = tmdb_clean.groupby('original_title')['profit_adj'].max().sort_values(ascending=False).head(10)
print('The most proftiable movies are: ' + str(successful_movies))
ax = sns.barplot(successful_movies, orient='h', palette='YlGn_r')
ax.set(xlabel = "Profit (adjusted to 2010 inflation rates)", ylabel = "Movie Title")
ax.set_title('The most financially succsseful movies (in billion USD)(1960-2015)')
plt.show()

#Box office failures
failed_movies = tmdb_clean.groupby('original_title')['profit_adj'].max().sort_values(ascending=True).head(10)
print('The most proftiable movies are: ' + str(failed_movies))
ax = sns.barplot(failed_movies, orient='h', palette='YlOrRd_r')
ax.set(xlabel = 'Loss (adjusted to 2010 inflation rates)', ylabel = 'Movie title')
ax.set_title('Box office failures (in million USD)(1960-2015)')
plt.show()

#What are the most popular movies from 1960 to 2015?
popular_movies = tmdb_clean.groupby('original_title')['popularity'].max().sort_values(ascending=False).head(10)
print('The most popular movies are: ' + str(popular_movies))
ax = sns.barplot(popular_movies, orient='h', palette='rainbow_r')
ax.set(xlabel = "Popularity rate", ylabel = "Movie title")
ax.set_title('The Most popular movies (1960-2015)')
plt.show()

#Did movies (on average) get longer or shorter overtime?
ax = sns.lineplot(data=tmdb_clean, x='release_year', y='runtime', errorbar=None, color='b')
ax.set(xlabel = "Release year", ylabel = "Runtime (minutes)")
ax.set_title('Average movie runtime (in minutes) (1960-2015)')
plt.show()

#Does spending (on average) more result in gaining more?
bud_v_rev = tmdb_clean.groupby('decade').agg({'budget_adj':'mean',
                                      'revenue_adj':'mean'})

ax = sns.scatterplot(bud_v_rev, s=200, palette='viridis_r')
ax.set(xlabel = "Decade", ylabel = "Average Value")
handles, labels  =  ax.get_legend_handles_labels()
ax.legend(handles, ['Budget', 'Revenue'])
ax.set_title('Relationship between Budget and Revenue (1960-2015)')
plt.savefig('filename.pdf')
plt.show()

#Which movie genres made the most profit?
genre_profit = tmdb_clean.groupby('genres')['profit_adj'].max().sort_values(ascending=False).head(5)
print('The genres that made the most profit are: ' + str(genre_profit))
labels = ['Action', 'Sci-Fi', 'Adventure', 'Fantasy', 'Drama']
def make_autopct(genre_profit):
    def my_autopct(pct):
        total = sum(genre_profit)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
    return my_autopct
plt.pie(genre_profit, labels=labels, autopct=make_autopct(genre_profit), shadow=True, colors=sns.color_palette('Set2'))
plt.title('Top 5 movie genres (1960-2015)')
plt.show()