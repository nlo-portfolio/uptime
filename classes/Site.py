#!/usr/bin/env python

import time


class Site(object):
    '''
    Class used to track the status of a website (site).
    
    Attributes:
        sort_alphabetic  (bool):         class variable for to determine sort type.
        id               (int):          id used for ordering based on creation (order in config).
        url              (str):          fqdn url of the site.
        status           (bool):         current status of the site (True == up, False == down)
        last_success     (time object):  local time of last successful request to the site.
        last failure     (time object):  local time of last failed request to the site.
        uptime_avg       (float):        current average for site uptime.
        total_successes  (int):          total number of successful requests (used for computing uptime_avg).
        total_failures   (int):          total number of failed requests (used for computing uptime_avg).
        state_change     (bool):         used for tracking recent state changes for alerts (deprecated).
    '''

    ''' Used for sorting either alphabetically or numerically by id (lower is higher priority). '''
    sort_alphabetic = None

    def __init__(self, id, url, status=True):
        """
        Class constructor.
        
        Parameters:
            id      (int):   id used for ordering based on creating (order in config).
            url     (str):   fqdn url of the site.
            status  (bool):  indicates whether the site is currently up or down.
        """
        self.id = id
        self.url = url
        self.status = status
        self.last_success = None
        self.last_failure = None
        self.uptime_avg = 0.0
        self.total_successes = 0
        self.total_failures = 0
        self.state_change = False

    def update_site(self, site_update):
        """
        Updates a number of site metrics after each request.
        
        Parameters:
            site_update  (bool):  indicates whether the site is currently up or down.
        """
        if site_update:
            self.state_change = True if not self.status else False
            self.status = True
            self.total_successes += 1
            self.last_success = time.time()
        else:
            self.state_change = False if self.status else True
            self.status = False
            self.total_failures += 1
            self.last_failure = time.time()
        self.update_uptime_avg()

    def update_uptime_avg(self):
        """
        Compute the site uptime average based on total successes and failures.
        
        Parameters:
            None
        """
        self.uptime_avg = (self.total_successes / (self.total_successes + self.total_failures))

    def __gt__(self, other):
        """
        Defines a greater than comparator for Site objects (used for sorting).
        Can compare alphabetically or by object id (assigned at creation in ascending order).
        
        Parameters:
            other  (Site):  the other object to compare against.
            
        Returns:
            bool: true if the other object has less priority alphabetically or by id (higher is lower).
        """
        if Site.sort_alphabetic:
            return True if self.url > other.url else False
        return True if self.id > other.id else False

    def __lt__(self, other):
        """
        Defines a less than comparator for Site objects (used for sorting).
        Can compare alphabetically or by object id (assigned at creation in ascending order).
        
        Parameters:
            other  (Site):  the other object to compare against.
            
        Returns:
            bool: true if the other object has less priority alphabetically or by id (lower is higher).
        """
        if Site.sort_alphabetic:
            return True if self.url < other.url else False
        return True if self.id < other.id else False

    def __str__(self):
        """
        Default print method for Site objects.
        
        Parameters:
            None
            
        Returns:
            str: string with relevant site details.
        """
        space = (32 - len(self.url)) * ' '
        status_str = '  UP  ' if self.status else ' DOWN '
        return '{}{} -  {}  -  Uptime: {}'.format(self.url[:29] + (self.url[29:] and '...'),
                                                  space, status_str, self.uptime_avg)

    @classmethod
    def set_alpha_sort(cls, alphabetic=True):
        """
        Set the sort method for all class instances. Alphabetic if True, otherwise the
        original ordering in the configuration file will be used if False.
        
        Parameters:
            alphabetic  (bool):  alphabetic (true) or in config order (false).
        """
        cls.sort_alphabetic = alphabetic
