from lxml import etree
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
    

    @mock.patch('ebook_image_extractor.zipfile.ZipFile')
    def test_get_info(self, mock_zip_file):
        test_dir = tempfile.mkdtemp()
        test_file1 = tempfile.mkstemp(suffix='.epub', dir=test_dir)
        ebook_image_extractor.temp_dir = test_dir
        epub = Epub(test_file1)

        mock_open_file = mock.mock_open()
        epub.get_info('OEPBS/content.opf')
        mock_zip_file.assert_called()

    def test_parse_container_file(self):
        test_dir = tempfile.mkdtemp()
        test_file1 = tempfile.mkstemp(suffix='.epub', dir=test_dir)
        ebook_image_extractor.temp_dir = test_dir
        epub = Epub(test_file1)
        container_file = 'META-INF/container.xml' #META-INF/container.xml tells us where the opf file is
        ebook_image_extractor.etree = mock.MagicMock()
        ebook_image_extractor.etree.parse = mock.MagicMock(return_value='test')
        container_tree = container_file(container_file)
        self.assertEqual(container_tree, 'test')

    def test_get_opf_from_container(self):
        test_dir = tempfile.mkdtemp()
        test_file1 = tempfile.mkstemp(suffix='.epub', dir=test_dir)
        ebook_image_extractor.temp_dir = test_dir
        epub = Epub(test_file1)
        container_str = '''<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'''
        container_tree = etree.fromstring(container_str)
        opf_file = epub.get_opf_from_container(container_tree)
        self.assertEqual(opf_file, 'OEBPS/content.opf')

    def test_get_opf_from_default(self):
        test_dir = tempfile.mkdtemp()
        test_file1 = tempfile.mkstemp(suffix='.epub', dir=test_dir)
        ebook_image_extractor.temp_dir = test_dir
        epub = Epub(test_file1)
        epub.get_info = mock.MagicMock(return_value='test')
        opf = epub.get_opf_from_default()
        self.assertEqual(opf, 'OEBPS/content.opf')

        epub.get_info = mock.MagicMock(return_value='test')
        opf = epub.get_opf_from_default()
        self.assertEqual(opf, None)

    def test_get_opf_from_contents(self):
        test_dir = tempfile.mkdtemp()
        test_file1 = tempfile.mkstemp(suffix='.epub', dir=test_dir)
        ebook_image_extractor.temp_dir = test_dir
        epub = Epub(test_file1)
        epub.get_all_contents = mock.MagicMock(return_value=['a', 'b','c.opf', 'd'])
        opf = epub.get_opf_from_contents()
        self.assertEqual(opf, 'c.opf')

        



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

    def test_get_opf_from_default(self):
        pass

    def test_get_opf_from_contents(self):
        pass

    #def test_get_image_from_cover_page(self):
    #    pass

    def test_get_cover_page(self):

        opf_str = '''
        <?xml version="1.0" encoding="UTF-8"?>
        <package version="2.0" unique-identifier="PrimaryID" xmlns="http://www.idpf.org/2007/opf">
	<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
		<dc:title>Galway Girl</dc:title>
		<dc:language>en-US</dc:language>
		<dc:identifier id="PrimaryID" opf:scheme="ISBN">9780802147943</dc:identifier>
		<dc:creator opf:role="aut" opf:file-as="Bruen, Ken">Ken Bruen</dc:creator>
		<dc:publisher>The Mysterious Press</dc:publisher>
		<dc:date opf:event="publication">2019</dc:date>
		<dc:rights>Copyright &#169; 2019 by Ken Bruen</dc:rights>
		<meta name="cover" content="my_cover_image"/>
	</metadata>
	<manifest>
		<item id="ncx" href="9780802147943_epub_ncx_r1.ncx" media-type="application/x-dtbncx+xml"/>
		<item id="cvi" href="OEBPS/cvi.htm" media-type="application/xhtml+xml"/>
		<item id="also" href="OEBPS/also.htm" media-type="application/xhtml+xml"/>
		<item id="tp" href="OEBPS/tp.htm" media-type="application/xhtml+xml"/>
		<item id="cop" href="OEBPS/cop.htm" media-type="application/xhtml+xml"/>
	</manifest>
	<spine toc="ncx">
		<itemref idref="cvi"/>
		<itemref idref="also"/>
		<itemref idref="tp"/>
		<itemref idref="cop"/>
	</spine>
	<guide>
		<reference type="text" title="Start" href="OEBPS/tp.htm"/>
		<reference type="cover" title="Cover" href="OEBPS/cvi.htm"/>
		<reference type="copyright-page" title="Copyright" href="OEBPS/cop.htm"/>
		<reference type="toc" title="Table of Contents" href="OEBPS/toc.htm"/>
	</guide>
</package>
        
        '''
        opf_tree = etree.fromstring(opf_str)
        opf_file = epub.get_cover_page(opf_tree)
        self.assertEqual(opf_file, 'OEBPS/toc.htm')
        pass

    def test_check_if_cover_is_image(self):
        pass

    def test_get_cover_tree(self):
        pass

    def test_get_image_from_src(self):
        pass

    def test_get_image_from_href(self):
        pass

    def test_correct_image_path(self):
        pass

    def test_get_image_location(self):
        test_dir = tempfile.mkdtemp()
        test_file1 = tempfile.mkstemp(suffix='.epub', dir=test_dir)
        ebook_image_extractor.temp_dir = test_dir
        epub = Epub(test_file1)
        epub.get_image_from_meta = mock.MagicMock(return_value='images/cover.jpg')
        epub.get_image_from_cover_page = mock.MagicMock()

        epub.get_image_location()

        epub.get_image_from_meta.assert_called()
        epub.get_image_from_cover_page.assert_not_called()

        test_dir = tempfile.mkdtemp()
        test_file1 = tempfile.mkstemp(suffix='.epub', dir=test_dir)
        ebook_image_extractor.temp_dir = test_dir
        epub = Epub(test_file1)
        epub.get_image_from_meta = mock.MagicMock(return_value=None)
        epub.get_image_from_cover_page = mock.MagicMock()

        epub.get_image_location()

        epub.get_image_from_cover_page.assert_called()
        epub.get_image_from_meta.assert_called()

    def test_extract_image(self):
        pass

class PdfTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_extract_file(self):
        pass

if __name__ == '__main__':
    unittest.main()
        


        

