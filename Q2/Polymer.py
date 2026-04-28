#region imports
import math
import random
import statistics
#endregion


#region constants
DEFAULT_DEGREE_OF_POLYMERIZATION = 1000
DEFAULT_MOLECULE_COUNT = 50
DEFAULT_SEGMENT_LENGTH = 0.154e-9
DEFAULT_MER_WEIGHT = 14
NM_PER_METER = 1.0e9
UM_PER_METER = 1.0e6
#endregion


#region position class
class Position:
    """
    Store and calculate with a point or vector in 3D space.
    """

    # Chat GPT helped me write this function.
    def __init__(self, position=None, x=None, y=None, z=None):
        """
        Create a position in 3D space.

        Args:
            position: Optional tuple containing x, y, and z values.
            x: Optional x-coordinate value.
            y: Optional y-coordinate value.
            z: Optional z-coordinate value.

        Returns:
            None.
        """
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        if position is not None:
            self.x, self.y, self.z = position

        self.x = float(x) if x is not None else self.x
        self.y = float(y) if y is not None else self.y
        self.z = float(z) if z is not None else self.z

    # Chat GPT helped me write this function.
    def __add__(self, other):
        """
        Add two Position objects.

        Args:
            other: Position object to add to this position.

        Returns:
            A new Position with each coordinate added together.
        """
        return Position(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    # Chat GPT helped me write this function.
    def __iadd__(self, other):
        """
        Add a scalar or Position object to this Position in place.

        Args:
            other: Number or Position object to add.

        Returns:
            This updated Position object.
        """
        if isinstance(other, (float, int)):
            self.x += other
            self.y += other
            self.z += other
        elif isinstance(other, Position):
            self.x += other.x
            self.y += other.y
            self.z += other.z
        return self

    # Chat GPT helped me write this function.
    def __sub__(self, other):
        """
        Subtract one Position from another.

        Args:
            other: Position object to subtract from this position.

        Returns:
            A new Position with each coordinate subtracted.
        """
        return Position(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)

    # Chat GPT helped me write this function.
    def __isub__(self, other):
        """
        Subtract a scalar or Position object from this Position in place.
