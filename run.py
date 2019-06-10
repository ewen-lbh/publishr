import os

from src.main import main
from src import internalconf
import logging
import argparse


def install_dependencies():
    import subprocess
    header = "Installing dependencies..."
    requirements = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    print(header)
    print("-" * len(header))
    print("""If this fails, 
    install dependencies yourself with
    pip install -r requirements.txt""")
    subprocess.call(['pip3', 'install', '-r', requirements])
    del header, requirements


if __name__ == '__main__':

    try:
        from src import main
        import coloredlogs
    except ModuleNotFoundError:
        install_dependencies()
    except ImportError:
        install_dependencies()

    parser = argparse.ArgumentParser(description='Automate music publishing')

    parser.add_argument('-c', '--config', metavar='PATH',
                        help='Use a config file (must be located in the repo\'s config folder')

    parser.add_argument('-v', '--verbosity', metavar='LEVEL', type=int, default=3,
                        help='Set verbosity level (0-4). Higher values fall back to 4. (0:FATAL (not recommended), 1:ERROR (only show errors), 2:WARNING (show errors & warnings), 3:INFO (default), 4:DEBUG (show everything, including debug information)')

    parser.add_argument('-d', '--dry-run', action='store_true',
                        help="Don't make any changes, but show what it would've done")

    parser.add_argument('-D', '--debug', action='store_true',
                        help='Debug mode')

    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Only shows errors.')

    parser.add_argument('-j','--no-auto-json', action='store_true',
                        help="Don't autocomplete the config filename with '.json'")
    
    parser.add_argument('-f', '--log-format', metavar='FORMAT NAME', default='notset',
                        help="Sets the format for logs: basic, minimal or extended.")

    args = parser.parse_args()

    # Fallback for verbosity levels > 4
    if args.verbosity > 4:
        args.verbosity = 4
    # Verbosity set to 4 if --debug
    if args.debug:
        args.verbosity = 4
    # Verbosity set to 1 if --quiet
    if args.quiet:
        args.verbosity = 1

    # Create a logger object.
    logger = logging.getLogger(__name__)

    # By default the install() function installs a handler on the root logger,
    # this means that log messages from your code and log messages from the
    # libraries that you use will all show up on the terminal.
    from src.internalconf import LOG_FORMATS, NUMERIC_LOG_LEVELS
    import coloredlogs

    if args.debug:
        format_type = 'extended'
    elif args.quiet:
        format_type = 'minimal'
    else:
        format_type = 'basic'

    if args.log_format != 'notset' and args.log_format in LOG_FORMATS.keys():
        format_type = args.log_format
    
    loglv = NUMERIC_LOG_LEVELS[args.verbosity]
    fmt = LOG_FORMATS[format_type]
    if args.dry_run:
        fmt = '(DRY RUN) '+fmt


    QUESTION = 60
    from logging import addLevelName
    addLevelName(QUESTION, "QUESTION")
    coloredlogs.install(level=loglv, fmt=fmt, style='{')

    main.main(args)