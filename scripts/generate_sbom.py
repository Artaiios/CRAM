#!/usr/bin/env python3
"""Erzeugt eine CycloneDX-1.5-SBOM für CRAM.

Die Komponenten sind hart kodiert, weil CRAM keine npm/pip-Manifest-Datei
hat und die Libraries inline im HTML eingebettet sind. Das ist pragmatischer
als ein voller Build-Chain-Auto-Scan für drei Komponenten.

Die SHA-256-Hashes der Libraries werden aus dem Tool-HTML extrahiert, damit
sie immer aktuell sind und mit der jeweils im Release ausgelieferten
Library-Version übereinstimmen.
"""
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Repo-relative Pfade: Script liegt in scripts/, Tool liegt auf Repo-Root
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
TOOL_HTML = REPO_ROOT / "crisis-role-manager.html"
OUT_SBOM = REPO_ROOT / "cram-sbom.cdx.json"

# ---- CRAM-Version aus dem Tool lesen --------------------------------------
html = TOOL_HTML.read_text(encoding="utf-8")
m = re.search(r"const APP_VERSION = '([^']+)'", html)
assert m, "APP_VERSION nicht gefunden"
CRAM_VERSION = m.group(1)

# ---- SHA-256 der Library-Blöcke --------------------------------------------
# Wir extrahieren die eingebetteten Scripts anhand der Kommentar-Marker.
def extract_lib(name_marker: str) -> str:
    """Extrahiert den Library-Code-Block (ohne Kommentarblock) für Hashing."""
    # Finde die Marker-Zeile und nimm alles bis zum nächsten </script>
    idx = html.find(name_marker)
    assert idx >= 0, f"Marker nicht gefunden: {name_marker}"
    end = html.find("</script>", idx)
    assert end >= 0
    # Nur den Code selbst nehmen (ohne den Marker-Kommentar davor)
    block_start = html.find("\n", idx) + 1
    return html[block_start:end]

fflate_code = extract_lib("/* fflate@0.8.2 */")
qrcode_code = extract_lib("/* qrcode-generator@1.4.4 */")

fflate_hash = hashlib.sha256(fflate_code.encode("utf-8")).hexdigest()
qrcode_hash = hashlib.sha256(qrcode_code.encode("utf-8")).hexdigest()

# ---- Hash der Tool-Datei selbst -------------------------------------------
tool_hash = hashlib.sha256(TOOL_HTML.read_bytes()).hexdigest()

# ---- CycloneDX-1.5-Dokument bauen -----------------------------------------
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
serial = f"urn:uuid:{uuid.uuid4()}"

sbom = {
    "$schema": "http://cyclonedx.org/schema/bom-1.5.schema.json",
    "bomFormat": "CycloneDX",
    "specVersion": "1.5",
    "serialNumber": serial,
    "version": 1,
    "metadata": {
        "timestamp": timestamp,
        "tools": [
            {
                "vendor": "CRAM project",
                "name": "generate_sbom.py",
                "version": "1.0.0"
            }
        ],
        "component": {
            "type": "application",
            "bom-ref": f"pkg:generic/cram@{CRAM_VERSION}",
            "name": "CRAM",
            "version": CRAM_VERSION,
            "description": "Crisis Role Availability Manager — single-file HTML tool for managing crisis committee roles and substitution chains",
            "licenses": [
                {"license": {"id": "Apache-2.0"}}
            ],
            "copyright": "Copyright 2026 Patrick Zeller",
            "purl": f"pkg:generic/cram@{CRAM_VERSION}",
            "hashes": [
                {"alg": "SHA-256", "content": tool_hash}
            ],
            "externalReferences": [
                {"type": "website", "url": "https://github.com/Artaiios/CRAM"},
                {"type": "vcs", "url": "https://github.com/Artaiios/CRAM.git"},
                {"type": "issue-tracker", "url": "https://github.com/Artaiios/CRAM/issues"}
            ]
        }
    },
    "components": [
        {
            "type": "library",
            "bom-ref": "pkg:npm/fflate@0.8.2",
            "name": "fflate",
            "version": "0.8.2",
            "description": "High performance (de)compression in an 8kB package",
            "scope": "required",
            "licenses": [
                {"license": {"id": "MIT"}}
            ],
            "copyright": "Copyright (c) 2023 Arjun Barrett",
            "purl": "pkg:npm/fflate@0.8.2",
            "hashes": [
                {"alg": "SHA-256", "content": fflate_hash}
            ],
            "externalReferences": [
                {"type": "website", "url": "https://github.com/101arrowz/fflate"},
                {"type": "distribution", "url": "https://www.npmjs.com/package/fflate/v/0.8.2"}
            ],
            "properties": [
                {"name": "cram:embedding", "value": "inline-in-crisis-role-manager.html"},
                {"name": "cram:purpose", "value": "gzip compression for JSON exports and QR-transfer payloads"}
            ]
        },
        {
            "type": "library",
            "bom-ref": "pkg:npm/qrcode-generator@1.4.4",
            "name": "qrcode-generator",
            "version": "1.4.4",
            "description": "QR Code Generator implementation in JavaScript",
            "scope": "required",
            "licenses": [
                {"license": {"id": "MIT"}}
            ],
            "copyright": "Copyright (c) 2009 Kazuhiko Arase",
            "purl": "pkg:npm/qrcode-generator@1.4.4",
            "hashes": [
                {"alg": "SHA-256", "content": qrcode_hash}
            ],
            "externalReferences": [
                {"type": "website", "url": "https://github.com/kazuhikoarase/qrcode-generator"},
                {"type": "distribution", "url": "https://www.npmjs.com/package/qrcode-generator/v/1.4.4"}
            ],
            "properties": [
                {"name": "cram:embedding", "value": "inline-in-crisis-role-manager.html"},
                {"name": "cram:purpose", "value": "QR code generation for device-to-device configuration and state transfer"},
                {"name": "cram:version-pin-rationale", "value": "Deliberately held at 1.4.4. The 2.0.x series adds TypeScript typings (issue #120) and one narrow bugfix (issue #121) with no runtime API changes. Revisit on security advisory or functional need."}
            ]
        }
    ],
    "dependencies": [
        {
            "ref": f"pkg:generic/cram@{CRAM_VERSION}",
            "dependsOn": [
                "pkg:npm/fflate@0.8.2",
                "pkg:npm/qrcode-generator@1.4.4"
            ]
        }
    ]
}

OUT_SBOM.write_text(json.dumps(sbom, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"✓ SBOM generated: {OUT_SBOM}")
print(f"  CRAM version:     {CRAM_VERSION}")
print(f"  Tool SHA-256:     {tool_hash}")
print(f"  fflate SHA-256:   {fflate_hash}")
print(f"  qrcode SHA-256:   {qrcode_hash}")
print(f"  Size:             {OUT_SBOM.stat().st_size:,} bytes")
