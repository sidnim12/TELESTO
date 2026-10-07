"""Channel data structure for IndPenSim.

Equivalent to createChannel.m - holds time history for a state/manipulated variable.
"""

import numpy as np


class Channel:
    """Holds the time history for a state or manipulated variable.

    Attributes:
        name: Channel name/description.
        yUnit: Measurement unit string.
        tUnit: Time unit string.
        t: Time vector (numpy array).
        y: Measurement vector (numpy array).
    """

    def __init__(self, name, y_unit, t_unit, t=None, y=None):
        self.name = name
        self.yUnit = y_unit
        self.tUnit = t_unit
        if t is not None and y is not None:
            t = np.asarray(t, dtype=float).flatten()
            y = np.asarray(y, dtype=float).flatten()
            if len(t) != len(y):
                raise ValueError("t and y must have the same length")
            self.t = t.copy()
            self.y = y.copy()
        else:
            self.t = np.array([], dtype=float)
            self.y = np.array([], dtype=float)


def create_channel(name, y_unit, t_unit, t=None, y=None):
    """Create a Channel structure.

    Parameters:
        name: Channel name.
        y_unit: Measurement unit.
        t_unit: Time unit.
        t: Time vector (optional).
        y: Measurement vector (optional).

    Returns:
        Channel instance.
    """
    return Channel(name, y_unit, t_unit, t, y)