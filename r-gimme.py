#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup, SoupStrainer
import requests
import sys

import os
import shlex
import struct
import platform
import subprocess


# get_terminal_size and related functionality from:
# https://gist.github.com/jtriley/1108174#file-terminalsize-py
def get_terminal_size():
    """ getTerminalSize()
     - get width and height of console
     - works on linux,os x,windows,cygwin(windows)
     originally retrieved from:
     http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        tuple_xy = (80, 25)  # default value
    return tuple_xy


def _get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except:
        pass


def _get_terminal_size_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return cols, rows
    except:
        pass


def _get_terminal_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh',
                               fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            return cr
        except:
            pass

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])


def get_links(url):
    hrefs = []
    try:
        page = requests.get(url)
        data = page.text
        soup = BeautifulSoup(data, "html.parser")

        for link in soup.find_all('a'):
            if link.get('href') is not None:

                if link.get('href')[0] == "/":
                    hrefs.append(url + link.get('href'))
                elif link.get('href')[0] == "#":
                    hrefs.append(url + "/" + link.get('href'))
                else:
                    hrefs.append(link.get('href'))
        return hrefs
    except:
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("urls", nargs="+", type=str)
    parser.add_argument("--output_file", type=str)

    args = parser.parse_args()

    columns = get_terminal_size()[0]

    separator = '-' * columns

    for url in args.urls:
        print("\n" + separator)
        print("Getting links from: " + url + "\n")

        links = get_links(url)
        if links is None:
            if not url.startswith("http://") or url.startswith("https://"):
                print(f"{url} failed.")
                url = "http://" + url
                print(f"Changed URL to {url}, trying again.\n")
                links = get_links(url)
        else:
            sys.exit("ERROR: Not valid URL -->: " + url)

        if args.output_file:
            print(f"Writing results to {args.output_file}.")
            with open(args.output_file, "w+") as output_file:
                output_file.writelines((link + "\n" for link in links))
        else:
            for link in links:
                print(link)
        print("\n" + separator + "\n")
