# Python Component as Component

```bash
cd example/pulumi_project
pulumi package gen-sdk ../my-component --out ../generated-sdk --language python
uv add --editable ../generated-sdk/python
pulumi preview
```


```
Updating (dev)

View in Browser (Ctrl+O): https://app.pulumi.com/v-julien-pulumi-corp/example/dev/updates/24

     Type                                         Name         Status
 +   pulumi:pulumi:Stack                          example-dev  created (8s)
 +   └─ my-component:index:SelfSignedCertificate  cert         created
 +      └─ tls:index:PrivateKey                   cert-ca      created (0.26s)
 +         ├─ tls:index:PrivateKey                cert-key     created (0.28s)
 +         └─ tls:index:SelfSignedCert            cert-ca      created (1s)

Outputs:
    cert: {
        algorithm  : "ECDSA"
        ca_cert_pem: "-----BEGIN CERTIFICATE-----\nMIIBZDCCAROgAwIBAgIQVdZhaWtWbAaJoltiS8QGWTAKBggqhkjOPQQDAjAcMRow\nGAYDVQQDExFoZWxsby5leGFtcGxlLmNvbTAeFw0yNTAxMTQxMzU0MjdaFw0yNTAx\nMTUxMzU0MjdaMBwxGjAYBgNVBAMTEWhlbGxvLmV4YW1wbGUuY29tME4wEAYHKoZI\nzj0CAQYFK4EEACEDOgAEiI9r5YkqkIK6DlytRRtjwDF4+Y63nItY64acXRN9C4uG\nmCcPYWd+wms7kJw9umKc3CfGGbSglMGjQjBAMA4GA1UdDwEB/wQEAwIFoDAPBgNV\nHRMBAf8EBTADAQH/MB0GA1UdDgQWBBQelE7GvwJKKPzvKHN6z0IXKg1yizAKBggq\nhkjOPQQDAgM/ADA8AhwUmc0F0wtiGk3bzlUrAsdauZkzCXzip+Uh4KhpAhxROM0k\nbC/dHfJDlXHbq6ZOUnh+qsDn7LDpJyk4\n-----END CERTIFICATE-----\n"
        ecdsa_curve: "P224"
        private_key: [secret]
        rsa_bits   : 2048
        urn        : "urn:pulumi:dev::example::my-component:index:SelfSignedCertificate::cert"
    }

Resources:
    + 5 created

Duration: 9s
```

Alternatively, add the package with `package add`, but this requires the Python Pulumi SDK to handle parameterization in `sdk/python/lib/pulumi/provider/provider.py`.

```bash
pulumi package add ../my-component
```
