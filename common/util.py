from copy import copy
import logging
import logging.config
import sys


def urljoin(*parts):
    if len(parts) == 1:
        return parts[0]
    first = parts[0]
    last = parts[-1]
    middle = parts[1:-1]

    first = first.rstrip('/')
    middle = list(map(lambda s: s.strip('/'), middle))
    last = last.lstrip('/')

    return '/'.join([first] + middle + [last])


class LogFormatter(logging.Formatter):
    level_colors = {
        logging.DEBUG: lambda level_name:
        f'{Bcolors.BOLD}{Bcolors.BLUE}{level_name}{Bcolors.RESET_ALL}',
        logging.INFO: lambda level_name:
        f'{Bcolors.BOLD}{Bcolors.GREEN}{level_name}{Bcolors.RESET_ALL}',
        logging.WARNING: lambda level_name:
        f'{Bcolors.BOLD}{Bcolors.YELLOW}{level_name}{Bcolors.RESET_ALL}',
        logging.ERROR: lambda level_name:
        f'{Bcolors.BOLD}{Bcolors.RED}{level_name}{Bcolors.RESET_ALL}',
    }

    def color_level_name(self, level_name, level_number):
        def default(level_name):
            return str(level_name)

        func = self.level_colors.get(level_number, default)
        return func(level_name)

    def formatMessage(self, record):
        record_copy = copy(record)
        levelname = record_copy.levelname
        if sys.stdout.isatty():
            levelname = self.color_level_name(levelname, record_copy.levelno)
            if "color_message" in record_copy.__dict__:
                record_copy.msg = record_copy.__dict__["color_message"]
                record_copy.__dict__["message"] = record_copy.getMessage()
        record_copy.__dict__["levelprefix"] = levelname
        return super().formatMessage(record_copy)


class Bcolors:
    RESET_ALL = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'


def configure_default_logging(
    stdout_level=None,
    force=True,
    print_thread_id=False,
):
    if not stdout_level:
        stdout_level = logging.INFO

    # make sure to have a clean root logger (in case setup is called multiple times)
    if force:
        for h in logging.root.handlers:
            logging.root.removeHandler(h)
            h.close()

    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setLevel(stdout_level)
    sh.setFormatter(LogFormatter(fmt=default_fmt_string(print_thread_id=print_thread_id)))
    logging.root.addHandler(hdlr=sh)
    logging.root.setLevel(level=stdout_level)


def default_fmt_string(print_thread_id: bool=False):
    ptid = print_thread_id
    return f'%(asctime)s [%(levelprefix)s] {"TID:%(thread)d " if ptid else ""}%(name)s: %(message)s'


def strip_time_str_to_int(
    timeout_str: str,
    ms=False,
    s=False,
    m=False,
    h=False,
    d=False,
) -> int:
    for e in (ms, s, m, h ,d):
        timeout_str = timeout_str.replace(e, '')
    return int(timeout_str)
