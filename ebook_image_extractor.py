#!/usr/bin/env python

from io import BytesIO
from lxml import etree
import os
import re
import shutil
import subprocess
import sys
import time
import tempfile
import zipfile

temp_dir = tempfile.mkdtemp()

class Book:
    def __init__(self, book_file):
        self.book_file = book_file
        self.directory_name = None

class Epub(Book):
    def __init__(self, book_file):
        super().__init__(book_file)
        self.opf = None
        self.image = None

    def extract_file(self, file_name, **kwargs):
        '''Method for extracting a file to the temporary directory, or alternatively to another directory'''
        directory = kwargs.get('directory', temp_dir)
        try:
            with zipfile.ZipFile(self.book_file, 'r') as epub_archive:
                epub_archive.extract(file_name, directory) 
        except zipfile.BadZipFile:
            return 1, f'Bad zip file for {self.book_file}'
        except KeyError:
            return 1, f'No such file {file_name}'
        else:
            return 0, None

    def get_all_contents(self):
        '''returns a list of all files in the epub archive'''
        try:
            with zipfile.ZipFile(self.book_file, 'r') as epub_archive:
                return epub_archive.read()
        except:
            return

    def get_info(self, afile):
        '''returns info about a given file in the archive'''
        try:
            with zipfile.ZipFile(self.book_file, 'r') as epub_archive:
                return epub_archive.getinfo(afile)
        except KeyError:
            return

    def parse_xml_file(self, file_name, dir_name=temp_dir):
        '''parse opf file contents'''
        try:
            return etree.parse(os.path.join(dir_name, file_name))
        except etree.ParseError:
            return None

    def get_opf_from_container(self, container_tree):
        '''Get the OPF file. First, try the most accurate, checking the container.xml file for its location.
        If not successful, guess the location as OEBPS/conetent.opf.
        If that file doesn't exist, get the first ocurrence on a list of all files in the archive'''
        for el in container_tree.iter('{*}rootfile'): #get the opf file path
            return el.attrib.get('full-path')

    def get_opf_from_default(self):
        '''Guess the most common location'''
        opf_info = self.get_info('OEPBS/content.opf')
        if opf_info:
            return 'OEPBS/content.opf'

    def get_opf_from_contents(self):
        # Finally, if nothing else works, do it the slow way
        contents = self.get_all_contents()
        for fname in contents:
            if fname.endswith('.opf'):
                return fname

    def get_cover_page_from_opf(self, opf_tree):
        '''First find the reference with type=cover'''
        '''<reference type="cover" title="Front Cover" href="page001.xhtml" />'''
        cover_page = None
        for e in opf_tree.iter('{*}reference'): ## 
            cover_type = e.attrib.get('type')
            if cover_type:
                if cover_type.lower() == 'cover':
                    cover_page = e.attrib['href']
                if cover_page:
                    return cover_page

        '''Then try the first itemref id, get the corresponding item's href'''
        el = opf_tree.find('.//{*}itemref')
        cover_id = el.attrib.get('idref')
        if cover_id:
            items = opf_tree.findall('.//{*}item')
            for item in items:
                if item.attrib.get('id') == cover_id:
                    return item.attrib.get('href')

    #else:
    def check_if_cover_is_image(self, cover_page):
        '''sometimes the <reference href=> refers to an image, which what we want'''
        #print 'cover page: %s' % cover_page
        _, ext = os.path.splitext(cover_page)
        if ext.lower() in ('.jpg', '.jpeg', '.png'): 
            return cover_page

    def get_cover_tree(self, cover_page, cover_page_path=temp_dir):
        cover_tree = None
        _, ext = os.path.splitext(cover_page)
        if ext.lower() in ('.html', '.xhtml', '.htm'):
            parser = etree.HTMLParser()
            try:
                with open(os.path.join(cover_page_path, cover_page)) as cover_tree_content:
                    cover_tree_text = cover_tree_content.read().encode('utf-8')
                    cover_tree = etree.parse(BytesIO(cover_tree_text), parser)
            except ValueError as v:
                print(v)
                return
            return cover_tree

        else:
            return self.parse_xml_file(cover_page)
        return cover_tree

    def get_image_from_src(self, cover_tree):
        for e in cover_tree.iter():
            dtd = e.nsmap.get('xlink')
            if dtd:
                src = '{' + dtd + '}src'
            else:
                src = 'src'
    
            src_file = e.attrib.get(src)
            if src_file and os.path.splitext(src_file)[1] in ('.jpg', '.jpeg', '.png'):
                return src_file
        return None
        '''for e in cover_tree.iter('{*}img'):
            #if e.attrib['alt'].lower() == 'cover':
            image = e.attrib['src']
            if image:
                break
        if not image:
            for e in cover_tree.iter('{*}svg'):
                #print e, e.attrib
                image = e.attrib['src']'''

    def get_image_from_href(self, cover_tree):
        for e in cover_tree.iter('*'):
            dtd = e.nsmap.get('xlink')
            if dtd:
                href = '{' + dtd + '}href'
            else:
                href = 'href'
            
            href_file = e.attrib.get(href)
            if href_file and os.path.splitext(href_file)[1] in ('.jpg', '.jpeg', '.png'):
                return href_file
    

    def correct_image_path(self, image, image_path):
        print(self.opf_path)
        print(image)
        print(image)
        image = os.path.join(image_path, image) # make corrections to image path
        image = re.sub('\/.+\/\.\.', '', image)
        return image

    def get_image_location(self):
        '''Find the image location by parsing the opf file'''
        self.image = self.get_image_from_meta()
        if not self.image:
            self.image = self.get_image_from_cover_page()
        if image:
            self.image = re.sub('^\/', '', self.image) #remove leading '/'
            return 0
        else:
            return 1

    def extract_image(self):
        status, msg = self.extract_file(self.cover_image)
        #if status != 0:
        #    status, msg = self.extract_file(os.path.join('OEBPS', self.cover_image))
        print(status)
        print(msg)
        _, imageext = os.path.splitext(self.cover_image)
        if imageext.lower() == '.jpeg' or '.jpg':
            try:
                shutil.copy(os.path.join(temp_dir, self.cover_image), os.path.splitext(self.book_file)[0] + '.jpg')
            except IOError as e:
                print('{}: {}'.format(os.path.splitext(self.book_file)[0], e))
                return 1
            print('Successfully extracted image from %s' % self.book_file)
            return 0
        else:
            returncode = subprocess.call(['convert', os.file.join(temp_dir, self.cover_image), os.path.splitext(self.book_file)[0] + '.jpg']) # if not jpeg, use imagemagick to convert
            if returncode == 0:
                print('Extraction completed for %s' % self.book_file)
                return 0
            else:
                print('Error converting image %s for epub %s. Do you have ImageMagick installed?' % (self.cover_image, self.book_file))
                return 1 

class Pdf(Book):
    def __init__(self, book_file):
        super().__init__(book_file)

    def extract_file(self): # to do: add settings configuration to increase/decrease file size, resolution
        bookname, _ = os.path.splitext(self.book_file)
        gscommand = '%s -dSAFER -dBATCH -dNOPAUSE -dNOPROMPT -dMaxBitmap=500000000 -dAlignToPixels=0 -dUseCropBox -dGridFitTT=2 -sDEVICE=jpeg -dTextAlphaBits=4 -dGraphicsAlphaBits=4 -dUseCIEColor -r250x250 -dFirstPage=1 -dLastPage=1' % config_cfg['gsCmd']#    -sOUTPUTFILE=' #%s %s' % (book, bookname + 'jpg')
        gsargs = shlex.split(gscommand)
        gsargs.append('-sOUTPUTFILE=' + bookname + '.jpg')
        gsargs.append(self.book_file)
        return subprocess.call(gsargs)

def get_epub_list():
    '''Get the epub/pdf full path file names from directory given as an argument'''
    usage = '''Ebook image extractor. 
    USAGE: python ebook_image_extractor.py epub_directory/
    '''
    args = sys.argv[1:]
    if len(args) != 1:
        print(usage)
        sys.exit(1)
    epub_dir = args[0]
    if os.path.isdir(epub_dir):
        return [os.path.join(epub_dir, f) for f in os.listdir(epub_dir) if f.lower().endswith('.epub') or f.lower().endswith('.pdf')]
    print(f'Directory Not Found {epub_dir}')
    print(usage)
    sys.exit(1)

def main():
    container_file = 'META-INF/container.xml' #META-INF/container.xml tells us where the opf file is
    start_time = time.time()
    skipped = 0
    created = 0
    failed = 0
    image_path = None
    for file_name in get_epub_list():
        print(file_name)
        fname, fext = os.path.splitext(file_name)
        if os.path.isfile(fname + '.jpg'): # skip if jpeg already exists
            print('Jpeg file exists for %s' % file_name)
            skipped += 1
            continue
        print(f'Getting image for {file_name}...')
        if file_name.lower().endswith('.epub'):
            ebook = Epub(file_name)
            #status = ebook.get_opf()
            #if status == 1:
            #    failed += 1
            #    continue
            status, msg = ebook.extract_file(container_file)
            if status != 0:
                print(msg)
                failed += 1
                continue
            container_tree = ebook.parse_xml_file(container_file)
            opf = ebook.get_opf_from_container(container_tree)
            if not opf:
                opf = ebook.get_opf_from_default()
            if not opf:
                opf = ebook.get_opf_from_contents()
            if opf:
                ebook.opf = re.sub('\%20', ' ', opf) # clean up spaces
                ebook.opf_path = os.path.dirname(ebook.opf)
                ebook.extract_file(ebook.opf)
            else:
                print('Cannot find opf file')
                failed += 1
                continue
            opf_tree = ebook.parse_xml_file(ebook.opf)
            cover_page = ebook.get_cover_page_from_opf(opf_tree)
            if not cover_page:
                print(f'cover page not found for {file_name}')
                failed += 1
                continue
            cover_page = re.sub('\%20', ' ', cover_page) # clean up spaces
            print(cover_page)
            cover_page = os.path.join(ebook.opf_path, cover_page)
            cover_image = ebook.check_if_cover_is_image(cover_page)
            if cover_image:
                image_path = ebook.opf_path
            else:
                status, msg = ebook.extract_file(cover_page)
                print(status, msg)
                if status != 0:
                    failed += 1
                    continue
                cover_tree = ebook.get_cover_tree(cover_page)
                cover_image = ebook.get_image_from_src(cover_tree)
                if not cover_image:
                    cover_image = ebook.get_image_from_href(cover_tree)
                image_path = os.path.dirname(cover_page)
            if cover_image:
                ebook.cover_image = ebook.correct_image_path(cover_image, image_path)


                status = ebook.extract_image()
                if status == 0:
                    created += 1
                else:
                    failed += 1

        else:
            ebook = Pdf(book_file)
            status, msg = ebook.extract_file()
            if status != 0:
                failed += 1
                print(f'Unable to retrieve image from {file_name}')
            else:
                created += 1



    print(f'''
    success: {created}
    failures: {failed}
    skipped: {skipped}
    ''')
            

if __name__ == '__main__':
    main()
