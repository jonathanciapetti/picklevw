# from multiprocessing import Process
#
#
# class CustomProcess(Process):
#     def __init__(self, queue):
#         super().__init__()
#         self.queue = queue
#
#     def run(self):
#         self.run(*self.func_args)
#         self.queue.put("Task finished")
