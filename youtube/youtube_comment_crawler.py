import sys
import re
import time
import argparse
import logging
from tqdm import tqdm
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import exceptions

mylogger = logging.getLogger("youtube")
mylogger.setLevel(logging.INFO)

file_handler = logging.FileHandler("youtube.log")
mylogger.addHandler(file_handler)
interval = 500


def scrape(url):
    """
    Extracts the comments from the Youtube video given by the URL.

    Args:
        url (str): The URL to the Youtube video

    Raises:
        selenium.common.exceptions.NoSuchElementException:
        When certain elements to look for cannot be found

        
    """

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome("./chromedriver", chrome_options=options)

    driver.get(url)
    driver.maximize_window()
    time.sleep(5)

    try:
        # Extract the elements storing the video title and
        # comment section.
        title = driver.find_element_by_xpath(
            '//*[@id="container"]/h1/yt-formatted-string'
        ).text
        info_string = driver.find_element_by_xpath('//*[@id="info-strings"]').text
        count_string = driver.find_element_by_xpath(
            '//*[@id="info-text"]/div[@id="count"]'
        ).text
        like_info = driver.find_element_by_xpath(
            '//*[@id="menu"]/ytd-menu-renderer'
        ).text
        like_count, dislike_count = 0, 0
        if like_info:
            like_nums = like_info.split("\n")
            if like_nums[0].isdigit():
                like_count = int(like_nums[0])
            if like_nums[1].isdigit():
                dislike_count = int(like_nums[1])
        comment_section = driver.find_element_by_xpath('//*[@id="comments"]')
    except exceptions.NoSuchElementException:
        # Note: Youtube may have changed their HTML layouts for
        # videos, so raise an error for sanity sake in case the
        # elements provided cannot be found anymore.
        error = "Error: Double check selector OR "
        error += (
            "element may not yet be on the screen at the time of the find operation"
        )
        print(error)

    # Scroll into view the comment section, then allow some time
    # for everything to be loaded as necessary.
    try:
        driver.execute_script("arguments[0].scrollIntoView();", comment_section)
    except Exception as e:
        driver.close()
        return None, None, None, None, None, 0, "error"

    time.sleep(7)

    # Scroll all the way down to the bottom in order to get all the
    # elements loaded (since Youtube dynamically loads them).
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        # Scroll down 'til "next load".
        driver.execute_script(
            "window.scrollTo(0, document.documentElement.scrollHeight);"
        )

        # Wait to load everything thus far.
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script(
            "return document.documentElement.scrollHeight"
        )
        if new_height == last_height:
            break
        last_height = new_height

    # One last scroll just in case.
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    try:
        # Extract the elements storing the usernames and comments.
        username_elems = driver.find_elements_by_xpath('//*[@id="author-text"]')
        comment_elems = driver.find_elements_by_xpath('//*[@id="content-text"]')
    except exceptions.NoSuchElementException:
        error = "Error: Double check selector OR "
        error += (
            "element may not yet be on the screen at the time of the find operation"
        )
        print(error)
        driver.close()
        return None, None, None, None, None, 0, "error"

    print("> VIDEO TITLE: " + title + "\n")
    try:
        comments_num = len(comment_elems)
        comments = ", ".join([comment.text for comment in comment_elems])
        count = re.search(r"([^\s]+) views", count_string)
        if len(count.groups()) == 1:
            count = int(count.group(1).replace(",", ""))
        else:
            count = 0

        print(
            f"조회수 : {count}, 날짜 : {info_string},  좋아요 수 : {like_count}, 싫어요 수 : {dislike_count} 댓글 수 : {comments_num}, 리뷰 {comments}"
        )
    except Exception as e:
        count = None
        print("can't anlayze as ", e)
    finally:
        driver.close()

    return count, title, info_string, like_count, dislike_count, comments_num, comments


def main(source_filename, target_filename):
    df = pd.read_csv(source_filename)
    df["조회수"] = 0
    df["타이틀"] = ""
    df["날짜"] = ""
    df["좋아요"] = 0
    df["싫어요"] = 0
    df["댓글수"] = 0
    df["댓글"] = ""

    for i, row in tqdm(df.iterrows()):

        url = "https://www.youtube.com" + row["url"]
        print(f"url : {url} ")
        (
            count,
            title,
            info_string,
            like_count,
            dislike_count,
            comments_num,
            comments,
        ) = scrape(url)

        if count and count > 0:
            df.loc[i, "조회수"] = count
            df.loc[i, "타이틀"] = title
            df.loc[i, "날짜"] = info_string
            df.loc[i, "좋아요"] = like_count
            df.loc[i, "싫어요"] = dislike_count
            df.loc[i, "댓글수"] = comments_num
            df.loc[i, "댓글"] = comments
        else:
            mylogger.info(f"error : {url}")

    df.to_csv(target_filename)


def parse_args(argv):  # save parsed arguments into args!
    """Parse command line arguments."""
    # generate parser
    parser = argparse.ArgumentParser(description=__doc__)

    # set the argument fomats
    parser.add_argument(
        "--source_filename",
        "-s",
        default="movie_data_youtube_20220107.csv",
        help="file name",
    )
    parser.add_argument(
        "--target_filename",
        "-t",
        default="movie_data_youtube_comments_20220107.csv",
        help="file name",
    )

    return parser.parse_args(argv[1:])


if __name__ == "__main__":
    args = parse_args(sys.argv)
    main(args.source_filename, args.target_filename)
