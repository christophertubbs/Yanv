"""
Runs YANV from the module level
"""
import sys

from yanv.launch_parameters import ApplicationArguments
from yanv.server import serve

serve(ApplicationArguments(*sys.argv[1:]))
