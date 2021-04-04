__all__ = ["OfflineCoroutineSpeedup"]


from functools import wraps
from typing import List

import gevent
from gevent import monkey

from gevent.queue import Queue

import logging
import os

monkey.patch_all(ssl=False)


class OfflineCoroutineSpeedup(object):
    max_queue_size = 0
    queue = Queue()
    power: int = None
    debug_logger: bool = True

    def __init__(self, power: int = None, debug: bool = True):
        # 协程数
        self.__class__.power = power
        # 是否打印日志信息
        self.__class__.debug_logger = debug

    @classmethod
    def __call__(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cls.queue.put_nowait({'function': func, 'param': (args, kwargs)})
            cls.max_queue_size = len(cls.queue)
            if cls.debug_logger:
                logging.info(f'<Gevent> add task {func.__name__} completed -- <{cls.__name__}>')

        return wrapper

    @classmethod
    def launch(cls):
        while not cls.queue.empty():
            task = cls.queue.get_nowait()
            cls.control_driver(task)

    @classmethod
    def run(cls, power: int = 8) -> None:
        """

        @param power: 协程功率
        @return:
        """

        task_list = []
        # 配置弹性采集功率
        power_ = cls.power if cls.power else power
        if cls.max_queue_size != 0:
            power_ = cls.max_queue_size if power_ > cls.max_queue_size else power_
        # 任务启动
        for x in range(power_):
            task = gevent.spawn(cls.launch)
            task_list.append(task)
        gevent.joinall(task_list)
        # 缓存回收
        cls.killer()
        # 全局日志信息打印
        if cls.debug_logger:
            logging.info(f'<Gevent> mission completed -- <{cls.__name__}>')

    @classmethod
    def control_driver(cls, task):
        task['function'](*task['param'][0], **task['param'][1])
        pass

    @classmethod
    def killer(cls):
        pass
