import os
import zipfile

CBZ = '{}_ch{:0>3}.cbz'

def make_cbz(imgs, manga, chapter):
    print(f'-> Creating CBZ of {manga} chapter {chpater}...', flush=True)
    with zipfile.ZipFile(CBZ.format(manga, chapter), 'w') as zip:
        for img in imgs:
            zip.write(img)
            os.remove(img)

