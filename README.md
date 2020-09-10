# datascience_helpers
A bunch of functions I use in data science


missing_data_finder looks for 'bad' data in Pandas Dataframe, such as 
- Numbers formatted like '10%' (not read as object)
- Unknown data like '?'
- np.nan
- bunch of other stuff that I will keep adding as I find.


markdown_table_generator
- makes a markdown table for each column describing dtype, mean, std dev
- It's not really that complicated, it just prints everything nicely.