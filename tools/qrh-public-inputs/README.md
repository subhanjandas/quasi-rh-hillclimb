# Rebuild the admitted public QRH inputs

This workflow recompiles existing public proof dependencies from
GTimG/QuasiRiemannTracker at commit
0ce80fdddebb03128d30a917006d8520e7a774b8.

It is a compiler-input preparation job. It does not submit a result PR, publish a
proposed candidate, prove a new numerical bound, or issue an admission record.

## What it builds

The 19 roots in input-roots.json select a dependency-closed graph of 6,632
Submissions modules. They include the existing full-family endpoint, variable-price
natural source theorem, NF theorem and generic return interfaces. Every source
file comes from the immutable public upstream tree.

The exact source/dependency graph was checked against the locally prepared input
contract. The cache format was tested using the upstream pack/restore functions.

## Runtime and checks

The workflow uses an Ubuntu 24.04 VM, the upstream pinned Node/Lean/package
revisions, and the upstream Palomar sandbox installer. The compiler is generated
from the pinned upstream replay driver. It retains the source/library/tool hashes,
sandbox confinement and mount controls, immutable challenge export and per-module
resource supervision.

Only the compiler's source subset and shared deadline change: public input modules
only, with five hours for compilation. The final new-result proof and kernel
checks are not part of this preparation job. Its report says
COMPILED_PUBLIC_INPUTS_ONLY and explicitly sets new_bound_verified and
official_admission to false.

The fresh disposable runner removes unused preinstalled .NET, Android and Haskell SDKs to leave room for the proof toolchains and libraries. It does not delete source checkouts.

The worker has read-only repository permission. Checkout credentials are not
persisted. Submitted Lean processes receive the minimal upstream environment and
cannot access the workflow credentials or the artifact publisher.

## Outputs

The qrh-public-input-build artifact contains:

- input-build-report.json, with source/compiler/environment identities and counts;
- input-contract.json and cache-inputs.json, binding modules to source and imports;
- checksummed public-inputs-NNN.tar.gz archives in the upstream cache format;
- the sandbox and compiler logs, including any resource failure.

If compilation stops early, a PARTIAL_PUBLIC_INPUTS report preserves only modules whose compilation returned successfully; the workflow still fails. It never marks an incomplete input rebuild as complete.

Each archive stays below the upstream cache size limit. Baseline modules restored
from the official signed cache are not duplicated. Artifacts expire after one day
because these files are temporary build inputs, rather than the evidence for a
new bound. The final public result must include its own proof source and pass the
target repository's canonical comparison and all three kernels.

A client must verify the source hashes, compiler and complete library fingerprint
before importing these products. This job's artifacts are not the upstream
maintainer's signed admission cache and must not be represented as such.

## Repository layout

Install the workflow as .github/workflows/qrh-public-inputs.yml.
Install this README, input-roots.json, scripts/make_input_builder.py, LICENSE, LICENSE-Apache-2.0 and
NOTICE.md under tools/qrh-public-inputs/.

The workflow runs on pushes to the isolated ci/qrh-public-inputs branch or through
workflow_dispatch. It does not change the fork's main branch or the upstream
QuasiRiemannTracker repository. No result PR is created.

## Attribution

Subhanjan Das prepared this orchestration with substantial OpenAI Codex assistance.
The upstream verifier, Palomar, Lean, mathematical dependencies and original
Collet/Lewko/OpenAI proofs retain their authorship and licenses. See NOTICE.md.
