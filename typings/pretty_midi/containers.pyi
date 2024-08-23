"""
This type stub file was generated by pyright.
"""

"""These classes simply hold MIDI data in a convenient form.

"""
class Note:
    """A note event.

    Parameters
    ----------
    velocity : int
        Note velocity.
    pitch : int
        Note pitch, as a MIDI note number.
    start : float
        Note on time, absolute, in seconds.
    end : float
        Note off time, absolute, in seconds.

    """
    def __init__(self, velocity, pitch, start, end) -> None:
        ...
    
    def get_duration(self):
        """Get the duration of the note in seconds."""
        ...
    
    @property
    def duration(self):
        ...
    
    def __repr__(self): # -> LiteralString:
        ...
    


class PitchBend:
    """A pitch bend event.

    Parameters
    ----------
    pitch : int
        MIDI pitch bend amount, in the range ``[-8192, 8191]``.
    time : float
        Time where the pitch bend occurs.

    """
    def __init__(self, pitch, time) -> None:
        ...
    
    def __repr__(self): # -> LiteralString:
        ...
    


class ControlChange:
    """A control change event.

    Parameters
    ----------
    number : int
        The control change number, in ``[0, 127]``.
    value : int
        The value of the control change, in ``[0, 127]``.
    time : float
        Time where the control change occurs.

    """
    def __init__(self, number, value, time) -> None:
        ...
    
    def __repr__(self): # -> LiteralString:
        ...
    


class TimeSignature:
    """Container for a Time Signature event, which contains the time signature
    numerator, denominator and the event time in seconds.

    Attributes
    ----------
    numerator : int
        Numerator of time signature.
    denominator : int
        Denominator of time signature.
    time : float
        Time of event in seconds.

    Examples
    --------
    Instantiate a TimeSignature object with 6/8 time signature at 3.14 seconds:

    >>> ts = TimeSignature(6, 8, 3.14)
    >>> print(ts)
    6/8 at 3.14 seconds

    """
    def __init__(self, numerator, denominator, time) -> None:
        ...
    
    def __repr__(self): # -> str:
        ...
    
    def __str__(self) -> str:
        ...
    


class KeySignature:
    """Contains the key signature and the event time in seconds.
    Only supports major and minor keys.

    Attributes
    ----------
    key_number : int
        Key number according to ``[0, 11]`` Major, ``[12, 23]`` minor.
        For example, 0 is C Major, 12 is C minor.
    time : float
        Time of event in seconds.

    Examples
    --------
    Instantiate a C# minor KeySignature object at 3.14 seconds:

    >>> ks = KeySignature(13, 3.14)
    >>> print(ks)
    C# minor at 3.14 seconds
    """
    def __init__(self, key_number, time) -> None:
        ...
    
    def __repr__(self): # -> str:
        ...
    
    def __str__(self) -> str:
        ...
    


class Lyric:
    """Timestamped lyric text.

    Attributes
    ----------
    text : str
        The text of the lyric.
    time : float
        The time in seconds of the lyric.
    """
    def __init__(self, text, time) -> None:
        ...
    
    def __repr__(self): # -> str:
        ...
    
    def __str__(self) -> str:
        ...
    


class Text:
    """Timestamped text event.

    Attributes
    ----------
    text : str
        The text.
    time : float
        The time it occurs in seconds.
    """
    def __init__(self, text, time) -> None:
        ...
    
    def __repr__(self): # -> str:
        ...
    
    def __str__(self) -> str:
        ...
    


