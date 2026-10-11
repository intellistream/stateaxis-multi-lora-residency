# stateaxis-multi-lora-residency

Extension ID: `org.vllm-hust.stateaxis-multi-lora-residency`

Identity, segmented execution, isolation and bounded residency for heterogeneous LoRA batches.

This repository is the independent MOD boundary for StateAxis issues [#16](https://github.com/Qixin-Gaoke/stateaxis/issues/16), [#103](https://github.com/Qixin-Gaoke/stateaxis/issues/103), [#104](https://github.com/Qixin-Gaoke/stateaxis/issues/104), [#105](https://github.com/Qixin-Gaoke/stateaxis/issues/105).
Version 0.2.0 is an active, default-off Manifest 0.3 `runtime_bridge`. It can only be
enabled through vLLM-HUST Extension Manager/ECPA in experimental mode. StateAxis
hash-binds the MOD, registry, worker manifest, base weights and adapter payloads,
then provides bounded host/HBM residency with generation checks and lease-safe LRU.

## Evidence boundary

Status: **active experimental; correctness-positive, performance-unqualified**.

The historical 8-adapter correctness foundation passed a 1+1 real-NPU gate. Candidate
throughput was 31.150412 req/s versus 31.276969 req/s control (-0.405%), so no
performance benefit is claimed. This result only describes that frozen workload.

The copied evidence and its SHA-256 are recorded in `PROVENANCE.json`. Negative,
failed, and inconclusive results are retained. Microbenchmarks and component results
must not be restated as online end-to-end gains.

## Install and launch through ECPA

```bash
python -m pip install .
vllm-hust-ext extension inspect org.vllm-hust.stateaxis-multi-lora-residency
vllm-hust-ext extension check org.vllm-hust.stateaxis-multi-lora-residency
export VLLM_HUST_EXT_CONFIG="$PWD/evidence/ecpa-contract-20261011/manager-config.json"
vllm-hust-ext extension check org.vllm-hust.stateaxis-multi-lora-residency
vllm-hust-ext run -- /path/to/native_state_engine [normal StateAxis arguments]
```

Run from the repository root so the signed fixture paths resolve. Direct multi-LoRA
CLI flags and environment activation are rejected. Disabling the extension restores
the unchanged base path and the host clears all worker multi-LoRA variables.

## Validate

```bash
python -m pip install -e '.[test]'
pytest -q
```

Maintainer: Shuhao Zhang (Tony), directly responsible; no advisor is declared.
