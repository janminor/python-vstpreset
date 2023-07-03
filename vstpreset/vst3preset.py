#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
#
""" 
Python Module for reading and writing VST3 presets

"""

import sys
from struct import calcsize, unpack_from, pack


#     VST 3 Preset File Format Definition
# ===================================

# 0   +---------------------------+
# | HEADER                    |
# | header id ('VST3')        |       4 Bytes
# | version                   |       4 Bytes (int32)
# | ASCII-encoded class id    |       32 Bytes
# +--| offset to chunk list      |       8 Bytes (int64)
# |  +---------------------------+
# |  | DATA AREA                 |<-+
# |  | data of chunks 1..n       |  |
# |  ...                       ...  |
# |  |                           |  |
# +->+---------------------------+  |
# | CHUNK LIST                |  |
# | list id ('List')          |  |    4 Bytes
# | entry count               |  |    4 Bytes (int32)
# +---------------------------+  |
# |  1..n                     |  |
# |  +----------------------+ |  |
# |  | chunk id             | |  |    4 Bytes
# |  | offset to chunk data |----+    8 Bytes (int64)
# |  | size of chunk data   | |       8 Bytes (int64)
# |  +----------------------+ |
# EOF +---------------------------+

HEADER_FMT = "<4si32sq"
HEADER_SIZE = calcsize(HEADER_FMT)
CHUNKLIST_HEADER = "<4si"
CL_HEADER_SIZE = calcsize(CHUNKLIST_HEADER)
CHUNKLIST_ENTRY = "<4sqq"
CL_ENTRY_SIZE = calcsize(CHUNKLIST_ENTRY)


class VST3Preset:
    def __init__(
        self,
        class_id: str,
        header_id: str = "VST3",
        version: int = 1,
        chunks: dict = None,
        chunklist_id: str = "List",
    ):
        self.header_id = header_id
        self.version = version
        self.class_id = class_id
        self.chunks = chunks if chunks else {}
        self.chunklist_id = chunklist_id

    @property
    def info(self) -> bytes:
        if "Info" in self.chunks:
            return self.chunks["Info"]
        return bytes()

    @property
    def cont(self) -> bytes:
        if "Cont" in self.chunks:
            return self.chunks["Cont"]
        return bytes()

    @property
    def comp(self) -> bytes:
        if "Comp" in self.chunks:
            return self.chunks["Comp"]
        return bytes()

    @property
    def header(self) -> tuple:
        return (self.header_id, self.version, self.class_id)

    def preset_data(self) -> bytes:
        """returns the full binary representation of the preset

        Returns:
            bytes: vstpreset as bytes
        """
        out = bytes()
        chunks = bytes()
        chunklist = []
        chunk_offset = 0
        for k, v in self.chunks.items():
            chunks += v
            chunklist.append((k.encode(), HEADER_SIZE + chunk_offset, len(v)))
            chunk_offset += len(v)

        out += pack(
            HEADER_FMT,
            self.header_id.encode(),
            self.version,
            self.class_id.encode(),
            HEADER_SIZE + len(chunks),
        )
        out += chunks
        out += pack(CHUNKLIST_HEADER, self.chunklist_id.encode(), len(self.chunks))
        for chunk_entry in chunklist:
            out += pack(CHUNKLIST_ENTRY, *chunk_entry)
        return out

    def write_file(self, filename: str):
        """writes the preset data to a file

        Args:
            filename (str): filename to write to
        """
        with open(filename, "wb") as fp:
            fp.write(self.preset_data())

    def __str__(self) -> str:
        out = []
        out.append(f"header_id={self.header_id}, class={self.class_id}")
        for k, v in self.chunks.items():
            out.append(f"; Chunk '{k}': {len(v)} bytes")
        return "".join(out)


def parse_vst3preset_file(filename: str) -> VST3Preset:
    """parse a vstpreset file from a file

    Args:
        filename (str): path to the vstpreset file

    Returns:
        VST3Preset: the preset as a class
    """
    with open(filename, "rb") as fp:
        presetdata = fp.read(-1)
    return parse_vst3preset(presetdata)


def parse_vst3preset(presetdata: bytes) -> VST3Preset:
    """parse a vstpreset file from a bytestring

    Args:
        presetdata (bytes): the content of a vstpreset file as bytes

    Returns:
        VST3Preset: the preset as a class
    """

    (header_id, version, class_id, chunklist_offset) = unpack_from(
        HEADER_FMT, presetdata, offset=0
    )
    preset = VST3Preset(class_id.decode(), header_id.decode(), version)

    (cl_list_id, cl_entry_count) = unpack_from(
        CHUNKLIST_HEADER, presetdata, offset=chunklist_offset
    )
    preset.chunklist_id = cl_list_id.decode()

    start_chunk = chunklist_offset + CL_HEADER_SIZE
    for _ in range(1, cl_entry_count + 1):
        (chunk_id, chunk_offset, chunk_size) = unpack_from(
            CHUNKLIST_ENTRY, presetdata, offset=start_chunk
        )
        end = chunk_offset + chunk_size
        preset.chunks[chunk_id.decode()] = presetdata[chunk_offset:end]
        start_chunk += CL_ENTRY_SIZE

    return preset


def main(args=None):
    for infile in sys.argv[1:]:
        with open(infile, "rb") as f:
            data = f.read(-1)
        preset = parse_vst3preset(data)
        print(preset)
        if preset.vstpreset() != data:
            print("data differs")


if __name__ == "__main__":
    sys.exit(main() or 0)
