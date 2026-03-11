#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging as log
import os
import platform
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import vstpreset

__version__ = "0.2.0"
log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)


def get_vst2presets(dir: str):
    """create a list of vstpreset files residing in 'dir' (no recursive)

    Args:
        dir (str): path to a directoy with vstpreset files

    Returns:
        _type_: list of paths
    """
    files = []
    for dirpath, dirnames, filenames in os.walk(dir):
        files.extend(filenames)
        break
    return [os.path.join(dirpath, file) for file in files if ".vstpreset" in file]  # pyright: ignore[reportPossiblyUnboundVariable]

def get_vst3cache_file(vst3cache: Path) -> Path:
    if vst3cache.suffix == ".xml":
        return vst3cache
    
    if vst3cache.is_dir():
        cachedirs  = vst3cache.glob("Cubase*64/*VST3 Cache/vst3plugins.xml")
        try:
            return list(cachedirs)[-1]
        except IndexError as e:
            log.error("Cannot automatically find the vst3plugins.xml. Please specify the path to ith with --vst3cache")
            raise ValueError("no vst3plugins.xml found") from e



def get_vst3_classid(vst3name: str, cachefile: Path):
    """tries go get the class id for a given VST3 plugin name from vst3plugins.xml

    Args:
        vst3name (str): name of the VST3
        basedir (str): Path to Steinberg preferences dir

    Raises:
        Exception: no Cubase pref dir found

    Returns:
        tuple: (classid, vendor)
    """
    log.info("Using VST3 Cache at '%s'", cachefile)
    tree = ET.parse(cachefile)
    root = tree.getroot()
    res = root.findall(f"./plugin/class/name[.='{vst3name}']/..")
    class_id = ""
    vendor = ""
    for a in res:
        if a.find("./category[.='Audio Module Class']/..") is not None:
            class_id = a.findtext("./cid")
            vendor = a.findtext("./vendor")
            break
    return (class_id, vendor)


def convert_presets(infiles: list, outputdir: str, class_id: str):
    for file in infiles:
        outfile = os.path.join(outputdir, "v2 " + os.path.basename(file))
        preset = vstpreset.parse_vst3preset_file(file)
        preset.class_id = class_id
        log.info("Converted preset %s", outfile)
        preset.write_file(outfile)


def main(args=None):
    os_platform = platform.system()
    userhome = os.path.expanduser("~")
    if os_platform == "Windows":
        default_prefs_basepath = Path(os.path.join(os.environ["APPDATA"], "Steinberg"))
        base_output_dir = os.path.join(userhome, "Documents", "VST3 Presets")
    elif os_platform == "Linux":  # well, just for testing under WSL
        current_user = os.environ["LOGNAME"]
        default_prefs_basepath = Path(
            f"/mnt/c/Users/{current_user}/AppData/Roaming/Steinberg"
        )
        base_output_dir = f"/mnt/c/Users/{current_user}/Documents/VST3 Presets"

    else:
        log.error("Sorry, this operating system is not supported")
        sys.exit(1)

    argparser = argparse.ArgumentParser(
        description="Converts .vstpreset files from VST2 plugins to .vstpreset files of the corresponding VST3 plugin, if they have differing VST IDs",
        epilog="USE AT YOUR OWN RISK! There is no warranty that this will work for any plugin",
    )
    argparser.add_argument(
        "--directory",
        "-d",
        type=str,
        required=True,
        help="Path to Directory with vstpresets of a VST2 plugin (IMPORTANT: no '\\' at the end!)",
    )
    argparser.add_argument(
        "--vst3name",
        "-3",
        type=str,
        required=True,
        help="Name of the corresponding VST3 plugin",
    )
    argparser.add_argument(
        "--vst3cache",
        type=str,
        default=None,
        help="Path to Cubase's vst3plugins.xml, e.g. c:\\User\\YOURUSERNAME\\AppData\\Roaming\\Steinberg\\Cubase 15_64\\Cubase Pro VST3 Cache\\vst3plugins.xml",
    )
    argparser.add_argument(
        "-i",
        "--id",
        type=str,
        help="Class ID of the target VST3 plugin, if it cannot be detected automatically",
    )
    argparser.add_argument(
        "--vendor",
        type=str,
        help="vendor name of the target VST3 plugin, if it cannot be detected automatically",
    )
    argparser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )

    args = argparser.parse_args(args)

    input_dir = args.directory or os.getcwd()
    infiles = get_vst2presets(input_dir.rstrip("\\").rstrip('"'))

    if args.vst3cache:
        vst3cache = Path(args.vst3cache.rstrip("\\"))
    else:
        vst3cache = default_prefs_basepath


    (class_id, vendor) = get_vst3_classid(args.vst3name, get_vst3cache_file(vst3cache))
    if not class_id:
        if args.id:
            class_id = args.id
        else:
            log.error(
                "Cannot determine class ID for '%s', please check the name given with --vst3name",
                args.vst3name,
            )
            sys.exit(2)
    if not vendor:
        if args.vendor:
            vendor = args.vendor
        else:
            log.error(
                "Cannot determine vendor name for '%s', please check the name given with --vst3name",
                args.vst3name,
            )
            sys.exit(2)

    output_dir = os.path.join(base_output_dir, vendor, args.vst3name)
    os.makedirs(output_dir, exist_ok=True)
    convert_presets(infiles, output_dir, class_id)


if __name__ == "__main__":
    sys.exit(main() or 0)
