import pandas as pd
from datetime import date, timedelta
from workalendar.america import UnitedStates

def isUSHoldiay(testdate):
	cal = UnitedStates()
	hol_dict = dict(cal.holidays(testdate.year))
	return testdate in hol_dict

def isUSHolidayWeekend(rdate):
	one_day = timedelta(1)
	dateList = [rdate - one_day - one_day, rdate - one_day, rdate, rdate + one_day, rdate + one_day + one_day,]
	HolidayList = [isUSHoldiay(d) for d in dateList]
	return any(HolidayList)


infile_name = "../Data/Reduced/numbers_RT_omdb.csv"
outfile_name = "../Data/Reduced/numbers_RT_omdb_cleaned.csv"

movies = pd.io.parsers.read_csv(infile_name)

del movies['level_0']
del movies['index']

# Some movies have RT critics score < 0

movies = movies[movies['RT_crit_score'] >= 0]

# Remove movies with lengths less than 60 minutes

movies = movies[movies['RT_runtime'] >= 60]

# Due to previous type - need to filter out old movies

movies = movies[movies['year'] >= 1980]

# Need to make MPAA rating into 2 variables: kid movies and adult movies

G = (movies['RT_mpaa_rating'] == 'G')
PG = (movies['RT_mpaa_rating'] == 'PG')
PG13 = (movies['RT_mpaa_rating'] == 'PG-13')
kid = G+PG+PG13

movies['mpaa_kid'] = 1*kid
movies['mpaa_adult'] = (1-kid)
del movies['RT_mpaa_rating']

# Left with 2500 movies

movies.reset_index()

# Calculate Holdiay weekends:

movies['Holiday'] = 0
movies['DayOfWeek'] = None

for i in movies.index:
	year = movies['year'].ix[i]
	month = movies['month'].ix[i]
	day = movies['day'].ix[i]

	rdate = date(year, month, day)

	movies['Holiday'].ix[i] =  isUSHolidayWeekend(rdate)
	movies['DayOfWeek'].ix[i] = date(year, month, day).weekday()

movies.to_csv(outfile_name, header = True, index = False)

