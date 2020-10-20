%reset -f
import pandas as pd
import numpy as np

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)



# import the CSV file using pandas
df= pd.read_csv('crsp_monthly_all.csv')

# look at size, data types, and first five rows of the dataframe
df.shape
df.dtypes
df.head()

# Make all variable/column names lower case
df.columns= df.columns.str.lower()

df.head()
df['date'].max()
df['date'].min()

# Panel data of monthly returns from 2/26/1954 to 10/31/2018.


# Let's restrict the analysis from 2010- 2017. First, deal with the date variable which is currently an object type.
# Convert to datetime
df['date']= pd.to_datetime(df['date'], format='%d%b%Y')


# Create a new dataframe that contains observations within the relevant date
# ranges.
df2=df[(df['date'] >= '01JAN2010') & (df['date'] <='31DEC2017')].copy()
df2.shape
df2['date'].describe()

df2['prc'].describe()

# Can see above that some prices are negative. Which, per this link
# https://faq.library.princeton.edu/econ/faq/11159,  is for prices calculated
# from the bid/ask average. This is done when closing price is not
# available.

df2[(df2['prc'] < 0)].count()
(df2['prc'] < 0).sum()
df2['bool']= (df2['prc'] < 0)
df2['bool'].sum()

df2[['prc', 'bool']][(df2['prc'] < 0)]

len(df2[['prc', 'bool']][(df2['prc'] < 0)])

# Replace negative prices to null value_counts
df2.loc[df2['prc'] < 0, 'prc']= np.nan
# Double check summary stats after the change.
df2['prc'].describe()

# Create a year variable for groupby
df2['year']= df2['date'].dt.year
# create a month variable to calc Dec- Jan prices later.
df2['month']= df2['date'].dt.month

# Keep only Dec. and Jan. obs, and make sure that each permno and year
# has both of these.
df3= df2[(df2['month']==12) | (df2['month']==1)].copy()

df3.dtypes

# CME had a stock split in 2012, so look at their price series. The prc variable
# must be adjusted for the split to make it comparable. The adjustment factor
# variables are cfacpr and cfacshr, both of which are equal to 5 for CME.
# Instead of using just prc later in the analysis, we will use prc/cfacpr.
df3.loc[df3['ticker']=='CME', :]

df_temp= df3.groupby(['permno', 'year'])['prc'].count().reset_index().copy()
df_temp

df_temp.rename(columns={'prc': 'count'}, inplace=True)

df_temp.head()
df_temp['count'].value_counts()

df4= pd.merge(df3, df_temp, on=['permno', 'year'], how='left')
df4.head()

df4['count'].value_counts()


df4[df4['count']==5].head(5)
# Above, ACP for 2013 has mostly the same values for variables for the Dec. obs.
# with the exception of variables related to dividends. For example, dclrdt,
# paydt, rcrdt, distcd, and divamt all vary to some degree.
df4[df4['count']==3].head(3)
# A similar pattern is observed for TROW for 2012 Dec. obs.

df4.head()

# Identify obs where there is no January using min. Need to remove this or
# Python will throw the error relating to an index being out of bounds
# for the series I generate in the user-defined function.
df4.groupby(['permno', 'year'])['month'].min().value_counts()

len(df4)
# Identify firms where the minimun is 12. These are firms with Dec. obs but no Jan. obs.
df4['bool1']= df4.groupby(['permno', 'year'])['month'].transform(lambda x: x.min()==12)
df4['bool1'].value_counts()
df4.drop(df4[df4['bool1'] == 1].index, inplace= True)

# identify firms where the maximum is 1. These are firms with Jan. obs but not Dec. obs.
df4['bool1']= df4.groupby(['permno', 'year'])['month'].transform(lambda x: x.max()==1)
df4['bool1'].value_counts()

len(df4)
df4.drop(df4[df4['bool1'] == 1].index, inplace= True)
len(df4)

# Create a price variable that has been adjusted for stock splits.
df4['adjusted_prc']= df4['prc']/ df4['cfacpr']
df4[['prc', 'adjusted_prc']].describe()

# The summary stats shown are thrown off because it appears that there
# are zeroes values for cfacpr which have resulted in dividing by zero.

df4['cfacpr'].isnull().sum()
df4['cfacpr'].describe()

# Count number of obs where cfacpr is 0.
(df4['cfacpr']==0).sum()
# Replace zero values of cfacrp with null values.
df4.loc[df4['cfacpr']==0, 'cfacpr'] = np.nan
df4['cfacpr'].isnull().sum()
381+ 479
df4['cfacpr'].describe()

# A split of .000001 also appears strange, but these are for reverse stock splits. See DCIX example below.
(df4['cfacpr']<1).sum()

df.loc[df['ticker'] =='DCIX', ['permno', 'shrcd', 'date', 'ticker', 'prc', 'cfacpr']]

# Below write up about DCIX is from: https://www.splithistory.com/dcix/ which is saved as DCIX_Split_History.pdf.

# Performance Shipping (DCIX) has 6 splits in our DCIX split history database. The first split for DCIX took place on June 09, 2016. This was a 1 for 8 reverse split, meaning for each 8 shares of DCIX owned pre-split, the shareholder now owned 1 share. For example, a 1000 share position pre-split, became a 125 share position following the split. DCIX's second split took place on July 05, 2017. This was a 1 for 7 reverse split, meaning for each 7 shares of DCIX owned pre-split, the shareholder now owned 1 share. For example, a 125 share position pre-split, became a 17.8571428571429 share position following the split. DCIX's third split took place on July 27, 2017. This was a 1 for 6 reverse split, meaning for each 6 shares of DCIX owned pre-split, the shareholder now owned 1 share. For example, a 17.8571428571429 share position pre-split, became a 2.97619047619048 share position following the split. DCIX's 4th split took place on September 25, 2017. This was a 1 for 3 reverse split, meaning for each 3 shares of DCIX owned pre-split, the shareholder now owned 1 share. For example, a 2.97619047619048 share position pre-split, became a 0.992063492063492 share position following the split. DCIX's 5th split took place on November 02, 2017. This was a 1 for 7 reverse split, meaning for each 7 shares of DCIX owned pre-split, the shareholder now owned 1 share. For example, a 0.992063492063492 share position pre-split, became a 0.14172335600907 share position following the split. DCIX's 6th split took place on August 24, 2017. This was a 1 for 7 reverse split, meaning for each 7 shares of DCIX owned pre-split, the shareholder now owned 1 share. For example, a 0.14172335600907 share position pre-split, became a 0.0202461937155815 share position following the split.
# When a company such as Performance Shipping conducts a reverse share split, it is usually because shares have fallen to a lower per-share pricepoint than the company would like. This can be important because, for example, certain types of mutual funds might have a limit governing which stocks they may buy, based upon per-share price. The $5 and $10 pricepoints tend to be important in this regard. Stock exchanges also tend to look at per-share price, setting a lower limit for listing eligibility. So when a company does a reverse split, it is looking mathematically at the market capitalization before and after the reverse split takes place, and concluding that if the market capitilization remains stable, the reduced share count should result in a higher price per share.

# The above site says that the starting purchase price of DCIX shares are $753,228. My quotient shows a starting price of $625,000 and this could easily be because my CRSP data only goes to 2018 and I Googled this on 1/18/2020. The website also shows that this starting value would be equal to $.02 today and the total return is -100%.

# My conclusion is that I still need to divide price, prc, by the adjustment factor, cfacpr, to calculate the adjusted price. I briefly thought that perhaps I should multiply these two together for companies that did reverse stock splits, but this is not accurate. The quotient shows the stock price decreasing monotonically through time which is what is actually happening. The product shows price increasing over time, which is not economically what is happening. However, a share price of $625,000 will also throw off the summary stats, so I think later in this file I am going to exclude firms cfacpr <1 from the summary stats.

len(df4)

(df4['cfacpr']<1).sum() / len(df4)
# Only 6.6% of obs have fractional cfacpr values.

# Look at examples of these firms.
df4.loc[df4['cfacpr'] <1, ['permno', 'shrcd', 'date', 'ticker', 'prc', 'cfacpr', 'adjusted_prc']].head(200)

df4['adjusted_prc']= df4['prc']/ df4['cfacpr']

# I am going to exclude firms that did reverse stock splits from the analysis.
# Overwrite adjusted_prc to null for firms that have reverse stock splits.
df4.loc[df4['cfacpr'] < 1, 'adjusted_prc']= np.nan
df4[['prc', 'adjusted_prc']].describe()

# Share prices of $297,600 appear large. See if, besides Berkshire Hathaway Class A who has adjusted prices > $100,000.
df4.loc[df4['adjusted_prc'] > 100000, ['permno', 'shrcd', 'date', 'ticker', 'prc', 'cfacpr', 'adjusted_prc']]
# Only Berkshire. Appears reasonable. p/f/r.

df4['shrcd'].value_counts()
# Academic research typically uses only shrcd= 10 or 11, but I see no reason to eliminate ADR's, with leading "3", or firms like KKR and TLP which have leading "7"'s for limited partnership units. Per above, there are also no instances of shrcd==10 in the dataset.
df4.loc[df4['shrcd'] ==71, ['permno', 'shrcd', 'date', 'ticker', 'prc', 'cfacpr', 'adjusted_prc']].head(200)
df4.loc[df4['ticker'] =='TLP', ['permno', 'shrcd', 'date', 'ticker', 'prc', 'cfacpr', 'adjusted_prc']].head(200)

# Function which takes the difference of the December and January prices. This will be fed into a groupby operation which performs this calculation for each permno and year.
# Note that her I am purposely not using the time series operators because I wanted to see if I could do this without them.
def new_calc(dataframe):
    end= dataframe['adjusted_prc'][(dataframe['month']==12)]
    begin= dataframe['adjusted_prc'][(dataframe['month']==1)]
    diff= end.iloc[0]- begin.iloc[0]
    return diff


df5= df4.groupby(['permno', 'year']).apply(new_calc)

df5.head()

df5= pd.DataFrame(df5, columns=['price_diff'])
df5.head()

df6= pd.merge(df4, df5, on=['permno', 'year'], how='left')

df6[['permno', 'date', 'ticker', 'prc', 'adjusted_prc', 'price_diff']].head(50)
# Manually checked the first 50 observations for accuracy. No exceptions noted.

len(df6)

# Identify January obs to then delete them. This results in a DataFrame
# with only one observation per permno-year, and this will be the December
# obs.
df6['bool1']= df6['month']==1
df6['bool1'].value_counts()

df6[['permno', 'date', 'bool1', 'ticker', 'prc', 'price_diff']].head(50)

df6.drop(df6[df6['bool1'] == 1].index, inplace= True)
len(df6)
df6['month'].value_counts()

df6['price_diff'].describe()

# A monthly drop of $18,065 look strange. Look into this below.

df6.loc[df6['price_diff']<= -10000, ['permno', 'date', 'ticker', 'prc', 'adjusted_prc', 'price_diff']].head()
# A drop of that size for BRK appears reasonable. p/f/r.
df6['price_diff'].isnull().sum()
df6['price_diff'].isnull().sum() / len(df6)
# Around 6% of of the obs have null price_diff's. This lines up with the 6.7% noted earlier for reverse stock splits. p/f/r.
len(df6)

# Drop obs with missing price_diff's.
df6.dropna(subset= ['price_diff'], inplace=True)

len(df6)

56367-3268

df6['gain']= df6['price_diff'] > 0
df6['loss']= df6['price_diff'] < 0
df6['flat']= df6['price_diff'] ==0

# Look at percentages of stocks that were up for the year for each year.
df6.groupby('year')['gain'].mean()
df6.groupby('year')['gain'].mean().mean()


# Look at percentages of stocks that were down for the year for each year.

df6.groupby('year')['loss'].mean()

# Look at percentages of stocks that were flat for the year for each year.
df6.groupby('year')['flat'].mean()

# The sum of the above groups is approximately 100% for each year. p/f/r.

# Look at one year of data to see if anything strange pops out per eyeball inspection. No exceptions noted. p/f/r.
df6.loc[df6['year']==2011, ['permno', 'date', 'ticker', 'prc', 'adjusted_prc', 'price_diff', 'gain', 'loss', 'flat']]
