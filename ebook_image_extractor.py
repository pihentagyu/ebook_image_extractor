#!/usr/bin/env python

import os
import sys
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

    def extract_file(self, file_name, **kwargs):
        '''Method for extracting a file to the temporary directory, or alternatively to another directory'''
        directory = kwargs.get('directory', temp_dir)
        try:
            with zipfile.ZipFile(self.book_file, 'r') as epub_archive:
                epub_archive.extract(file_name, directory) 
        except zipfile.BadZipFile:
            return f'Bad zip file for {file_name}'
        else:
            return 0



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
        else:
            ebook = Pdf(book_file)
            status = book.extract_file()
            if status != 0:
                print(f'Unable to retrieve image from {file_name}')
            


            

if __name__ == '__main__':
    main()
