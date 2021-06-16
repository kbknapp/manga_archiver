import sys


class Printer:
    def __init__(self, args):
        self.verbose = args.verbose
        if args.no_color:
            self.colors = {
                "RED": "",
                "GREEN": "",
                "BLUE": "",
                "PURPLE": "",
                "CYAN": "",
                "WHITE": "",
                "YELLOW": "",
                "BOLD": "",
                "OFF": "",
            }
        else:
            self.colors = {
                "RED": "\033[0;31m",
                "GREEN": "\033[0;32m",
                "BLUE": "\033[0;34m",
                "PURPLE": "\033[0;35m",
                "CYAN": "\033[0;36m",
                "WHITE": "\033[0;37m",
                "YELLOW": "\033[0;33m",
                "BOLD": "\033[1m",
                "OFF": "\033[0m",
            }

    def _print(
        self,
        msg,
        color="GREEN",
        indent=None,
        sigil="->",
        header=None,
        color_header=False,
    ):
        if header is None:
            header = ""
        color = self.colors[color]
        off = self.colors["OFF"]
        if indent is not None:
            spaces = "-" * indent
        else:
            spaces = ""
        if color_header:
            print(f"{color}{spaces}{sigil}{header} {off} {msg}")
        else:
            print(f"{color}{spaces}{sigil}{off}{header} {msg}")

    def vprint(self, msg, indent=None, sigil="", color_header=False):
        if self.verbose:
            self._print(
                msg,
                color="WHITE",
                indent=indent,
                sigil=sigil,
                header="INFO:",
                color_header=color_header,
            )

    def wprint(self, msg, indent=None, sigil="", color_header=False):
        self._print(
            msg,
            color="YELLOW",
            indent=indent,
            sigil=sigil,
            header="WARN:",
            color_header=color_header,
        )

    def print(self, msg, indent=None, sigil="->"):
        self._print(msg, color="GREEN", indent=indent, sigil=sigil)

    def eprint(self, msg, indent=None, sigil="", color_header=True, do_exit=False):
        self._print(
            msg,
            color="RED",
            indent=indent,
            sigil=sigil,
            header="error:",
            color_header=color_header,
        )
        if do_exit:
            sys.exit(1)
