import billboard_running as song
import sys
import uuid
import config

from jdw_billboarding.lib import jdw_osc_utils

config.load()

BBD_ROOT = config.BBD_ROOT

def resolve_bbd_path() -> str | None:
    for arg in sys.argv[1:]:
        if arg.endswith(".bbd"):
            return arg
    return None

def beep(amp=1.0):
    song.default_client().send(jdw_osc_utils.create_msg("/note_on_timed", [
            "blip",
            "beep-" + str(uuid.uuid4()),
            "0.25",
            0,
            "freq",
            875.0,
            "relT",
            0.2,
            "amp",
            amp
        ]))

bbd_path = resolve_bbd_path()

if "--stop" in sys.argv:
    song.quiet(bbd_path or BBD_ROOT + "tmp.bbd")

elif "--setup" in sys.argv:
    path = bbd_path or BBD_ROOT + "tmp.bbd"
    song.setup(path)
    song.configure(path)
    beep()

elif "--update" in sys.argv:
    if bbd_path:
        song.configure(bbd_path)
        beep(0.1)

elif "--nrt" in sys.argv:
    song.nrt_record(bbd_path or BBD_ROOT + "tmp.bbd")
else:
    if bbd_path:
        song.update_queue(bbd_path)

if not bbd_path and not any(f in sys.argv for f in ("--stop", "--setup", "--nrt")):
    print(f"Usage: {sys.argv[0]} <song.bbd> [--update|--setup|--stop|--nrt]", file=sys.stderr)
