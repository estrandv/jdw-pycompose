import os
import tomllib

BBD_ROOT = "/home/estrandv/programming/jdw-pycompose/songs/"
ROUTER_HOST = "127.0.0.1"
ROUTER_PORT = 13339
SAMPLE_PACK_DIR = "~/sample_packs"
SYNTHDEFS_SCD_PATH = "/home/estrandv/programming/jdw-pycompose/scd/synthDefs.scd"
TEMPLATE_SYNTHS_PATH = "/home/estrandv/programming/jdw-pycompose/scd-templating/template_synths.txt"
COMMON_MACROS_DIR = "/home/estrandv/programming/jdw-pycompose/songs"
FIRST_BUFFER_INDEX = 100
DELAY_INTER_MESSAGE = 0.005
DELAY_CONFIGURE = 0.001
DELAY_NRT_PRELOAD = 0.005
DELAY_UPDATE = 0.005
DELAY_QUIET = 0.005

_loaded = False


def _central_config_path():
    if jdw_config := os.environ.get("JDW_CONFIG"):
        if os.path.exists(jdw_config):
            return jdw_config
    xdg = os.path.expanduser("~/.config/jdw.toml")
    if os.path.exists(xdg):
        return xdg
    return None


def _load_central():
    path = _central_config_path()
    if path is None:
        return {}
    try:
        with open(path, "rb") as f:
            root = tomllib.load(f)
        return root.get("pycompose", {})
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        return {}


def _apply(cfg):
    global BBD_ROOT, ROUTER_HOST, ROUTER_PORT, SAMPLE_PACK_DIR
    global SYNTHDEFS_SCD_PATH, TEMPLATE_SYNTHS_PATH, COMMON_MACROS_DIR
    global FIRST_BUFFER_INDEX
    global DELAY_INTER_MESSAGE, DELAY_CONFIGURE, DELAY_NRT_PRELOAD
    global DELAY_UPDATE, DELAY_QUIET

    BBD_ROOT = cfg.get("bbd_root", BBD_ROOT)
    ROUTER_HOST = cfg.get("router_host", ROUTER_HOST)
    ROUTER_PORT = cfg.get("router_port", ROUTER_PORT)
    SAMPLE_PACK_DIR = cfg.get("sample_pack_dir", SAMPLE_PACK_DIR)
    SYNTHDEFS_SCD_PATH = cfg.get("synthdefs_scd_path", SYNTHDEFS_SCD_PATH)
    TEMPLATE_SYNTHS_PATH = cfg.get("template_synths_path", TEMPLATE_SYNTHS_PATH)
    COMMON_MACROS_DIR = cfg.get("common_macros_dir", COMMON_MACROS_DIR)
    FIRST_BUFFER_INDEX = cfg.get("first_buffer_index", FIRST_BUFFER_INDEX)

    delays = cfg.get("delays", {})
    DELAY_INTER_MESSAGE = delays.get("inter_message", DELAY_INTER_MESSAGE)
    DELAY_CONFIGURE = delays.get("configure", DELAY_CONFIGURE)
    DELAY_NRT_PRELOAD = delays.get("nrt_preload", DELAY_NRT_PRELOAD)
    DELAY_UPDATE = delays.get("update", DELAY_UPDATE)
    DELAY_QUIET = delays.get("quiet", DELAY_QUIET)


def load(path="config.toml"):
    global _loaded

    _loaded = True

    # Layer 1: central config (~/.config/jdw.toml)
    central = _load_central()
    _apply(central)

    # Layer 2: per-app config.toml (overrides central)
    try:
        with open(path, "rb") as f:
            local = tomllib.load(f)
        _apply(local)
    except FileNotFoundError:
        pass
    except tomllib.TOMLDecodeError as e:
        print(f"Warning: Failed to parse config file '{path}': {e}")
