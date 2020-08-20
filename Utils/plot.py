from argparse import Namespace
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime
from Utils.util import get_slash


def timestamp_to_datetime(ts: int):
    return datetime.fromtimestamp(ts).strftime('%H:%M:%S')


def convert_timestamp(first_timestamp: int):
    return lambda ts: ts - first_timestamp


def create_options(stats_history, image_prefix, process=None):
    opt = Namespace()
    opt.stats_history = stats_history
    opt.image_prefix = image_prefix
    opt.process = process
    return opt


class PlotPeerCsv(object):
    def __init__(self, autodetect: str, node: str):
        self.autodetect = pd.read_csv(autodetect, sep=',', header=0)
        self.node = pd.read_csv(node, sep=',', header=0)
        convert_fun = convert_timestamp(self.autodetect['Timestamp'].min())
        self.autodetect['Timestamp'] = self.autodetect['Timestamp']\
            .apply(convert_fun)
        convert_fun = convert_timestamp(self.node['Timestamp'].min())
        self.node['Timestamp'] = self.node['Timestamp']\
            .apply(convert_fun)

    def plot(self, column: str, xlabel: str, ylabel: str):
        df_autodetect = self.autodetect[self.autodetect['Name'] == 'Aggregated']
        df_node = self.node[self.node['Name'] == 'Aggregated']
        _, ax = plt.subplots(figsize=(10, 8))

        ax.plot(df_autodetect['Timestamp'], df_autodetect[column], marker=',', label=f'Dotnet {column}')
        ax.plot(df_node['Timestamp'], df_node[column], marker=',', label=f'Node {column}')

        ax.legend(loc=1)
        ax.set(title=f"{column}",
               xlabel=xlabel,
               ylabel=ylabel)
        if len(df_autodetect.index) > 10:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(len(df_autodetect.index) / 10))
        plt.setp(ax.get_xticklabels(), rotation=45)
        plt.show()
        pass

    def plot_80(self):
        self.plot('80%', "Time", "Response Time", )

    def plot_90(self):
        self.plot('90%', "Time", "Response Time", )

    def plot_95(self):
        self.plot('95%', "Time", "Response Time", )

    def plot_99(self):
        self.plot('99%', "Time", "Response Time", )

    def plot_median(self):
        self.plot('Total Median Response Time', "Time", "Response Time", )


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
        df = self.stats_history[self.stats_history['Name'] == 'Aggregated']
        _, ax = plt.subplots(figsize=(10, 8))
        ax.plot(df['Timestamp'], df['Requests/s'], marker=',', label='Requests/s')

        ax.plot(df['Timestamp'], df['Failures/s'], marker=',', label='Failures/s')
        ax.legend(loc=1)
        ax.set(title="RPS Over Time",
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

    def plot_threads_used(self):
        df = self.process
        _, ax = plt.subplots(figsize=(10, 8))
        ax.plot(df['Timestamp'], df['Threads Number'], marker=',')
        ax.set(title="Threads Count Over Time",
               xlabel="Time",
               ylabel="Threads number")
        if len(df.index) > 10:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(len(df.index) / 100))
        plt.setp(ax.get_xticklabels(), rotation=45)
        plt.savefig(f'{self.options.image_prefix}_threads.png')

    def plot_response_time(self):
        df = self.stats_history[self.stats_history['Name'] == 'Aggregated']
        _, ax = plt.subplots(figsize=(10, 8))
        ax.plot(df['Timestamp'], df['Total Median Response Time'], marker=',', label='Total Median Response Time')

        ax.plot(df['Timestamp'], df['95%'], marker=',', label='95%')
        ax.legend(loc=1)
        ax.set(title="Response Time Over Time",
               xlabel="Time",
               ylabel="Response Time")
        if len(df.index) > 10:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(len(df.index) / 10))
        plt.setp(ax.get_xticklabels(), rotation=45)
        plt.savefig(f'{self.options.image_prefix}_response_time.png')

    def plot_tile(self):
        df = self.stats_history[self.stats_history['Name'] == 'Aggregated']
        _, ax = plt.subplots(figsize=(10, 8))
        ax.plot(df['Timestamp'], df['99%'], marker=',', label='99%')
        ax.plot(df['Timestamp'], df['95%'], marker=',', label='95%')
        ax.plot(df['Timestamp'], df['90%'], marker=',', label='90%')
        ax.plot(df['Timestamp'], df['80%'], marker=',', label='80%')
        ax.plot(df['Timestamp'], df['50%'], marker=',', label='50%')
        ax.legend(loc=1)
        ax.set(title="Response Time Over Time",
               xlabel="Time",
               ylabel="Response Time")
        if len(df.index) > 10:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(len(df.index) / 10))
        plt.setp(ax.get_xticklabels(), rotation=45)
        plt.savefig(f'{self.options.image_prefix}_tile.png')

    def run(self):
        if self.process is not None:
            self.plot_cpu()
            self.plot_memory()
        #self.plot_user_count()
        self.plot_qps()
        self.plot_threads_used()
        self.plot_response_time()
        self.plot_tile()


if __name__ == '__main__':
    #options = create_options('../Data/2020-08-20_11-40-46_100_AutoDetect_stats_history.csv',
    #                         '../Data/2020-08-20_11-40-46_100_AutoDetect',
    #                         '../Data/2020-08-20_11-40-46_100_AutoDetect_process.csv')
    #pc = PlotCsv(options)
    #pc.run()
    ps = PlotPeerCsv('../Data/2020-08-20_11-40-46_100_AutoDetect_stats_history.csv',
                     '../Data/2020-08-06_16-07-42_100_node_stats_history.csv')
    ps.plot_80()
    ps.plot_90()
    ps.plot_95()
    ps.plot_99()
    #ps.plot_median()
    #2020-08-06_13-25-31_100_AutoDetect_stats_history.csv
    #2020-08-06_16-07-42_100_node_stats_history.csv
    pass

