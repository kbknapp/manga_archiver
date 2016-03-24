import sys
import zipfile
import os
from lxml import html
import requests
import hashlib
from functools import partial

# TODO:
#  * Add files to dirs
#  * Stop at md5: 492b6905734dc0010017c4d7f177daf1

STOP = '492b6905734dc0010017c4d7f177daf1'

def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

def main():
    # prefix for CBR and JPG files
    manga = 'Ousama_Game'
    # without trailing chapter, page, or '/'
    manga_base_url =  'http://www.mangareader.net/ousama-game'
    file_name = '{}_{:0>3}_{:0>3}.jpg'
    cbr = '{}_ch{:0>3}.cbr'
    manga_url = '{}/{}/{}'

    chapter = 0
    page = 0
    stops = 0

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
                if md5sum(img_name) == STOP:
                    stops += 1
                    if stops > 1:
                        stops = 0
                        imgs.append(img_name)
                        for img in imgs:
                            os.remove(img)
                        return 
                else:
                    stops = 0
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
