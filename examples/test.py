# Author: BeiYu
# Github: https://github.com/beiyuouo
# Date  : 2021/4/4 10:35
# Description:

__author__ = "BeiYu"

import time

import aiohttp

from src.vulcan_engine.async_vulcan.async_kernel import AsyncPool


async def thread_example(i):
    url = "http://127.0.0.1:8080/app04/async4?num={}".format(i)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            # print(res.status)
            # print(res.content)
            return await res.text()


def my_callback(future):
    result = future.result()
    print('返回值: ', result)


def main():
    # 任务组， 最大协程数
    pool = AsyncPool(maxsize=100000)

    print('initialize successfully')
    return

    # 插入任务任务
    for i in range(100000):
        pool.submit(thread_example(i), my_callback)

    print("等待子线程结束1...")
    # 停止事件循环
    pool.release()

    # 获取线程数
    # print(pool.running)
    print("等待子线程结束2...")
    # 等待
    pool.wait()

    print("等待子线程结束3...")


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    print("run time: ", end_time - start_time)