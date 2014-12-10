#!/usr/bin/python
# EASY-INSTALL-ENTRY-SCRIPT: 'screenshot==1.0.0','console_scripts','screenshot'
__requires__ = 'screenshot==1.0.0'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('screenshot==1.0.0', 'console_scripts', 'screenshot')()
    )
