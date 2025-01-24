# Python Component as Component

This is a proof of concept to build a provider from Python code using type annotations to define the schema.

## Usage

Subclass `pulumi.ComponentResource` and use type annotations to define the schema:

```python
# A class defining the inputs for the component
@dataclass
class ServiceArgs:
    region: pulumi.Input[str]
    project: pulumi.Input[str]
    app_path: Optional[pulumi.Input[str]] = "./app"
    image_name: Optional[pulumi.Input[str]] = "image"

# The component class that will be constructed by the provider
class Service(pulumi.ComponentResource):
    # Define the outputs of the component
    url: pulumi.Output[Optional[str]]
    image_digest: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        args: ServiceArgs,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__("cloudrun:index:Service", name, {}, opts)
        # Create your resources etc.
```

Create a hosting provider for the class by adding a `__main__.py` file that uses `componentProviderHost`:

```python
from component.host import componentProviderHost
from component.metadata import Metadata

componentProviderHost(
    Metadata(name="my-component", version="1.2.3", display_name="My Component")
)
```

## Example

The example folder contains a component in `my-component` that generates a self-signed certificate.
The `pulumi_project_yaml` folder contains a Pulumi YAML project that uses
The `pulumi_project_py` folder contains a Pulumi Python project that uses the component via the generated SDK.

```bash
cd example/pulumi_project_py
pulumi package gen-sdk ../my-component --out ../generated-sdk --language python
uv add --editable ../generated-sdk/python
pulumi preview
```

```
Updating (dev)

View in Browser (Ctrl+O): https://app.pulumi.com/v-julien-pulumi-corp/example/dev/updates/27

     Type                                         Name         Status
 +   pulumi:pulumi:Stack                          example-dev  created (9s)
 +   └─ my-component:index:SelfSignedCertificate  cert         created
 +      └─ tls:index:PrivateKey                   cert-ca      created (0.31s)
 +         ├─ tls:index:PrivateKey                cert-key     created (0.55s)
 +         └─ tls:index:SelfSignedCert            cert-ca      created (1s)

Outputs:
    cert: {
        algorithm  : "ECDSA"
        ca_cert_pem: "-----BEGIN CERTIFICATE-----...-----END CERTIFICATE-----\n"
        ecdsa_curve: "P224"
        private_key: [secret]
        rsa_bits   : 2048
        urn        : "urn:pulumi:dev::example::my-component:index:SelfSignedCertificate::cert"
    }

Resources:
    + 5 created

Duration: 11s
```

Alternatively, add the package with `package add`, but this requires the Python Pulumi SDK to handle parameterization in `sdk/python/lib/pulumi/provider/provider.py`.

```bash
pulumi package add ../my-component
```
