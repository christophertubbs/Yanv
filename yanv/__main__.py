"""
Runs YANV from the module level
"""
import sys
import logging
import logging.handlers
import typing

from yanv.launch_parameters import ApplicationArguments
from yanv.server import serve

if __name__.endswith("__main__"):
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s %(lineno)d: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S%z",
        force=True,
        handlers=[
            logging.StreamHandler(),
            logging.handlers.RotatingFileHandler(
                filename="yanv.log",
                maxBytes=5 * 1000 * 1000,
            )
        ]
    )
    aiohttp_logger: logging.Logger = logging.getLogger("aiohttp")
    aiohttp_logger.setLevel(logging.WARNING)
    aiohttp_access_logger: logging.Logger = logging.getLogger("aiohttp.access")
    aiohttp_access_logger.setLevel(logging.WARNING)


def main() -> typing.NoReturn:
    try:
        logging.info(f"Launching yanv from a module level...")
        exit_code: int = serve(ApplicationArguments(*sys.argv[1:]))
    except KeyboardInterrupt:
        logging.critical(f"Uncaught keyboard interrupt encountered. Exitting...")
        exit_code: int = 0
    except BaseException as unexpected_error:
        logging.critical(f"Unexpected error encountered: {unexpected_error}", exc_info=True)
        exit_code: int = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
