#!/usr/bin/env python

import responses
import threading
import unittest
import yaml
from unittest import mock
from queue import Queue


from classes import Site
from modules import request_worker


class TestRequestWorker(unittest.TestCase):

    def setUp(self):
        self.site_one = Site.Site(1, 'https://www.google.com')
        self.site_two = Site.Site(2, 'https://www.yahoo.com')
        self.site_three = Site.Site(3, 'https://www.microsoft.com')
        with open('config.yml', 'r') as stream:
            self.config = yaml.safe_load(stream)

    def tearDown(self):
        pass

    @responses.activate
    def test_send_request_pass(self):
        responses.add(responses.GET, self.site_one.url, body='{}', status=200)
        response = request_worker.send_request(self.site_one.url)
        self.assertTrue(response)

    @responses.activate
    def test_send_request_fail(self):
        responses.add(responses.GET, self.site_one.url, status=404)
        response = request_worker.send_request(self.site_one.url)
        self.assertFalse(response)

    @mock.patch('modules.request_worker.send_request', return_value=True)
    def test_run_pass(self, response):
        queue_in = Queue()
        queue_out = Queue()
        queue_in.put(self.site_one)
        queue_in.put(self.site_two)
        queue_in.put(self.site_three)
        thread = threading.Thread(target=request_worker.run, args=(self.config, queue_in, queue_out), daemon=True)
        thread.start()
        site_one = queue_out.get()
        site_two = queue_out.get()
        site_three = queue_out.get()
        self.assertTrue(site_one.status)
        self.assertTrue(site_one.status)
        self.assertTrue(site_one.status)


if __name__ == '__main__':
    unittest.main()
