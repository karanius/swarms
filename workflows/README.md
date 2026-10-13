# Reusable workflow snapshots

`images-on-my-mac.json` preserves the six-node image inventory canvas, its layout and connections, and its Markdown output node. The folder scope is portable (`~`). Run histories, filesystem inventory records, credentials, and permission grants are excluded.

To restore it to Saved workflows, start the project service and import the snapshot:

```sh
curl --fail --request POST http://127.0.0.1:52418/workflows \
  --header 'Content-Type: application/json' \
  --data-binary @workflows/images-on-my-mac.json
```

Then open Saved workflows in the app and load **Images on my Mac**. The restored workflow needs a new run to obtain current results.

The source code, settings defaults, dependency manifests, and selected verification evidence are already tracked in this repository. Browser-specific configurations and Docker database/storage contents are separate local data and are not included in this snapshot.

## macOS background service

`services/local.swarms.log-pipeline.plist.template` is a portable version of the local service configuration. Replace each `@PROJECT_ROOT@` with the restored repository's absolute path. Ensure the runtime environment and service dependencies have been installed before installing the rendered plist in your user's LaunchAgents directory.

Do not put local environment files, credentials, or sign-in tokens in GitHub.
