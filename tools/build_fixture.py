#!/usr/bin/env python3
"""Build the byte-identical two-adapter Qwen2.5-14B ECPA fixture."""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

BASE_SHA256 = "4ca9cbc269c4605424d3170d614f43854388b19bee70ade62c28ce054ee9033a"
HIDDEN_SIZE = 5120
VOCAB_SIZE = 152064
RANK = 4


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def framed(digest: object, value: bytes) -> None:
    digest.update(struct.pack("<Q", len(value)))
    digest.update(value)


def bf16(value: float) -> int:
    bits = struct.unpack("<I", struct.pack("<f", value))[0]
    return (bits + 0x7FFF + ((bits >> 16) & 1)) >> 16


def payload_root(a_sha: str, b_sha: str) -> str:
    digest = hashlib.sha256()
    for value in (
        b"statecentric-peft-lora-payload-root-v1",
        a_sha.encode(),
        b_sha.encode(),
    ):
        framed(digest, value)
    return digest.hexdigest()


def identity_sha(identity: dict[str, object]) -> str:
    digest = hashlib.sha256()
    values = (
        b"statecentric-peft-lora-identity-v1",
        str(identity["adapter_id"]).encode(),
        struct.pack("<Q", int(identity["generation"])),
        str(identity["base_weights_sha256"]).encode(),
        b"lm_head",
        struct.pack("<I", HIDDEN_SIZE),
        struct.pack("<I", VOCAB_SIZE),
        struct.pack("<H", RANK),
        b"bf16",
        b"hidden_rank_rank_vocab",
        struct.pack("<I", int(identity["scale_bits"])),
        str(identity["a_sha256"]).encode(),
        str(identity["b_sha256"]).encode(),
        str(identity["payload_root_sha256"]).encode(),
        struct.pack("<H", 1),
        struct.pack("<H", 0),
        struct.pack("<H", 1),
        struct.pack("<H", 0),
    )
    for value in values:
        framed(digest, value)
    return digest.hexdigest()


def main() -> None:
    root = Path(__file__).parents[1] / "fixtures" / "qwen2.5-14b"
    root.mkdir(parents=True, exist_ok=True)
    adapters: list[dict[str, object]] = []
    rows = [
        "\t".join(
            (
                "statecentric-multilora-pack-v1",
                BASE_SHA256,
                str(HIDDEN_SIZE),
                str(VOCAB_SIZE),
                "bf16",
            )
        )
    ]
    for slot in (1, 2):
        a_payload = bytearray(HIDDEN_SIZE * RANK * 2)
        for inner in range(RANK):
            struct.pack_into("<H", a_payload, inner * 2, bf16(1.0 / RANK))
        b_payload = bytearray(RANK * VOCAB_SIZE * 2)
        for inner in range(RANK):
            for token in (525, 264):
                struct.pack_into(
                    "<H",
                    b_payload,
                    (inner * VOCAB_SIZE + token) * 2,
                    bf16(-0.001 * slot),
                )
        a_name = f"adapter-{slot:02d}.a.bf16"
        b_name = f"adapter-{slot:02d}.b.bf16"
        (root / a_name).write_bytes(a_payload)
        (root / b_name).write_bytes(b_payload)
        a_sha, b_sha = sha256(a_payload), sha256(b_payload)
        identity: dict[str, object] = {
            "adapter_id": f"ecpa-fixture-lm-head-{slot:02d}",
            "generation": 1,
            "base_weights_sha256": BASE_SHA256,
            "module": "lm_head",
            "hidden_size": HIDDEN_SIZE,
            "vocab_size": VOCAB_SIZE,
            "rank": RANK,
            "dtype": "bf16",
            "layout": "hidden_rank_rank_vocab",
            "scale_bits": 1065353216,
            "a_sha256": a_sha,
            "b_sha256": b_sha,
            "payload_root_sha256": payload_root(a_sha, b_sha),
            "tp_degree": 1,
            "tp_rank": 0,
            "ep_degree": 1,
            "ep_rank": 0,
        }
        identity["identity_sha256"] = identity_sha(identity)
        adapters.append({"slot": slot, "identity": identity})
        rows.append(
            "\t".join(
                str(value)
                for value in (
                    slot,
                    1,
                    RANK,
                    1065353216,
                    identity["identity_sha256"],
                    a_sha,
                    b_sha,
                    a_name,
                    b_name,
                )
            )
        )
    (root / "registry.json").write_text(
        json.dumps(
            {"schema_version": 1, "adapters": adapters}, indent=2, sort_keys=True
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "worker_manifest.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
