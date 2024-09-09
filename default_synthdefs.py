import os

def get() -> list[str]:

    defs: list[str] = []
    # TODO: Not sure how to get "path of script but not path of any script executing the script"
    with open("/home/estrandv/programming/jdw-pycompose/scd/synthDefs.scd") as synthDefs:
        content = synthDefs.read()
        for cut in content.split("SynthDef.new"):
            if cut.strip() != "":
                full = "SynthDef.new" + cut
                defs.append(full)

    print(defs)
    return defs
