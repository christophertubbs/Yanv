"""
Runs YANV from the module level
"""
import sys

from launch_parameters import ApplicationArguments
from server import serve

serve(ApplicationArguments(*sys.argv))
