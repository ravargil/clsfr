import unittest
import os
from distutils import dir_util
import shutil
from classifier import FilesClassifier
from classifier import BaseFileSelector
from classifier import DateFilesSelector

class FilesSelectorMock(BaseFileSelector):
    files = []
    dirs = []
    file_key_generator = lambda f: "my-dir"

    def get_files(self, current_dir):
        return FilesSelectorMock.files

    def get_dirs(self, current_dir):
        return FilesSelectorMock.dirs
    
    def generate_file_key(self, file_path):
        return FilesSelectorMock.file_key_generator(file_path)

class FilesClassifierTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self.__rootdir = os.path.dirname(os.path.abspath(__file__)) + "\\rootdir"
        self.__files_selector_mock = FilesSelectorMock()
        super(FilesClassifierTests, self).__init__(*args, **kwargs)
    

    def setUp(self):
        FilesSelectorMock.files = []
        FilesSelectorMock.dirs = []
        return super().setUp()

    def tearDown(self):
        FilesSelectorMock.files = []
        FilesSelectorMock.dirs = []
        return super().tearDown()

    def test_empty_dir__classify__empty_iter(self):
        #Arrange:
        clsfr = FilesClassifier(self.__files_selector_mock)
        
        #Act:
        clsfr.classify(os.getcwd())
        
        #Assert:
        msg = "expected no elemnts in clsfr"
        self.assertEqual(len(clsfr._FilesClassifier__files_dict), 0, msg)

    def test_no_such_dir__classify__empty_iter(self):
        #Arrange:
        clsfr = FilesClassifier(self.__files_selector_mock)
        
        #Act:
        clsfr.classify("abc")
        
        #Assert:
        msg = "expected no elemnts in clsfr"
        self.assertEqual(len(clsfr._FilesClassifier__files_dict), 0, msg)

    def test_not_a_dir__classify__empty_iter(self):
        #Arrange:
        clsfr = FilesClassifier(self.__files_selector_mock)
        
        #Act:
        clsfr.classify(__file__)
        
        #Assert:
        msg = "expected no elemnts in clsfr"
        self.assertEqual(len(clsfr._FilesClassifier__files_dict), 0, msg)

    def test_only_files__classify__iter_not_empty(self):
        #Arrange:
        FilesSelectorMock.files = ["file1.txt", "file2.txt"]
        clsfr = FilesClassifier(self.__files_selector_mock)
        
        #Act:
        clsfr.classify(os.getcwd())
        
        #Assert:
        msg = "expected 1 key in clsfr"
        self.assertEqual(len(clsfr._FilesClassifier__files_dict), 1, msg)

    # The following tests use the provided files:
    # rootdir -->
    #       file        modified-date     modified-month   modified-year
    # rootdir:
    #       a02.txt     2015-11-07        2015-11          2015
    #       a03.txt     2015-08-07        2015-08          2015
    #       a04.txt     2016-02-02        2015-02          2016
    #       a06.txt     2016-03-04        2016-03          2016
    #       a06.txt     2017-12-02        2017-12          2017
    #       a09.txt     2017-05-30        2017-05          2017
    # rootdir/dir1/
    #       a01.txt     2015-08-07        2015-08          2015
    #       a03.txt     2016-08-02        2016-02          2016
    # rootdir/dir2/
    #       a08.txt     2017-05-22        2017-05          2017

    def test_files_and_dirs__classify_by_day__iter_not_empty(self):
        #Arrange:
        # The package comes with 9 files where 2 of them has exactly the same 
        # modified date (a03.txt & a01.txt). 
        # Which means in this test there will be 8 elements 
        # because the test classify by modified day.
        expected_keys = 8
        expected_values = 9
        fs = DateFilesSelector()
        clsfr = FilesClassifier(fs)
        
        #Act:
        clsfr.classify(self.__rootdir)
        
        #Assert:
        msg = "expected {} keys in clsfr".format(expected_keys)
        self.assertEqual(len(clsfr._FilesClassifier__files_dict), expected_keys, msg)
        total = sum(1 for _ in clsfr) 
        msg = "expected {} values in clsfr".format(expected_values)
        self.assertEqual(expected_values, total, msg)

    def test_files_and_dirs__classify_by_month__iter_not_empty(self):
        #Arrange:
        # The package comes with 9 files where 2 pairs have the same year and month. 
        # Which means in this test there will be 7 different keys.
        expected_keys = 7
        expected_values = 9
        fs = DateFilesSelector("month")
        clsfr = FilesClassifier(fs)
        
        #Act:
        clsfr.classify(self.__rootdir)
        
        #Assert:
        msg = "expected {} keys in clsfr".format(expected_keys)
        self.assertEqual(len(clsfr._FilesClassifier__files_dict), expected_keys, msg)
        total = sum(1 for _ in clsfr) 
        msg = "expected {} values in clsfr".format(expected_values)
        self.assertEqual(expected_values, total, msg)

    def test_files_and_dirs__classify_by_year__iter_not_empty(self):
        #Arrange:
        # The package comes with 9 files divided to 3 different years. 
        # Which means in this test there will be 3 keys.
        expected_keys = 3
        expected_values = 9
        fs = DateFilesSelector("year")
        clsfr = FilesClassifier(fs)
        
        #Act:
        clsfr.classify(self.__rootdir)
        
        #Assert:
        msg = "expected {} keys in clsfr".format(expected_keys)
        self.assertEqual(len(clsfr._FilesClassifier__files_dict), expected_keys, msg)
        total = sum(1 for _ in clsfr) 
        msg = "expected {} values in clsfr".format(expected_values)
        self.assertEqual(expected_values, total, msg)

    def test_two_calls__classify_by_day__no_duplication(self):
        #Arrange:
        # This test makes sure internal clean before classify.
        expected_keys = 8
        expected_values = 9
        fs = DateFilesSelector()
        clsfr = FilesClassifier(fs)
        
        #Act:
        clsfr.classify(self.__rootdir)
        clsfr.classify(self.__rootdir)
        
        #Assert:
        msg = "expected {} keys in clsfr".format(expected_keys)
        self.assertEqual(len(clsfr._FilesClassifier__files_dict), expected_keys, msg)
        total = sum(1 for _ in clsfr) 
        msg = "expected {} values in clsfr".format(expected_values)
        self.assertEqual(expected_values, total, msg)
    