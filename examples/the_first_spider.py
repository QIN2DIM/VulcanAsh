import logging
import random
import time

import requests
from bs4 import BeautifulSoup

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
    """
    # =========================================================================================================
    # T 01-01 : [100/100] |  9.775s
    # T 01-02 : [100/100] |  10.052s
    # T 01-03 : [100/100] |  9.983s
    # ---------------------------------------------------------------------------------------------------------
    # T 01-11 : [200/200] |  19.805s
    # T 01-12 : [200/200] |  20.698s
    # T 01-13 : [200/200] |  19.828s
    # ---------------------------------------------------------------------------------------------------------
    # T 01-21 : [500/500] |  50.455s
    # =========================================================================================================
    :param task_docker:
    :return:
    """
    # 测试任务
    for task in task_docker:
        try:
            test_business(html=task)
        except Exception as e:
            logging.error(f"---> GeneralSpider | {e}")


@task_timer
def launcher_vulcan(task_list, power_=1):
    """
    # =========================================================================================================
    # 无反爬虫限制——理想条件下
    # =========================================================================================================
    # T 01-01 : [100/100] | power:16 |  5.821s
    # T 01-02 : [100/100] | power:16 |  5.814s
    # T 01-03 : [100/100] | power:16 |  5.822s
    # T 01-04 : [100/100] | power:32 |  5.547s
    # T 01-05 : [100/100] | power:32 |  5.476s
    # T 01-06 : [100/100] | power:32 |  5.732s
    # T 01-07 : [100/100] | power:64 |  5.34s
    # T 01-08 : [100/100] | power:64 |  5.495s
    # T 01-09 : [100/100] | power:64 |  5.573s
    # ---------------------------------------------------------------------------------------------------------
    # T 01-11 : [200/200] | power:2  |  15.417s
    # T 01-12 : [200/200] | power:4  |  13.157s
    # T 01-13 : [200/200] | power:8  |  11.484s
    # T 01-14 : [200/200] | power:16 |  11.221s
    # T 01-15 : [200/200] | power:16 |  62.542s ERROR:root:---> VulcanSpider | HTTPConnectionPool
    # T 01-16 : [200/200] | power:32 |  10.587s
    # T 01-17 : [200/200] | power:64 |  10.462s
    # ---------------------------------------------------------------------------------------------------------
    # T 01-22 : [500/500] | power:16 |  42.402s
    # T 01-21 : [500/500] | power:64 |  26.417s
    # =========================================================================================================
    :return:
    """
    import os
    from src.vulcan_engine.kernel import CoroutineSpeedup

    class VulcanEngine(CoroutineSpeedup):
        def __init__(self, task_docker: list = None, power: int = os.cpu_count()):
            super(VulcanEngine, self).__init__(task_docker=task_docker, power=power)

        def control_driver(self, task):
            try:
                test_business(html=task)
            except Exception as e:
                logging.error(f"---> VulcanSpider | {e}")

    VulcanEngine(task_docker=task_list, power=power_).interface()


if __name__ == '__main__':
    html_list = [
        "http://www.ylshuo.com/article/310000.html",
        "http://www.ylshuo.com/article/310010.html",
    ]
    # launcher_general(TASK_DOCKER[:10])
    launcher_vulcan(TASK_DOCKER[:100], power_=16)
    # launcher_use_plugin(html_list)
