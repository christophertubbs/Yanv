"""
Handling for when a requester interrogates the host file system
"""
import logging
import ipaddress

from pathlib import Path

from aiohttp import web

from yanv.utilities.common import local_only

LOGGER: logging.Logger = logging.getLogger(Path(__file__).stem)


@local_only
async def navigate(request: web.Request) -> web.Response:
    """
    Provide file system autocomplete suggestions based on the 'term' passed. Marked as 'local_only' due to
    enormous security risks related to remote investigation of the file system.

    Args:
        request: A request with a key of 'term' containing a partial file system path

    Returns:
        A json response with a list of valid paths
    """
    paths = []

    # Force an empty result if the call isn't coming from within the house, for safety
    caller_ip: tuple[str, str] = request.transport.get_extra_info("peername")
    server_ip: tuple[str, str] = request.transport.get_extra_info("sockname")

    if not (caller_ip and server_ip):
        return web.json_response(data=paths)

    caller_address: ipaddress.IPv4Address = ipaddress.ip_address(address=caller_ip[0])
    server_address: ipaddress.IPv4Address = ipaddress.ip_address(address=server_ip[0])

    if caller_address != server_address and not caller_address.is_loopback:
        return web.json_response(data=paths)

    term = request.query.get("term")
    LOGGER.debug(f"Navigating from: %s", term)

    if term and not any(map(lambda protocol: term.startswith(protocol), ["ssh", "http", "ftp", "sftp"])):
        term_path = Path(term)

        if term_path.exists() and term_path.is_dir():
            paths.extend([
                str(child)
                for child in term_path.iterdir()
                if (child.is_dir() or str(child).endswith("nc"))
                   and not str(child.name).startswith(".")
            ])
        elif not term_path.exists():
            match_name = str(term_path)
            term_path = term_path.parent

            if term_path.exists():
                paths.extend([
                    str(child)
                    for child in term_path.iterdir()
                    if str(child).startswith(match_name)
                        and (child.is_dir() or str(child).endswith("nc"))
                ])

    return web.json_response(data=paths)
