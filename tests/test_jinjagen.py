#!/bin/env python3
import unittest
import os
import tempfile
import json
import yaml
import subprocess
import sys
from pathlib import Path


class TestJinjagen(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.python_cmd = [sys.executable, "-m", "jinjagen"]

        # Print separator for test visibility
        print(f"\n{'-'*60}")

    def create_temp_file(self, content, suffix=".txt"):
        fd, path = tempfile.mkstemp(suffix=suffix, dir=self.temp_dir.name)
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def run_command(self, args, capture_output=True):
        """Run command and print what's being executed"""
        cmd = self.python_cmd + args
        print(f"[COMMAND] {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=capture_output, text=True)
        if capture_output:
            print(f"[STDOUT]\n{result.stdout}")
            if result.stderr:
                print(f"[STDERR]\n{result.stderr}")
        return result

    # @unittest.skip("Enable when needed")
    def test_basic_template_generation(self):
        # Create test files
        template = self.create_temp_file("Hello {{ name }}!", ".txt")
        data = self.create_temp_file(json.dumps({"name": "World"}), ".json")
        output = os.path.join(self.temp_dir.name, "output.txt")

        # Run generation
        result = self.run_command([template, output, "-d", data])

        # Verify output
        with open(output) as f:
            content = f.read()
            print(f"[OUTPUT FILE CONTENT]\n{content}")
            self.assertEqual(content, "Hello World!")

    # @unittest.skip("Enable when needed")
    def test_yaml_data_input(self):
        template = self.create_temp_file("Value: {{ value }}")
        data = self.create_temp_file("value: 42", ".yaml")
        output = os.path.join(self.temp_dir.name, "out.yaml")

        result = self.run_command([template, output, "-d", data, "-D."])

        with open(output) as f:
            content = f.read()
            print(f"[OUTPUT FILE CONTENT]\n{content}")
            self.assertEqual(content, "Value: 42")

    # @unittest.skip("Enable when needed")
    def test_auto_delimiters_for_code_files(self):
        template = self.create_temp_file("/*{ var }*/\n/*% if true %*/\nint x = 42;\n/*% endif %*/", ".c")
        data = self.create_temp_file(json.dumps({"var": "DECLARATION"}), ".json")
        output = os.path.join(self.temp_dir.name, "out.c")

        result = self.run_command([template, output, "-d", data])

        with open(output) as f:
            content = f.read()
            print(f"[OUTPUT FILE CONTENT]\n{content}")
            self.assertIn("DECLARATION", content)
            self.assertIn("int x = 42;", content)

    # @unittest.skip("Enable when needed")
    def test_explicit_delimiters(self):
        template = self.create_temp_file("#{ var }#\n#% if true %#\nx = 42\n#% endif %#", ".py")
        data = self.create_temp_file(json.dumps({"var": "GENERATED"}), ".json")
        output = os.path.join(self.temp_dir.name, "out.py")

        result = self.run_command([template, output, "-d", data, "-D", "#"])

        with open(output) as f:
            content = f.read()
            print(f"[OUTPUT FILE CONTENT]\n{content}")
            self.assertIn("GENERATED", content)
            self.assertIn("x = 42", content)

    # @unittest.skip("Enable when needed")
    def test_stdin_stdout(self):
        template_content = "Input: {{ input }}"
        data_content = json.dumps({"input": "from stdin"})
        data_file = self.create_temp_file(data_content)

        # Use subprocess with pipes
        cmd = self.python_cmd + ["-d", data_file, "-"]
        print(f"[COMMAND] {' '.join(cmd)} (with stdin pipe)")

        result = subprocess.run(cmd, input=template_content, capture_output=True, text=True)

        print(f"[STDOUT]\n{result.stdout}")
        self.assertEqual(result.stdout, "Input: from stdin")

    # @unittest.skip("Enable when needed")
    def test_template_directory(self):
        # Create template directory structure
        templates_dir = os.path.join(self.temp_dir.name, "templates")
        os.mkdir(templates_dir)

        base_template = os.path.join(templates_dir, "base.txt")
        with open(base_template, "w") as f:
            f.write("{% include 'partial.txt' %}")

        partial_template = os.path.join(templates_dir, "partial.txt")
        with open(partial_template, "w") as f:
            f.write("Partial content")

        output = os.path.join(self.temp_dir.name, "output.txt")

        result = self.run_command(["base.txt", output, "-t", templates_dir])

        with open(output) as f:
            content = f.read()
            print(f"[OUTPUT FILE CONTENT]\n{content}")
            self.assertEqual(content, "Partial content")

    # @unittest.skip("Enable when needed")
    def test_invalid_data_file(self):
        template = self.create_temp_file("{{ value }}")
        data = self.create_temp_file("not valid json or yaml", ".txt")
        output = os.path.join(self.temp_dir.name, "out.txt")

        result = self.run_command([template, output, "-d", data])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error", result.stderr)

    # @unittest.skip("Enable when needed")
    def test_missing_input_file(self):
        result = self.run_command(["nonexistent.txt"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error", result.stderr)

    # @unittest.skip("Enable when needed")
    # def test_version_flag(self):
    #     result = self.run_command(["--version"])
    #     self.assertEqual(result.returncode, 0)
    #     self.assertIn("0.0.1", result.stdout)

    # @unittest.skip("Enable when needed")
    def test_test_extra(self):
        with tempfile.TemporaryDirectory() as top:
            tmp = Path(top)
            input = tmp.joinpath("input.html")
            data = tmp.joinpath("data.json")
            config = tmp.joinpath("config.json")
            input.write_bytes(
                rb"""
<div>
{% if x == 3 %}
<small>{{ x }}</small>
{% endif %}
</div>"""
            )
            data.write_bytes(b'{"x":3}')
            # config.write_bytes(rb'{  "trim_blocks": false,   "lstrip_blocks": false}')
            config.write_bytes(rb'{  "trim_blocks": true,   "lstrip_blocks": false}')
            result = self.run_command([str(input), "-", "-d", str(data), "-c", str(config)])
            self.assertRegex(result.stdout, r"\n<div>\n<small>3</small>\n</div>")
            config.write_bytes(rb'{  "trim_blocks": false,   "lstrip_blocks": false}')
            result = self.run_command([str(input), "-", "-d", str(data), "-c", str(config)])
            self.assertRegex(result.stdout, r"\n<div>\n\n+<small>3</small>\n\n+</div>")


if __name__ == "__main__":
    unittest.main()
