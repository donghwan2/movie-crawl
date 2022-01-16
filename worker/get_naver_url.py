import os
import pandas as pd
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

datadir_path = os.getcwd() + '/datas'
#################################
# get naver_movie review page url

kofic_upcoming_df = pd.read_csv(datadir_path + '/kofic_upcoming_movie.csv')
df = kofic_upcoming_df.copy()

# "data_info"
data_info = []
# "url"
data_url = []
# naver movie review url head
url_head = "https://movie.naver.com"
# requests headers
headers = {"user-agent": "Mozilla/5.0"}


for idx, movie_title in enumerate(tqdm(df['영화명'])):
    is_exist_search_results = False

    year_of_made = df.iloc[idx]['year_of_made']
    # print(year_of_made)
    country = df.iloc[idx]['국적']
    # print(country)
    director = df.iloc[idx]['감독']
    # print(director)

    # for testing
    # if idx == 100:
    #     break

    # 네이버 리뷰 url 양식
    query_url = url_head + \
        f"/movie/search/result.naver?section=movie&query={movie_title}"
    res = requests.get(query_url, headers=headers)
    search_soup = BeautifulSoup(res.content, 'html.parser')

    try:
        movie_list = search_soup.select_one(".search_list_1").find_all("li")
        is_exist_search_results = True

    except:
        None

    if is_exist_search_results == True:
        is_collect = False

        # 1등급 (만장일치)
        for i in movie_list:
            if (str(year_of_made) in i.text) and (country in i.text) and (str(director) in i.text):
                url_tail = i.find("dl").find("a")["href"]
                collect_movie_url = url_head + url_tail

                # 비고작성
                data_info.append(1)
                data_url.append(collect_movie_url)

                is_collect = True
                break

        # 감독과 국가 일치하는 경우 (2등급), 제목까지 일치 (1등급)-> 대부분 맞음
        if is_collect == False:
            for i in movie_list:
                if (str(director) in i.text) and (country in i.text):
                    url_tail = i.find("dl").find("a")["href"]
                    collect_movie_url = url_head + url_tail

                    # 제목과 일치여부 확인 후 비고작성
                    if movie_title in i.find("dt").text:
                        data_info.append(1)
                    else:
                        data_info.append(2)
                    data_url.append(collect_movie_url)

                    is_collect = True
                    break

        # 감독명만 일치 (3등급), 제목까지 일치 (2등급)
        if is_collect == False:
            for i in movie_list:
                if (str(director) in i.text):
                    url_tail = i.find("dl").find("a")["href"]
                    collect_movie_url = url_head + url_tail

                    # 제목과 일치여부 확인 후 비고작성
                    if movie_title in i.find("dt").text:
                        data_info.append(2)
                    else:
                        data_info.append(3)
                    data_url.append(collect_movie_url)

                    is_collect = True
                    break

        # 연도와 국가 일치 (4등급), 제목까지 (2등급)
        if is_collect == False:
            for i in movie_list:
                if (str(year_of_made) in i.text) and (country in i.text):
                    url_tail = i.find("dl").find("a")["href"]
                    collect_movie_url = url_head + url_tail

                    # 제목과 일치여부 확인 후 비고작성
                    if movie_title in i.find("dt").text:
                        data_info.append(2)
                    else:
                        data_info.append(4)
                    data_url.append(collect_movie_url)

                    is_collect = True
                    break

        # 그래도 없을때. (5등급) 제목일치 (4등급)-> 첫번째것으로 가져옴 ("영화제목이 일치하는지 확인 일치하지 않는다면 데이터 없음.") 다만 5번의 경우 직접 확인이 필요한 데이터.
        if is_collect == False:
            i = movie_list[0]
            url_tail = i.find("dl").find("a")["href"]
            collect_movie_url = url_head + url_tail

            # 제목과 일치여부 확인 후 비고 작성
            if movie_title in i.find("dt").text:
                data_info.append(4)
            else:
                data_info.append(5)
            data_url.append(collect_movie_url)

    if is_exist_search_results == False:
        data_info.append(6)
        data_url.append(None)

df['data_url'] = data_url
df['data_info'] = data_info

df.to_csv(datadir_path + "/upcoming_movie_naver_url.csv", index=False)
