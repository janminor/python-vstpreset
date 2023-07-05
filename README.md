# vstpreset

A simple python module for reading and writing VST3 preset files. Not sure whether it is actually useful... :)

No documentation, no tests yet. This is beta, use at your own risk.

## vst2tovst3

This is a simple script that will convert .vstpreset-Files create by the VST2 version of a plugin to 
a .vstpreset for the VST3 version. Some plugin vendors use a different plugin ID for the VST2 and VST3
versions of the same plugin, and for Cubase those are different plugins. 

It is not guaranteed that this will work, I have test it with u-he plugins, and the VST3 version can load the 
converted presets just fine, but for any other plugins it might just not work or - worst case - crash. 
Save your work before trying.

This is a command line program, and it only works on Windows so far.

I've compiled a windows executable, so no one needs to download python and whatnot

Use it like this:

Open a Windows PowerShell. Navigate to where you put the .exe (a good idea would be your "Documents\VST3 Presets" Folder, I'll 
use that for the example).

Type the following, using as an examples u-he's Zebra2
```
cd '.\Documents\VST3 Presets\'
.\vst2tovst3.exe -d '.\u-he\Zebra2(x64)' --vst3name Zebra2
```
The "--vst3name" Parameter requires the exact name of the VST3 plugin version. If you do not know that, check in Cubase's Plugin Manager. 

The result should be that all .vstpreset-Files in the '.\u-he\Zebra2(x64)' Folder are now in the '.\u-he\Zebra3'-Folder, but with a "v2"-Prefix, as not to overwrite any existing presets.



## Usage in python

```python
import vstpreset

preset = vstpreset.parse_vst3preset_file("filename.vstpreset")
preset.write_file("new.vstpreset")
# should write a bit-identical new preset file. If not, it is totally my fault
```
