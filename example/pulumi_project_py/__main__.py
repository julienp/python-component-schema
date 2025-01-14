import pulumi
import pulumi_my_component

args = pulumi_my_component.SelfSignedCertificateArgs(
    algorithm="ECDSA",
    ecdsa_curve="P224",
    rsa_bits=2048,
)

res = pulumi_my_component.SelfSignedCertificate("cert", args)

pulumi.export("cert", res)