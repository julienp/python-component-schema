import ast
import inspect
import textwrap
from pathlib import Path
from typing import Optional

import pulumi

from analyzer import Analyzer, ComponentSchema, SchemaProperty


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

    a = Analyzer(Path("."))
    comp = a.analyze_component(SelfSignedCertificate)
    assert comp == ComponentSchema(
        description="A self-signed certificate.",
        inputs={
            "algorithm": SchemaProperty(type=str, ref=None, optional=True),
            "ecdsaCurve": SchemaProperty(type=str, ref=None, optional=True),
        },
        outputs={
            "pem": SchemaProperty(type=str, ref=None, optional=False),
            "privateKey": SchemaProperty(type=str, ref=None, optional=False),
            "caCert": SchemaProperty(type=str, ref=None, optional=False),
        },
        type_definitions={},
    )


def test_analyze_from_path():
    a = Analyzer(Path("tests/testdata/tls"))
    comps = a.analyze()
    assert comps == {
        "SelfSignedCertificate": ComponentSchema(
            description="A self-signed certificate.",
            inputs={
                "algorithm": SchemaProperty(
                    type=str,
                    ref=None,
                    optional=True,
                    description="The algorithm to use for the key.",
                ),
                "ecdsaCurve": SchemaProperty(
                    type=str,
                    ref=None,
                    optional=True,
                    description="The curve to use for ECDSA keys.",
                ),
            },
            outputs={
                "pem": SchemaProperty(type=str, ref=None, optional=False),
                "privateKey": SchemaProperty(
                    type=str, ref=None, optional=False, description="The private key."
                ),
                "caCert": SchemaProperty(type=str, ref=None, optional=False),
            },
            type_definitions={},
        )
    }


def test_analyze_types_plain():
    class SelfSignedCertificateArgs:
        algorithm: Optional[str]

    a = Analyzer(Path("."))
    args = a.analyze_types(SelfSignedCertificateArgs)
    assert args == {"algorithm": SchemaProperty(type=str, ref=None, optional=True)}


def test_analyze_types_output():
    class SelfSignedCertificateArgs:
        algorithm: pulumi.Output[str]
        ecdsa_curve: Optional[pulumi.Output[str]]

    a = Analyzer(Path("."))
    args = a.analyze_types(SelfSignedCertificateArgs)
    assert args == {
        "algorithm": SchemaProperty(type=str, ref=None, optional=False),
        "ecdsaCurve": SchemaProperty(type=str, ref=None, optional=True),
    }


def test_analyze_types_input():
    class SelfSignedCertificateArgs:
        algorithm: pulumi.Input[str]
        ecdsa_curve: Optional[pulumi.Input[str]]

    a = Analyzer(Path("."))
    args = a.analyze_types(SelfSignedCertificateArgs)
    assert args == {
        "algorithm": SchemaProperty(type=str, ref=None, optional=False),
        "ecdsaCurve": SchemaProperty(type=str, ref=None, optional=True),
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

    a = Analyzer(Path("."))
    docstrings = a.find_docstrings_in_module(t)
    assert docstrings == {
        "SelfSignedCertificateArgs": {
            "algorithm": "The algorithm to use for the private key.",
            "ecdsa_curve": "The curve to use for ECDSA keys.",
        }
    }


def test_find_docstrings():
    a = Analyzer(Path("tests/testdata/tls"))
    docstrings = a.find_docstrings()
    assert docstrings == {
        "SelfSignedCertificate": {"private_key": "The private key."},
        "SelfSignedCertificateArgs": {
            "algorithm": "The algorithm to use for the key.",
            "ecdsa_curve": "The curve to use for ECDSA keys.",
        },
    }
