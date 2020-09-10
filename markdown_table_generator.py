# put a df in and it prints out something
# that you can use as a markdown table (just copy and paste)

import pandas as pd
import numpy as np

def markdown_table_generator(df, default_text = "DESCRIPTION_HERE", sig_figs = 3):
    
    #print out the headers
    print("|Column Name|dtype|Mean|Std Dev|Description|")
    print( ("|---")*5 + "|")
    
    for colname in df.columns:
        
        col_dtype = df[colname].dtype
        
        # if numeric get the mean and std dev to specified sig figs
        if pd.api.types.is_numeric_dtype(df[colname]):
            col_mean = np.mean(df[colname]) 
            col_mean = np.format_float_positional(col_mean, precision=sig_figs, fractional=False)
            
            col_std_dev = np.std(df[colname])
            col_std_dev = np.format_float_positional(col_std_dev, precision=sig_figs, fractional=False)
        
        else:
            col_mean = "-"
            col_std_dev = "-"
        
        #print out a column
        print("|{}|{}|{}|{}|{}|".format(
            colname,
            col_dtype,
            col_mean,
            col_std_dev,
            default_text))
