import json
import subprocess
import tempfile
import os
import pytest


def run_cli(*args, input_data=None):
    """Helper function to run the CLI and capture output."""
    cmd = ["json-flatten"] + list(args)
    result = subprocess.run(
        cmd,
        input=input_data,
        capture_output=True,
        text=True,
    )
    return result


def test_cli_stdin_to_stdout():
    """Test reading from stdin and writing to stdout."""
    input_json = '{"foo": {"bar": [1, true, null]}}'
    result = run_cli(input_data=input_json)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output == {
        "foo.bar.[0]$int": "1",
        "foo.bar.[1]$bool": "True",
        "foo.bar.[2]$none": "None",
    }


def test_cli_explicit_stdin_to_stdout():
    """Test with explicit '-' for stdin and stdout."""
    input_json = '{"test": [1, 2, 3]}'
    result = run_cli("-", "-", input_data=input_json)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output == {
        "test.[0]$int": "1",
        "test.[1]$int": "2",
        "test.[2]$int": "3",
    }


def test_cli_file_to_file():
    """Test reading from file and writing to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = os.path.join(tmpdir, "input.json")
        output_file = os.path.join(tmpdir, "output.json")

        # Create input file
        input_data = {"user": {"name": "Alice", "age": 28, "active": True}}
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        # Run CLI
        result = run_cli(input_file, output_file)
        assert result.returncode == 0

        # Check output file
        with open(output_file, "r") as f:
            output = json.load(f)

        assert output == {
            "user.name": "Alice",
            "user.age$int": "28",
            "user.active$bool": "True",
        }


def test_cli_file_to_stdout():
    """Test reading from file and writing to stdout."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = os.path.join(tmpdir, "input.json")

        # Create input file
        input_data = {"key": "value"}
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        # Run CLI
        result = run_cli(input_file, "-")
        assert result.returncode == 0

        output = json.loads(result.stdout)
        assert output == {"key": "value"}


def test_cli_stdin_to_file():
    """Test reading from stdin and writing to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "output.json")

        input_json = '{"nested": {"obj": {"key": "value"}}}'
        result = run_cli("-", output_file, input_data=input_json)
        assert result.returncode == 0

        # Check output file
        with open(output_file, "r") as f:
            output = json.load(f)

        assert output == {"nested.obj.key": "value"}


def test_cli_invalid_json():
    """Test error handling for invalid JSON input."""
    result = run_cli(input_data="invalid json")

    assert result.returncode == 1
    assert "Error: Invalid JSON input" in result.stderr


def test_cli_list_at_top_level():
    """Test error handling for list at top level."""
    result = run_cli(input_data='[{"name": "john"}]')

    assert result.returncode == 1
    assert "Error: Expected dict, got <class 'list'>" in result.stderr


def test_cli_complex_nested_structure():
    """Test with complex nested structure."""
    input_data = {
        "user": {
            "name": "Bob",
            "hobbies": ["reading", "swimming"],
            "address": {"city": "NYC", "zip": 10001},
        }
    }
    result = run_cli(input_data=json.dumps(input_data))

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output == {
        "user.name": "Bob",
        "user.hobbies.[0]": "reading",
        "user.hobbies.[1]": "swimming",
        "user.address.city": "NYC",
        "user.address.zip$int": "10001",
    }


def test_cli_empty_dict():
    """Test with empty dictionary."""
    result = run_cli(input_data="{}")

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output == {"$empty": "{}"}


def test_cli_help():
    """Test help message."""
    result = subprocess.run(
        ["json-flatten", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Flatten a JSON object" in result.stdout
    assert "infile" in result.stdout
    assert "outfile" in result.stdout
