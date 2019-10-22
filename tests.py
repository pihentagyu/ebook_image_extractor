#!/usr/bin/env python

from lxml import etree
import os
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
        self.test_dir = tempfile.mkdtemp()
        test_file1 = tempfile.mkstemp(suffix='.epub', dir=self.test_dir)
        ebook_image_extractor.temp_dir = self.test_dir
        self.epub = Epub(test_file1)

    @mock.patch('ebook_image_extractor.zipfile.ZipFile')
    def test_extract_file(self, mock_zip_file):
        '''https://gist.github.com/Bergvca/069d50d58b56fba0f9ee695d92ccebde'''
        self.epub.extract_file('test.opf', directory=self.test_dir)

        mock_zip_file.assert_called()

    @mock.patch('ebook_image_extractor.zipfile.ZipFile')
    def test_get_all_contents(self, mock_zip_file):
        #mock_open_file = mock.mock_open()
        self.epub.get_all_contents()
        mock_zip_file.assert_called()
    

    @mock.patch('ebook_image_extractor.zipfile.ZipFile')
    def test_get_info(self, mock_zip_file):
        #mock_open_file = mock.mock_open()
        self.epub.get_info('OEBPS/content.opf')
        mock_zip_file.assert_called()

    def test_parse_xml_file(self):
        container_file = 'META-INF/container.xml' #META-INF/container.xml tells us where the opf file is
        ebook_image_extractor.etree = mock.MagicMock()
        ebook_image_extractor.etree.parse = mock.MagicMock(return_value='test')
        container_tree = self.epub.parse_xml_file(container_file)
        self.assertEqual(container_tree, 'test')

    def test_get_opf_from_container(self):
        container_str = '''<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'''
        container_tree = etree.fromstring(container_str)
        opf_file = self.epub.get_opf_from_container(container_tree)
        self.assertEqual(opf_file, 'OEBPS/content.opf')

    def test_get_opf_from_default(self):
        self.epub.get_info = mock.MagicMock(return_value='test')
        opf = self.epub.get_opf_from_default()
        self.assertEqual(opf, 'OEBPS/content.opf')

    def test_get_opf_from_contents(self):
        self.epub.get_all_contents = mock.MagicMock(return_value=['a', 'b','c.opf', 'd'])
        opf = self.epub.get_opf_from_contents()
        self.assertEqual(opf, 'c.opf')

        
    #def test_get_image_from_cover_page(self):
    #    pass

    def test_get_cover_page_from_opf(self):
        opf_str = b'''<?xml version="1.0" encoding="UTF-8"?>
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
        opf_file = self.epub.get_cover_page_from_opf(opf_tree)
        self.assertEqual(opf_file, 'OEBPS/cvi.htm')
        opf_str = '''<package version="3.0" unique-identifier="pub-id" xmlns="http://www.idpf.org/2007/opf" dir="ltr" xml:lang="en">
          <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:opf="http://www.idpf.org/2007/opf">
            <dc:title id="title">Cinemagritte</dc:title>
            <meta refines="#title" property="title-type">main</meta>
            <meta refines="#title" property="display-seq">1</meta>
            <dc:title id="subtitle">René Magritte within the Frame of Film History, Theory, and Practice</dc:title>
            <meta refines="#subtitle" property="title-type">subtitle</meta>
            <meta refines="#subtitle" property="display-seq">2</meta>
            <dc:title id="collection_title">Contemporary Approaches to Film and Media Series</dc:title>
            <meta refines="#collection_title" property="title-type">collection</meta>
            <meta refines="#collection_title" property="display-seq">3</meta>
            <dc:language id="lang1">en-US</dc:language>
            <meta refines="#lang1" property="display-seq">1</meta>
            <dc:creator id="creator1">Lucy Fischer</dc:creator>
            <meta refines="#creator1" property="file-as">Fischer, Lucy</meta>
            <meta refines="#creator1" property="role" scheme="marc:relators">aut</meta>
            <dc:creator id="creator2">Barry Keith Grant</dc:creator>
            <meta refines="#creator2" property="file-as">Grant, Barry Keith</meta>
            <meta refines="#creator2" property="role" scheme="marc:relators">edt</meta>
            <dc:identifier id="pub-id">978-0-8143-4638-9</dc:identifier>
            <meta refines="#pub-id" property="identifier-type" scheme="xsd:string">unique</meta>
            <dc:source id="src-id">urn:isbn:978-0-8143-4637-2</dc:source>
            <dc:publisher>Wayne State University Press</dc:publisher>
            <dc:description>Cinemagritte: René Magritte within the Frame of Film History, Theory, and Practice investigates the dynamic relationship between the Surrealist modernist artist René Magritte (1898-1967) and the cinema-a topic largely ignored in the annals of film and art criticism. Magritte once said that he used cinema as &quot;a trampoline for the imagination,&quot; but here author Lucy Fischer reverses that process by using Magritte's work as a stimulus for an imaginative examination of film.While Fischer considers direct influences of film on Magritte and Magritte on film, she concentrates primarily on &quot;resonances&quot; of Magritte's work in international cinema-both fiction and documentary, mainstream and experimental. These resonances exist for several reasons. First, Magritte was a lover of cinema and created works as homages to the medium, such as Blue Cinema (1925), which immortalized his childhood movie theater. Second, Magritte's style, though dependent on bizarre juxtapositions, was characterized by surface realism-which ties it to the nature of the photographic and cinematic image. Third, Magritte shares with film a focus on certain significant concepts: the frame, voyeurism, illusionism, the relation between word and image, the face, montage, variable scale, and flexible point of view. Additionally, the volume explores art documentaries concerning Magritte as well as the artist's whimsical amateur &quot;home movies,&quot; made with his wife, Georgette, friends, and Belgian Surrealist associates. The monograph is richly illustrated with images of Magritte's oeuvre as well as film stills from such diverse works as The Eternal Sunshine of the Spotless Mind, Eyes Without a Face, American Splendor, The Blood of a Poet, Zorns Lemma, The Island of Dr. Moreau, The Draughtsman's Contract, and many more. Cinemagritte brings a novel and creative approach to the work of Magritte and both film and art criticism. Students, scholars, and fans of art history and film will enjoy this thoughtful marriage of the two.</dc:description>
            <dc:date>2019-11-25</dc:date>
            <meta property="dcterms:modified">2019-09-17T19:51:16Z</meta>
            <dc:subject>ART009000 Art / Criticism &amp; Theory</dc:subject>
            <dc:subject>PER004030 Performing Arts / Film &amp; Video / History &amp; Criticism</dc:subject>
            <dc:rights>All rights reserved</dc:rights>
            <meta name="cover" content="My_Cover"/>
          </metadata>
          <manifest>
            <item id="toc" properties="nav" href="toc.xhtml" media-type="application/xhtml+xml"/>
            <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
            <item href="wsu-fischercinemagritte-0001.xhtml" id="wsu-fischercinemagritte-0001"  media-type="application/xhtml+xml"/>
            <item href="wsu-fischercinemagritte-0002.xhtml" id="wsu-fischercinemagritte-0002"  media-type="application/xhtml+xml"/>
            <item href="wsu-fischercinemagritte-0003.xhtml" id="wsu-fischercinemagritte-0003"  media-type="application/xhtml+xml"/>
            <item href="wsu-fischercinemagritte-0004.xhtml" id="wsu-fischercinemagritte-0004"  media-type="application/xhtml+xml"/>
            <item href="wsu-fischercinemagritte-0005.xhtml" id="wsu-fischercinemagritte-0005"  media-type="application/xhtml+xml"/>
            <item href="images/wsu-fischercinemagritte-fig1-1.jpeg" id="imgwsu-fischercinemagritte-fig1-1"  media-type="image/jpeg" />
            <item href="images/wsu-fischercinemagritte-fig2-2.jpeg" id="imgwsu-fischercinemagritte-fig2-2"  media-type="image/jpeg" />
            <item href="images/wsu-fischercinemagritte-fig2-3.jpeg" id="imgwsu-fischercinemagritte-fig2-3"  media-type="image/jpeg" />
            <item href="images/wsu-fischercinemagritte-fig2-1.jpeg" id="imgwsu-fischercinemagritte-fig2-1"  media-type="image/jpeg" />
            <item href="images/wsu-fischercinemagritte-fig2-4.jpeg" id="imgwsu-fischercinemagritte-fig2-4"  media-type="image/jpeg" />
            <item href="images/wsu-fischercinemagritte-fig2-5.jpeg" id="imgwsu-fischercinemagritte-fig2-5"  media-type="image/jpeg" />
            <item href="wsu.css" id="default"  media-type="text/css"/>
            <item href="fonts/FreeSerifBold.otf" id="FreeSerifBold"  media-type="application/font-sfnt"/>
            <item href="fonts/FreeSerifBoldItalic.otf" id="FreeSerifBoldItalic"  media-type="application/font-sfnt"/>
            <item href="fonts/FreeSerifItalic.otf" id="FreeSerifItalic"  media-type="application/font-sfnt"/>
            <item href="fonts/FreeSerif.otf" id="FreeSerif"  media-type="application/font-sfnt"/>
          </manifest>
          <spine toc="ncx">
            <itemref idref="wsu-fischercinemagritte-0001"/>
            <itemref idref="wsu-fischercinemagritte-0002"/>
            <itemref idref="wsu-fischercinemagritte-0003"/>
            <itemref idref="wsu-fischercinemagritte-0004"/>
            <itemref idref="wsu-fischercinemagritte-0005"/>
          </spine>
        </package>
        '''
        opf_tree = etree.fromstring(opf_str)
        opf_file = self.epub.get_cover_page_from_opf(opf_tree)
        self.assertEqual(opf_file, 'wsu-fischercinemagritte-0001.xhtml')

    def test_check_if_cover_is_image(self):
        cover_image = self.epub.check_if_cover_is_image('test.htm')
        self.assertEqual(cover_image, None)

        cover_image = self.epub.check_if_cover_is_image('test.jpg')
        self.assertEqual(cover_image, 'test.jpg')
        cover_image = self.epub.check_if_cover_is_image('test.jpeg')
        self.assertEqual(cover_image, 'test.jpeg')
        cover_image = self.epub.check_if_cover_is_image('test.png')
        self.assertEqual(cover_image, 'test.png')


    #@mock.patch(ebook_image_extractor.open, mock.mock_open(read_data='test text'))
    def test_get_cover_tree(self):
        cover_html = '''<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
            <html xmlns="http://www.w3.org/1999/xhtml" >
            <head>
            <title>Analytic Functions</title>
            </head>
            <body style="margin-top: 0px; margin-left: 0px; margin-right: 0px; margin-bottom: 0px; text-align: center; background-color: #FFFFFF;">
            <div><img src="../img/1_1.jpg" alt="cover" style="height: 100%"/></div>
            </body>
            </html>
            '''
        #ebook_image_extractor.etree = mock.MagicMock()
        #ebook_image_extractor.etree.HTMLParser = mock.MagicMock()
        #ebook_image_extractor.etree.parse = mock.MagicMock()
        with mock.patch('ebook_image_extractor.open', mock.mock_open(read_data=cover_html)) as mock_file:
            cover_tree = self.epub.get_cover_tree('cover_page.html', self.test_dir)
            mock_file.assert_called_once_with(os.path.join(self.test_dir, 'cover_page.html'))
            self.assertIsInstance(cover_tree, etree._ElementTree)


    def test_get_image_from_src(self):
        cover_html = b'''<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
            <html xmlns="http://www.w3.org/1999/xhtml" >
            <head>
            <title>Analytic Functions</title>
            </head>
            <body style="margin-top: 0px; margin-left: 0px; margin-right: 0px; margin-bottom: 0px; text-align: center; background-color: #FFFFFF;">
            <div><img src="../img/1_1.jpg" alt="cover" style="height: 100%"/></div>
            </body>
            </html>
            '''
        cover_tree = etree.fromstring(cover_html)
        src_file = self.epub.get_image_from_src(cover_tree)
        print(src_file)

    def test_get_image_from_href(self):
        pass

    def test_correct_image_path(self):
        image = '../images/cover.jpg'
        image_path = 'OEBPS/text'
        new_image = self.epub.correct_image_path(image, image_path)
        self.assertEqual(new_image, 'OEBPS/images/cover.jpg')

    def test_get_image_location(self):
        self.epub.get_image_from_meta = mock.MagicMock(return_value='images/cover.jpg')
        self.epub.get_image_from_cover_page = mock.MagicMock()

        self.epub.get_image_location()

        self.epub.get_image_from_meta.assert_called()
        self.epub.get_image_from_cover_page.assert_not_called()

        self.epub.get_image_from_meta = mock.MagicMock(return_value=None)
        self.epub.get_image_from_cover_page = mock.MagicMock(return_value=None)

        self.epub.get_image_location()

        self.epub.get_image_from_cover_page.assert_called()
        self.epub.get_image_from_meta.assert_called()

    def test_extract_image(self):
        pass

class PdfTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_extract_file(self):
        pass

if __name__ == '__main__':
    unittest.main()
        


        

