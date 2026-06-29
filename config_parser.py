import ast
import re
from collections import OrderedDict


class GodotConfig:

    def __init__(self):
        self.sections = OrderedDict()

    # ----------------------------
    # Reading
    # ----------------------------

    @classmethod
    def loads(cls, text: str):

        cfg = cls()

        current = None

        for raw_line in text.splitlines():

            line = raw_line.strip()

            if not line:
                continue

            if line.startswith(";"):
                continue

            if line.startswith("[") and line.endswith("]"):
                current = line[1:-1]

                cfg.sections[current] = OrderedDict()

                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            cfg.sections[current][key] = cls.parse_value(value)

        return cfg

    # ----------------------------
    # Values
    # ----------------------------

    @staticmethod
    def parse_value(value):

        value = value.strip()

        if value == "true":
            return True

        if value == "false":
            return False

        if re.fullmatch(r"-?\d+", value):
            return int(value)

        if re.fullmatch(r"-?\d+\.\d+", value):
            return float(value)

        try:
            return ast.literal_eval(value)
        except Exception:
            return value.strip('"')

    # ----------------------------
    # Access
    # ----------------------------

    def get(self, section, key, default=None):
        return self.sections.get(section, {}).get(key, default)

    def set(self, section, key, value):

        if section not in self.sections:
            self.sections[section] = OrderedDict()

        self.sections[section][key] = value

    # ----------------------------
    # Writing
    # ----------------------------

    def dumps(self):

        out = []

        for section, values in self.sections.items():

            out.append(f"[{section}]")
            out.append("")

            for key, value in values.items():

                out.append(
                    f"{key}={self.format_value(value)}"
                )

            out.append("")

        return "\n".join(out)

    @staticmethod
    def format_value(value):

        if isinstance(value, bool):
            return "true" if value else "false"

        if isinstance(value, str):
            return '"' + value.replace('"', '\\"') + '"'

        if isinstance(value, list):

            items = []

            for item in value:
                items.append(
                    GodotConfig.format_value(item)
                )

            return "[" + ", ".join(items) + "]"

        if isinstance(value, dict):

            items = []

            for k, v in value.items():

                items.append(
                    f'{GodotConfig.format_value(k)}: {GodotConfig.format_value(v)}'
                )

            return "{" + ", ".join(items) + "}"

        return str(value)