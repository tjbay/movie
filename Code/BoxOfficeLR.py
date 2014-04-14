from math import sqrt
import numpy as np
import pandas as pd
import operator
import matplotlib.pyplot as plt
#import prettyplotlib as ppl
from sklearn.metrics import mean_squared_error
from sklearn.cross_validation import train_test_split
from sklearn.utils import shuffle
from sklearn.linear_model import LinearRegression


# ------------------------------------------------------------------------------------

def CalculateStarDict(df2):

	castdict = {}
	stardict = {}

	for i in df2.index:
		cast = [df2['RT_cast1'].ix[i], df2['RT_cast2'].ix[i], df2['RT_cast3'].ix[i]]
		hit = df2['dom_gross'].ix[i] > 200000000
		if hit:
			for actor in cast:
				if actor in castdict:
					castdict[actor] += 1
				else: 
					castdict[actor] = 1

	for actor, starpower in castdict.iteritems():
		if starpower > 1:
			stardict[actor] = starpower 

	return stardict

def AddStarpowerCol(df2, stardict):

	df2['starpower'] = 0

	for i in df2.index:
		totalstarpower = 0
		castList = [df2['RT_cast1'].ix[i], df2['RT_cast2'].ix[i], df2['RT_cast3'].ix[i]]
		for actor in castList:
			try: 
				totalstarpower += stardict[actor]
			except:
				totalstarpower += 0

		df2['starpower'].ix[i] = totalstarpower
		
	return

def CalculateDirDict(df2):

	dirdict = {}
	dirstars = {}

	for i in df2.index:
		director_name = df2['Director'].ix[i]
		hit = df2['dom_gross'].ix[i] > 200000000
		if hit:
			if director_name in dirdict:
				dirdict[director_name] += 1
			else:
				dirdict[director_name] = 1
			
	for director_name, starpower in dirdict.iteritems():
		if starpower > 1:
			dirstars[director_name] = starpower 

	return dirstars

def AddDirCol(df2, dirstars):
	df2['dirpower'] = 0

	for i in df2.index:
		totaldirpower = 0
		name =  df2['Director'].ix[i]
		
		try: 
			totaldirpower = dirstars[name]
		except:
			totaldirpower = 0

		df2['dirpower'].ix[i] = totaldirpower

	return

def AddGenreFeatures():
	genreDict = {}

	for item in movies['Genre'].values:
		genres = item.split(',')
		for g in genres:
			g = g.strip()
			if g in genreDict:
				genreDict[g] += 1
			else:
				genreDict[g] = 1

	sortedGenres = sorted(genreDict.items(), key=operator.itemgetter(1), reverse=True)

	for i in range(len(sortedGenres)):
		g = sortedGenres[i][0]
		movies[g] = 0

	for i in movies.index:
		genres = movies['Genre'].ix[i].split(',')
		for g in genres:
			g = g.strip()
			movies[g].ix[i] = 1

	return

def KFoldCrossVal(df, featureNames, Yname, KFolds = 5):

	sum_rmse = 0
	rmse = 0
	N = len(df)
	shuff_index = movies.index.values
	np.random.shuffle(shuff_index)

	num_per_fold = N / KFolds

	for i in range(KFolds):
		test_index = shuff_index[i*num_per_fold:(i+1)*num_per_fold]

		if i == (KFolds - 1): 
			test_index = shuff_index[i*num_per_fold:]

		train_index = list(set(shuff_index) - set(test_index))

		Test = df.ix[test_index]
		Train = df.ix[train_index]

		train_stardict = CalculateStarDict(Train)
		train_dirstars = CalculateDirDict(Train)

		AddStarpowerCol(Train, train_stardict)
		AddStarpowerCol(Test, train_stardict)
		AddDirCol(Train, train_dirstars)
		AddDirCol(Test, train_dirstars)

		# Xtrain = Train[featureNames]
		# Ytrain = Train[Yname]
		# Xtest = Test[featureNames]
		# Ytest = Test[Yname]

		Xtrain = Train[featureNames].values
		Ytrain = Train[Yname].values
		Xtest = Test[featureNames].values
		Ytest = Test[Yname].values


		sum_rmse += computeLRACCuracy(Xtrain, Ytrain, Xtest, Ytest)

	rmse = 1.0*sum_rmse/KFolds
	return rmse

def computeLRACCuracy(Xtrain, Ytrain, Xtest, Ytest):

	acc = 0
	clf = LinearRegression(normalize=True)

	clf.fit(Xtrain, Ytrain)
 	Ypred = clf.predict(Xtest)

 	rmse = sqrt(mean_squared_error(Ytest, Ypred))

 	return rmse

# ------------------------------------------------------------------------------------

infile_name = "../Data/Reduced/numbers_RT_omdb_cleaned.csv"
movies = pd.io.parsers.read_csv(infile_name)

# ------------------------------------------------------------------------------------

AddGenreFeatures()
 
# Extract features from dataframes:
# movies.columns.values

featureNames = ['budget', 'year', 'month', 'RT_aud_score', 'RT_crit_score',
		'RT_runtime', 'Metascore', 'imdbRating', 'imdbVotes', 'mpaa_kid',
       'mpaa_adult', 'Holiday', 'DayOfWeek', 'starpower', 'dirpower',
       'Drama', 'Comedy', 'Action', 'Adventure', 'Crime', 'Thriller',
       'Romance', 'Fantasy', 'Sci-Fi', 'Mystery', 'Horror', 'Family',
       'Biography', 'Animation', 'Music', 'History', 'Sport', 'War',
       'Documentary', 'Musical', 'Western']

# featureNames = ['budget', 'year', 'month','RT_aud_score', 'RT_crit_score', 'RT_runtime', 'Metascore',
#    		'imdbRating', 'imdbVotes']

Yname = ['dom_gross']

KFolds_vals = [5]

print 'Using features:', featureNames
print ''

for KFolds in KFolds_vals:
	avg_error = KFoldCrossVal(movies, featureNames, Yname, KFolds)/1e6
	print 'With {0} Folds, the average error is {1:.4} Million dollars'.format(KFolds, avg_error)
