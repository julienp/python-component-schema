import sys
from pathlib import Path

from pulumi.provider import main

from provider import ComponentProvider

# Bail out if we're already hosting. This prevents recursion when the analyzer
# loads this file. It's usually good style to not run code at import time, and
# use `if __name__ == "__main__"`, but let's make sure we guard against this
is_hosting = False


def componentProviderHost():
    global is_hosting
    if is_hosting:
        return
    is_hosting = True
    path = Path(sys.argv[0])
    name = path.absolute().name
    main(ComponentProvider(name, "1.0.0", path), sys.argv[1:])
