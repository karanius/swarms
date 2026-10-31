# Explicit rule learning and masked-feature experiment

The real executable notebook block is in Section7 of Paper6, after the implementation discussion. It runs PyClause's AnyBURL wrapper, queries the native rule application module, independently recounts the saved results, runs12 contract tests and8 intentional artifact-corruption tests, then displays tables, charts, clauses and a symbolic design. Earlier graphs and executed cells are preserved.

## Reproduce

Use the existing Research Python environment. Dependencies are pinned in `relational-requirements.txt`; the full observed environment is in `relational-environment.lock`. PyClause upstream documents Windows/Linux rather than macOS support. On this Mac the native extension was built using installed Homebrew libomp and the checked-in build-only `toolchain/clang-openmp` adapter. No upstream source changes were made. The source clone is under the ignored notebook runtime directory at the pinned commit.

```
CC="$PWD/knowledge/research/paper-6-study/toolchain/clang-openmp" \
CXX="$PWD/knowledge/research/paper-6-study/toolchain/clang-openmp" \
uv pip install --python services/research-notebook/.venv/bin/python \
  'git+https://github.com/symbolic-kg/PyClause.git@87c82ec3dd904767741a493dcbdf7605377d4535'

services/research-notebook/.venv/bin/python knowledge/research/paper-6-study/relational_experiment.py
services/research-notebook/.venv/bin/python knowledge/research/paper-6-study/verify_relational.py
services/research-notebook/.venv/bin/python -m unittest discover \
  -s knowledge/research/paper-6-study -p 'test_relational*.py' -v
```

Running `update_relational_paper.py` executes the notebook's real learner/testing block and integrates its actual results into the manuscript. It requires the local `research-python` kernel and preserves a pre-extension notebook backup. Each engine invocation uses a fresh batch directory; prior raw rules and failure logs remain available. New stochastic runs can change rule coverage. The accepted language, counts, split and canonical tie-break are explicit; AnyBURL random seeds are not controlled.

## Interpretation

`has_feature(X,fB) <= has_feature(X,fA)` is a learned local implication with exact source evidence. This is an association represented in relational syntax, not a discovered semantic composition law. Only same-subject single-body clauses are accepted. Native sampled scores, exact neighborhood confidence and center-conditioned lift are distinct. All training facts are retained, and guidance is recomputed from training only. The shortlist comparison happens after learning; it does not establish faster training.

One complete saved feature is hidden per eligible assessment neighborhood. The source-group split is retrospective because the corpus was already explored. Answered-only recovery, overall recovery, abstention and vocabulary coverage must be reported together. Non-recovery need not mean a bad alternative; no behavioral negatives are invented.

The proposal writer uses training-only saved port declarations and fresh symbolic neighbor roles. It retains required inputs, resource fields, source references and unknown purpose/configuration/aliasing. Connectedness and acyclicity of its two-edge skeleton are construction properties. Declared type overlap is not native component certification, output activation, behavioral correctness or evidence of an appropriate composite boundary.

The separate typed-wire probe is constrained by the same512MB heap cap; the observed Java preparation failure is reported separately as infrastructure failure. It is not a zero-rule scientific result. The initial failed integration and its raw logs are retained. No parameters are tuned after results to hide the failure.

Artifacts under `paper-6-corpus/relational/` include summary, exact and learned rule catalogs, train-only guidance, cases, predictions, all symbolic proposals, provenance catalog, independent verification, figures, and immutable batch logs/configs. Raw corpus data stays local. No downloaded node code, saved configuration values, credentials, models or workflows are executed.
