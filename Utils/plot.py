from argparse import Namespace
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime
from Utils.util import get_slash


def timestamp_to_datetime(ts: int):
    return datetime.fromtimestamp(ts).strftime('%H:%M:%S')


def create_options(stats_history, image_prefix, process=None):
    opt = Namespace()
    opt.stats_history = stats_history
    opt.image_prefix = image_prefix
    opt.process = process
    return opt


class PlotCsv(object):
    def __init__(self, options):
        self.stats_history = pd.read_csv(options.stats_history, sep=',', header=0)
        self.stats_history['Timestamp'] = self.stats_history['Timestamp'].apply(timestamp_to_datetime)
        self.options = options
        if options.process is not None:
            self.process = pd.read_csv(options.process, sep=',', header=0)
            self.process['Timestamp'] = self.process['Timestamp'].apply(timestamp_to_datetime)
        else:
            self.process = None

    def plot_user_count(self):
        df = self.stats_history
        _, ax = plt.subplots(figsize=(10, 8))
        ax.plot(df['Timestamp'], df['User Count'], marker=',')
        ax.set(title="Users Over Time",
               xlabel="Time",
               ylabel="Users")
        if len(df.index) > 10:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(len(df.index) / 10))
        plt.setp(ax.get_xticklabels(), rotation=45)
        plt.savefig(f'{self.options.image_prefix}_user.png')

    def plot_qps(self):
        df = self.stats_history
        _, ax = plt.subplots(figsize=(10, 8))
        ax.plot(df['Timestamp'], df['Requests/s'], marker=',', label='Requests/s')

        ax.plot(df['Timestamp'], df['Failures/s'], marker=',', label='Failures/s')
        ax.legend(loc=1)
        ax.set(title="RPS over time",
               xlabel="Time",
               ylabel="RPS")
        if len(df.index) > 10:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(len(df.index) / 10))
        plt.setp(ax.get_xticklabels(), rotation=45)
        plt.savefig(f'{self.options.image_prefix}_qps.png')

    def plot_cpu(self):
        df = self.process
        _, ax = plt.subplots(figsize=(10, 8))
        ax.plot(df['Timestamp'], df['Cpu Usage'], marker=',')
        ax.set(title="CPU Usage Over Time",
               xlabel="Time",
               ylabel="CPU Using rate")
        if len(df.index) > 10:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(len(df.index) / 100))
        ax.yaxis.set_major_formatter(ticker.PercentFormatter())
        plt.setp(ax.get_xticklabels(), rotation=45)
        plt.savefig(f'{self.options.image_prefix}_cpu.png')

    def plot_memory(self):
        df = self.process
        df['Memory Usage'] = df['Memory Usage'].apply(lambda x: x / 1024 / 1024)
        _, ax = plt.subplots(figsize=(10, 8))
        ax.plot(df['Timestamp'], df['Memory Usage'], marker=',')
        ax.set(title="Memory Usage Over Time",
               xlabel="Time",
               ylabel="memory usage")
        if len(df.index) > 10:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(len(df.index) / 100))

        plt.setp(ax.get_xticklabels(), rotation=45)
        plt.savefig(f'{self.options.image_prefix}_memory.png')

    def run(self):
        if self.process is not None:
            self.plot_cpu()
            self.plot_memory()
        self.plot_user_count()
        self.plot_qps()


if __name__ == '__main__':
    options = create_options('../node_stats_history.csv', '../test', '../node_process.csv')
    pc = PlotCsv(options)
    pc.run()
