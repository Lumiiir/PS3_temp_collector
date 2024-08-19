import argparse
from pathlib import Path
import requests
import re
import time
import csv
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


def plot_graph(path, title):
    cpu = []
    rsx = []
    time_sec = []

    with open(f"{path}/{title}.csv", 'r') as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            time_sec.append(row[0])
            cpu.append((row[1]))
            rsx.append(row[2])

    plt.plot(time_sec, cpu, label='CPU')
    plt.plot(time_sec, rsx, label='RSX')
    plt.xlabel('Time')
    plt.ylabel('Temp C')
    plt.title(f"CPU and RSX temps| Fan {row[3]}%")
    plt.legend()
    plt.savefig(f"{path}/{title}.svg")


def collect_data(ip_addr, title, path, duration, interval):
    url = f"http://{ip_addr}/cpursx.ps3?/sman.ps3"
    start_time = time.time()

    with open(f"{path}/{title}.csv", 'w', encoding='UTF-8') as f:
        writer = csv.writer(f)
        writer.writerow(['TIME', 'CPU', 'RSX', 'FAN'])
        while True:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')

            data = soup.find('a', class_='s', href='/cpursx.ps3?up').get_text()
            timestamp = int(time.time() - start_time)
            cpu_temp = re.search(r'CPU:\s(\d+)°C', data).group(1)
            rsx_temp = re.search(r'RSX:\s(\d+)°C', data).group(1)
            fan_speed = re.search(r'FAN:\s(\d+)%', data).group(1)

            print(f"CPU: {cpu_temp} °C, RSX: {rsx_temp} °C, FAN: {fan_speed} %")
            writer.writerow([timestamp, cpu_temp, rsx_temp, fan_speed])
            if time.time() - int(start_time) > int(duration): break
            time.sleep(int(interval))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', type=str, required=True,
                        help='Measurement title. This will be used as file name.')
    parser.add_argument('-d', '--description', type=str, required=False,
                        help='Description which will be added into output.')
    parser.add_argument('-o', '--output-path', type=str, default='./data/',
                        help='Output path directory')
    parser.add_argument('-a', '--ip-addr', type=str, required=True,
                        help='IP address of PS3 webman UI')
    parser.add_argument('-t', '--time', default=1800, type=str,
                        help='Collect duration in seconds')
    parser.add_argument('-i', '--interval', default=10, type=str,
                        help='Collection interval in seconds')

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    output_path = Path(args.output_path)
    if not output_path.exists():
        raise FileNotFoundError(f'Output path does not exist: {args.output_path}')
    collect_data(ip_addr=args.ip_addr, title=args.name, path=output_path, duration=args.time, interval=args.interval)
    plot_graph(path=args.output_path, title=args.name)


if __name__ == "__main__":
    main()
