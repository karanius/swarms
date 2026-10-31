# Local Kestra playground

Open http://localhost:8080 after startup.

Start:

```sh
docker compose -f services/kestra/compose.yaml up -d
```

Stop (preserves workflows and execution history):

```sh
docker compose -f services/kestra/compose.yaml down
```

The setup uses the official Kestra v2.0.7 core image and PostgreSQL 18, persistent Docker volumes, and a localhost-only web port. The core image omits optional integration plugins; install those when needed. Docker socket access is not enabled. Commands that require a Docker task runner need additional configuration.

`input-output-demo.yaml` defines editable message and uppercase inputs, a transformation, a log step, and a declared result output. It needs no external credentials or paid services.

Based on the [official Compose setup](https://kestra.io/docs/installation/docker-compose).

Login credentials are in the ignored `.env` file beside this guide. The generated local admin username is `admin@localhost.test`. Keep `.env` when restarting this setup.

Verified 2026-10-24: browser login and editor worked; execution `62BJobhaSkKJoi0ootFLHB` finished SUCCESS in 0.212 seconds with declared output `{"result":"BUILD WORKFLOWS QUICKLY"}`. Initial execution requests timed out while first-start plugin installation was still initializing the execution engine; the later browser-triggered run succeeded.
