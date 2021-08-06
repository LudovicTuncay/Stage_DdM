import pandas as pd

# Initilise des dataframes pour qu'ils soient accessibles a tous les autres
# fichiers du dashboard


def initialize(dataframe=pd.DataFrame()):
    global df
    df = dataframe


def initialize_df_to_study(dataframe=pd.DataFrame()):
    global df_to_study
    df_to_study = dataframe
