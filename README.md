# Python Component as Component

```bash
cd example/pulumi_project
pulumi package gen-sdk ../my-component --out ../generated-sdk --language python
uv add --editable ../generated-sdk/python
pulumi preview
```

Alternatively, add the package with `package add`, but this requires the Python Pulumi SDK to handle parameterization in `sdk/python/lib/pulumi/provider/provider.py`.

```bash
pulumi package add ../my-component
```
