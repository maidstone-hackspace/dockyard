#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import os, sys

sys.path.insert(0, os.path.abspath('../'))
from libs import utils


class TestBasePage(unittest.TestCase):
    def test_user_in_group(self):
        self.assertTrue(utils.test_in_group())
        
        with self.assertRaises(SystemExit) as sys_exit:
            utils.test_in_group('fake_docker_group')
        self.assertEqual(sys_exit.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
