import ast
import inspect
import textwrap
from pathlib import Path
from typing import Optional

import pulumi

from component.analyzer import Analyzer, ComponentSchema, SchemaProperty, TypeDefinition
from component.metadata import Metadata

metadata = Metadata("my-component", "0.0.1")


def test_analyze_component():
    class SelfSignedCertificateArgs:
        """The arguments for creating a self-signed certificate."""

        algorithm: Optional[pulumi.Input[str]]
        ecdsa_curve: Optional[pulumi.Input[str]]

    class SelfSignedCertificate(pulumi.ComponentResource):
        """A self-signed certificate."""

        pem: pulumi.Output[str]
        private_key: pulumi.Output[str]
        ca_cert: pulumi.Output[str]

        def __init__(self, args: SelfSignedCertificateArgs):
            pass

    a = Analyzer(metadata, Path("."))
    comp = a.analyze_component(SelfSignedCertificate)
    assert comp == ComponentSchema(
        description="A self-signed certificate.",
        inputs={
            "algorithm": SchemaProperty(type_=str, optional=True),
            "ecdsaCurve": SchemaProperty(type_=str, optional=True),
        },
        outputs={
            "pem": SchemaProperty(type_=str),
            "privateKey": SchemaProperty(type_=str),
            "caCert": SchemaProperty(type_=str),
        },
    )


def test_analyze_from_path():
    a = Analyzer(metadata, Path("tests/testdata/tls"))
    comps = a.analyze()
    assert comps == {
        "SelfSignedCertificate": ComponentSchema(
            description="A self-signed certificate.",
            inputs={
                "algorithm": SchemaProperty(
                    type_=str,
                    optional=True,
                    description="The algorithm to use for the key.",
                ),
                "ecdsaCurve": SchemaProperty(
                    type_=str,
                    optional=True,
                    description="The curve to use for ECDSA keys.",
                ),
                "subject": SchemaProperty(
                    ref="#/types/my-component:index:Subject",
                    optional=True,
                ),
            },
            outputs={
                "pem": SchemaProperty(type_=str),
                "privateKey": SchemaProperty(type_=str, description="The private key.", optional=True),
                "caCert": SchemaProperty(type_=str),
                "subject": SchemaProperty(
                    ref="#/types/my-component:index:Subject",
                    description="The subject.",
                ),
            },
        )
    }

    assert a.type_definitions == {
        "Subject": TypeDefinition(
            name="Subject",
            type="object",
            properties={
                "cn": SchemaProperty(
                    type_=str,
                    description="The common name.",
                ),
            },
            description="The subject of a certificate.",
        )
    }


def test_analyze_types_plain():
    class SelfSignedCertificateArgs:
        algorithm: Optional[str]

    a = Analyzer(metadata, Path("."))
    args = a.analyze_types(SelfSignedCertificateArgs)
    assert args == {"algorithm": SchemaProperty(type_=str, optional=True)}


def test_analyze_types_output():
    class SelfSignedCertificateArgs:
        algorithm: pulumi.Output[str]
        ecdsa_curve: Optional[pulumi.Output[str]]

    a = Analyzer(metadata, Path("."))
    args = a.analyze_types(SelfSignedCertificateArgs)
    assert args == {
        "algorithm": SchemaProperty(type_=str),
        "ecdsaCurve": SchemaProperty(type_=str, optional=True),
    }


def test_analyze_types_input():
    class SelfSignedCertificateArgs:
        algorithm: pulumi.Input[str]
        ecdsa_curve: Optional[pulumi.Input[str]]

    a = Analyzer(metadata, Path("."))
    args = a.analyze_types(SelfSignedCertificateArgs)
    assert args == {
        "algorithm": SchemaProperty(type_=str),
        "ecdsaCurve": SchemaProperty(type_=str, optional=True),
    }


def test_analyze_type_definition():
    # TODO test "pulumi.json#/Archive"

    class Subject:
        """The subject of a certificate."""

        cn: pulumi.Input[str]
        """The common name."""

    class SelfSignedCertificateArgs:
        subject: Optional[pulumi.Input[Subject]]
        subjectRequired: pulumi.Input[Subject]

    class SelfSignedCertificate(pulumi.ComponentResource):
        subject: pulumi.Output[Subject]

        def __init__(self, args: SelfSignedCertificateArgs):
            pass

    a = Analyzer(metadata, Path("."))
    comp = a.analyze_component(SelfSignedCertificate)
    assert comp == ComponentSchema(
        inputs={
            "subject": SchemaProperty(
                ref="#/types/my-component:index:Subject",
                optional=True,
            ),
            "subjectRequired": SchemaProperty(
                ref="#/types/my-component:index:Subject",
            ),
        },
        outputs={
            "subject": SchemaProperty(ref="#/types/my-component:index:Subject"),
        },
    )

    assert a.type_definitions == {
        "Subject": TypeDefinition(
            name="Subject",
            type="object",
            properties={
                "cn": SchemaProperty(
                    type_=str,
                    # TODO: pick up docstring here
                    # description="The common name.",
                ),
            },
            description="The subject of a certificate.",
        )
    }


def test_find_docstrings_in_module():
    class SelfSignedCertificateArgs:
        no_docstring: pulumi.Input[str]
        algorithm: pulumi.Input[str]
        """The algorithm to use for the private key."""

        ecdsa_curve: Optional[pulumi.Input[str]]
        # a comment

        """The curve to use for ECDSA keys."""

    src = inspect.getsource(SelfSignedCertificateArgs)
    src = textwrap.dedent(src)
    t = ast.parse(src)

    a = Analyzer(metadata, Path("."))
    docstrings = a.find_docstrings_in_module(t)
    assert docstrings == {
        "SelfSignedCertificateArgs": {
            "algorithm": "The algorithm to use for the private key.",
            "ecdsa_curve": "The curve to use for ECDSA keys.",
        }
    }


def test_find_docstrings():
    a = Analyzer(metadata, Path("tests/testdata/tls"))
    docstrings = a.find_docstrings()
    assert docstrings == {
        "SelfSignedCertificate": {
            "private_key": "The private key.",
            "subject": "The subject.",
        },
        "SelfSignedCertificateArgs": {
            "algorithm": "The algorithm to use for the key.",
            "ecdsa_curve": "The curve to use for ECDSA keys.",
        },
        "Subject": {
            "cn": "The common name.",
        },
    }
