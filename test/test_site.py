#!/usr/bin/env python

import time
import unittest

from classes import Site


class TestSite(unittest.TestCase):

    def setUp(self):
        self.site_one = Site.Site(1, 'https://www.google.com')
        self.site_two = Site.Site(2, 'https://www.yahoo.com')
        self.site_three = Site.Site(3, 'https://www.microsoft.com')

    def tearDown(self):
        pass

    def test_update_site_pass(self):
        self.assertTrue(self.site_one.status)
        self.assertEqual(self.site_one.uptime_avg, 0.0)
        self.assertEqual(self.site_one.last_success, None)
        self.assertEqual(self.site_one.last_failure, None)
        self.assertEqual(self.site_one.uptime_avg, 0.0)
        self.assertEqual(self.site_one.total_successes, 0)
        self.assertEqual(self.site_one.total_failures, 0)
        self.assertFalse(self.site_one.state_change)

        self.site_one.update_site(False)

        self.assertFalse(self.site_one.status)
        self.assertEqual(self.site_one.last_success, None)
        self.assertLess(self.site_one.last_failure, time.time())
        self.assertEqual(self.site_one.uptime_avg, 0.0)
        self.assertEqual(self.site_one.total_successes, 0)
        self.assertEqual(self.site_one.total_failures, 1)
        self.assertFalse(self.site_one.state_change)

        self.site_one.update_site(True)

        self.assertTrue(self.site_one.status)
        self.assertLess(self.site_one.last_success, time.time())
        self.assertLess(self.site_one.last_failure, time.time())
        self.assertEqual(self.site_one.uptime_avg, 0.5)
        self.assertEqual(self.site_one.total_successes, 1)
        self.assertEqual(self.site_one.total_failures, 1)
        self.assertTrue(self.site_one.state_change)

    def test_update_uptime_avg_pass(self):
        self.site_one.total_successes = 1
        self.site_one.total_failures = 1
        self.site_one.update_uptime_avg()
        self.assertEqual(self.site_one.uptime_avg, 0.5)

    def test_lt_comp_alpha_pass(self):
        Site.Site.set_alpha_sort()
        self.assertLess(self.site_one, self.site_two)
        self.assertLess(self.site_three, self.site_two)

    def test_gt_comp_alpha_pass(self):
        Site.Site.set_alpha_sort()
        self.assertGreater(self.site_two, self.site_one)
        self.assertGreater(self.site_three, self.site_one)

    def test_lt_comp_non_alpha_pass(self):
        Site.Site.set_alpha_sort(False)
        self.assertLess(self.site_one, self.site_two)
        self.assertLess(self.site_two, self.site_three)

    def test_gt_comp_non_alpha_pass(self):
        Site.Site.set_alpha_sort(False)
        self.assertGreater(self.site_two, self.site_one)
        self.assertGreater(self.site_three, self.site_two)

    def test_str_pass(self):
        self.assertEqual(str(self.site_one), 'https://www.google.com           -    UP    -  Uptime: 0.0')

    def test_set_sort_pass(self):
        self.assertFalse(self.site_one.sort_alphabetic)
        Site.Site.set_alpha_sort(True)
        self.assertTrue(self.site_one.sort_alphabetic)
        Site.Site.set_alpha_sort(False)
        self.assertFalse(self.site_one.sort_alphabetic)


if __name__ == '__main__':
    unittest.main()
