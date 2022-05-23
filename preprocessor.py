import pandas as pd

def preprocess(df,region_df):
    
    # we are analyzing for summer olympics only
    df = df[df['Season'] != 'Winter']
    
    # Merge two dataframes to find country name
    df = df.merge(region_df, on='NOC', how='left')
    
    # Drop duplicates
    df.drop_duplicates(inplace=True)
    
    #Perform one hot encoder on Medals column
    df = pd.concat([df, pd.get_dummies(df.Medal)], axis=1)
    return df
