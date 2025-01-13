import pulumi
from typing import Optional


class SelfSignedCertificateArgs:
    algorithm: Optional[pulumi.Input[str]]
    ecdsa_curve: Optional[pulumi.Input[str]]


class SelfSignedCertificate(pulumi.ComponentResource):
    pem: pulumi.Output[str]
    private_key: pulumi.Output[str]
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
