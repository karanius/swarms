# Paper 3 initial structural study

Open `../notebooks/Paper 3 - Iterative Development of Boundary Resolution.ipynb` in Research. Run its three code cells in order to regenerate the recorded tables and figures. The first cell imports `study.py`; keep this directory alongside the notebook in the repository.

This is a synthetic finite source–transform–sink grammar, not a full implementation of Paper 2 or behavioral evaluation of Langflow. Protocol, code, inputs and reference checks were authored by the same assistant. The evaluation collection is designated evaluation but exposed/same-author, not independently held out. The packaging defect/correction was planned before execution.

Artifacts:
- `protocol.json`: scope, decision criteria and method comparison.
- `study.py`: generator, synthetic cases and separately invoked assessor.
- `observations/`: all 51 method–case attempts, aggregate counts and content hashes.
- `pre-experiment-paper3.ipynb`: archived draft before the study executed.

The notebook requires a Python kernel with IPython and Matplotlib, available in the existing Research environment. It finds the module by searching the notebook working directory's ancestors for the repository-relative study path. No models, credentials or network access are used by the experiment.

Rerunning overwrites current observations deterministically. Preserve a versioned copy before changing code or protocol for a new comparison. Original recorded observations remain in Git history. The manuscript reports only the narrow study outcomes and explicitly limits generalization.
