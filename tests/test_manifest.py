import hashlib
import json
from pathlib import Path

import pytest
from vllm_hust_ext.manifest import activation_blocker, load_manifest

import stateaxis_multi_lora_residency
from stateaxis_multi_lora_residency import (
    MultiLoraResidencyConfig,
    multi_lora_residency,
)


def roots() -> tuple[Path, Path]:
    package = Path(stateaxis_multi_lora_residency.__file__).parent
    return package, package.parents[1]


def test_manifest_is_active_and_hash_bound() -> None:
    package, repo = roots()
    path = package / "vllm-hust-extension-v0.3.json"
    manifest = load_manifest(path)
    assert manifest.bundle_id == "org.vllm-hust.stateaxis-multi-lora-residency"
    assert manifest.schema_version == "0.3-experimental"
    assert activation_blocker(manifest) is None
    raw = json.loads(path.read_text(encoding="utf-8"))
    expected = raw["activation"]["additional_config"]["stateaxis_mod"][
        "manifest_sha256"
    ]
    assert (
        hashlib.sha256((repo / "RESEARCH_MANIFEST.json").read_bytes()).hexdigest()
        == expected
    )


def test_fixture_bytes_are_exact() -> None:
    _, repo = roots()
    mechanism = json.loads((repo / "RESEARCH_MANIFEST.json").read_text())["mechanism"]
    for path_key, digest_key in (
        ("registry_path", "registry_sha256"),
        ("worker_manifest_path", "worker_manifest_sha256"),
    ):
        assert (
            hashlib.sha256((repo / mechanism[path_key]).read_bytes()).hexdigest()
            == mechanism[digest_key]
        )
    assert (
        len(json.loads((repo / mechanism["registry_path"]).read_text())["adapters"])
        == 2
    )


def test_activation_contract_is_exact() -> None:
    assert multi_lora_residency() == MultiLoraResidencyConfig()
    with pytest.raises(ValueError, match="reviewed bounded contract"):
        MultiLoraResidencyConfig(lease_safe_lru=False)
