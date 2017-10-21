# coding=utf-8
import sys


PY3 = sys.version_info[0] == 3
if PY3:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse  # noqa
