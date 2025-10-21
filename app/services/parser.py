import json
from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component
from cyclonedx.output import OutputFormat, make_outputter
from cyclonedx.schema import SchemaVersion
import re


async def parse_manifest(filename: str, content: bytes) -> dict:
    """
    Parse manifest (requirements.txt, package-lock.json, etc.)
    and return CycloneDX-like JSON
    """
    text = content.decode("utf-8", errors="ignore")

    if filename.endswith("requirements.txt"):
        components = _parse_requirements(text)
    elif filename.endswith("package-lock.json"):
        components = _parse_npm_lock(text)
    else:
        raise ValueError("Unsupported manifest type")

    bom = Bom()
    for name, version in components:
        bom._components.add(Component(name=name, version=version))

    outputter = make_outputter(bom, OutputFormat.JSON, SchemaVersion.V1_5)
    return json.loads(outputter.output_as_string())


def _parse_requirements(content: str):
    """Parse Python requirements.txt lines"""
    comps = []
    for line in content.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        match = re.match(r"([a-zA-Z0-9_\-]+)==([0-9a-zA-Z\.\-]+)", line)
        if match:
            comps.append(match.groups())
    return comps


def _parse_npm_lock(content: str):
    """Parse Node package-lock.json"""
    data = json.loads(content)
    comps = []
    if "packages" in data:
        for pkg, info in data["packages"].items():
            if "version" in info:
                comps.append((pkg or "root", info["version"]))
    return comps


def _parse_npm_lock(content: str):
    """Parse Node package-lock.json"""
    data = json.loads(content)
    comps = []
    if "packages" in data:
        for pkg, info in data["packages"].items():
            if "version" in info:
                comps.append((pkg or "root", info["version"]))
    return comps
