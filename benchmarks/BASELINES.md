# Render Benchmarks — Baselines

Run with: `python -m benchmarks.bench_render`

## 2026-04-09 — After optimization pass (cache, counter IDs)

| Benchmark | avg | p50 | p95 | p99 |
|---|---|---|---|---|
| minimal_component | 1688µs | 1620µs | 1983µs | 2622µs |
| nested_10_deep | 7684µs | 7350µs | 9086µs | 10740µs |
| wide_20_children | 21845µs | 20710µs | 24141µs | 38682µs |
| hooks_combo | 2263µs | 2083µs | 2895µs | 4833µs |
| rerender_state_persist | 3000µs | 2908µs | 3540µs | 4683µs |
| context_provider | 2817µs | 2721µs | 3353µs | 4010µs |
| element_text_input | 1984µs | 1920µs | 2308µs | 3029µs |
| unmount_cycle | 4183µs | 3834µs | 4808µs | 5893µs |
| functional_component | 1698µs | 1649µs | 1903µs | 2667µs |

## 2026-04-09 — Before optimizations (initial baselines)

| Benchmark | avg | p50 | p95 | p99 |
|---|---|---|---|---|
| minimal_component | 1863µs | 1719µs | 2680µs | 3798µs |
| nested_10_deep | 8322µs | 7836µs | 10344µs | 13620µs |
| wide_20_children | 23678µs | 22263µs | 27431µs | 35864µs |
| hooks_combo | 2420µs | 2208µs | 3368µs | 4603µs |
| rerender_state_persist | 3343µs | 3116µs | 4578µs | 5793µs |
| context_provider | 3447µs | 2909µs | 5501µs | 10621µs |
| element_text_input | 2111µs | 2035µs | 2431µs | 3350µs |
| unmount_cycle | 4542µs | 4154µs | 5408µs | 6877µs |
| functional_component | 1887µs | 1822µs | 2304µs | 3126µs |

### Bottleneck analysis

~90% of render time is spent in `modict.__init__` (type validation, coercion,
config copy). Each Component/Element instantiation creates 2 modict objects
(Props + State), and mounting adds a Fiber. This is intrinsic to modict's
design — further gains require changes in modict itself (e.g. a fast-init mode
that skips validation for trusted internal types).

The framework's own overhead (fiber resolution, key stacks, context management)
is <10% of total time after the caching optimizations.
