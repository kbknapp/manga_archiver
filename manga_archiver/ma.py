#!/usr/bin/env python3

import sys
import os
import os.path

#import hashlib
#from functools import partial
import requests

from manga_archiver.providers import manganelo


from http import cookiejar  # Python 2: import cookielib as cookiejar
class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False

# def md5sum(filename):
#     with open(filename, mode='rb') as f:
#         d = hashlib.md5()
#         for buf in iter(partial(f.read, 128), b''):
#             d.update(buf)
#     return d.hexdigest()

def cleanup(imgs):
    print(' -> Cleaning Up...', end='', flush=True)
    for img in imgs:
       os.remove(img)
    print('Done')

def main(args):
    s = requests.Session()
    s.cookies.set_policy(BlockAll())
    s.headers.update({'User-Agent': args.user_agent})
    if args.source == 'manganelo':
        archiver = manganelo.MangaNelo(args, s)
        return archiver.run()
    return 1

if __name__ == '__main__':
    sys.exit(main())
