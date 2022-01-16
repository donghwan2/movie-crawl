from operator import index
import os
import time
import pandas as pd

# os.chdir('../')
datadir_path = os.getcwd() + '/datas'

kofic = pd.read_csv(datadir_path + '/upcoming_movie_naver_url.csv')
naver = pd.read_csv(datadir_path + '/naver_upcoming_movie.csv')
kofic_df = kofic.copy()
naver_df = naver.copy()

merged_df = pd.merge(kofic_df, naver_df, how='outer', on='영화명')

# timestamp
timestamp = time.strftime("%Y%m%d-%H%M%S")

merged_df.to_csv(datadir_path + f'/upcoming_data_{timestamp}.csv', index=False)

# remove extra files
os.remove(datadir_path + '/kofic_upcoming_movie.csv')
os.remove(datadir_path + '/naver_upcoming_movie.csv')
os.remove(datadir_path + '/upcoming_movie_naver_url.csv')
