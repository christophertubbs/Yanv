"""
Runs YANV from the module level
"""
import sys
import logging

from yanv.launch_parameters import ApplicationArguments
from yanv.server import serve

if __name__.endswith("__main__"):
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s %(lineno)d: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S%z"
    )
    aiohttp_logger: logging.Logger = logging.getLogger("aiohttp")
    aiohttp_logger.setLevel(logging.WARNING)
    aiohttp_access_logger: logging.Logger = logging.getLogger("aiohttp.access")
    aiohttp_access_logger.setLevel(logging.WARNING)


serve(ApplicationArguments(*sys.argv[1:]))
