""" Defines an nbtlib schema for schematic files """
from typing import Tuple
import numpy as np
import nbtlib as nbt


Entity = nbt.schema('Entity', {
    'id': nbt.String,
    'Pos': nbt.List[nbt.Double],
    'Motion': nbt.List[nbt.Double],
    'Rotation': nbt.List[nbt.Float],
    'FallDistance': nbt.Float,
    'Fire': nbt.Short,
    'Air': nbt.Short,
    'OnGround': nbt.Byte,
    'NoGravity': nbt.Byte,
    'Invulnerable': nbt.Byte,
    'PortalCooldown': nbt.Int,
    'UUIDMost': nbt.Long,
    'UUIDLeast': nbt.Long
})

BlockEntity = nbt.schema('BlockEntity', {
    'id': nbt.String,
    'x': nbt.Int,
    'y': nbt.Int,
    'z': nbt.Int
})

Schematic = nbt.schema('Schematic', {
    'Height': nbt.Short,
    'Length': nbt.Short,
    'Width': nbt.Short,
    'Materials': nbt.String,
    # 8 bits per block. Sorted by height (bottom to top) then length then width
    # -- the index of the block at X,Y,Z is Y×length×width + Z×width + X.
    'Blocks': nbt.ByteArray,
    'Data': nbt.ByteArray,
    'Entities': nbt.List[Entity],
    'TileEntities': nbt.List[BlockEntity]
})

""" Indicates schematic from a Classic world """
MATERIAL_CLASSIC = "Classic"

""" Indicates schematic from a Pocket world """
MATERIAL_POCKET = "Pocket"

""" Indicates schematic from Alpha and newer levels (Default) """
MATERIAL_ALPHA = "Alpha"


class SchematicFile(nbt.File, Schematic):
    """
    Schematic File

    Schematic files are commonly used by world editors such as MCEdit,
    Schematica, and WorldEdit. They are intended to represent a small
    section of a level for the purposes of interchange or permanent
    storage.

    The origin of the schematic is always ``X = 0``, ``Y = 0``, ``Z = 0``.
    All positions for blocks, entities, and block entities are transformed
    into the schematic's coordinate system.

    Schematic coordinates map directly to data indices. Blocks and block
    data are stored in contiguous numpy byte arrays. The first dimension
    in these arrays is height (``Y``). The second and third dimensions
    are ``Z`` and ``X``, respectively.
    """

    def __init__(self, shape: Tuple[int, int, int] = (1, 1, 1),
                 blocks=None, data=None):
        super().__init__({'': {}})
        self.gzipped = True
        self.byteorder = 'big'
        self.root_name = 'Schematic'
        self.root['Materials'] = MATERIAL_ALPHA
        self.resize(shape)
        if blocks is not None:
            self.blocks = blocks
        if data is not None:
            self.data = data

    def resize(self, shape: Tuple[int, int, int]) -> None:
        """
        Resize the schematic file

        Resizing the schematic clears the blocks and data

        :param shape: New dimensions for the schematic, as a tuple of
        ``(n_y, n_z, n_z)``.
        """

        self.root['Height'] = nbt.Short(shape[0])
        self.root['Length'] = nbt.Short(shape[1])
        self.root['Width'] = nbt.Short(shape[2])
        self.blocks = np.zeros(shape, dtype=np.uint8, order='C')
        self.data = np.zeros(shape, dtype=np.uint8, order='C')

    @classmethod
    def load(cls, filename, gzipped=True, byteorder='big') -> 'SchematicFile':
        return super().load(filename=filename,
                            gzipped=gzipped, byteorder=byteorder)

    @property
    def shape(self) -> Tuple[nbt.Short, nbt.Short, nbt.Short]:
        """ Schematic shape
        :return: Shape of the schematic, as a tuple of ``Y``, ``Z``, and ``X``
        size.
        """
        return self.root['Height'], self.root['Length'], self.root['Width']

    @property
    def blocks(self) -> np.array:
        """ Block IDs

        Entries in this array are the block ID at each coordinate of
        the schematic. This method returns an nbtlib type, but you may
        coerce it to a pure numpy array with ``numpy.asarray()``

        :return: 3D array which contains a view into the block IDs.
        Array indices are in ``Y``,``Z``,``X`` order.
        """
        return self.root['Blocks'].reshape(self.shape, order='C').view()

    @blocks.setter
    def blocks(self, value):
        if not np.all(value.shape == self.shape):
            raise ValueError("Input shape %s does not match schematic shape %s"
                             % (value.shape, self.shape))

        self.root['Blocks'] = nbt.ByteArray(value.reshape(-1))

    @property
    def data(self) -> nbt.ByteArray:
        """ Block data

        Entries in this array are the block data values at each
        coordinate of the schematic. Only the lower four bits
        are used.  This method returns an nbtlib type, but you may
        coerce it to a pure numpy array with ``numpy.asarray()``

        :return: 3D array which contains a view into the block data.
        Array indices are in ``Y``,``Z``,``X`` order.
        """
        return self.root['Data'].reshape(self.shape, order='C').view()

    @data.setter
    def data(self, value):
        if not np.all(value.shape == self.shape):
            raise ValueError("Input shape %s does not match schematic shape %s"
                             % (value.shape, self.shape))

        self.root['Data'] = nbt.ByteArray(value.reshape(-1))

    @property
    def entities(self) -> nbt.List[nbt.Compound]:
        """ Entities

        Each Entity in the schematic is a Compound tag. The schema only
        represents keys which are common to all Entities.

        :return: List of entities
        """
        return self.root['Entities']

    @entities.setter
    def entities(self, value: nbt.List[nbt.Compound]):
        self.root['Entities'] = value

    @property
    def blockentities(self) -> nbt.List[nbt.Compound]:
        """ Block Entities

        Block entities were previously known as "tile entities" and
        contain extended attributes for placed blocks. The schematic
        only enforces keys which are common to all entities, including
        a position and an ID.

        :return: List of block entities
        """
        return self.root['TileEntities']

    @blockentities.setter
    def blockentities(self, value: nbt.List[nbt.Compound]):
        self.root['TileEntities'] = value

    def __enter__(self):
        return self.root
