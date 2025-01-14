import sys
from pathlib import Path

from pulumi.provider import main

from provider import ComponentProvider

if __name__ == "__main__":
    main(ComponentProvider("banana", "1.2.3", Path(sys.argv[0])), sys.argv[1:])
