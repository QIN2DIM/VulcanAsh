__all__ = ["VulcanCoroutineSpeedup"]

import atexit
from functools import wraps
from typing import Dict, List, Callable

import os

import logging

import time
import queue
from threading import Thread

import gevent
from gevent.queue import JoinableQueue
from gevent import monkey

monkey.patch_all(ssl=False)

logging.getLogger().setLevel(logging.INFO)


class VulcanCoroutineSpeedup(object):
    power: int = 8
    debug_logger: bool = True
    queue = None

    def __init__(self, power: int = 8, debug: bool = True):
        # 协程数
        self.__class__.power = power
        # 是否打印日志信息
        self.__class__.debug_logger = debug

        if not self.__class__.queue:
            self.__class__.queue = JoinableQueue(maxsize=power)

        for _ in range(power):
            gevent.spawn(self.__class__.__worker)
        atexit.register(self.__class__.__atexit)

        if self.__class__.debug_logger:
            logging.info(f'<Gevent> class initialize completed -- <{self.__class__.__name__}>')

    @classmethod
    def __worker(cls):
        while True:
            if cls.queue.empty():
                gevent.sleep(0.1)
            fn, (args, kwargs) = cls.queue.get()
            # print(args, kwargs)
            try:
                fn(*args[0], **args[1])
            except Exception as exc:
                logging.info(f'函数 {fn.__name__} 中发生错误，错误原因是 {type(exc)} {exc} ')
            finally:
                cls.queue.task_done()

    @classmethod
    def submit(cls, fn: Callable, *args, **kwargs):
        cls.queue.put((fn, (args, kwargs)))

    @classmethod
    def __atexit(cls):
        if cls.debug_logger:
            logging.info('exit.')
        cls.queue.join()

    @classmethod
    def __call__(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cls.submit(func, args, kwargs)
            if cls.debug_logger:
                logging.info(f'<Gevent> add task {func.__name__} completed -- <{cls.__name__}>')

        return wrapper
