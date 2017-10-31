# -*- coding: utf-8 -*-

import math, os, re, string, sys

spark_chars = u"▁▂▃▄▅▆▇█"
"""Eight unicode characters of (nearly) steadily increasing height."""

def sparkify(series, minimum=None, maximum=None):
    u"""Converts <series> to a sparkline string.

    Optional override the data range with <minimum> / <maximum> values

    Example:
    >>> sparkify([ 0.5, 1.2, 3.5, 7.3, 8.0, 12.5, 13.2, 15.0, 14.2, 11.8, 6.1,
    ... 1.9 ])
    u'▁▁▂▄▅▇▇██▆▄▂'
    >>> sparkify([1, 1, -2, 3, -5, 8, -13])
    u'▆▆▅▆▄█▁'
    Raises ValueError if input data cannot be converted to float.
    Raises TypeError if series is not an iterable.
    """
    series = [ float(i) for i in series ]

    series_min = min(series)
    if minimum is not None:
        minimum = min(series_min, float(minimum))
    else:
        minimum = series_min

    series_max = max(series)
    if maximum is not None:
        maximum = max(series_max, float(maximum))
    else:
        maximum = series_max

    data_range = maximum - minimum
    if data_range == 0.0:
        # Graph a baseline if every input value is equal.
        return u''.join([ spark_chars[0] for i in series ])

    coefficient = (len(spark_chars) - 1.0) / data_range

    return u''.join([
        spark_chars[
            int(round((x - minimum) * coefficient))
        ] for x in series
    ])
