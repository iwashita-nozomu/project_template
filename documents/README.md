# ドキュメント ハブ

`documents/` は、この repo の正本文書だけを置く場所です。
workflow 系の正本は shared agent canon に寄せ、template root と派生 repo root では symlink view として同じ path を使います。
experiment canon のうち、再利用する review guide、registry contract、report style、scaffold 方針も shared agent canon に寄せます。
ここでは「agent/workflow canon」「experiment canon」「template/environment canon」を分けて辿れるようにします。

## 最初に読む

- [conventions/README.md](/mnt/l/workspace/project_template/documents/conventions/README.md)
- [coding-conventions-project.md](/mnt/l/workspace/project_template/documents/coding-conventions-project.md)
- [linux-wsl-host-requirements.md](/mnt/l/workspace/project_template/documents/linux-wsl-host-requirements.md)
- [template-bootstrap.md](/mnt/l/workspace/project_template/documents/template-bootstrap.md)
- [WORKFLOW_GUIDE.md](/mnt/l/workspace/project_template/documents/WORKFLOW_GUIDE.md)
- [implementation-waterfall-workflow.md](/mnt/l/workspace/project_template/documents/implementation-waterfall-workflow.md)
- [FILE_CHECKLIST_OPERATIONS.md](/mnt/l/workspace/project_template/documents/FILE_CHECKLIST_OPERATIONS.md)
- [remote-execution-repo-contract.md](/mnt/l/workspace/project_template/documents/remote-execution-repo-contract.md)
- [server-host-contract.md](/mnt/l/workspace/project_template/documents/server-host-contract.md)

## Agent・Workflow Canon

- [WORKFLOW_GUIDE.md](/mnt/l/workspace/project_template/documents/WORKFLOW_GUIDE.md)
- [implementation-waterfall-workflow.md](/mnt/l/workspace/project_template/documents/implementation-waterfall-workflow.md)
- [main-integration-workflow.md](/mnt/l/workspace/project_template/documents/main-integration-workflow.md)
- [long-form-writing-workflow.md](/mnt/l/workspace/project_template/documents/long-form-writing-workflow.md)
- [notes-lifecycle.md](/mnt/l/workspace/project_template/documents/notes-lifecycle.md)
- [experiment-workflow.md](/mnt/l/workspace/project_template/documents/experiment-workflow.md)
- [research-workflow.md](/mnt/l/workspace/project_template/documents/research-workflow.md)
- [AGENTS_COORDINATION.md](/mnt/l/workspace/project_template/documents/AGENTS_COORDINATION.md)
- [agent-canon-subtree-migration.md](/mnt/l/workspace/project_template/documents/agent-canon-subtree-migration.md)
- [REVIEW_PROCESS.md](/mnt/l/workspace/project_template/documents/REVIEW_PROCESS.md)
- [BRANCH_SCOPE.md](/mnt/l/workspace/project_template/documents/BRANCH_SCOPE.md)
- [WORKTREE_SCOPE_TEMPLATE.md](/mnt/l/workspace/project_template/documents/WORKTREE_SCOPE_TEMPLATE.md)
- [workflow-references.md](/mnt/l/workspace/project_template/documents/workflow-references.md)

## 実験・研究 Canon

- [experiment-registry.md](/mnt/l/workspace/project_template/documents/experiment-registry.md)
- [experiment-critical-review.md](/mnt/l/workspace/project_template/documents/experiment-critical-review.md)
- [experiment-report-style.md](/mnt/l/workspace/project_template/documents/experiment-report-style.md)
- [coding-conventions-experiments.md](/mnt/l/workspace/project_template/documents/coding-conventions-experiments.md)

## コーディング規約

- [conventions/README.md](/mnt/l/workspace/project_template/documents/conventions/README.md)
- [coding-conventions-project.md](/mnt/l/workspace/project_template/documents/coding-conventions-project.md)
- [coding-conventions-house-style.md](/mnt/l/workspace/project_template/documents/coding-conventions-house-style.md)
- [coding-conventions-testing.md](/mnt/l/workspace/project_template/documents/coding-conventions-testing.md)
- [coding-conventions-reviews.md](/mnt/l/workspace/project_template/documents/coding-conventions-reviews.md)
- 言語補足が必要な場合だけ `coding-conventions-python.md` や `coding-conventions-cpp.md` を読みます。

## Template・Environment・Contract

- [templates/README.md](/mnt/l/workspace/project_template/documents/templates/README.md)
- [tools/README.md](/mnt/l/workspace/project_template/documents/tools/README.md)
- [tools/TOOLS_DIRECTORY.md](/mnt/l/workspace/project_template/documents/tools/TOOLS_DIRECTORY.md)
- [linux-wsl-host-requirements.md](/mnt/l/workspace/project_template/documents/linux-wsl-host-requirements.md)
- [remote-execution-repo-contract.md](/mnt/l/workspace/project_template/documents/remote-execution-repo-contract.md)
- [server-host-contract.md](/mnt/l/workspace/project_template/documents/server-host-contract.md)

## 困ったとき

- [TROUBLESHOOTING.md](/mnt/l/workspace/project_template/documents/TROUBLESHOOTING.md)
- [README.md](/mnt/l/workspace/project_template/README.md)
- [QUICK_START.md](/mnt/l/workspace/project_template/QUICK_START.md)

## 文書管理ルール

- `documents/` に正本以外を置きません。
- 規約変更時は、対応する正本を同じ変更で更新します。
- 履歴説明、日付付き報告、個別実験のメモは `notes/` 側へ分離します。
