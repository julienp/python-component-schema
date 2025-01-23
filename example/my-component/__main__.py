from component.host import componentProviderHost
from component.metadata import Metadata

componentProviderHost(
    Metadata(name="my-component", version="1.2.3", display_name="My Component")
)
