__all__ = ["AsyncCoroutineSpeedup", "AsyncPool"]

from functools import wraps
from typing import Dict, List

import os

import logging

import asyncio
import aiohttp
import time
import nest_asyncio
import queue
from threading import Thread

logging.getLogger().setLevel(logging.INFO)


class AsyncPool(object):
    """
    1. 支持动态添加任务
    2. 支持自动停止事件循环
    3. 支持最大协程数
    """

    def __init__(self, maxsize=1, loop=None):
        """
        初始化
        :param loop:
        :param maxsize: 默认为1
        """
        # 在jupyter需要这个，不然asyncio运行出错
        # import nest_asyncio
        # nest_asyncio.apply()

        # 队列，先进先出，根据队列是否为空判断，退出协程
        self.task = queue.Queue()

        # 协程池
        self.loop, _ = self.start_loop(loop)
        # 限制并发量为500
        self.semaphore = asyncio.Semaphore(maxsize, loop=self.loop)

    def task_add(self, item=1):
        """
        添加任务
        :param item:
        :return:
        """
        self.task.put(item)

    def task_done(self, fn):
        """
        任务完成
        回调函数
        :param fn:
        :return:
        """
        if fn:
            pass
        self.task.get()
        self.task.task_done()

    def wait(self):
        """
        等待任务执行完毕
        :return:
        """
        self.task.join()

    @property
    def running(self):
        """
        获取当前线程数
        :return:
        """
        return self.task.qsize()

    @staticmethod
    def _start_thread_loop(loop):
        """
        运行事件循环
        :param loop: loop以参数的形式传递进来运行
        :return:
        """
        # 将当前上下文的事件循环设置为循环。
        asyncio.set_event_loop(loop)
        # 开始事件循环
        loop.run_forever()

    async def _stop_thread_loop(self, loop_time=1):
        """
        停止协程
        关闭线程
        :return:
        """
        while True:
            if self.task.empty():
                # 停止协程
                self.loop.stop()
                break
            await asyncio.sleep(loop_time)

    def start_loop(self, loop):
        """
        运行事件循环
        开启新线程
        :param loop: 协程
        :return:
        """
        # 获取一个事件循环
        if not loop:
            loop = asyncio.new_event_loop()

        loop_thread = Thread(target=self._start_thread_loop, args=(loop,))
        # 设置守护进程
        loop_thread.setDaemon(True)
        # 运行线程，同时协程事件循环也会运行
        loop_thread.start()

        return loop, loop_thread

    def stop_loop(self, loop_time=1):
        """
        队列为空，则关闭线程
        :param loop_time:
        :return:
        """
        # 关闭线程任务
        asyncio.run_coroutine_threadsafe(self._stop_thread_loop(loop_time), self.loop)

    def release(self, loop_time=1):
        """
        释放线程
        :param loop_time:
        :return:
        """
        self.stop_loop(loop_time)

    async def async_semaphore_func(self, func):
        """
        信号包装
        :param func:
        :return:
        """
        async with self.semaphore:
            return await func

    def submit(self, func, callback=None):
        """
        提交任务到事件循环
        :param func: 异步函数对象
        :param callback: 回调函数
        :return:
        """
        self.task_add()

        # 将协程注册一个到运行在线程中的循环，thread_loop 会获得一个环任务
        # 注意：run_coroutine_threadsafe 这个方法只能用在运行在线程中的循环事件使用
        # future = asyncio.run_coroutine_threadsafe(func, self.loop)
        future = asyncio.run_coroutine_threadsafe(self.async_semaphore_func(func), self.loop)

        # 添加回调函数,添加顺序调用
        if callback:
            future.add_done_callback(callback)
        future.add_done_callback(self.task_done)


class AsyncCoroutineSpeedup(object):
    max_queue_size: int = 8
    queue = None
    power: int = None
    debug_logger: bool = True

    def __init__(self, power: int = None, debug: bool = True):
        # 协程数
        self.__class__.power = power
        # 是否打印日志信息
        self.__class__.debug_logger = debug
        if not self.__class__.queue:
            self.__class__.queue = AsyncPool(maxsize=self.__class__.max_queue_size)
        logging.info(f'<Gevent> class initialize completed -- <{self.__class__.__name__}>')

    @classmethod
    def __call__(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cls.queue.submit(cls.control_driver({'function': func, 'param': (args, kwargs)}))
            if cls.debug_logger:
                logging.info(f'<Gevent> add task {func.__name__} completed -- <{cls.__name__}>')

        return wrapper

    @classmethod
    def control_driver(cls, task):
        # cls.control_driver.__name__ = "control_driver"
        task['function'](*task['param'][0], **task['param'][1])
        pass

    @classmethod
    def killer(cls):
        pass


import requests
from bs4 import BeautifulSoup
test_group = []


@AsyncCoroutineSpeedup()
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

    for item in test_group:
        print(item)