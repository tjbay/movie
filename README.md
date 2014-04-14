Movie Box Office Estimates - T.J. Bay

This project uses movie data collected from several sources to predict box office performance 
of large Hollywood movies.

Information sources:

1.  This website features budget data, box office and release date data on about 4000 movies.  
This data set is my starting point.  I used only movies from 1980 or later and only those with 
a domestic gross of over 1 million.  This data is in the file /Data/Raw/box_office.txt

http://www.the-numbers.com/movie/budgets/all

2.  For the remaining movies I used the Rotten Tomatoes API to get additional data: RT critics score, 
RT user score, MPAA rating, runtime and cast list.  The API description says it provides director, 
but it does not.  It also provides the IMDB id.

http://www.rottentomatoes.com/

3.  IMDB does not have an API.  Instead, its data is available in dozens of text files.  I found another
source that claims to have collated most of the same information - The Open Movie Database API.  
It is searchable using the IMDB id and provides additional data on the director, language, metascore,
IMDB score, total IMDB votes, genre.

http://www.omdbapi.com/

The code for collecting the data from these 3 sources is in /Code/boxoffice.py and the output is saved 
in the file /Data/Reduced/numbers_RT_omdb.csv. 


Cleaning the data and building features:

In the file data_munge.py I prepare the data for linear regression and create a few new features.  Linear 
regression requires numerical data that isn't categorical or ordinal.  

Features built:  
1. Using the release date to determine if it was released on a holdiay weekend.
2. Cast star power - must be computed using only the training set to not pollute testing
3. Director star power - must be computed using only the training set to not pollute testing


Testing the data:
I'm left with exactly 2500 movies.  I used a K-fold cross validation and RMSE to asses the accuracy of the
linear regression.





