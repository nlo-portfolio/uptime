#!/usr/bin/env python

import curses
import logging
import os
import queue
import requests
import socket
import sys
import threading
import time
import yaml
from collections import deque
from queue import Queue

from classes import Site
from modules import request_worker


def parse_config(filename):
    '''
    Opens and loads the yaml configuration file for reading and returns the configuration as a dictionary.
    
    Paramaters:
        filename  (str):  filename for the configuration file.
        
    Returns:
        dict: contains the keys and values for the configuration.
    '''
    with open(filename, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)

def print_and_log_sites(config, logger, stdscr, temp_deque):
    """
    Output site status to string and log to failures to file.
    
    Parameters:
        config      (dict):    configuration to be used.
        logger      (logger):  logging object to be used.
        stdscr      (curses):  curses screen object to be used.
        temp_deque  (deque):   deque of sites to display.
    """
    try:
        stdscr.erase()
        stdscr.addstr("               Site              -  Status  -  Uptime Average\n")
        stdscr.addstr("--------------------------------------------------------------\n")

        for site in temp_deque:
            # Form first part of site output string.
            blank_space = (32 - len(site.url)) * ' '
            site_title = '{}{} -   '.format(site.url[:29] + (site.url[29:] and '...'), blank_space)
            stdscr.addstr(site_title)

            # Form second part of site output string.
            if site.status:
                stdscr.addstr(' UP    -  Uptime: ')
            else:
                stdscr.addstr('DOWN', curses.A_BLINK)
                stdscr.addstr('   -  Uptime: ')

            # Form third part of site output string.
            if site.uptime_avg > config['env']['uptime_threshhold']:
                stdscr.addstr("{:.2f}%\n".format(round(site.uptime_avg * 100, 2)))
            else:
                stdscr.addstr("{:.2f}%\n".format(round(site.uptime_avg * 100, 2)), curses.A_BLINK)

        stdscr.addstr("------------------------------------------------------------\n")
        stdscr.addstr("Last updated: {}\n".format(
            time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())))
        stdscr.addstr('Press <CTRL> + C to exit.')
        stdscr.refresh()
    except curses.error as e:
        stdscr.clear()
        stdscr.addstr('Enlarge window to display data...')
        stdscr.refresh()


def main():
    """
    Main driver for the program: sets up the config, logger, site objects, and worker threads.
    Also starts the main refresh loop which runs until the program exits, which continuously
    passes site objects to the worker threads, waits for their return and outputs their status.
    
    Parameters:
        None
    """
    logging.basicConfig(filename='log/uptime_-_{}.log'.format(time.strftime("%M-%d-%Y:%H:%M:%S", time.localtime())),
                        filemode='w+',
                        level=logging.WARNING)
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    config = parse_config('config.yml')
    thread_list = []
    queue_in = Queue(maxsize=len(config['sites']))
    queue_out = Queue(maxsize=len(config['sites']))
    stdscr = curses.initscr()

    # Append sites to the queue_in.
    Site.Site.set_alpha_sort(config['env']['alphabetize'])
    for id, site_url in enumerate(config['sites']):
        queue_in.put(Site.Site(id, site_url))

    # Start worker threads.
    for i in range(config['env']['num_threads']):
        thread = threading.Thread(target=request_worker.run, args=(config, queue_in, queue_out), daemon=True)
        thread_list.append(thread)
        thread.start()

    stdscr.erase()
    stdscr.addstr('Waiting for initial responses...')
    stdscr.refresh()

    # Start main refresh loop.
    try:
        while True:
            # Wait for queue_in to be empty and queue_out to be full.
            while True:
                if queue_in.empty() and queue_out.full():
                    break
                else:
                    time.sleep(0.05)

            print_and_log_sites(config, logger, stdscr, sorted(deque(queue_out.queue)))
            time.sleep(int(config['env']['refresh_normal']))

            # Re-add sites to queue_in for processing by the workers.
            while not queue_out.empty():
                queue_in.put(queue_out.get())

    except KeyboardInterrupt:
        stdscr.clear()
        stdscr.addstr("\nExiting...\n")
        stdscr.refresh()
    except Exception as e:
        logger.error('Exception encountered: {}'.format(e))
        raise e


if __name__ == '__main__':
    main()
