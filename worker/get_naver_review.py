import os
import re
import pandas as pd
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

datadir_path = os.getcwd() + '/datas'
#######################
# get naver_review page

# requests headers
headers = {"user-agent": "Mozilla/5.0"}

url_rank_df = pd.read_csv(datadir_path + '/upcoming_movie_naver_url.csv')
df = url_rank_df.copy()

# 1. create empty dataframe
columns = [
    '영화명',
    'naver_mvcode',
    'likes',
    'num_photos',
    'num_videos',
    'main_actors',
    'sub_actors']

empty_df = pd.DataFrame(columns=columns)

for i in tqdm(range(len(df))):
    # if data is not exists
    if df.iloc[i]['data_info'] == 6:
        data_row = [None if j != 0 else df.iloc[i]['영화명']
                    for j in range(len(columns))]
    else:
        # check index
        # print("index:",i)

        detail_page_url = df.iloc[i]['data_url']
        title = df.iloc[i]['영화명']

        # create data row
        data_row = []

        # >>>>> append title
        data_row.append(title)
        # print("title:", title)

        # 3. extract code from url
        naver_mvcode = re.sub("[\D$]", "", detail_page_url)

        # >>>>> append naver_mvcode
        data_row.append(naver_mvcode)
        # print("code:", naver_mvcode)

        # 4. get likes
        json_movie_like_url = f"https://common.like.naver.com/likeIt/likeItContent.jsonp?_callback=window.__jindo2_callback._469&serviceId=MOVIE&displayId=MOVIE&contentsId={naver_mvcode}&lang=ko&viewType=like"
        res_json = requests.get(json_movie_like_url)

        # byte to str -> https://stackoverflow.com/questions/606191/convert-bytes-to-a-string
        text = res_json.content.decode("utf-8")
        rgx = re.search(r'("likeItCount":).*?(,"serviceName")', text)
        likes = int(re.sub("[^\d]", "", rgx.group()))

        # >>>>> append likes
        data_row.append(likes)
        # print("likes:", likes)

        # 5. num photos
        res = requests.get(detail_page_url, headers=headers)
        detail_soup = BeautifulSoup(res.content, 'html.parser')

        try:
            num_photos = int(detail_soup.select(".pg_cnt")[0].find("em").text)
        except:
            num_photos = 0

        # >>>>> append num_photos
        data_row.append(num_photos)
        # print("num_photos:", num_photos)

        # 6. num videos
        try:
            num_videos = int(detail_soup.select(".pg_cnt")[1].find("em").text)
        except:
            num_videos = 0

        # >>>>> append num_videos
        data_row.append(num_videos)
        # print("num_videos:", num_videos)

        # 9. get main, sub actors
        main_actors = ""
        sub_actors = ""
        res = requests.get(
            f"https://movie.naver.com/movie/bi/mi/detail.naver?code={naver_mvcode}", headers=headers)
        actor_soup = BeautifulSoup(res.content, 'html.parser')
        try:
            for i in actor_soup.select(".p_info"):
                member = i.find("a")['title']
                if "주연" in i.select_one(".p_part").text:
                    main_actors += f"{member},"
                elif "조연" in i.select_one(".p_part").text:
                    sub_actors += f"{member},"
        except:
            main_actors = None
            sub_actors = None

        # >>>>> append actors
        if main_actors == None:
            data_row.append(main_actors)
        else:
            data_row.append(main_actors[:-1])

        if sub_actors == None:
            data_row.append(sub_actors)
        else:
            data_row.append(sub_actors[:-1])

    # >>>
    tmp = pd.DataFrame([data_row], columns=columns)
    empty_df = pd.concat([empty_df, tmp])

    empty_df.to_csv(datadir_path + '/naver_upcoming_movie.csv', index=False)
