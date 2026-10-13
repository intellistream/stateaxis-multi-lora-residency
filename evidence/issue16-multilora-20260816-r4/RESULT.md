# Historical R4 real-NPU result

This bundle preserves the compact machine-readable evidence for the successful
StateAxis issue #16 R4 gate. It is a historical **1+1 correctness/authority gate**,
not a performance qualification of the current ECPA revision.

| Metric | Control | Candidate | Delta |
|---|---:|---:|---:|
| Request throughput | 31.276969 req/s | 31.150412 req/s | -0.405% |
| Output-token throughput | 62.553939 tok/s | 62.300824 tok/s | -0.405% |
| Request latency p50 | 74.301 ms | 247.984 ms | +233.753% |
| Request latency p95 | 202.862 ms | 251.639 ms | +24.044% |
| Peak HBM | 58,569 MiB | 58,633 MiB | +64 MiB |

Both fresh-process arms returned exact responses. Both recorded 64 authority-applied
rows and zero fallback. The candidate exercised one heterogeneous 32-row batch with
eight adapter segments; control used eight homogeneous four-row batches.

The candidate was slower in this frozen workload. Because there is only one repetition
per arm, this is a descriptive, workload-scoped negative observation with no confidence
interval or significance claim. It does not establish that multi-LoRA residency is
universally harmful, and it must not be inherited by the current implementation.

A current qualification needs at least three fresh-process repetitions per arm, the
same signed model/adapter identities, exactness and authority checks, and traffic cells
that vary adapter skew, reuse, rank, batch occupancy and residency pressure. The source
attempts R1-R3 remain preserved in StateAxis; they are described in the historical
closure report and were not rewritten as successful runs.
