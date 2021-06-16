USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'

try:
    import argparse
except Exception:
    print(
        'This script uses the python "argparse" module. Please use Python '
        "2.7 or greater. Preferably Python 3.7"
    )
    raise

from manga_archiver import __version__


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="ma", description="Archive Manga into CBR format"
    )

    parser.add_argument(
        "--no-color", action="store_true", help="Do not use output coloring"
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-v", "--verbose", action="count", help="Display additional output"
    )
    parser.add_argument(
        "-D",
        "--delay",
        metavar="SECS",
        default="10",
        help=f"Time to delay between downloading chapters (default: 30)",
    )
    parser.add_argument(
        "-U",
        "--user-agent",
        metavar="STRING",
        help=f"The user-agent string to use (default: {USER_AGENT})",
    )
    parser.add_argument(
        "-M",
        "--manga-id",
        metavar="STRING",
        help="The URL ID of the manga to archive",
    )
    parser.add_argument(
        "-N",
        "--name",
        metavar="STRING",
        help="The name of the manga",
    )
    parser.add_argument(
        "--start-page",
        metavar="NUM",
        default="0",
        help="Start at page number NUM (default: 0)",
    )
    parser.add_argument(
        "--end-page",
        metavar="NUM",
        default=None,
        help="End at page number NUM)",
    )
    parser.add_argument(
        "--start-chapter",
        metavar="NUM",
        default="0",
        help="Start at chapter number NUM (default: 0)",
    )
    parser.add_argument(
        "--end-chapter",
        metavar="NUM",
        default=None,
        help="End at chapter number NUM)",
    )
    parser.add_argument(
        "--max-retries",
        metavar="NUM",
        default="3",
        help="Maximum number of retries for an image download (default: 3)",
    )
    parser.add_argument(
        "-s", "--source",
        default="manganelo",
        choices=["manganelo"],
        help="Where to obtain the manga (default: manganelo)",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip validation of image files",
    )

    return parser.parse_args(argv)

