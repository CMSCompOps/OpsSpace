#! /usr/bin/env python

"""
``test/test_unmerged_cleaner.py`` performs the unit tests for the :ref:`unmerged-ref`.
The script can take two optional arguments for testing for the file system at your site.

- The first argument is the location of the directory to be tested.
  This should be a directory that does not exist,
  and it should be in a location managed by the filesystem to test.
- The second argument is the type of filesystem testing for.
  See **STORAGE_TYPE** under :ref:`listdel-config-ref` for the currently supported file system types.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""

from __future__ import print_function

import os
import sys
import unittest
import random
import uuid
import testfixtures
import time
import shutil

import cmstoolbox._loadtestpath
from cmstoolbox.unmergedcleaner import listdeletable


listdeletable.set_config()
# Check if the place to do the test is already used or not
unmerged_location = listdeletable.config.UNMERGED_DIR_LOCATION


if os.path.exists(unmerged_location):
    print('Path %s already exists. Refusing to do unit tests.' % 
          unmerged_location)
    exit()
else:
    print('Running test at %s' % unmerged_location)


protected_list = ['protected1', 'dir/that/is/protected', 'delete/except/protected']
listdeletable.PROTECTED_LIST = [os.path.join(listdeletable.config.LFN_TO_CLEAN, protected) \
                                    for protected in protected_list]
listdeletable.PROTECTED_LIST.sort()
listdeletable.PROTECTED_UPPER_DIRS = set()
listdeletable.ALL_LENGTHS = list(set(
        len(protected) for protected in listdeletable.PROTECTED_LIST))
listdeletable.ALL_LENGTHS.sort()


class TestUnmergedFunctions(unittest.TestCase):

    def test_search_numbers(self):
        test_list = random.sample(range(1000), 100)
        test_list.sort()

        for i in range(10):
            element = test_list[int(random.random() * len(test_list))]
            self.assertEqual(listdeletable.bi_search(test_list, element),
                             True, 'bi_search did not find number when it should.')

            popped = test_list.pop(int(random.random() * len(test_list)))
            self.assertEqual(listdeletable.bi_search(test_list, popped),
                             False, 'bi_search found a number when it should not.')

    def test_search_strings(self):
        test_list = list(set(str(uuid.uuid4()) for i in range(1000)))
        test_list.sort()

        for i in range(100):
            element = test_list[int(random.random() * len(test_list))]
            self.assertEqual(listdeletable.bi_search(test_list, element),
                             True, 'bi_search did not find string when it should.')

            popped = test_list.pop(int(random.random() * len(test_list)))
            self.assertEqual(listdeletable.bi_search(test_list, popped),
                             False, 'bi_search found a string when it should not.')

    def test_get_protected(self):
        if os.environ.get('TRAVIS'):
            # Can't run this test on Travis-CI due to certificate
            return

        protected = listdeletable.get_protected()
        self.assertTrue(isinstance(protected, list), 'Protected list is not a list.')
        self.assertNotEqual(len(protected), 0, 'Protected list is empty.')
        for one_dir in protected:
            self.assertTrue(one_dir.startswith('/store/'),
                            'Protected directory %s does not have expected LFN.' % one_dir)


class TestUnmergedFileChecks(unittest.TestCase):

    tmpdir = None

    def setUp(self):
        self.tmpdir = testfixtures.TempDirectory(path=unmerged_location)

    def tearDown(self):
        self.tmpdir.cleanup()
        if os.path.exists(unmerged_location):
            shutil.rmtree(unmerged_location)

    def test_size(self):
        for log_size in range(1, 7):
            size = 10 ** log_size
            tmp_file = self.tmpdir.write('size/file_{0}'.format(size),
                                         bytearray(os.urandom(size)))

            self.assertEqual(listdeletable.get_file_size(tmp_file), size,
                             'get_file_size is returning wrong value -- %s for %s.' %
                             (listdeletable.get_file_size(tmp_file), size))

    def test_time(self):
        print('Testing timing. Will take a few seconds.')
        start_time = time.time()
        time.sleep(2)
        tmp_file = self.tmpdir.write('time/file.txt', 'Testing time since created.'.encode())
        time.sleep(2)
        after_create = time.time()

        self.assertTrue(listdeletable.get_mtime(tmp_file) >= int(start_time),
                        'File appears older than it actually is.')

        self.assertTrue(listdeletable.get_mtime(tmp_file) <= int(after_create),
                        'File appears newer than it actually is.')

    def do_deletion(self, delete_function):
        # Pass a function that does the deletion

        to_delete = ['delete/not/protected', 'dir/to/delete', 'make/a/dir/to/delete', 'hello/delete']
        touched_new = ['touch/this']
        too_new = ['hello/new', 'new']
        all_dirs = to_delete + too_new + touched_new + \
            listdeletable.config.DIRS_TO_AVOID + protected_list

        start_time = time.time()
        for next_dir in all_dirs:
            if next_dir not in too_new:
                self.tmpdir.write(os.path.join(next_dir, 'test_file.root'),
                                  bytearray(os.urandom(1024)))

        print('Waiting for some time.')

        time.sleep(5)
        cutoff_time = int(time.time())
        time.sleep(5)

        for next_dir in too_new:
            self.tmpdir.write(os.path.join(next_dir, 'test_file.root'),
                              bytearray(os.urandom(1024)))
        for next_dir in touched_new:
            os.utime(self.tmpdir.getpath(os.path.join(next_dir, 'test_file.root')),
                     None)

        listdeletable.config.MIN_AGE = int(time.time() - cutoff_time)
        listdeletable.NOW = int(time.time())
        listdeletable.main()

        delete_function() # Function that does deletion is done here

        for dir in all_dirs:
            check_file = self.tmpdir.getpath(os.path.join(dir, 'test_file.root'))
            self.assertEqual(os.path.exists(check_file), dir not in to_delete,
                             'File status is unexpected: %s' % check_file)

    def test_deletions(self):
        methods = {
            'posix': [
                listdeletable.do_delete
                ],         # Test the do_delete function
            'hadoop': [
                listdeletable.do_delete,               # Test the do_delete function
# The Perl script is not configurable enough for unit tests at the moment
#                lambda: os.system(                     # Test the Perl script
#                    '%s %s' % (
#                        os.path.join(os.path.dirname(__file__), '../unmerged-cleaner/HadoopDelete.pl'),
#                        listdeletable.config.DELETION_FILE
#                        )
#                    )
                ],
            'dcache': []
            }

        for i, method in enumerate(methods[listdeletable.config.STORAGE_TYPE]):
            for which in ['directories', 'files']:

                print('Testing deletions on %s using %s' % (listdeletable.config.STORAGE_TYPE, which))

                listdeletable.config.WHICH_LIST = which

                self.tearDown()
                self.setUp()

                self.do_deletion(method)

    def test_directory_reduction(self):
        test_to_delete = 'dir/to/delete/test_file.root'

        self.tmpdir.write(test_to_delete,
                          bytearray(os.urandom(1024)))

        print('Waiting for some time.')

        time.sleep(5)
        cutoff_time = int(time.time())
        time.sleep(5)

        listdeletable.config.WHICH_LIST = 'directories'
        listdeletable.config.MIN_AGE = int(time.time() - cutoff_time)
        listdeletable.NOW = int(time.time())
        listdeletable.main()

        listdeletable.do_delete()

        self.assertFalse(os.path.exists(self.tmpdir.getpath(test_to_delete)))
        self.assertFalse(os.path.exists(self.tmpdir.getpath(os.path.dirname(test_to_delete))))
        self.assertTrue(os.path.exists(self.tmpdir.getpath('dir')))


class TestConditions(unittest.TestCase):

    def test_no_protected(self):
        protected = listdeletable.PROTECTED_LIST
        listdeletable.PROTECTED_LIST = []
        self.assertRaises(listdeletable.SuspiciousConditions, listdeletable.main)

        listdeletable.PROTECTED_LIST = protected

    def test_no_unmerged_pfn(self):
        self.assertTrue(listdeletable.config.UNMERGED_DIR_LOCATION.endswith('/store/unmerged'))

        unmerged = listdeletable.config.UNMERGED_DIR_LOCATION
        listdeletable.config.UNMERGED_DIR_LOCATION = '/'.join(
            listdeletable.config.UNMERGED_DIR_LOCATION.split('/')[:-2])

        self.assertFalse(listdeletable.config.UNMERGED_DIR_LOCATION.endswith('/store/unmerged'))

        self.assertRaises(listdeletable.SuspiciousConditions, listdeletable.main)

        listdeletable.config.UNMERGED_DIR_LOCATION = unmerged

    def test_bad_file_start(self):
        self.assertRaises(listdeletable.SuspiciousConditions, listdeletable.filter_protected,
                          [os.path.join(listdeletable.config.UNMERGED_DIR_LOCATION.replace('/store/', '/disk/store/'),
                                        'example/file/location.root')], [])

        self.assertRaises(listdeletable.SuspiciousConditions, listdeletable.filter_protected,
                          [os.path.join(listdeletable.config.UNMERGED_DIR_LOCATION.replace('/store/', '/disk/store/'),
                                        'example/file/location.root')], ['/store/unmerged/protected/'])


if __name__ == '__main__':
    unittest.main()
