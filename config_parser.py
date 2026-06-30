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
        """
        Godot's ConfigFile writes non-trivial Array/Dictionary values
        across multiple lines (e.g. a populated inventory dict). Values
        are accumulated until braces/brackets balance before parsing.
        """

        cfg = cls()

        current = None

        lines = text.splitlines()
        i = 0

        while i < len(lines):

            raw_line = lines[i]
            line = raw_line.strip()
            i += 1

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

            key, value_text = line.split("=", 1)
            key = key.strip()

            while cls._is_unbalanced(value_text) and i < len(lines):
                value_text += "\n" + lines[i]
                i += 1

            cfg.sections[current][key] = cls.parse_value(value_text)

        return cfg

    @staticmethod
    def _is_unbalanced(text: str) -> bool:
        """True if text has more open {[ than close }] outside of quotes."""

        depth = 0
        in_string = False
        quote_char = ""
        escape = False

        for ch in text:

            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == quote_char:
                    in_string = False
                continue

            if ch in ('"', "'"):
                in_string = True
                quote_char = ch
            elif ch in "{[":
                depth += 1
            elif ch in "}]":
                depth -= 1

        return depth > 0

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