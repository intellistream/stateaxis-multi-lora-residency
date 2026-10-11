"""Identity-bound multi-LoRA residency activation contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass

MOD_ID = "org.vllm-hust.stateaxis-multi-lora-residency"


@dataclass(frozen=True, slots=True)
class MultiLoraResidencyConfig:
    """Reviewed StateAxis authority policy; paths and digests live in the manifest."""

    enabled: bool = True
    identity_bound: bool = True
    generation_bound: bool = True
    lease_safe_lru: bool = True
    strict_payload_sha256: bool = True
    fallback_to_base: bool = True
    fail_closed: bool = True
    hbm_capacity_bytes: int = 67_108_864
    host_capacity_bytes: int = 67_108_864

    def __post_init__(self) -> None:
        expected = {
            "enabled": True,
            "identity_bound": True,
            "generation_bound": True,
            "lease_safe_lru": True,
            "strict_payload_sha256": True,
            "fallback_to_base": True,
            "fail_closed": True,
            "hbm_capacity_bytes": 67_108_864,
            "host_capacity_bytes": 67_108_864,
        }
        if asdict(self) != expected:
            raise ValueError(
                "multi-LoRA residency requires the reviewed bounded contract"
            )


def multi_lora_residency() -> MultiLoraResidencyConfig:
    """Return the default-off candidate's exact admitted ON policy."""

    return MultiLoraResidencyConfig()


__all__ = ["MOD_ID", "MultiLoraResidencyConfig", "multi_lora_residency"]
