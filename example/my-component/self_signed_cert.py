from dataclasses import dataclass
from typing import Optional

import pulumi
import pulumi_tls as tls


# TODO: do we want a helper class to create the args? should we encourage TypedDict?
@dataclass
class SelfSignedCertificateArgs:
    # subject: pulumi.Input[tls.SelfSignedCertSubjectArgsDict]  # TODO: handle this
    algorithm: Optional[pulumi.Input[str]]
    """The algorithm to use for the key."""
    ecdsa_curve: Optional[pulumi.Input[str]]
    rsa_bits: Optional[pulumi.Input[int]]


class SelfSignedCertificate(pulumi.ComponentResource):
    ca_cert_pem: pulumi.Output[str]
    private_key: pulumi.Output[str]
    """The private key."""

    def __init__(
        self,
        name: str,
        # TODO: support key=value args in schema discovery vs args?
        args: SelfSignedCertificateArgs,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__(
            "my-component:index:SelfSignedCertificate",
            name,
            {},
            opts,
        )
        algorithm = args.algorithm or "RSA"
        ecdsa_curve = args.ecdsa_curve or "P224"
        ecdsa_curve = args.ecdsa_curve or "P224"
        rsa_bits = args.rsa_bits or 2048

        ca_key = tls.PrivateKey(
            f"{name}-ca",
            algorithm=algorithm,
            ecdsa_curve=ecdsa_curve,
            rsa_bits=rsa_bits,
            opts=pulumi.ResourceOptions(parent=self),
        )

        ca_cert = tls.SelfSignedCert(
            f"{name}-ca",
            private_key_pem=ca_key.private_key_pem,
            is_ca_certificate=True,
            allowed_uses=["key_encipherment", "digital_signature"],
            validity_period_hours=24,
            subject={
                "common_name": "hello.example.com",
            },
            opts=pulumi.ResourceOptions(parent=ca_key),
        )

        private_key = tls.PrivateKey(
            f"{name}-key",
            algorithm=algorithm,
            ecdsa_curve=ecdsa_curve,
            rsa_bits=rsa_bits,
            opts=pulumi.ResourceOptions(parent=ca_key),
        )

        self.ca_cert_pem = ca_cert.cert_pem
        self.private_key = private_key.private_key_pem
