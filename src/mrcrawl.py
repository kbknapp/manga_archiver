import sys
import zipfile
import os
from lxml import html
import requests
import hashlib
from functools import partial

# TODO:
#  * Add files to dirs

def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

def main():
    # prefix for CBR and JPG files
    manga = ''
    # without trailing chapter, page, or '/'
    manga_base_url =  ''
    file_name = '{}_{:0>3}_{:0>3}.jpg'
    cbr = '{}_ch{:0>3}.cbr'
    manga_url = '{}/{}/{}'

    chapter = 0
    page = 0
    curr = ''
    prev = ''
    dups = 0

    while True:
        chapter += 1
        base_url = manga_url.format(manga_base_url, chapter, page)
        if not requests.get(base_url):
            break
        print('Downloading Chapter...{}'.format(chapter))
        imgs = []
        while True:
            page += 1
            base_url = manga_url.format(manga_base_url, chapter, page)
            req = requests.get(base_url)
            if req:
                html_page = requests.get(base_url).text
                doc = html.fromstring(html_page)
                img_urls = [i.attrib['src'] for i in doc.cssselect('img')]
                img = img_urls[0]
                print(' -> Downloading page...{}'.format(page))
                img_name = file_name.format(manga, str(chapter).rjust(3, '0'), str(page).rjust(3, '0'))
                with open(img_name, 'wb') as f:
                    f.write(requests.get(img).content)
                curr = md5sum(img_name)
                if curr == prev:
                    print(' -> Found Duplicate Image')
                    dups += 1
                    if dups > 5:
                        print(' -> Found Multiple Duplicates')
                        print(' -> Cleaning Up')
                        imgs.append(img_name)
                        for img in imgs:
                           os.remove(img)
                        print(' -> Done')
                        return 
                else:
                    prev = curr
                    dups = 0
                imgs.append(img_name)
            else:
                page = 0
                print(' -> Creating CBR...')
                zip = zipfile.ZipFile(cbr.format(manga, chapter), 'w')
                for img in imgs:
                    zip.write(img)
                    os.remove(img)
                zip.close()
                print(' -> Done')
                break

if __name__ == '__main__':
    sys.exit(main())
