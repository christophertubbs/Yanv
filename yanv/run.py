#!/usr/bin/env python3
"""
@TODO: Describe the application here
"""
import typing

from argparse import ArgumentParser


class Arguments(object):
    def __init__(self, *args):
        # Replace '__option' with any of the expected arguments
        self.__option: typing.Optional[str] = None

        self.__parse_command_line(*args)

    # Add a property for each argument
    @property
    def option(self) -> str:
        return self.__option

    def __parse_command_line(self, *args):
        parser = ArgumentParser("Put the description of your application here")

        # Add Arguments
        parser.add_argument(
            "-o",
            metavar="option",
            dest="option",
            type=str,
            default="default",
            help="This is an example of an option"
        )

        # Parse the list of args if one is passed instead of args passed to the script
        if args:
            parameters = parser.parse_args(args)
        else:
            parameters = parser.parse_args()

        # Assign parsed parameters to member variables
        self.__option = parameters.option


def main():
    """
    Define your main function here
    """
    arguments = Arguments()


if __name__ == "__main__":
    main()
