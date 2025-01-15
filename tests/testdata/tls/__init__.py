from typing import Optional

import pulumi


class SelfSignedCertificateArgs:
    """
    The arguments for creating a self-signed certificate.
    """

    algorithm: Optional[pulumi.Input[str]]
    """The algorithm to use for the key."""
    ecdsa_curve: Optional[pulumi.Input[str]]
    """The curve to use for ECDSA keys."""


class SelfSignedCertificate(pulumi.ComponentResource):
    """
    A self-signed certificate.
    """

    pem: pulumi.Output[str]
    private_key: pulumi.Output[str]
    """The private key."""
    ca_cert: pulumi.Output[str]

    def __init__(
        self,
        args: SelfSignedCertificateArgs,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__(
            "example:component:SelfSignedCertificate",
            "SelfSignedCertificate",
            {},
            opts,
        )
        self.algorithm = args.algorithm
        self.ecdsa_curve = args.ecdsa_curve
        # do things ...
        self.pem = pulumi.Output.from_input("le pem")
        self.private_key = pulumi.Output.from_input("secret thing")
        self.ca_cert = pulumi.Output.from_input("ca cert")
