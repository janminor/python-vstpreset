#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fxp
import vstpreset
import argparse
import re
from pathlib import Path


def log_fxp_info(fxp_preset):
    print(f"Plugin ID: {fxp_preset.plugin_id}")
    print(f"Preset Name: {fxp_preset.name}")
    print(f"Is Opaque?: {fxp_preset.is_opaque()}")
    print(f"Is Regular?: {fxp_preset.is_regular()}")
    print(f"Num Params: {fxp_preset.param_count}")
    print(f"Params: {fxp_preset.is_regular() and fxp_preset.params}")

    print(re.sub(r"(\n\s+\d+)+", "...", f"Struct Representation: {fxp_preset._struct}"))

    for key in dir(fxp_preset._struct):
        if not key.startswith("__") and key not in {"content"}:
            try:
                print(f"{key}: {fxp_preset._struct[key]}")
            except Exception as e:
                pass

    # # --- Save param list for inspection ---
    param_data = []
    if fxp_preset.is_regular():
        for p in fxp_preset.params:
            param_data.append(
                {
                    "id": p.id,
                    "name": p.name,
                    "value": p.value,
                    "value_normalized": p.normalized_value,
                }
            )
    print(f"Enumerated {len(param_data)} params vs count: {fxp_preset.param_count}")

    # --- Save opaque chunk if present ---
    # if fxp_preset.is_opaque():
    #     with open(Path(output_path) / f"{Path(input_path).stem}.bin", "wb") as f:
    #         f.write(fxp_preset.data)
    #     print(f"Saved opaque chunk to {f.name} ({len(fxp_preset.data)} bytes)")
    # else:
    #     print("No opaque chunk found — param-only preset.")


def convert(
    input_path,
    output_path,
    class_id=None,
    chunklist_id="List",
    chunk_id_default="Comp",
    header_id="VST3",
    version=1,
):
    fxp_preset = fxp.FXP(input_path)
    print(f"Loaded FXP file: {input_path}")
    log_fxp_info(fxp_preset)

    # --- Create VSTPreset and write .vstpreset file ---
    chunks = None
    if fxp_preset.is_opaque():
        chunks = {chunk_id_default: fxp_preset.data}

    vst = vstpreset.VST3Preset(
        class_id=class_id,
        chunks=chunks,
        chunklist_id=chunklist_id,
        header_id=header_id,
        version=version,
    )

    if fxp_preset.is_regular():
        for p in fxp_preset.params:
            vst.parameters[p.id] = p.normalized_value

    out = Path(output_path) / f"{Path(input_path).stem}.vstpreset"
    vst.write_file(out)
    print(f"Wrote .vstpreset to: {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("preset_path", help="Path to the .fxp or .vstpreset file")
    parser.add_argument(
        "--out", help="Optional path for output .vstpreset", default="/tmp"
    )
    parser.add_argument(
        "--vst3-preset",
        help="Path to a sample .vstpreset file to use for defaults (e.g. class_id, version)",
        default=None,
    )
    parser.add_argument(
        "--class-id", help="Override class_id for the output .vstpreset", default=None
    )
    parser.add_argument(
        "--version",
        type=int,
        help="Override version for the output .vstpreset",
        default=None,
    )
    parser.add_argument(
        "--header", help="Override header_id for the output .vstpreset", default=None
    )
    parser.add_argument(
        "--chunklist-id",
        help="Override chunklist_id for the output .vstpreset",
        default=None,
    )
    args = parser.parse_args()

    # Defaults
    class_id = None
    version = 1
    header_id = "VST3"
    chunklist_id = "List"

    # If --vst3-preset is provided, parse it for defaults
    if args.vst3_preset:
        sample = vstpreset.parse_vst3preset_file(args.vst3_preset)
        class_id = sample.class_id
        version = sample.version
        header_id = sample.header_id
        chunklist_id = sample.chunklist_id
        print(f"Using defaults from {args.vst3_preset}: {sample}")

    # Apply direct overrides if provided
    if args.class_id:
        class_id = args.class_id
    if args.version is not None:
        version = args.version
    if args.header:
        header_id = args.header
    if args.chunklist_id:
        chunklist_id = args.chunklist_id

    assert class_id is not None, "class_id is required"

    output_path = Path(args.out)
    output_path.mkdir(parents=True, exist_ok=True)

    convert(
        args.preset_path,
        output_path,
        class_id=class_id,
        chunklist_id=chunklist_id,
        header_id=header_id,
        version=version,
    )
