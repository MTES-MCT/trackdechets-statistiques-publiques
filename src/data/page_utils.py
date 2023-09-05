"""
This module contains utility functions useful for all pages.
"""
import re


def format_number(input_number: float, precision: int = 0) -> str:
    """Format a float to a string with thousands separated by space and rounding it at the given precision."""
    input_number = round(input_number, precision)
    return re.sub(r"\.0+", "", "{:,}".format(input_number).replace(",", " "))


def break_long_line(line: str, max_line_length: int = 26) -> str:
    """Format a string to add HTML line breaks (<br>) if it exceeds max_line_length."""
    length = 0

    new_pieces = []
    for piece in line.split(" "):
        length += len(piece)
        if length > max_line_length:
            piece = "<br>" + piece
            length = 0
        new_pieces.append(piece)

    return " ".join(new_pieces).replace(" <br>", "<br>")
