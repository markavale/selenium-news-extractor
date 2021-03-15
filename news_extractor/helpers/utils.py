import time, os, timezone, datetime

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