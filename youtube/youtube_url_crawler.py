import re
import sys
import argparse
import logging
from tqdm import tqdm
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

mylogger = logging.getLogger("film")
mylogger.setLevel(logging.INFO)

file_handler = logging.FileHandler("film_url.log")
mylogger.addHandler(file_handler)


options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome("./chromedriver", chrome_options=options)
interval = 2000

pattern_parenthesis = re.compile(r"(\[|\()(.*?)(\]|\))")


def main(source_filename, target_filename):
    df = pd.read_csv(source_filename)

    df["urls"] = None

    # df = df[interval * part : interval * part + interval]
    for i, row in tqdm(df.iterrows()):

        urls = get_url(row["영화명"])
        df.loc[i, "urls"] = ",".join(urls)

    df.to_csv(target_filename)


def check_title(source_title, target_title):

    _source_title = re.sub("\s", "", source_title)
    _target_title = re.sub("\s", "", target_title)

    matched = pattern_parenthesis.findall(target_title)

    for m in matched:
        if re.sub("\s", "", m[1]) == _source_title:
            return True

    matched = re.search(_source_title, _target_title)
    if matched:
        if matched.end() == len(target_title):
            return True

        next_char = target_title[matched.end()]
        if next_char.isdigit():
            return False
        elif next_char in ["-", "_"]:
            return True
        else:
            mylogger.info(f" source : {source_title}, target : {target_title}")

    return False


def get_url(file_title):
    url = "https://www.youtube.com/results?search_query=예고편+{}".format(
        file_title.replace(" ", "+")
    )

    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    try:
        film_infos = soup.select("a#video-title")
    except Exception as e:
        print(f"error : {file_title}")
        return

    print(len(film_infos))

    urls = []

    for film_info in film_infos:
        title = film_info.text
        if title.find("예고편") != -1 or title.lower().find("trailer") != -1:
            if check_title(file_title, title):
                urls.append("https://www.youtube.com" + film_info.attrs["href"])
        else:
            pass
            mylogger.info(f" not matched : {title}, target : {file_title}")

    return urls


def parse_args(argv):  # save parsed arguments into args!
    """Parse command line arguments."""
    # generate parser
    parser = argparse.ArgumentParser(description=__doc__)

    # set the argument fomats
    parser.add_argument(
        "--source_filename", "-s", default="movie_data_20220107.csv", help="file name",
    )
    parser.add_argument(
        "--target_filename",
        "-t",
        default="movie_data_youtube_20220107.csv",
        help="file name",
    )

    return parser.parse_args(argv[1:])


if __name__ == "__main__":
    args = parse_args(sys.argv)
    main(args.source_filename, args.target_filename)
    # get_url("어벤져스")
    # merge_files(4)
