import pandas as pd


def initialize(dataframe=pd.DataFrame()):
    global df
    df = dataframe


def initialize_df_to_study(dataframe=pd.DataFrame()):
    global df_to_study
    df_to_study = dataframe
