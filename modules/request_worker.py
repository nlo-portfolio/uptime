#!/usr/bin/env python

import requests
import time

from queue import Queue


def send_request(site_url):
    """
    Output site status to string and log to failures to file.
    
    Parameters:
        site_url  (str):  fqdn of the site to be contacted.
        
    Returns:
        bool: boolean indicating success (true) or failure (false).
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1", "DNT": "1", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate"}
    try:
        r = requests.get(site_url, headers=headers)
    except requests.exceptions.RequestException as e:
        return False
    return True if r.status_code == 200 else False

def run(config, queue_in, queue_out):
    """
    Runs the worker thread as an infinite loop, sending requests and updating
    the objects before placing them back in the outgoing queue.
    
    Parameters:
        config     (dict):         config object to be used.
        queue_in   (queue.Queue):  queue for sites being passed out to workers.
        queue_out  (queue.Queue):  queue for sites being passed back to main.
    """
    while True:
        site = queue_in.get()
        if send_request(site.url):
            site.update_site(True)
            queue_out.put(site)
        else:
            site.update_site(False)
            queue_out.put(site)
        queue_in.task_done()
