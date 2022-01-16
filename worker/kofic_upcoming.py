import os
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.common import exceptions

# os.chdir("./")
datadir_path = os.getcwd() + '/datas'

if not os.path.exists(datadir_path):
    os.mkdir(datadir_path)

URL = 'https://www.kobis.or.kr/kobis/business/mast/mvie/findOpenScheduleList.do'

options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome(executable_path=os.getcwd() +
                          '/chromedriver', options=options)

# load kofic upcoming movie page
driver.get(url=URL)
driver.implicitly_wait(time_to_wait=5)

# compare date
today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
today = int(today.replace("-", ""))

# open upcoming movie code tab
mvcode_tab = driver.find_element_by_xpath(
    '/html/body/div/div[2]/div[2]/form/div[3]/ul/li[4]/a')
mvcode_tab.click()

driver.implicitly_wait(time_to_wait=5)

# select combobox
view_all = driver.find_element_by_xpath(
    '/html/body/div/div[2]/div[2]/form/div[3]/div/div[2]/select/option[1]')
view_all.click()

driver.implicitly_wait(time_to_wait=5)


# task
# crate empty dataframe
columns = [
    'mvcode',
    '영화명',
    '감독',
    '배급사',
    '개봉일',
    'year_of_made',
    '국적',
    '영화형태',
    '영화유형',
    '장르',
    '등급',
    'num_cinemas',
    'num_screens']
empty_df = pd.DataFrame(columns=columns)


# if date is after today -> get datas
i = 1

# If the code is updated with a for loop, execution speed can be improved.
# must check the last child of the cell.
try:
    while True:
        data_row = []

        check_date = driver.find_element_by_xpath(
            f'/html/body/div/div[2]/div[2]/form/div[4]/table/tbody/tr[{i}]/td[4]').text
        open_day = int(check_date.replace("-", ""))
        if open_day > today:
            # main table #
            # kofic movie code
            kofic_mvcode = driver.find_element_by_xpath(
                f'/html/body/div/div[2]/div[2]/form/div[4]/table/tbody/tr[{i}]/td[1]').text
            # print(kofic_mvcode)
            data_row.append(kofic_mvcode)

            # movie title
            title = driver.find_element_by_xpath(
                f'/html/body/div/div[2]/div[2]/form/div[4]/table/tbody/tr[{i}]/td[2]').text
            print(title)
            data_row.append(title)

            # director
            director = driver.find_element_by_xpath(
                f'/html/body/div/div[2]/div[2]/form/div[4]/table/tbody/tr[{i}]/td[6]').text
            # print(director)
            data_row.append(director)

            # movie distributor
            distributor = driver.find_element_by_xpath(
                f'/html/body/div/div[2]/div[2]/form/div[4]/table/tbody/tr[{i}]/td[8]').text
            # print(distributor)
            data_row.append(distributor)

            # release date
            # print(open_day)
            data_row.append(open_day)

            # year of filming
            year_of_made = driver.find_element_by_xpath(
                f'/html/body/div/div[2]/div[2]/form/div[4]/table/tbody/tr[{i}]/td[3]').text
            # print(year_of_made)
            data_row.append(year_of_made)

            # country
            country = driver.find_element_by_xpath(
                f'/html/body/div/div[2]/div[2]/form/div[4]/table/tbody/tr[{i}]/td[7]').text
            # print(country)
            data_row.append(country)

            # open detail page
            detail_btn = driver.find_element_by_xpath(
                f'/html/body/div/div[2]/div[2]/form/div[4]/table/tbody/tr[{i}]/td[2]/a')
            detail_btn.click()
            driver.implicitly_wait(time_to_wait=5)

            # get detail page datas
            summary = driver.find_element_by_xpath(
                '/html/body/div[2]/div[2]/div/div[1]/div[2]/dl/dd[4]').text
            values = summary.split("|")

            # movie format
            mv_format = values[0].strip()
            # print(mv_format)
            data_row.append(mv_format)

            # category of movie
            category = values[1].strip()
            # print(category)
            data_row.append(category)

            # genre
            genre = values[2].strip()
            # print(genre)
            data_row.append(genre)

            # movie rating
            rating = values[4].strip()
            # print(rating)
            data_row.append(rating)

            # status tab
            status_tab = driver.find_element_by_xpath(
                '/html/body/div[2]/div[1]/div[2]/ul/li[3]/a')
            status_tab.click()
            driver.implicitly_wait(time_to_wait=5)

            j = 1
            num_cinemas = 0
            num_screens = 0

            # --->
            try:
                while True:
                    # cinema
                    num_cinema = driver.find_element_by_xpath(
                        f'/html/body/div[2]/div[2]/div/div[3]/div[1]/table/tbody/tr[{j}]/td[2]').text
                    num_cinema = re.sub(r'[^0-9]', '', num_cinema)
                    num_cinemas += int(num_cinema)
                    # screen
                    num_screen = driver.find_element_by_xpath(
                        f'/html/body/div[2]/div[2]/div/div[3]/div[1]/table/tbody/tr[{j}]/td[3]').text
                    num_screen = re.sub(r'[^0-9]', '', num_screen)
                    num_screens += int(num_screen)

                    j += 1
            except exceptions.NoSuchElementException:
                #
                None

            # total number of cinemas - variable
            # print(num_cinemas)
            data_row.append(num_cinemas)

            # total number of screens - variable
            # print(num_screens)
            data_row.append(num_screens)

            # print("-"*30, "\n")

            # closed detail page
            back_btn = driver.find_element_by_xpath(
                '/html/body/div[2]/div[1]/div[1]/a[2]/span')
            back_btn.click()
            driver.implicitly_wait(time_to_wait=5)

            # dataframe to csv
            tmp = pd.DataFrame([data_row], columns=columns)
            empty_df = pd.concat([empty_df, tmp])
            empty_df.to_csv(
                datadir_path + '/kofic_upcoming_movie.csv', index=False)

        i += 1
except Exception as e:
    driver.close()
