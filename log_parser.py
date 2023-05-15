import re
import json
import os
import argparse


def get_path_to_log(path, true=None):
    if path != true:
        path = "."
    log_collector = []
    if path[-4:] == ".log":
        return os.path.abspath(path)
    for file in os.listdir(path):
        if file[-4:] == ".log":
            log_collector.append(os.path.abspath(file))
    if log_collector:
        return log_collector
    else:
        return None


def main(path = "."):
    total_stat = {}
    idx = 0
    top_ips = {}
    duration_full = []
    top_third_durability = []
    for log_file in get_path_to_log(path):
        with open(log_file) as f:
            for line in f:
                ip_match = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
                method = re.search(r"(POST|GET|PUT|DELETE|HEAD|OPTIONS)", line)
                duration = re.search(r"\d{4}$", line)
                date = re.search(r"\[.*\]", line)
                url = re.search(r"https?:[a-z0-9-/.?+()+=_&]+", line)
                if ip_match is not None:
                    ip = ip_match.group()
                    if ip in top_ips:
                        top_ips[ip] += 1
                    else:
                        top_ips.update({ip: 1})
                if method is not None:
                    stat = method.group()
                    if stat in total_stat:
                        total_stat[stat] += 1
                    else:
                        total_stat.update({stat: 1})
                if url is not None:
                    url = url.group()
                else:
                    url = "-"
                if date is not None:
                    date = date.group()
                if duration is not None:
                    dur = duration.group()
                    duration_dict = [
                        ("ip", ip),
                        ("date", date),
                        ("method", stat),
                        ("url", url),
                        ("duration", dur)
                    ]
                duration_full.append(duration_dict)
                idx += 1
            sorted_ip = sorted(top_ips.items(), key=lambda x: x[1])
            top_third_count = dict(list(sorted_ip)[-1:-4:-1])
            sorted_by_duration = sorted(duration_full, key=lambda x: x[4][1])
            for data in sorted_by_duration[-1:-4:-1]:
                top_third_durability.append(dict(data))
            total = {
                     "top_ips": top_third_count,
                     "top_longest": top_third_durability,
                     "total_stat": total_stat,
                     "total_requests": idx,
            }

            print(json.dumps(total, indent=4))
            output_file_name = f'{log_file}.result'
            with open(output_file_name, 'w') as out:
                out.write(json.dumps(total, indent=4))
            total.clear()
            top_ips.clear()
            total_stat.clear()
            idx = 0
            top_third_durability.clear()
            duration_full.clear()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process access.log')
    parser.add_argument(dest='path')
    args = parser.parse_args()
    main(args.path)
