

from decimal import Decimal

from shuttle_notation.parsing.information_parsing import DynamicArg, parse_args


# Allows parsing of args strings in order, applying the operands of the latter to the former
# This is normally done as part of a full Element parse, but becomes necessary for element-less arg strings with "parents"
def parse_orphaned_args(sources: list[str]) -> dict[str, Decimal]:

    final_args: dict[str, Decimal] = {}
    for source in sources:
        rel_args: dict[str, DynamicArg] = parse_args(source)
        for arg_key in rel_args:
            if arg_key not in final_args:
                value = rel_args[arg_key].value
                if rel_args[arg_key].operator == "-":
                    value *= -1
                final_args[arg_key] = value
            else:
                new = rel_args[arg_key]

                if new.operator == "*":
                    final_args[arg_key] *= new.value
                elif new.operator == "+":
                    final_args[arg_key] += new.value
                elif new.operator == "-":
                    final_args[arg_key] -= new.value
                else:
                    final_args[arg_key] = new.value

    return final_args
