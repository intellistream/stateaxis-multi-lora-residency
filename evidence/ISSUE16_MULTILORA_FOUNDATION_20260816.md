# Issue #16 identity-bound multi-LoRA foundation

> **Point-in-time closure report, not current repository status.** Current
> capability classification is owned by
> [`NATIVE_ENGINE_STATUS.md`](../../NATIVE_ENGINE_STATUS.md); immutable attempts and
> run detail are retained in the result directories named below.

## Scope and implementation

This change establishes the default-off production foundation for heterogeneous
multi-LoRA execution. Adapter identity binds the base-model digest, adapter ID
and generation, module, A/B digests and payload root, shape, rank, BF16 layout,
scale, and TP/EP placement. Request, wire and retained-state identity carry the
adapter generation, so stale continuation and cross-adapter KV reuse fail before
execution.

The scheduler preserves its selected request set and groups rows into stable
adapter segments. Canonical base-only batches retain the previous protocol
bytes. An adapted frame adds one ordered 56-byte record per row. The resident
Qwen worker applies the base `lm_head` to the full batch and then applies
`scale * B(A(x))` to each adapter segment before greedy selection. The first
module set is deliberately limited to `lm_head` and BF16 rank buckets
4/8/16/64.

Adapter tensors are fully SHA-verified into a bounded host staging area, then
demand-loaded under a fixed HBM budget. Stable LRU selection, generation checks
and per-batch leases prevent replacement while in flight. Cache load/hit,
eviction, resident bytes, host bytes, segment count, physical rows, authority
and fallback are bounded telemetry. Graph and dual-microbatch paths explicitly
fall back for adapted batches. The public default remains disabled.

Rust tests cover identity mutation, segment coverage/order, stale generations,
capacity, lease-safe eviction, base-path byte compatibility, state isolation and
mock-worker dispatch. Cross-language protocol tests pass. The official `.23`
image built the full C++ worker and its protocol test. A producer round-trip now
validates the exact worker-manifest field order plus every A/B size and SHA.

## Preserved diagnostics

- R1 exited before worker launch because the outer runner supplied a nested
  output root rejected by the generic runner.
- R2 fixed that path but correctly triggered the formal-run artifact-name
  heuristic for a 1+1 correctness gate.
- R3 separated correctness output custody from formal performance output. It
  reached the real worker and exposed a manifest schema bug: the producer wrote
  `slot, rank, generation` while the worker reads
  `slot, generation, rank`. Slot one was therefore parsed as rank one and its
  valid 40,960-byte A tensor was rejected against a 10,240-byte expectation.
- R4 fixes only that binding, freezes a new fixture identity, and passes.

No failed attempt was deleted or reclassified as a successful NPU run. The
retained directories are:

- `results/issue16-multilora-20260816-r1-gate/`;
- `results/issue16-multilora-20260816-r2-gate/`;
- `results/issue16-multilora-20260816-r3-gate/`;
- `results/issue16-multilora-20260816-r4-gate/`.

## Frozen identity and real-NPU gate

R4 binds source commit `0f5c17f0388ef52fb0ddfead30af81aa221c7b91`,
server SHA-256
`8317e330d575a41cd3ffb638e535a7d070a469ab87f7de2522bb9578062132d9`,
worker SHA-256
`f5630c95b830e66a2e8bfac6937b905e6279a05bca853c42983b471521af56f5`,
execution-artifact SHA-256
`64fc253139d901837cb534d77f6bdb70ad642b5d3962707ed164e39e4d7af94e`,
and fixture identity SHA-256
`d37af3794b517f3724b5a00aff48cdd759629a81bc51e3498149640a7d6a1193`.
The local official image was
`quay.io/ascend/vllm-ascend:v0.23.0rc1-openeuler`, image ID
`sha256:f4c89c293e076453e9eef9edb5fb9669740dccbd3c48619a9f976d775fc29b81`.

Dynamic two-snapshot admission selected physical NPU3 with zero AICore use and
sufficient free HBM. Both arms were independent fresh processes over the same
32 requests, prompt, two-token oracle, eight adapters, rank sequence
4/8/16/64/4/8/16/64, capacity and timing boundary. Control submitted eight
homogeneous four-row batches; candidate submitted one heterogeneous 32-row
batch. Process-to-ready was 322.809/322.871 seconds.

| Metric | Control | Candidate |
|---|---:|---:|
| exact responses / lifecycle | pass | pass |
| request throughput | 31.276969 req/s | 31.150412 req/s |
| output-token throughput | 62.553939 tok/s | 62.300824 tok/s |
| request latency p50 | 74.301 ms | 247.984 ms |
| request latency p95 | 202.862 ms | 251.639 ms |
| peak HBM | 58,569 MiB | 58,633 MiB |
| maximum physical rows | 4 | 32 |
| maximum adapter segments | 1 | 8 |
| authority-applied rows | 64 | 64 |
| loads / hits / fallback | 8 / 8 / 0 | 8 / 8 / 0 |

The matched identity-set and workload digests are identical across arms. The
experiment container was removed, no foreign resource was modified, and all
NPUs returned to zero process occupancy.

## Classification and transferred acceptance scope

This is a successful correctness/authority 1+1 for the narrow unmerged
`lm_head` foundation. It is not a performance repeat: the descriptive request
throughput delta is -0.405% and candidate p95 is higher, so no speedup,
significance or vLLM/vLLM-HUST comparison is claimed.

The broader #16 acceptance is preserved in dedicated trackers rather than
hidden inside an indefinitely open umbrella:

- #103 owns multi-module segmented kernels, fault coverage and the complete
  adapter/rank/batch/traffic matrix;
- #104 owns asynchronous bounded staging, swap/eviction pressure and graph
  safety;
- #105 owns skew-aware merge/unmerge policy and its matched baselines.

Until those gates pass, multi-LoRA remains default-off and is classified as a
narrow production foundation rather than complete production LoRA serving.
