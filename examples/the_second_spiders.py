import logging

import random
import time

import requests
from bs4 import BeautifulSoup

from src.vulcan_engine.offline_vulcan.offline_kernel import OfflineCoroutineSpeedup

logging.getLogger().setLevel(logging.INFO)

"""===========================================全局变量=========================================="""
test_group = []

output_file_general = "test_one_step_spider.txt"
output_file_speedup = "test_speedup_spider.txt"
with open("seed_url.txt", "r", encoding="utf8") as f_:
    TASK_DOCKER = [i.strip() for i in f_.read().split("\n") if i]
    random.shuffle(TASK_DOCKER)
with open(output_file_general, "w", encoding="utf8") as f_g:
    pass
with open(output_file_speedup, "w", encoding="utf8") as f_s:
    pass
"""===========================================辅助工具==========================================="""


def task_timer(func):
    def wrapper(*args, **kwargs):
        start_ = time.time()
        func(*args, **kwargs)
        print(f"---> {func.__name__} | {round(time.time() - start_, 3)}s")

    return wrapper


def capture_flow(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        # 缓存语料
        with open(output_file_general, "w", encoding="utf8") as f:
            for cor in test_group:
                f.write(cor)

    return wrapper


"""===========================================测试业务==========================================="""


# @task_timer
@OfflineCoroutineSpeedup()
def test_business(html: str = "http://www.ylshuo.com/article/310000.html"):
    res = requests.get(html)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")

    batch = [i.text.strip() for i in soup.find("div", class_="g-detail-font").find_all("p")]

    title = soup.find("h1").text
    content = batch[1:]

    test_group.append("title:{}\ncontent:{}\nsource:{}\n\n".format(title, "$".join(content), html))


"""===========================================启动接口==========================================="""

if __name__ == '__main__':
    html_list = [
        "http://www.ylshuo.com/article/310000.html",
        "http://www.ylshuo.com/article/310010.html",
    ]
    for html_item in html_list:
        test_business(html_item)

    OfflineCoroutineSpeedup.run()

    # for x in test_group:
    #     print(x)
