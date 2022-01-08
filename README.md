# nbtschematic

> A simple [nbtlib](https://github.com/vberlier/nbtlib) Schema for reading or
> writing Schematic files for
> [MCEdit](https://github.com/Podshot/MCEdit-Unified) and other world editors.

## Installation

Python 3.8 or higher is required. You should probably create a new
[virtual environment](https://docs.python.org/3/tutorial/venv.html) before you
install. Once you have activated your virtual environment, run

```bash
pip3 install nbtschematic
```

## Examples

To load an existing MCEdit or other schematic file from disk, run:

```python
from nbtschematic import SchematicFile
sf = SchematicFile.load('tests/test_schematic/simple.schematic')
print("The block at Y=%d, Z=%d, X=%d has block ID %d" %
(2, 3, 0, sf.blocks[2, 3, 0]))
```

To generate a schematic file in python, run:

```python
from nbtschematic import SchematicFile
sf = SchematicFile(shape=(10, 8, 4))
assert sf.blocks.shape == (10, 8, 4)
sf.blocks[2, 3, 0] = 42
sf.save('example.schematic')
```

The size of the schematic should be defined at construction time. Resizing it
will clear the blocks and block data.

Other fields of interest include:

* `data`: Block data for each and every block
* `entities`: Everything that is not a block
* `blockentities`: Extended metadata for blocks

## Further Reading

For more information about the underlying objects, see `nbtlib`'s excellent
[examples](https://github.com/vberlier/nbtlib/blob/master/docs/Usage.ipynb)
page.

----

License - [MIT](https://github.com/cbs228/nbtschematic/blob/master/LICENSE)
