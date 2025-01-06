"""

Template language for on-demand code generation.

Syntax:

    $plain = 1 2 3
        > 0 $plain 4 => 0 1 2 3 4

    $with_arg(arg, arg2) = I have $:arg hamsters and $:arg2 are long-haired
        > $with_arg(3, 0) => I have 3 hamsters and 0 are long-haired

"""
from dataclasses import dataclass
import re

# $ + lowercase letter or '_' + optional parenthesis
MACRO_CALL = "\\$[a-z|_]+(\\([1-9a-zA-Z,]+\\))?"
# Include '=', with or without whitespace separation, and the rest of the line
MACRO_DEFINITION = MACRO_CALL + "\\s+?=\\s+?(.*)"
WITHIN_PARENTHESES = "(?<=\\()(.*)(?=\\))"

@dataclass
class MacroDefinition:
    name: str
    args: list[str]
    template: str

@dataclass
class MacroCall:
    name: str
    args: list[str]
    source: str

def find_macro_defs(source: str) -> list[str]:
    lists =  regex_find(MACRO_DEFINITION, source)
    return lists

def find_macro_calls(source: str) -> list[str]:
    lists =  regex_find(MACRO_CALL, source)
    return lists

def parse_macro_def(source_line: str) -> MacroDefinition:
    assert len(regex_find(MACRO_DEFINITION, source_line)) > 0

    # e.g. $fish(head) = abcd:$head
    func_def = source_line.split("=")[0].strip()
    content_def = "=".join(source_line.split("=")[1:]).strip()
    args: list[str] = regex_find(WITHIN_PARENTHESES, func_def)[0].split(",") if "(" in func_def else []

    # Unbroken letters and bottom lines after '$'
    name = regex_find("(?<=\\$)[a-zA-Z|_]+", func_def)[0]

    return MacroDefinition(name, args, content_def)

def parse_macro_call(text: str) -> MacroCall:
    assert len(regex_find(MACRO_CALL, text)) > 0
    arg_values: list[str] = regex_find(WITHIN_PARENTHESES, text)[0].split(",") if "(" in text else []
    name: str = regex_find("(?<=\\$)[a-zA-Z|_]+", text)[0]

    return MacroCall(name, arg_values, text)

def resolve_macro(call: MacroCall, definitions: list[MacroDefinition]) -> str:
    filtered = [d for d in definitions if d.name == call.name]
    assert len(filtered) == 1
    definition = filtered[0]
    template = definition.template
    for i in range(0, len(call.args)):
        template = template.replace("$:" + definition.args[i], call.args[i])

    print("MACRO RESOLVED", template)
    return template


# Behaves like you would expect findall to do
def regex_find(regex: str, source: str) -> list[str]:
    return [s.group() for s in re.finditer(regex, source)]

def compile_macros(text: str, supplied_defs: list[str] = []) -> str:


    definition_lines = find_macro_defs(text) + supplied_defs
    definitions_removed = text
    for d in definition_lines:
        definitions_removed = definitions_removed.replace(d, "")

    definitions = [parse_macro_def(s) for s in definition_lines]
    calls = [parse_macro_call(call) for call in find_macro_calls(definitions_removed)]
    print("CALLS", calls)

    end_text = definitions_removed
    for c in calls:
        end_text = end_text.replace(c.source, resolve_macro(c, definitions))

    return end_text

if __name__ == "__main__":


    test_source = """

                        $fish = Sometimes I dream of fish
        $more_than(times) = more than $:times times

$fish $more_than(6)

    """

    end_text = compile_macros(test_source)

    print(end_text)
