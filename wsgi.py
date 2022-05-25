from app import app
import pandas as pd
from preprocessor import preprocess

df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')

if __name__ == "__main__":
    print(" * Going for dataset preprocessing")
    preprocessed_df = preprocess(df, region_df)
    print(" * Preprocessing completed!!! ")
    preprocessed_df.to_csv('processedfile.csv')
    print(" * Saving new csv file")
    app.run(debug=True)
