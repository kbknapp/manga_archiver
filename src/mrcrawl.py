#!/usr/bin/env python
import clapp
import hashlib
from functools import partial
from lxml import html
import requests
import sys
import os
import os.path
import zipfile
from PIL import Image

# TODO:

MANGAREADER = 'http://www.mangareader.net/{}/{}/{}'
MANGATOWN = 'http://www.mangatown.com/manga/{}/{}c{:0>3}/{}.html'
FILE_NAME = '{}_{:0>3}_{:0>3}.jpg'
CBR = '{}_ch{:0>3}.cbr'

def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

def getonly(cxt):
    if cxt['only']:
        if cxt['page']:
            return 'PAGE'
        elif cxt['chapter']:
            return 'CHAPTER'
        elif cxt['vol']:
            return 'VOLUME'
    return ''

def validjpg(jpg, verb):
    if verb: print(' -> Validating Image...')
    if verb: print('   -> Zero length...', end='', flush=True)
    if os.path.getsize(jpg) == 0:
        if verb: print('Yes')
        return False
    if verb: print('No')
    try:
        if verb: print('   -> Can open image...', end='', flush=True)
        im = Image.open(jpg)
        if verb: print('Yes')
        if verb: print('   -> Image verifies...', end='', flush=True)
        im.verify()
        if verb: print('Yes')
        # if verb: print('   -> Image loads...', end='', flush=True)
        # im.load()
        # if verb: print('Yes')
    except:
        if verb: print('No')
        return False
    if verb: print('   -> Valid Image...')
    return True

def parse_cli():
    app = clapp.App()
    app.name = 'MR Crawl'
    app.author = 'Kevin K. <kbknapp@gmail.com>'
    app.version = '0.2.3'
    app.about = 'Command Line utility to download manga into CBR files'
    
    app.new_arg('manga', \
            index=1, \
            required=True, \
            help='The name of the manga, lowercase, hyphens for spaces')
    app.new_arg('page', \
            short='-p', \
            long='--page',\
            args_taken=1, \
            help='Start at page number')
    app.new_arg('chapter', \
            short='-c', \
            long='--chapter',\
            args_taken=1, \
            help='Start at chapter number')
    app.new_arg('src', \
            short='-s', \
            long='--src',\
            args_taken=1, \
            help='Source to download from (all lowercase, nospaces; i.e mangareader [default])')
    app.new_arg('vol', \
            short='-V', \
            long='--volume',\
            args_taken=1, \
            help='Start at volume number (implies --volumes)')
    app.new_arg('vols', \
            long='--volumes',\
            help='This manga uses volumes in the URL (mangatown only)')
    app.new_arg('verb', \
            long='--verbose',\
            help='Use verbose output')
    app.new_arg('only', \
            long='--only',\
            help='Only download the specified page, volume, or chapter')

    return app.start()

def make_cbr(imgs, manga, chapter):
    print('\n -> Creating CBR...', end='', flush=True)
    zip = zipfile.ZipFile(CBR.format(manga, chapter), 'w')
    for img in imgs:
        zip.write(img)
        os.remove(img)
    zip.close()
    print('Done')

def cleanup(imgs):
    print(' -> Cleaning Up...', end='', flush=True)
    for img in imgs:
       os.remove(img)
    print('Done')

def mangareader(cxt):
    print('Downloading {} from {}'.format(cxt['manga'], 'mangareader'))
    # prefix for CBR and JPG files
    manga = cxt['manga']
    only = getonly(cxt)
    verb = cxt['verb']

    chapter = 0
    if cxt['chapter']:
        chapter = int(cxt['chapter'][0]) - 1
        if verb: print(':: Starting with chapter...{}'.format(chapter))
    page = 0
    if cxt['page']:
        page = int(cxt['page'][0]) - 1
        if verb: print(':: Starting with page...{}'.format(page))
    curr = ''
    prev = ''
    dups = 0

    while True:
        chapter += 1
        url = MANGAREADER.format(manga, chapter, page)
        if not requests.get(url):
            break
        print(':: Downloading Chapter...{}'.format(chapter))
        imgs = []
        while True:
            page += 1
            url = MANGAREADER.format(manga, chapter, page)
            req = requests.get(url)
            if req:
                html_txt = requests.get(url).text
                doc = html.fromstring(html_txt)
                img_urls = [i.attrib['src'] for i in doc.cssselect('img')]
                img = img_urls[0]
                print(' -> Page...%d\r'%page, end='')
                img_name = FILE_NAME.format(manga, str(chapter).rjust(3, '0'), str(page).rjust(3, '0'))
                with open(img_name, 'wb') as f:
                    f.write(requests.get(img).content)
                if only == 'PAGE':
                    return
                curr = md5sum(img_name)
                if curr == prev:
                    dups += 1
                    if dups > 3:
                        print('\n -> Found Multiple Duplicates')
                        imgs.append(img_name)
                        cleanup(imgs)
                        return 
                else:
                    prev = curr
                    dups = 0
                imgs.append(img_name)
            else:
                page = 0
                make_cbr(imgs, manga, chapter)
                if only == 'CHAPTER':
                    return
                break

def mangatown(cxt):
    print(':: Downloading {} from {}'.format(cxt['manga'], 'mangatown'))
    verb = cxt['verb']
    # prefix for CBR and JPG files
    manga = cxt['manga']
    only = getonly(cxt)

    chapter = 1
    if cxt['chapter']:
        chapter = int(cxt['chapter'][0])
        if verb: print(':: Starting with chapter...{}'.format(chapter))
    page = 1
    if cxt['page']:
        page = int(cxt['page'][0])
        if verb: print(':: Starting with page...{}'.format(page))
    vol = 1
    uses_vols = False
    if cxt['vol'] or cxt['vols']:
        uses_vols = True
    if uses_vols:
        if verb: print(':: Using volumes')
        if cxt['vol']:
            vol = int(cxt['vol'][0]) 
            if verb: print(':: Starting with volume...{}'.format(vol))
    incd_ch   = False
    incd_vol  = False

    while True:
        vol_str = ''
        if cxt['vol'] or cxt['vols']:
            vol_str = 'v{:0>2}/'.format(vol)
        url = MANGATOWN.format(manga, vol_str, chapter, page)
        if verb: print(':: Using URL...{}'.format(url))
        print(':: Downloading Chapter...{}'.format(chapter))
        imgs = []

        while True:
            url = MANGATOWN.format(manga, vol_str, chapter, page)
            req = requests.get(url)
            if req:
                if verb: print(' -> Good Request')
                html_txt = req.text
                doc = html.fromstring(html_txt)
                img_urls = [i.attrib['src'] for i in doc.cssselect('img')]
                img = img_urls[0]
                link_urls = [i.attrib['href'] for i in doc.cssselect('a') if i.get('onclick') == 'return next_page();']
                if verb and link_urls: print(' -> Found next page URL...{}'.format(link_urls[0]))
                if not link_urls and uses_vols and not incd_vol:
                    if verb: 
                        print(' -> No valid link for next page')
                        print(' -> Incrementing volume number')
                    vol += 1
                    vol_str = 'v{:0>2}/'.format(vol)
                    page = 1
                    incd_vol = True
                    if imgs:
                        make_cbr(imgs, manga, chapter-1)
                        if only == 'VOLUME':
                            return
                        imgs = []
                    continue

                if link_urls[0] == 'javascript:void(0);' and not incd_ch:
                    if verb: 
                        print(' -> No valid link for next page')
                        print(' -> Incrementing chapter number')
                    chapter += 1
                    page = 1
                    incd_ch = True
                    if imgs:
                        make_cbr(imgs, manga, chapter-1)
                        if only == 'CHAPTER':
                            return
                        imgs = []
                    break
                elif link_urls[0] == 'javascript:void(0);' and uses_vols and not incd_vol:
                    if verb: 
                        print(' -> No valid link for next page')
                        print(' -> Incrementing volume number')
                    vol += 1
                    page = 1
                    incd_vol = True
                    if imgs:
                        make_cbr(imgs, manga, chapter-1)
                        if only == 'VOLUME':
                            return
                        imgs = []
                    break
                elif link_urls[0] == 'javascript:void(0);' and incd_ch and (incd_vol or not uses_vols):
                    if verb: 
                        print(' -> No valid link for next page')
                    print(' :: Done')
                    if imgs:
                        make_cbr(imgs, manga, chapter-1)
                        imgs = []
                    return
                else:
                    incd_vol = False
                    incd_ch = False
                url = link_urls[0]
                if not verb:
                    print(' -> Downloading Page...%d\r'%page, end='')
                else:
                    print(' -> Downloading Page...%d'%page)
                img_name = FILE_NAME.format(manga, str(chapter).rjust(3, '0'), str(page).rjust(3, '0'))
                retry = True 
                while retry:
                    with open(img_name, 'wb') as f:
                        if verb: print(' -> Using IMG URL...{}'.format(img))
                        f.write(requests.get(img).content)
                    if not validjpg(img_name, verb):
                        if verb: print(' -> Bad image file, retrying...{}'.format(img))
                    else:
                        retry = False
                if only == 'PAGE':
                    return
                imgs.append(img_name)
            else:
                if verb: 
                    print(' -> Bad Request')
                    print(' -> Resetting Page Number')
                    print(' -> Incrementing Chapter Number')
                page = 1
                make_cbr(imgs, manga, chapter)
                chapter += 1
                break
            page += 1

if __name__ == '__main__':
    cxt = parse_cli()
    src = ''
    if cxt['src']:
        src = cxt['src'][0]
    if src == 'mangatown' or cxt['vol'] or cxt['vols']:
        sys.exit(mangatown(cxt))
    sys.exit(mangareader(cxt))
