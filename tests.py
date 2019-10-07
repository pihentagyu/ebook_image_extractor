import tempfile
import unittest
from unittest import mock

import ebook_image_extractor
from ebook_image_extractor import Epub, Pdf

class EbookImageExtractorTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_epub_list(self):
        test_dir = tempfile.mkdtemp()
        test_file1 = tempfile.mkstemp(suffix='.epub', dir=test_dir)
        test_file2 = tempfile.mkstemp(suffix='.epub', dir=test_dir)
        test_file3 = tempfile.mkstemp(suffix='.pdf', dir=test_dir)
        test_file4 = tempfile.mkstemp(suffix='.txt', dir=test_dir)


        ebook_image_extractor.sys.argv = ['ebook_image_extractor.py', test_dir]
        file_list = ebook_image_extractor.get_epub_list()
        self.assertEqual(len(file_list), 3)
        print(file_list)

        ebook_image_extractor.sys.argv = ['ebook_image_extractor.py', 'two', 'three']
        
        with self.assertRaises(SystemExit) as se:
            file_list = ebook_image_extractor.get_epub_list()
        self.assertEqual(se.exception.code, 1)


        ebook_image_extractor.sys.argv = ['ebook_image_extractor.py', '/nonexist/directory']
        
        with self.assertRaises(SystemExit) as se:
            file_list = ebook_image_extractor.get_epub_list()
        self.assertEqual(se.exception.code, 1)

class EpubTests(unittest.TestCase):
    def setUp(self):
        pass

    @patch('ebook_image_extractor.zipfile.ZipFile')
    def test_extract_file(self, mock_zip_file):
        '''https://gist.github.com/Bergvca/069d50d58b56fba0f9ee695d92ccebde'''
        test_dir = tempfile.mkdtemp()
        test_file1 = tempfile.mkstemp(suffix='.epub', dir=test_dir)

        mock_open_file = mock.mock_open
        ebook_image_extractor.temp_dir = test_dir
        epub = Epub(test_file1)
        epub.extract_file('test.opf', directory=test_dir)
        print(ebook_image_extractor.zipfile.ZipFile.method_calls)
        print(ebook_image_extractor.zipfile.ZipFile.extract.method_calls)






if __name__ == '__main__':
    unittest.main()
        


        

