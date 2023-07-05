#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys
import platform
import os
import xml.etree.ElementTree as ET
import vstpreset
import logging as log
__version__="0.1.0"
log.basicConfig(format='%(levelname)s: %(message)s', level=log.INFO)


def get_vst2presets(dir: str):
    """create a list of vstpreset files residing in 'dir' (no recursive)

    Args:
        dir (str): path to a directoy with vstpreset files

    Returns:
        _type_: list of paths
    """
    files = []
    for (dirpath, dirnames, filenames) in os.walk(dir):
        files.extend(filenames)
        break
    return [os.path.join(dirpath, file) for file in files if ".vstpreset" in file ]

def get_vst3_classid(vst3name: str, basedir: str):
    """tries go get the class id for a given VST3 plugin name from vst3plugins.xml

    Args:
        vst3name (str): name of the VST3
        basedir (str): Path to Steinberg preferences dir

    Raises:
        Exception: no Cubase pref dir found

    Returns:
        tuple: (classid, vendor)
    """
    dirs = []
    cachefile = ""
    if "vst3plugins.xml" in basedir:
        cachefile = basedir
    else:
        for (dirpath, dirnames, filenames) in os.walk(basedir):
            dirs = [os.path.join(dirpath, d) for d in dirnames if "Cubase" in d]
            break
        for nr in ("12","11","10"):
            appdirs = [d for d in dirs if nr in d]
            if appdirs:
                break
        try:
            appdir = appdirs.pop(0)
        except IndexError:
            log.error("Cannot find Preferences Directory for Cubase in %s. Please specify one with --prefdir", basedir)
            raise
        for (dirpath, dirnames, filenames) in os.walk(appdir):
            for d in dirnames:
                if "VST3 Cache" in d:
                    cachefile = os.path.join(dirpath, d, "vst3plugins.xml")
                    break
            break

    if not os.path.isfile(cachefile):
        log.error("Cannot find vst3plugins.yaml in '%s/VST3 Cache'", appdir)
        raise FileNotFoundError(f"{appdir}/VST3 Cache/vst3plugins.xml")
    
    tree = ET.parse(cachefile)
    root = tree.getroot()
    res = root.findall(f"./plugin/class/name[.='{vst3name}']/..")
    class_id = ""
    vendor = ""
    for a in res:
        if a.find("./category[.='Audio Module Class']/.."):
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
        default_prefs_basepath = os.path.join(os.environ["APPDATA"], "Steinberg")
        base_output_dir = os.path.join(userhome, "Documents", "VST3 Presets")
    elif os_platform == "Linux": # well, just for testing under WSL
        current_user = os.environ["LOGNAME"]
        default_prefs_basepath = f"/mnt/c/Users/{current_user}/AppData/Roaming/Steinberg"
        base_output_dir =  f"/mnt/c/Users/{current_user}/Documents/VST3 Presets"

    else:
        log.error("Sorry, this operating system is not supported")
        sys.exit(1)

    argparser = argparse.ArgumentParser(
        description="Converts .vstpreset files from VST2 plugins to .vstpreset files of the corresponding VST3 plugin, if they have differing VST IDs",
        epilog="USE AT YOUR OWN RISK! There is no warranty that this will work for any plugin"
        )
    argparser.add_argument('-d', '--directory', type=str, 
                           help="Path to Directory with vstpresets of a VST2 plugin")
    argparser.add_argument('--vst3cache', type=str, default=default_prefs_basepath,
                           help="Path to Cubase's vst3plugins.xml, e.g. c:\\User\\YOURUSERNAME\\AppData\\Roaming\\Steinberg\\Cubase 12\\Cubase Pro VST3 Cache\\vst3plugins.xml")
    argparser.add_argument('-i', '--id', type=str, 
                           help="Class ID of the target VST3 plugin, if it cannot be detected automatically")
    argparser.add_argument('--vendor', type=str, 
                           help="vendor name of the target VST3 plugin, if it cannot be detected automatically")
    argparser.add_argument('-3', '--vst3name', type=str, required=True,
                           help="Name of the corresponding VST3 plugin")
    argparser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))
                        
    args = argparser.parse_args(args)

    input_dir = args.directory or os.getcwd()
    infiles = get_vst2presets(input_dir.rstrip("\\").rstrip('"'))

    (class_id, vendor) = get_vst3_classid(args.vst3name, args.vst3cache.rstrip("\\"))
    if not class_id:
        if args.id:
            class_id = args.id
        else:
            log.error("Cannot determine class ID for '%s', please check the name given with --vst3name", args.vst3name)
            sys.exit(2)
    if not vendor:
        if args.vendor:
            class_id = args.vendor
        else:
            log.error("Cannot determine vendor name for '%s', please check the name given with --vst3name", args.vst3name)
            sys.exit(2)
    
    output_dir = os.path.join(base_output_dir, vendor, args.vst3name )
    os.makedirs(output_dir, exist_ok=True)
    convert_presets(infiles, output_dir, class_id)

if __name__ == '__main__':
    sys.exit(main() or 0)
