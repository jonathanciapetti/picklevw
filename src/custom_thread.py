from threading import Thread


class CustomThread(Thread):
    def __init__(self, queue, func, func_args):
        super().__init__()
        self.queue = queue

        if not callable(func):
            raise TypeError(f"func is {type(func)} which is not callable.")
        self.func = func

        try:
            iter(func_args)
        except TypeError:
            print(f"self.func_args is {type(func_args)} which is not iterable.")
        self.func_args = func_args

    def run(self):
        self.func(*self.func_args)
        self.queue.put("Task finished")
