"""
Application specific metadata values used to convey basic operating parameters
"""
import logging
import os
import typing

APPLICATION_NAME: typing.Final[str] = os.environ.get("YANV_APPLICATION_NAME", "Yanv")
APPLICATION_DESCRIPTION: typing.Final[str] = os.environ.get(
    "YANV_APPLICATION_DESCRIPTION",
    """Displays information about Netcdf-like files within your browser"""
)
DEFAULT_PORT: typing.Final[int] = int(os.environ.get("YANV_DEFAULT_PORT", 10324))
ALLOW_REMOTE: typing.Final[bool] = os.environ.get("YANV_ALLOW_REMOTE", "no").lower() in ('t', 'true', 'y', 'yes', '1')
INDEX_PAGE: typing.Final[str] = os.environ.get("YANV_INDEX_PAGE", "")

if ALLOW_REMOTE:
    logging.warning(
        f"{APPLICATION_NAME} has been configured to allow remote connections. "
        f"Ensure https is enable or else risk internal file inspection from remote sources."
        f"Use at your own risk."
    )