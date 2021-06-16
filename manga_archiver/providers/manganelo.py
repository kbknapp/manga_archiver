import os
import sys
import time

from lxml import html
from PIL import Image

from manga_archiver.archiver import Archiver
from manga_archiver.printer import Printer
from manga_archiver import FILE_NAME, cbz

class MangaNelo(Archiver):
    #MANGANELO = 'https://manganelo.tv/chapter/manga-dr980474/chapter-0
    URL = 'https://manganelo.tv/chapter/{}/chapter-{}'
    BASE_URL = 'https://manganelo.tv/{}'

    def __init__(self, args, session):
        Archiver.__init__(self, args, session)

    def run(self):
        self.print(f'Downloading {self.name} from MangaNelo')
        self.vprint(f'Starting with chapter...{self.start_ch}')

        curr = ''
        prev = ''
        ch = self.start_ch
        url = MangaNelo.URL.format(self.manga_id, ch)
        has_end = self.args.end_chapter is not None
        if has_end:
            end_ch = int(self.args.end_chapter)

        while True:
            self.print(f'Downloading Chapter...{ch}')
            imgs = []

            self.vprint(f'Downloading from URL: {url}')
            req = self.session.get(url)
            html_txt = req.text
            doc = html.fromstring(html_txt)
            img_urls = [i.attrib['data-src'] for i in doc.cssselect('img') if i.attrib.has_key('class') and i.attrib['class'] == 'img-loading']
            num_imgs = len(img_urls)
            for (pg, img) in enumerate(img_urls):
                self.ptr.vprint(f'Downloading page...{pg}/{num_imgs}')
                retries = 0
                success = False
                while retries < self.max_retries:
                    img_name = FILE_NAME.format(self.name, '', str(ch).rjust(3, '0'), str(pg).rjust(3, '0'))
                    with open(img_name, 'wb') as f:
                        f.write(self.session.get(img).content)

                    if self.args.no_validate or self._validjpg(img_name):
                        imgs.append(img_name)
                        success = True
                        break
                    else:
                        self.vprint(f'Bad image file, retrying...{retries}/{self.max_retries}')
                        retries += 1
                if not success:
                    self.eprint('Could not download image', do_exit=True)
            cbz.make_cbz(imgs, self.name, ch)
            next_ch_route = [i.attrib['href'] for i in doc.cssselect('a') if i.attrib.has_key('class') and i.attrib['class'] == 'navi-change-chapter-btn-next a-h']
            ch += 1
            if next_ch_route:
                self.vprint('Found another chapter')
                url = self.BASE_URL.format(next_ch_route[0])
            else:
                self.print('No more chapters!')
                break
            if has_end and ch > end_ch:
                break
            self.print(f'Sleeping for {self.delay}s')
            time.sleep(self.delay)

    def _validjpg(self, jpg):
        self.ptr.vprint('Validating Image...')
        if os.path.getsize(jpg) == 0:
            self.ptr.vprint('Is zero length...')
            return False
        self.ptr.vprint('Is not zero length...')
        try:
            im = Image.open(jpg)
            self.ptr.vprint('Can open image...')
        except:
            self.ptr.vprint(f'Image does not open...{e}')
            return False
        try:
            im.verify()
            self.ptr.vprint('Image verifies...')
            # if verb: print('   -> Image loads...', end='', flush=True)
            # im.load()
            # if verb: print('Yes')
        except:
            self.ptr.vprint('Image does not verify...')
            return False
        self.ptr.vprint('Valid Image!')
        return True
