#!/usr/bin/env python

from lxml import etree
import os
import sys
import tempfile
import zipfile

temp_dir = tempfile.mkdtemp()
container_file = 'META-INF/container.xml' #META-INF/container.xml tells us where the opf file is

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
        try:
            with zipfile.ZipFile(self.book_file, 'r') as epub_archive:
                return epub_archive.read()
        except:
            return

    def get_info(self, afile):
        try:
            with zipfile.ZipFile(self.book_file, 'r') as epub_archive:
                return epub_archive.getinfo(afile)
        except KeyError:
            return

    def opf_from_container(self):
        for el in container_tree.iter('{*}rootfile'): #get the opf file path
            return el.attrib.get('full-path')

    def get_opf(self):
        '''Get the OPF file. First, try the most accurate, checking the container.xml file for its location.
        If not successful, guess the location as OEBPS/conetent.opf.
        If that file doesn't exist, get the first ocurrence on a list of all files in the archive'''
        status, msg = self.extract_file(container_file)
        if status != 0:
            print(msg)
            return 1
        try:
            container_tree = etree.parse(os.path.join(temp_dir, container_file))
        except etree.ParseError:
            print('{}: Could not parse Container file'.format(base))
            container_tree = None
        if container_tree:
            self.opf = self.opf_from_container(container_tree)

        if not self.opf:
            # Guess the most common location
            opf_info = self.get_info('OEPBS/content.opf')
            if opf_info:
                self.opf = 'OEPBS/content.opf'
            else:
                # Finally, if nothing else works, do it the slow way
                contents = get_all_contents()
                for fname in contents:
                    if fname.endswith('.opf'):
                        self.opf = fname
                        break

    def get_image_location(self):
        '''Find the image location by parsing the opf file'''
        self.image = self.get_image_from_meta(opf)
        if not image:
            self.image = self.get_image_from_cover_page(opf, book)

    def extract_image(self):
        print('image, 232: {}'.format(image))
        image = re.sub('^\/', '', image) #remove leading '/'
        extract(book, temp_dir, image)
        _, imageext = os.path.splitext(image)
        if imageext.lower() == '.jpeg' or '.jpg':
            try:
                shutil.copy(os.path.join(temp_dir, image), file_name + '.jpg')
            except IOError as e:
                print('{}: {}'.format(base, e))
                return 1
            print('Successfully extracted image from %s' % book)
            created += 1
        else:
            returncode = subprocess.call(['convert', os.file.join(temp_dir, image), filename + '.jpg']) # if not jpeg, use imagemagick to convert
            if returncode == 0:
                print('Extraction completed for %s' % book)
                created += 1
            else:
                print('Error converting image %s for epub %s. Do you have ImageMagick installed?' % (image, book))
                failed += 1

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
    start_time = time.time()
    skipped = 0
    created = 0
    failed = 0
    for file_name in get_epub_list():
        fname, fext = os.path.splitext(book)
        if os.path.isfile(file_name + '.jpg'): # skip if jpeg already exists
            print('Jpeg file exists for %s' % file_name)
            skipped += 1
            continue
        print(f'Getting image for {file_name}...')
        if file_name.lower().endswith('.epub'):
            ebook = Epub(file_name)
            status = ebook.get_opf()
            if status == 1:
                failed += 1
                continue
            if ebook.opf:
                status = self.extract_file(book, opf)
        if status != 0: ## Bad zip file already checked above!!
            print(status)
            failed += 1
            continue
        else:
            ebook = Pdf(book_file)
            status = book.extract_file()
            if status != 0:
                print(f'Unable to retrieve image from {file_name}')
            


            

if __name__ == '__main__':
    main()
