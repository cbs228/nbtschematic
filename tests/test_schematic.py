import numpy as np
import os
import io
import gzip

from nbtschematic import SchematicFile, Entity, BlockEntity, Material

COUNTING_C = \
    np.asarray(range(0, 27), dtype=np.uint8, order='C'). \
    reshape((3, 3, 3), order='C')

COUNTING_F = \
    np.asarray(range(0, 27), dtype=np.uint8, order='F'). \
    reshape((3, 3, 3), order='F')


def test_blocks_from_numpy():
    sf = SchematicFile(shape=(3, 3, 3))
    sf.blocks = COUNTING_C
    sf.data = np.transpose(COUNTING_C)
    assert np.all(np.asarray(sf.blocks) == COUNTING_C)
    assert np.all(np.asarray(sf.root['Blocks']) == range(0, 27))
    assert np.all(np.asarray(sf.data) == np.transpose(COUNTING_C))
    assert np.all(np.asarray(sf.root['Data']) ==
                  np.transpose(COUNTING_C).flatten())

    sf.blocks = COUNTING_F
    sf.data = np.transpose(COUNTING_F)
    assert np.all(np.asarray(sf.blocks) == COUNTING_F)
    assert np.all(np.asarray(sf.root['Blocks']) == COUNTING_F.reshape(-1))
    assert np.all(np.asarray(sf.data) == np.transpose(COUNTING_F))
    assert np.all(np.asarray(sf.root['Data']) ==
                  np.transpose(COUNTING_F).reshape(-1))


def test_init_writeread(datadir):
    sf = SchematicFile(shape=(3, 3, 3), blocks=COUNTING_C, data=COUNTING_C)
    assert np.all(np.asarray(sf.blocks) == COUNTING_C)
    assert np.all(np.asarray(sf.data) == COUNTING_C)
    outbuf = io.BytesIO()
    outbuf.name = 'none'
    sf.write(outbuf)
    outbuf.seek(0, 0)

    # Can we read it from bytes?
    sf2 = SchematicFile.from_buffer(outbuf)
    assert np.all(np.asarray(sf2.shape) == (3, 3, 3))
    assert np.all(np.asarray(sf2.blocks) == COUNTING_C)
    assert np.all(np.asarray(sf2.data) == COUNTING_C)

    # Does it match our existing schematic file?
    test_file = os.path.join(datadir, 'counting.schematic')
    with gzip.open(test_file, 'rb') as fd:
        in_bytes = fd.read()
    assert np.all(in_bytes == outbuf.getvalue())


def test_resize():
    sf = SchematicFile(shape=(3, 2, 1))
    assert np.all(sf.shape == (3, 2, 1))
    sf.resize((3, 1, 2))
    assert np.all(sf.shape == (3, 1, 2))
    assert np.all(sf.blocks.shape == (3, 1, 2))
    assert np.all(sf.data.shape == (3, 1, 2))


def test_shape_mismatch():
    sf = SchematicFile(shape=(3, 2, 1))
    sf.blocks = np.zeros((3, 2, 1))
    sf.data = np.zeros((3, 2, 1))
    try:
        sf.blocks = np.zeros((3, 1, 2))
        assert False
    except ValueError:
        assert True
    try:
        sf.data = np.zeros((3, 1, 2))
        assert False
    except ValueError:
        assert True


def test_load_verify(datadir):
    sf = SchematicFile.load(os.path.join(datadir, 'simple.schematic'))
    assert (sf.material == Material.Alpha)
    assert (np.all(sf.shape == (4, 4, 4)))

    # all blocks are air, except on main diagonal
    expect_blocks = np.zeros((4, 4, 4), dtype=np.uint8)
    expect_blocks[0, 0, 0] = 1
    expect_blocks[1, 1, 1] = 4
    expect_blocks[2, 2, 2] = 24
    expect_blocks[3, 3, 3] = 54
    assert np.all(np.asarray(sf.blocks) == expect_blocks)
    assert sf.data[3, 3, 3] == 2

    # chicken entity
    assert len(sf.entities) == 1
    assert sf.entities[0]['id'] == 'minecraft:chicken'

    # chest tile entity, one occupied slot
    assert len(sf.blockentities) == 1
    assert sf.blockentities[0]['id'] == 'minecraft:chest'
    assert len(sf.blockentities[0]['Items']) == 1


def test_set_materials():
    sf = SchematicFile()
    sf.material = Material.Classic
    assert (sf.material == Material.Classic)


def test_set_entities():
    sf = SchematicFile()
    sf.entities = [Entity()]
    sf.entities[0]['id'] = 'awe:some'
    sf.entities[0]['Pos'] = [0, 0, 0]
    sf.block_entities = [BlockEntity()]
    sf.block_entities[0]['id'] = 'awe:somer'
    sf.block_entities[0]['x'] = 0
    sf.block_entities[0]['y'] = 0
    sf.block_entities[0]['z'] = 0


def test_rewrite_identical(datadir):
    test_file = os.path.join(datadir, 'simple.schematic')
    with gzip.open(test_file, 'rb') as fd:
        in_bytes = fd.read()

    outbuf = io.BytesIO()
    sf = SchematicFile.load(test_file)
    sf.write(outbuf)
    out_bytes = outbuf.getvalue()

    assert np.all(in_bytes == out_bytes)
