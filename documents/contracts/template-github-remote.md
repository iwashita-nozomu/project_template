# Template GitHub remote contract

`iwashita-nozomu/project_template` on branch `main` is the canonical template source. A derived repository owns its own `origin`; bootstrap does not preserve the template remote as a runtime dependency and does not configure any secondary source checkout.

## Publish a derived repository

After local initialization, review and commit the generated tree. Then attach the destination repository and push the committed branch:

```bash
git remote set-url origin <destination-url>
git push -u origin main
```

Creating the destination repository and authenticating that push are caller
responsibilities. They are the only network-dependent publication steps for a
parent project. No recursive clone, submodule credential, AgentCanon token, or
source/runtime seed refresh is part of publication.

## Branch protection baseline

For repositories that use protected `main`, require pull requests and these project-owned checks:

- `Repository CI`
- `Fresh Clone Acceptance`

Require the Docker workflow when Docker-owned paths change. Disable force-push and branch deletion for the protected branch, and keep conversation resolution enabled when review is required.
