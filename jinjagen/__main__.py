from jinja2 import Environment
from .main import Main, arg, flag


class Generate(Main):
    delimiters: str = flag("delimiters", "D", "Delimiters style", default="", choices=["#", "/", "."])
    templates: str = flag("templates", "t", "Template searchpath", default="", metavar="DIR")
    config_file: str = flag("config", "c", "Config file (YAML/JSON)", default="", metavar="FILE")
    data_file: str = flag("data", "d", "Data file (YAML/JSON)", default="", metavar="FILE")
    input: str = arg("Input file", "INPUT", default="-")
    output: str = arg("Output file", "OUTPUT", default="-", nargs="?")

    def __init__(self):
        self.params = {}

    def setup_delimeters(self, code: str, opt: dict):
        if code == "/":
            opt["block_start_string"] = "/*%"
            opt["block_end_string"] = "%*/"
            opt["variable_start_string"] = "/*{"
            opt["variable_end_string"] = "}*/"
            opt["comment_start_string"] = "/*#"
            opt["comment_end_string"] = "#*/"
        elif code == "#":
            opt["block_start_string"] = "#%"
            opt["block_end_string"] = "%#"
            opt["variable_start_string"] = "#{"
            opt["variable_end_string"] = "}#"
            opt["comment_start_string"] = "##"
            opt["comment_end_string"] = "##"
        else:
            assert not code or code == "."

    def load_data(self, f: str):
        if f.endswith(".json"):
            import json

            with as_source(f, "r") as r:
                return json.load(r)
        else:
            import yaml

            with as_source(f, "r") as r:
                return yaml.safe_load(r)

    def start(self):
        import re
        from jinja2 import FileSystemLoader, Template

        kwargs = {
            "trim_blocks": True,
            "lstrip_blocks": True,
        }
        delimiters = self.delimiters
        params = self.params

        if self.data_file:
            params.update(self.load_data(self.data_file))

        if self.config_file:
            kwargs.update(self.load_data(self.config_file))

        templates = self.templates
        if templates:
            kwargs["loader"] = FileSystemLoader(templates)

        input = self.input
        output = self.output

        if input:
            if not delimiters:
                if re.search(
                    r"(?i)\.(c|h|cpp|cxx|cc|hpp|java|kt|scala|js|jsx|ts|tsx|css|scss|sass|php|go|swift|dart|m|mm|groovy|rs|json)$",
                    output,
                ):
                    delimiters = "/"
                elif re.search(
                    r"(?i)\.(py|sh|rb|pl|tcl|lua|r|ps1|yaml|yml|conf|ini|cfg|dockerfile|awk|sed|vim|el|coffee|jl|nim|f|for)$",
                    output,
                ):
                    delimiters = "#"

            self.setup_delimeters(delimiters, kwargs)

            if templates:
                env = Environment(**kwargs)
                template = env.get_template(input)
            else:
                with as_source(input, "r") as r:
                    kwargs.pop("loader", None)
                    template = Template(r.read(), **kwargs)

            out = template.render(params)
            with as_sink(output, "w") as w:
                w.write(out)


def as_source(path="-", mode="rb"):
    if path != "-":
        return open(path, mode)
    from sys import stdin

    return stdin.buffer if "b" in mode else stdin


def as_sink(path="-", mode="wb"):
    if path != "-":
        return open(path, mode)
    from sys import stdout

    return stdout.buffer if "b" in mode else stdout


def main():
    """CLI entry point."""
    Generate().main()


if __name__ == "__main__":
    main()
