from argparse import ArgumentParser

from jinja2 import Environment
from .main import Main


class Generate(Main):
    def __init__(self):
        self.output = "-"
        self.input = "-"
        self.data = ""
        self.params = {}

    def add_arguments(self, argp: ArgumentParser) -> None:
        argp.add_argument("--input", "-i", help="Input file")
        argp.add_argument("--output", "-o", help="Output")
        argp.add_argument("--data", "-d", help="Data file (YAML/JSON)")
        argp.add_argument("--config", "-c")
        # argp.add_argument("--templates", "-t")
        argp.add_argument("--delimiters", "-D", help="Delimiters style")
        return super().add_arguments(argp)

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
            assert not code

    def start(self):
        import yaml, json, re
        from jinja2 import FileSystemLoader, Template

        kwargs = {
            "trim_blocks": True,
            "lstrip_blocks": True,
        }
        delimiters = self.delimiters

        params = self.params
        data = self.data
        if data:
            if data.endswith(".json"):
                with as_source(data, "r") as r:
                    d = json.load(r)
                    params.update(d)
                    # pprint.pprint(d, stream=stderr)
            else:
                with as_source(data, "r") as r:
                    d = yaml.safe_load(r)
                    params.update(d)
                    # pprint.pprint(d, stream=stderr)

        config = self.config
        if config:
            kwargs = yaml.safe_load(config)

        # templates = self.templates
        # if templates:
        #     kwargs["loader"] = FileSystemLoader(templates)

        input = self.input
        output = self.output

        # env = Environment(**kwargs)
        if input:
            if not delimiters:
                if re.search(
                    r"(?i)\.(c|h|cpp|cxx|cc|hpp|java|kt|scala|js|jsx|ts|tsx|css|scss|sass|php|go|swift|dart|m|mm|groovy|rs|json)$",
                    input,
                ):
                    delimiters = "/"
                elif re.search(
                    r"(?i)\.(py|sh|rb|pl|tcl|lua|r|ps1|yaml|yml|conf|ini|cfg|dockerfile|awk|sed|vim|el|coffee|jl|nim|f|for)$",
                    input,
                ):
                    delimiters = "#"

            self.setup_delimeters(delimiters, kwargs)

            # print("kwargs:", kwargs)
            # print("delimiters:", delimiters)
            with as_source(input, "r") as r:
                kwargs.pop("loader", None)
                template = Template(r.read(), **kwargs)
            # template = env.get_template(input)
            out = template.render(params)
            with as_sink(output, "w") as w:
                w.write(out)

        # print(template.render(config_data))


def as_source(path="-", mode="rb"):
    if path and path != "-":
        return open(path, mode)
    assert path
    from sys import stdin

    return stdin.buffer if "b" in mode else stdin


def as_sink(path="-", mode="wb"):
    if path and path != "-":
        return open(path, mode)
    from sys import stdout

    return stdout.buffer if "b" in mode else stdout


if __name__ == "__main__":
    Generate().main()
