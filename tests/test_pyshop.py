#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pyshop
----------------------------------

Tests for `pyshop` module.
"""

import logging
import sys
import threading
import unittest

from pyshop import utils


class TestPyshop(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_001_threads(self):
        def test_thread(e):
            e.wait()

        ts = utils.running_threads()
        self.assertEqual(len(ts), 0)

        e = threading.Event()
        t = threading.Thread(target=test_thread, args=(e, ))
        t.start()

        ts = utils.running_threads()
        self.assertEqual(len(ts), 1)

        e.set()
        t.join()

        ts = utils.running_threads()
        self.assertEqual(len(ts), 0)

    def test_002_loggers(self):
        ls = utils.loggers()
        self.assertEqual(len(ls), 0)

        logger = logging.getLogger('test')

        ls = utils.loggers()
        self.assertEqual(len(ls), 1)
        self.assertEqual(ls[0].name, 'test')






if __name__ == '__main__':
    sys.exit(unittest.main())
