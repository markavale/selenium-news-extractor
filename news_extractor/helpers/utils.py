import time, os, datetime, json
from urllib.parse import urlparse

# def time_in_range(start, end, x):
#     today = timezone.localtime().date()
#     start = timezone.make_aware(datetime.datetime.combine(today, start))
#     end = timezone.make_aware(datetime.datetime.combine(today, end))
#     x = timezone.make_aware(datetime.datetime.combine(today, x))
#     if end <= start:
#         end += datetime.timedelta(days=1) # tomorrow!
#     if x <= start
#         x += datetime.timedelta(days=1) # tomorrow!
#     return start <= x <= end

def time_in_range(start, end, x):
    """Return False if x is in the range [start, end]"""

    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def get_host_name(url):
    parsed_uri = urlparse(str(url))
    host_name = '{uri.netloc}'.format(uri=parsed_uri)
    clear_url = host_name.replace(r'www.', '').strip()
    return clear_url


### MAIN SCRAPER FUNCTION ###
def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)

def __total_data_and_workers(_data, _workers):
    return len(_data), _workers

def delete_all_logs(info_path, debug_path, error_path, json_path):
    with open(str(info_path), 'w') as info_file, open(str(debug_path), 'w') as debug_file, open(str(error_path), 'w') as erorr_file, open(str(json_path), 'w') as json_file:
        info_file.write("")
        debug_file.write("")
        erorr_file.write("")
        json_file.write("")

def save_all_logs(info_path, debug_path, error_path, json_path):
    info_log    = []
    debug_log   = []
    error_log   = []
    json_log    = []
    with open(str(info_path), 'r') as info_file, open(str(debug_path), 'r') as debug_file, open(str(error_path), 'r') as erorr_file, open(str(json_path)) as json_file:
        [info_log.append(line) for line in info_file]
        [debug_log.append(line) for line in debug_file]
        [error_log.append(line) for line in erorr_file]
        [json_log.append(json.loads(line)) for line in json_file]

    return info_log, debug_log, error_log, json_log
