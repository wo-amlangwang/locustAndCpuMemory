import psutil
import threading
import time
import os
from queue import Queue
from Utils.util import get_slash
import logging

logger = logger = logging.getLogger(__name__)

def get_process_by_name(name: str):
    if name is None:
        return None
    result_process = []
    for process in psutil.process_iter():
        if process.pid == 0:
            continue
        if process.name().find(name) >= 0:
            result_process.append(process)
    return result_process

def get_process_by_pid(pid: int):
    if pid is None:
        return []
    for process in psutil.process_iter():
        if process.pid == pid:
            return [process]
    return []


def function_wrapper(fun):
    try:
        return_value = fun()
    except psutil.AccessDenied:
        return_value = 'N/A'
    return return_value


def write_csv_header(csv_file: str):
    with open(csv_file, 'w') as fd:
        header = 'Timestamp,Cpu Usage,Memory Usage,Threads Number\n'
        fd.write(header)


def sleep_and_execute(time_to_sleep: int, fun):
    time.sleep(time_to_sleep)
    fun()


def get_default_csvfile():
    return f'{os.path.dirname(os.path.realpath(__file__))}{get_slash()}process.csv'


class ProcessMonitor(object):
    def __init__(self, pid: int = None, name: str = None, csv_file: str = get_default_csvfile()):
        self.process = get_process_by_pid(pid)
        if len(self.process) == 0 and name is not None:
            self.process = get_process_by_name(name)
        if len(self.process) == 0:
            raise Exception("Process Not found.")
        for prodess in self.process:
            logger.info(f'Found process {prodess.name()}')
        logger.info(f'{len(self.process)} process found.')
        self.csv_file = csv_file
        self.message_queue = Queue()
        self.can_continue = True

    def get_stats(self):
        try:
            cpu_usage = 0
            memory_usage = 0
            threads_number = 0
            time_stamp = time.time()
            for pr in self.process:
                with pr.oneshot():
                    cpu_usage += function_wrapper(pr.cpu_percent)
                    memory_usage += function_wrapper(lambda: pr.memory_full_info().uss)
                    threads_number += function_wrapper(pr.num_threads)
            self.message_queue.put(f'{time_stamp},{cpu_usage},{memory_usage},{threads_number}')
        except psutil.NoSuchProcess:
            logger.warning(f"Monitored process terminated..")
            logger.warning("Update the process list")
            self.process = get_process_by_name(self.process_name)

    def stop(self):
        self.can_continue = False

    def stop_late(self, time_to_sleep: int):
        threading.Thread(target=sleep_and_execute, args=(time_to_sleep, self.stop)).start()

    def write_to_csv(self):
        write_csv_header(self.csv_file)
        with open(self.csv_file, 'a') as fd:
            while True:
                line = self.message_queue.get()
                fd.write(f'{line}\n')
                self.message_queue.task_done()

    def run(self, collect_in_millisecond: float = 100, time_to_stop: int = None):
        threading.Thread(target=self.write_to_csv, daemon=True).start()
        if time_to_stop is not None:
            self.stop_late(time_to_stop)
        while self.can_continue:
            self.get_stats()
            time.sleep(collect_in_millisecond / 1000)
        self.message_queue.join()
