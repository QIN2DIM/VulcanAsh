__all__ = ['VulcanEngine']

import os

from .kernel import CoroutineSpeedup


class VulcanEngine(CoroutineSpeedup):
    def __init__(self, task_docker: list = None, power: int = os.cpu_count()):
        super(VulcanEngine, self).__init__(task_docker=task_docker, power=power)
