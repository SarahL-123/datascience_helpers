# A function that checks your dataframe for missing things that you might want to fix!
# To be honest you probably don't want to use the replacing functionality
# it's a bit dangerous because it can change quite a lot.
# By Sarah
import pandas as pd
import numpy as np
import regex as re

def find_bad_data(df, cols = [], replace_with = None, checks=[], help_me = False, print_all = True):
    """Checks for NaNs in the specified columns, call it with help_me = True
    to see the arguments
    """
    # print help message if user asked to
    # note: I did it this way (instead of docstring) because you can just print to a new cell
    # and then you don't have to press shift+tab each time
    if help_me:
        print("This function looks at your dataframe and finds things that COULD be missing or 'wrong' data")
        print("-" * 20)
        print("---Arguments---")
        print("df: your dataframe (no series! cast it first)")
        print("cols: columns to check/operate on as list of strings, defaults to all")
        print("replace_with: replaces nan values with this, if not specified then it doesn't replace")
        print("You probably DONT want to use this, it really will replace everything which is risky.")
        print("show_help: shows this list, note: it also stops the function doing anything")
        print("print_all: if True, it prints all the column names and dtypes, if false then only the ones that are bad")
        print("args: list of things to check (as str), defaults to all")
        print("\t'npnan' checks for np.nan values")
        print("\t'zero' checks for zero values")
        print("\t'negative' checks for negative values")
        print("\t'regex' checks for common unknown things based on regex like '?'")
        print("\t'whitespace' checks for spaces at start and end of the string")
        print("\t'numberformat' checks if string type columns can become numeric if specific chars are removed (e.g. '10%' to 10)")
        print("\t\tnote that this doesn't count towards being 'missing data' for the sake of replacing values, it just tells you")
        print("\t\tthis is because it isn't really 'missing' just in the wrong format")
        print("\t\tI am also not sure exactly how reliable this check is!")
        print("\t'colname' checks if your column names are lowercase and has no spaces")
        return
    
    # Print shape
    print("DF shape:{}".format(df.shape))
    print("-"*15)
    
    # If user didn't specify any columns then do this for all the columns
    if cols == []:
        cols = df.columns
        
    # at the end, print out how many rows are bad so we need to record which rows are bad
    # this doesn't work for now
    any_col_bad_boolean = [False for _ in range(df.shape[0])]
    
    # loop through only the specified columns
    for one_col in cols:
        
        # create a new boolean array, all false
        row_is_bad = [False for _ in range(len(df[one_col]))]
        
        # do the things that the user asked 
        if "npnan" in checks or checks == []:
            row_is_bad = np.logical_or(row_is_bad,
                                    check_np_null(df[one_col]))
        
        if "zero" in checks or checks == []:
            row_is_bad = np.logical_or(row_is_bad,
                                    check_zero(df[one_col]))
            
        if "negative" in checks or checks == []:
            row_is_bad = np.logical_or(row_is_bad,
                                    check_negatives(df[one_col]))
            
        if "regex" in checks or checks == []:
            row_is_bad = np.logical_or(row_is_bad,
                                    check_common_unknowns(df[one_col]))
            
        if "whitespace" in checks or checks == []:
            row_is_bad = np.logical_or(row_is_bad, 
                                    check_whitespace(df[one_col]))
                
        # this doesn't count as 'bad' so there is no logical_or
        if "numberformat" in checks or checks == []:
            row_is_bad = check_numeric_format(df[one_col])
            
        # print the column name but only if there's something wrong!:
        if any(row_is_bad) or print_all == True:    
            print("{}".format(one_col))
            print(f"dtype: \t{df[one_col].dtype}\t")
            print("-" * 15)
        
        # Replace if the user specified something
        if replace_with is not None:
            df[one_col] = replace_values(df[one_col], row_is_bad, replace_with)
        
        # record the number of bad rows
        any_col_bad_boolean = np.logical_or(any_col_bad_boolean, row_is_bad)
    
    # --- end of for loop ---
    
    # at the end return the number of rows that are 'bad'
    print("Total bad rows across all columns (if any in the row are bad): {}"
        .format(np.sum(any_col_bad_boolean)))
    
    if replace_with is not None:
        print("Values were replaced")
    else:
        print("Values were not replaced")
        
    if "colname" in checks or checks == []:
        check_column_names(df.columns)
    
    if replace_with is not None:
        return df
    else:
        return None
    
# check if anything is np.nan
def check_np_null(one_series):
    # check if each item is np null
    is_np_null = one_series.isnull()
            
    if any(is_np_null):
        print("np.nan counts: {}".format(np.sum(is_np_null)))  
    return is_np_null
    
# check if anything in the series is zero
def check_zero(one_series):
    
    # return if not numeric   
    if not pd.api.types.is_numeric_dtype(one_series):
        return
    
    # check if any are zero    
    is_zero = one_series == 0
    if any(is_zero):
        print("Zero values count: {}".format(np.sum(is_zero)))
    
    # return boolean array
    return is_zero

# check if anything negative
def check_negatives(one_series):
    
    # return if not numeric   
    if not pd.api.types.is_numeric_dtype(one_series):
        return
    
    # check if any are negative
    is_negative = one_series < 0
    if any(is_negative):
        print("Negative values count: {}".format(np.sum(is_negative)))
    
    # return boolean array
    return is_negative

# check if anything in the series matches a common 'unknown' thing
def check_common_unknowns(one_series):
    
    # This regex string matches any combination of the characters:
    # ? , [space] \ / " ' \n . 'unknown' 
    # in any quantity (but it can ONLY be made of those chars)
    regex_str = "^(?:\\?|\\ |\\.|\\\\|\\/|\\n|\\\"|\\'|unknown|unkown)*$"
    
    # use list comprehension to apply regex to all items in series
    # True = match (looks like an unknown value), False = not match
    regex_matches = [re.match(regex_str, str(s).lower().rstrip()) is not None
                    for s in one_series]
    
    if any(regex_matches):
        print("Num of entries that look empty based on regex: {}".format(np.sum(regex_matches)))
    
    # return boolean series showing the things that don't match
    return regex_matches
        
# Takes in a series and a binary series, and replaces it
def replace_values(one_series, boolean_series, replace_with = np.nan):
    
    # Use list comprehension to replace items in series
    # but only if the boolean matches
    one_series = [replace_with if should_replace == True else one_series[i]
                for i, should_replace in enumerate(boolean_series)]
    
    return one_series

# Checks the series to see if it matches anything else that the user specified
def check_other_values(one_series, items_to_check):
    
    # checks if anything matches
    is_match = [s in items_to_check for s in one_series]
    
    if any(is_match):
        print("Num of other user-specified matching values: {}".format(np.sum(is_match)))
        
    # return the boolean array
    return is_match

# checks if text has a whitespace at the start and end
def check_whitespace(one_series):
    # return if not text   
    if not pd.api.types.is_string_dtype(one_series):
        return
    
    stripped_series = one_series.str.strip(" \n")
    mismatches = np.sum(stripped_series!= one_series)
    num_mismatch = np.sum(mismatches)
    if num_mismatch > 0:
        print("Num of rows with space or \\n at start or end: {}".format(num_mismatch))
        
    # return boolean array
    return mismatches

# check if a series looks like numeric but with added stuff:
# e.g. 10%, 20%, 30.5% are all numeric but with a % sign.
# This checks if that is an issue!
def check_numeric_format(one_series):
    
    # return if not text
    if not pd.api.types.is_string_dtype(one_series):
        return
    
    # check if there are even any digits
    # if your column is just 'cat' 'cat' 'cat'
    # we don't want to say that it's all the same
    has_digits = [re.match("[0-9]", s) is not None
                for s in one_series]
    
    if np.mean(has_digits) <= 0.9:
        return
    
    # remove all digits and decimal points
    digits_removed = one_series.map(lambda s: re.sub("[0-9|.]", "", s))
    
    # if they are MOSTLY the same, this means one or two have an
    # easily fixed issue, e.g. most are 10%, 12.5%, and one is "13.5 %"
    # with a space.
    # This takes the most common string (after removing digits 0-9)
    # and sees how many there are
    highest_count = digits_removed.value_counts().sort_values(ascending=False)[0]
    
    series_size = one_series.size  

    if highest_count == series_size:
        print("Can be entirely converted to numeric by removing specific characters")

    # If over 90% (arbitrarily I picked this number, I guess it could be different)
    elif highest_count > (0.9 * one_series.size):
        print("(Most likely) over 90% of column can be converted to numeric apart from specific chars")

    # This one doesn't return anything, not really sure what to return.
    
# checks if the column names are lowercase, no space
def check_column_names(names):
    print("-"*15)
    print("Column Name Checker:")
    for name in names:
        if " " in name:
            print("'{}' has space in column name".format(name))
        if not name.islower():
            print("'{}' has uppercase chars in column name".format(name))
        if len(name) >= 15:
            print("'{}' is annoyingly long to type, please change it".format(name))