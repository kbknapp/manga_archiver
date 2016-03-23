import sys
import zipfile
import os
from lxml import html
import requests

# TODO:
#  * Add files to dirs

def main():
    # prefix for CBR and JPG files
    manga = 'Blood_Lad'
    # without trailing chapter, page, or '/'
    manga_base_url =  'http://www.mangareader.net/blood-lad'
    file_name = '{}_{:0>3}_{:0>3}.jpg'
    cbr = '{}_ch{:0>3}.cbr'
    manga_url = '{}/{}/{}'

    chapter = 0
    page = 0

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
