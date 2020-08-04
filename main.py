import argparse
import os
import logging
import threading
from Utils.util import get_slash
from Users.access_log_user import AccessLogUser
from locust_runner import LocustRunner
from process_monitor import ProcessMonitor
from locust.log import setup_logging


def config_argument_parser():
    parser = argparse.ArgumentParser(description='Tool to send http request and monitor the server process')
    parser.add_argument('--target_server_address', help='Http server to send the request', required=True)
    parser.add_argument('--process_pid', help='Target process to monitor on')
    parser.add_argument('--process_name', help='Target process to monitor on')
    parser.add_argument('--collect_time_in_second', help='Total time to run', default=60, type=float)
    parser.add_argument('--locust_csv_prefix', help='locust csv prefix')
    parser.add_argument('--total_user', help='Amount user to simulate', default=100, type=int)
    parser.add_argument('--hatch_rate', help='User hatch rate', default=10, type=int)
    parser.add_argument('--should_start_web_ui', help='Should start web ui for locust', default=False)

    arguments = parser.parse_args()
    if not (arguments.process_pid or arguments.process_name):
        parser.error('Process needed, add --process_pid or --process_name')
    if not arguments.target_server_address.startswith("http://"):
        parser.error('Target server address should  start with http://')
    if not arguments.locust_csv_prefix:
        if arguments.process_name is not None:
            arguments.locust_csv_prefix = get_default_locust_csv_prefix(arguments.process_name)
        else:
            arguments.locust_csv_prefix = get_default_locust_csv_prefix(arguments.procsee_pid)
    return arguments


def get_default_locust_csv_prefix(process_name_or_pid):
    return f'{os.path.dirname(os.path.realpath(__file__))}{get_slash()}{process_name_or_pid}'


def get_default_process_monitor_csv_prefix(name, pid):
    if name is None:
        return f'{os.path.dirname(os.path.realpath(__file__))}{get_slash()}{pid}_process.csv'
    else:
        return f'{os.path.dirname(os.path.realpath(__file__))}{get_slash()}{name}_process.csv'


def run_locust(locust_runner: LocustRunner, options):
    logger = logging.getLogger(__name__)
    logger.info('Start the locust runner..')
    if options.should_start_web_ui:
        locust_runner.start_web_ui()
    locust_runner.run(options.total_user,
                      options.hatch_rate,
                      options.collect_time_in_second,
                      options.locust_csv_prefix)
    locust_runner.wait_runner()
    if options.should_start_web_ui:
        locust_runner.stop_web_ui()


def run_process_monitor(process_monitor: ProcessMonitor, options):
    logger = logging.getLogger(__name__)
    logger.info('Start the process runner..')
    process_monitor.run(time_to_stop=options.collect_time_in_second)
    pass


if __name__ == '__main__':
    setup_logging('INFO')
    args = config_argument_parser()
    logger = logging.getLogger(__name__)
    locust_runner = LocustRunner(args.target_server_address, AccessLogUser)
    try:
        process_monitor = ProcessMonitor(pid=args.process_pid,
                                         name=args.process_name,
                                         csv_file=get_default_process_monitor_csv_prefix(args.process_pid,
                                                                                         args.process_name))
        process_monitor_task = threading.Thread(target=run_process_monitor, args=(process_monitor, args))
        process_monitor_task.start()
    except:
        logger.warning('Cannot find target process')
        logger.warning('Will not run process monitor')
        process_monitor_task = None
        pass
    locust_task = threading.Thread(target=run_locust, args=(locust_runner, args))
    locust_task.start()
    locust_task.join()
    if process_monitor_task is not None:
        process_monitor_task.join()
    logger.info("Load test done")

