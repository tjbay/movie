import pandas as pd
import time
import os
import csv
from rottentomatoes import RT
import string
import urllib2
import urllib
import json

''' 
Box office data from http://www.the-numbers.com/movie/budgets/all
Cut and pasted into the file box_office_file.txt
A tab-separated file of ~4000 movies with name, release data, budget, domestic gross, worldwide gross.
I'm going to build my dataset out of movies with domestic gross > $1 million.  That will
let me keep only movies that I can be reasonably sure have sufficient data.
'''

def getRTdata(title, year, KEY):

 	time.sleep(0.25)
	all_movies = RT(KEY).search(title)
	N = len(all_movies)
	mdata = []

	for i in range(N):
		RT_year = all_movies[i]['year']

		same_year = abs(int(year)-RT_year) <= 1

		if same_year:
			mdata = all_movies[i]
			break

	RT_title = mdata['title']
	RT_aud_score = mdata['ratings']['audience_score']
	RT_crit_score = mdata['ratings']['critics_score']
	RT_mpaa_rating = mdata['mpaa_rating']
	RT_runtime = mdata['runtime']

	cast1 = mdata['abridged_cast'][0]['name']
	cast2 = mdata['abridged_cast'][1]['name']
	cast3 = mdata['abridged_cast'][2]['name']

	imdb_id = 'tt' + mdata['alternate_ids']['imdb']

	return [RT_title, RT_aud_score, RT_crit_score, RT_mpaa_rating, RT_runtime, cast1, cast2, cast3, imdb_id]

def getOMDBdata(imdb_id):

	url = "http://www.omdbapi.com/?i=" + imdb_id
	omdb_data = json.loads(urllib2.urlopen(url).read())

	metascore = omdb_data['Metascore']
	lang = omdb_data['Language']
	director = omdb_data['Director']
	genres = omdb_data['Genre']
	imdbRating = omdb_data['imdbRating']
	imdbVotes = omdb_data['imdbVotes']

	return [metascore, lang, director, genres, imdbRating, imdbVotes]


infile_name = "../Data/Raw/box_office.txt"
outfile_name = "../Data/Reduced/numbers_RT_omdb.csv"
KEY = open('RT_KEY').read()

# Read and parse the data

print "Reading data file from the-numbers.com"

numbers = pd.io.parsers.read_csv(infile_name, sep = '\t')

numbers['budget'] = 0
numbers['dom_gross'] = 0
numbers['year'] = 0
numbers['month'] = 0
numbers['day'] = 0
#numbers['language'] = None

for i in numbers.index:
	date = numbers['Release Date'].ix[i]
	[month, day, year] = date.split('/')
	numbers['year'].ix[i] = int(year)
	numbers['month'].ix[i] = int(month)
	numbers['day'].ix[i] = int(day)

	numbers['budget'].ix[i] = int(numbers['Production Budget'].ix[i].replace('$','').replace(',',''))
	numbers['dom_gross'].ix[i] = int(numbers['Domestic Gross'].ix[i].replace('$','').replace(',',''))

del numbers['Worldwide Gross']
del numbers['Production Budget']
del numbers['Domestic Gross']
del numbers['Index']
del numbers['Release Date']

numbers = numbers[numbers['dom_gross'] >= 1000000]
numbers = numbers[numbers['year'] >= 1980]

numbers = numbers.reset_index()

# Now to get more data from Rotten Tomatoes API
# I'm only using the top hit from RT.  I'll check the release year to
# help make sure I'm getting the right movie.
# Info to keep: critics rating, audience rating, MPAA rating, runtime

# I'm using a wrapper to the RT API that simplifies things, found at:
# https://github.com/zachwill/rottentomatoes/tree/master/rottentomatoes

numbers['RT_title'] = ''
numbers['RT_aud_score'] = 0.0
numbers['RT_crit_score'] = 0.0
numbers['RT_mpaa_rating'] = ''
numbers['RT_runtime'] = 0.0
numbers['RT_cast1'] = ''
numbers['RT_cast2'] = ''
numbers['RT_cast3'] = ''
numbers['imdb_id'] = ''

numbers['Metascore'] = 0.0
numbers['Language'] = ''
numbers['Director'] = ''
numbers['Genre'] = ''
numbers['imdbRating'] = 0.0
numbers['imdbVotes'] = 0.0


print "Collecting data from Rotten Tomatoes and OMDB\n"
fails_index = []

#for i in numbers.index:
for i in numbers.index:
	title = numbers['Movie'].ix[i]
	year = numbers['year'].ix[i]

	#if i > 10: break

	print i, title

	try:
		[RT_title, RT_aud_score, RT_crit_score, RT_mpaa_rating, RT_runtime, cast1, cast2, cast3, imdb_id] = getRTdata(title, year, KEY)

		numbers['RT_title'].ix[i] = RT_title
		numbers['RT_aud_score'].ix[i] = RT_aud_score
		numbers['RT_crit_score'].ix[i] = RT_crit_score
		numbers['RT_mpaa_rating'].ix[i] = RT_mpaa_rating
		numbers['RT_runtime'].ix[i] = RT_runtime
		numbers['RT_cast1'].ix[i] = cast1
		numbers['RT_cast2'].ix[i] = cast2
		numbers['RT_cast3'].ix[i] = cast3
		numbers['imdb_id'].ix[i] = imdb_id

		print "Movie updated with RT data: Success"

		try:
			[metascore, lang, director, genres, imdbRating, imdbVotes] = getOMDBdata(imdb_id)

			numbers['Metascore'].ix[i] = metascore
			numbers['Language'].ix[i] = lang
			numbers['Director'].ix[i] = director
			numbers['Genre'].ix[i] = genres
			numbers['imdbRating'].ix[i] = float(imdbRating)
			numbers['imdbVotes'].ix[i] = float(imdbVotes.replace(",",""))

			print "Movie updated with OMDB data: Success\n"

		except:
			print "Movie updated with OMDB data: Failure\n"
			fails_index.append(i)

	except:
		print "Movie updated with RT data: Failure"
		fails_index.append(i)


all_index = numbers.index
suc_index = list(set(all_index)-set(fails_index))

output_df = numbers.ix[suc_index]

output_df.to_csv(outfile_name, header = True, index = False)




