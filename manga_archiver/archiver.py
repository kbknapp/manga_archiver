from manga_archiver.printer import Printer

class Archiver:

    def __init__(self, args, session):
        self.args = args
        self.ptr = Printer(args)
        self.name = args.name
        self.manga_id = args.manga_id
        self.start_ch = int(args.start_chapter)
        self.start_pg = int(args.start_page)
        self.max_retries = int(args.max_retries)
        self.session = session
        self.delay = int(args.delay)
        self.verbose = args.verbose

    def print(self, msg):
        self.ptr.print(msg)

    def vprint(self, msg):
        self.ptr.vprint(msg)

    def eprint(self, msg):
        self.ptr.eprint(msg)

    def run(self):
        pass
