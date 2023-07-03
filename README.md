# vstpreset

A simple python module for reading and writing VST3 preset files. Not sure whether it is actually useful... :)

No documentation, no tests yet. This is beta, use at your own risk.

## Usage

```python
import vstpreset

preset = vstpreset.parse_vst3preset_file("filename.vstpreset")
preset.write_file("new.vstpreset")
# should write a bit-identical new preset file. If not, it is totally my fault
````
