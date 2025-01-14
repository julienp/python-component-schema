from pathlib import Path
from typing import Optional

import pulumi

from analyzer import Analyzer, ComponentSchema, SchemaProperty


def test_analyze_component():
    class SelfSignedCertificateArgs:
        algorithm: Optional[pulumi.Input[str]]
        ecdsa_curve: Optional[pulumi.Input[str]]

    class SelfSignedCertificate(pulumi.ComponentResource):
        pem: pulumi.Output[str]
        private_key: pulumi.Output[str]
        ca_cert: pulumi.Output[str]

        def __init__(self, args: SelfSignedCertificateArgs):
            pass

    a = Analyzer(Path("."))
    comp = a.analyze_component(SelfSignedCertificate)
    assert comp == ComponentSchema(
        description="",
        inputs={
            "algorithm": SchemaProperty(
                type=str, ref=None, optional=True, description=""
            ),
            "ecdsa_curve": SchemaProperty(
                type=str, ref=None, optional=True, description=""
            ),
        },
        outputs={
            "pem": SchemaProperty(type=str, ref=None, optional=False, description=""),
            "private_key": SchemaProperty(
                type=str, ref=None, optional=False, description=""
            ),
            "ca_cert": SchemaProperty(
                type=str, ref=None, optional=False, description=""
            ),
        },
        type_definitions={},
    )


def test_analyze_from_path():
    a = Analyzer(Path("tests/testdata/tls"))
    comps = a.analyze()
    assert comps == {
        "SelfSignedCertificate": ComponentSchema(
            description="",
            inputs={
                "algorithm": SchemaProperty(
                    type=str, ref=None, optional=True, description=""
                ),
                "ecdsa_curve": SchemaProperty(
                    type=str, ref=None, optional=True, description=""
                ),
            },
            outputs={
                "pem": SchemaProperty(
                    type=str, ref=None, optional=False, description=""
                ),
                "private_key": SchemaProperty(
                    type=str, ref=None, optional=False, description=""
                ),
                "ca_cert": SchemaProperty(
                    type=str, ref=None, optional=False, description=""
                ),
            },
            type_definitions={},
        )
    }


def test_analyze_types_plain():
    class SelfSignedCertificateArgs:
        algorithm: Optional[str]

    a = Analyzer(Path("."))
    args = a.analyze_types(SelfSignedCertificateArgs)
    assert args == {
        "algorithm": SchemaProperty(type=str, ref=None, optional=True, description="")
    }


def test_analyze_types_output():
    class SelfSignedCertificateArgs:
        algorithm: pulumi.Output[str]
        ecdsa_curve: Optional[pulumi.Output[str]]

    a = Analyzer(Path("."))
    args = a.analyze_types(SelfSignedCertificateArgs)
    assert args == {
        "algorithm": SchemaProperty(type=str, ref=None, optional=False, description=""),
        "ecdsa_curve": SchemaProperty(
            type=str, ref=None, optional=True, description=""
        ),
    }


def test_analyze_types_input():
    class SelfSignedCertificateArgs:
        algorithm: pulumi.Input[str]
        ecdsa_curve: Optional[pulumi.Input[str]]

    a = Analyzer(Path("."))
    args = a.analyze_types(SelfSignedCertificateArgs)
    assert args == {
        "algorithm": SchemaProperty(type=str, ref=None, optional=False, description=""),
        "ecdsa_curve": SchemaProperty(
            type=str, ref=None, optional=True, description=""
        ),
    }
