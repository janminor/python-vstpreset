#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
#
"""
"""

import argparse
import os
import sys
from typing import List
from dataclasses import dataclass
from struct import calcsize,  unpack_from

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

HEADER_FMT = '<4si32sq'
HEADER_SIZE = calcsize(HEADER_FMT)
CHUNKLIST_HEADER = '<4si'
CL_HEADER_SIZE = calcsize(CHUNKLIST_HEADER)
CHUNKLIST_ENTRY = '<4sqq'
CL_ENTRY_SIZE = calcsize(CHUNKLIST_ENTRY)


@dataclass
class VST3PresetHeader:
    header_id: str
    version: int
    class_id: str
    chunklist_offset: int

@dataclass
class VST3ChunklistHeader:
    list_id: str
    entry_count: int
    
@dataclass
class VST3Chunk:
    chunk_id: str
    offset: int
    size: int
    data: bytes

class VST3Preset():
    def __init__(self, header: VST3PresetHeader, chunks: List[VST3Chunk] = None):
        self.header = header
        self.chunks = chunks if chunks else []
        
    def get_chunk(self, chunk_id: str) -> VST3Chunk:
        found = [ a for a in self.chunks if a.chunk_id == chunk_id ]
        if found:
            return found[0]
        return None
        
def parse_vst3preset(filename: str) -> VST3Preset:
    
    with open(filename, 'rb') as fp:
        presetdata = fp.read(-1)

    header = VST3PresetHeader(*unpack_from(HEADER_FMT, presetdata, offset=0))
    preset = VST3Preset(header)
    chunklist_header = VST3ChunklistHeader(*unpack_from(CHUNKLIST_HEADER, presetdata, offset=preset.header.chunklist_offset))

    start_chunk = preset.header.chunklist_offset + CL_HEADER_SIZE
    for chunknr in range(1, chunklist_header.entry_count + 1):
        # (id, offset, size)
        chunk = unpack_from(CHUNKLIST_ENTRY, presetdata, offset=start_chunk)
        start = chunk[1]
        end = start + chunk[2]
        preset.chunks.append(VST3Chunk(chunk[0].decode(), chunk[1], chunk[2],  presetdata[start:end]))
        start_chunk += CL_ENTRY_SIZE
    
    return preset
        


def main(args=None):

    for infile in sys.argv[1:]:
        preset = parse_vst3preset(infile)

        print(preset.header)
        print(preset.chunks)
        #print(preset.get_chunk('Info'))



if __name__ == '__main__':
    sys.exit(main() or 0)
