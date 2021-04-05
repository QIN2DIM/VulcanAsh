# Author: BeiYu
# Github: https://github.com/beiyuouo
# Date  : 2021/4/4 10:17
# Description:

__author__ = "BeiYu"

import logging

import random
import time

import requests
from bs4 import BeautifulSoup

# logging.getLogger().setLevel(logging.INFO)

from src.vulcan_engine.async_vulcan.async_kernel import AsyncCoroutineSpeedup
from src.vulcan_engine.offline_vulcan.offline_kernel import OfflineCoroutineSpeedup

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


@AsyncCoroutineSpeedup(power=1000, debug=False)
def test_vulcan_business(html: str = "http://www.ylshuo.com/article/310000.html"):
    res = requests.get(html)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")

    batch = [i.text.strip() for i in soup.find("div", class_="g-detail-font").find_all("p")]

    title = soup.find("h1").text
    content = batch[1:]

    test_group.append("title:{}\ncontent:{}\nsource:{}\n\n".format(title, "$".join(content), html))


@OfflineCoroutineSpeedup(power=16, debug=False)
def test_offline_business(html: str = "http://www.ylshuo.com/article/310000.html"):
    res = requests.get(html)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")

    batch = [i.text.strip() for i in soup.find("div", class_="g-detail-font").find_all("p")]

    title = soup.find("h1").text
    content = batch[1:]

    test_group.append("title:{}\ncontent:{}\nsource:{}\n\n".format(title, "$".join(content), html))


def test_business(html="http://www.ylshuo.com/article/310000.html"):
    res = requests.get(html)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")

    batch = [i.text.strip() for i in soup.find("div", class_="g-detail-font").find_all("p")]

    title = soup.find("h1").text
    content = batch[1:]

    test_group.append("title:{}\ncontent:{}\nsource:{}\n\n".format(title, "$".join(content), html))


"""===========================================启动接口==========================================="""


# -----------------------------------------------------------------
# target 01. Collect N pages of data on English proverbs
# -----------------------------------------------------------------
@task_timer
def launcher_general(task_docker):
    # 测试任务
    for task in task_docker:
        try:
            test_business(html=task)
        except Exception as e:
            logging.error(f"---> GeneralSpider | {e}")


@task_timer
def launcher_vulcan(task_list, power_=1):
    import os
    from src.vulcan_engine.kernel import CoroutineSpeedup

    class VulcanEngine(CoroutineSpeedup):
        def __init__(self, task_docker: list = None, power: int = os.cpu_count()):
            super(VulcanEngine, self).__init__(task_docker=task_docker, power=power, debug=False)

        def control_driver(self, task):
            try:
                test_business(html=task)
            except Exception as e:
                logging.error(f"---> VulcanSpider | {e}")

    VulcanEngine(task_docker=task_list, power=power_).interface()


@task_timer
def launcher_asyncvulcan(html_list):
    for item in html_list:
        test_vulcan_business(item)


@task_timer
def launcher_offlinevulcan(html_list):
    for item in html_list:
        test_offline_business(item)

    OfflineCoroutineSpeedup.run()


if __name__ == '__main__':
    print('init')
    launcher_asyncvulcan(TASK_DOCKER[:100])
    launcher_offlinevulcan(TASK_DOCKER[:100])
    launcher_vulcan(TASK_DOCKER[:100], power_=16)
    launcher_general(TASK_DOCKER[:100])
