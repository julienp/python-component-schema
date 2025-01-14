import pulumi
import pulumi_banana

args = pulumi_banana.SelfSignedCertificateArgs(
    algorithm="ECDSA",
    ecdsa_curve="P224",
    rsa_bits=2048,
)

res = pulumi_banana.SelfSignedCertificate("cert", args)

pulumi.export("cert", res)
