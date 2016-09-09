#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import os, sys

sys.path.insert(0, os.path.abspath('../'))
from libs import utils


class TestBasePage(TestUtils):
    def test_local_search(self):
        utils.return_browsers()


if __name__ == '__main__':
    unittest.main()
