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

    @mock.patch('ebook_image_extractor.zipfile.ZipFile')
    def test_extract_file(self, mock_zip_file):
        '''https://gist.github.com/Bergvca/069d50d58b56fba0f9ee695d92ccebde'''
        test_dir = tempfile.mkdtemp()
        test_file1 = tempfile.mkstemp(suffix='.epub', dir=test_dir)
        ebook_image_extractor.temp_dir = test_dir
        epub = Epub(test_file1)

        epub.extract_file('test.opf', directory=test_dir)

        mock_zip_file.assert_called()

    @mock.patch('ebook_image_extractor.zipfile.ZipFile')
    def test_get_all_contents(self, mock_zip_file):
        test_dir = tempfile.mkdtemp()
        test_file1 = tempfile.mkstemp(suffix='.epub', dir=test_dir)
        ebook_image_extractor.temp_dir = test_dir
        epub = Epub(test_file1)

        mock_open_file = mock.mock_open()
        epub.get_all_contents()
        mock_zip_file.assert_called()

    @mock.patch('ebook_image_extractor.etree')
    def test_get_opf(self, mock_etree):

        test_dir = tempfile.mkdtemp()
        test_file1 = tempfile.mkstemp(suffix='.epub', dir=test_dir)
        ebook_image_extractor.temp_dir = test_dir
        epub = Epub(test_file1)
        
        epub.extract_file = mock.MagicMock(return_value=(0, None))
        mock_etree.parse = mock.MagicMock(return_value='test_container')
        epub.opf_from_container = mock.MagicMock(return_value='OEPBS/content.opf')
        epub.get_opf()
        self.assertEqual(epub.opf, 'OEPBS/content.opf')


        test_dir = tempfile.mkdtemp()
        test_file1 = tempfile.mkstemp(suffix='.epub', dir=test_dir)
        ebook_image_extractor.temp_dir = test_dir
        epub = Epub(test_file1)
        
        epub.extract_file = mock.MagicMock(return_value=(0, None))
        epub.get_info = mock.MagicMock(return_value=('info'))
        mock_etree.parse = mock.MagicMock(return_value='test_container')
        epub.opf_from_container = mock.MagicMock(return_value=None)
        epub.get_opf()

        self.assertEqual(epub.opf, 'OEPBS/content.opf')
        


if __name__ == '__main__':
    unittest.main()
        


        

