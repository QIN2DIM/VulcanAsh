# VulcanAsh
 基于gevent和asyncio的异步协程加速解决方案
> 用装饰器模式，采用一种极简的异步方式，让你的爬虫获得协程引擎

| Py / Version | v_0.0.x |
| :--------: | :--: |
| 3.6        | ✅  |
| 3.7        | ✅  |
| 3.8        | ➖  |
| 3.9        | ➖  |


## How to use

```python
pip install vulcanash  # 打开冰箱门，暂未发版，将会在v_1.x之后打包加入pip

from vulcanash import VulcanCoroutineSpeedup  # 把大象放进冰箱

@VulcanCoroutineSpeedup(power=64)  # 关闭冰箱门
```

## Examples

> 例程省去了部分代码细节，完整代码请参考`vulcanash/examples/the_x_spider(s).py`
> 同时`example/spider_race.py`中有两种调用方法的速度比较

例如你原先的代码写成这个样子

```python
def test_business(html: str = "http://www.ylshuo.com/article/310000.html"):
    res = requests.get(html)
    pass


if __name__ == '__main__':
    html_format = "http://www.ylshuo.com/article/{}.html"

    for page in range(310000, 310101):
        test_business(html_format.format(page))
```

如果你想让他获得协程加速，可能会写一个任务队列，依次处理所有任务。 但是现在，你只需要直接把大象塞进冰箱再关上门即可。

```python
from vulcanash import VulcanCoroutineSpeedup

@VulcanCoroutineSpeedup(power=64)
def test_business(html: str = "http://www.ylshuo.com/article/310000.html"):
    res = requests.get(html)
    pass


if __name__ == '__main__':
    html_format = "http://www.ylshuo.com/article/{}.html"

    for page in range(310000, 310101):
        test_business(html_format.format(page))
```