# Python Component as Component

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
