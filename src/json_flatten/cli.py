"""
Command-line interface for json-flatten.

Usage: json-flatten [options] [infile] [outfile]
"""

import argparse
import json
import sys
from json_flatten import flatten


def main():
    """Main entry point for the json-flatten CLI tool."""
    parser = argparse.ArgumentParser(
        prog="json-flatten",
        description="Flatten a JSON object to a single dictionary of pairs",
    )
    parser.add_argument(
        "infile",
        nargs="?",
        default="-",
        help="Input JSON file (default: stdin, use '-' for stdin)",
    )
    parser.add_argument(
        "outfile",
        nargs="?",
        default="-",
        help="Output file (default: stdout, use '-' for stdout)",
    )

    args = parser.parse_args()

    # Read input
    if args.infile == "-":
        input_data = sys.stdin.read()
    else:
        with open(args.infile, "r") as f:
            input_data = f.read()

    # Parse JSON
    try:
        json_obj = json.loads(input_data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Flatten
    try:
        flattened = flatten(json_obj)
    except TypeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Convert flattened dict to JSON
    output_data = json.dumps(flattened, indent=2)

    # Write output
    if args.outfile == "-":
        print(output_data)
    else:
        with open(args.outfile, "w") as f:
            f.write(output_data)
            f.write("\n")


if __name__ == "__main__":
    main()
