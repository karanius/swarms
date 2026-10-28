# API Proxy

API Proxy turns your signed-in account into a local LLM endpoint. It remembers your session, lets you choose a model and reasoning settings, and serves requests from programs on your computer. You can operate it from an interactive terminal screen or with commands.

API Proxy uses your ChatGPT account for model access, so your account's access and usage limits apply. It forwards model requests and responses; it does not execute functions requested by a model. Your client runs those functions and sends their results back.

## Run it

Install [Rust with rustup](https://rustup.rs/), then from this directory run:

```sh
./run.sh
```

On first use, choose **Sign in / refresh status** and follow the browser sign-in. Use ↑/↓ and Enter to select actions. Choose **Start local API** when you want to accept requests. The screen shows whether you are signed in, the selected model, and whether the API is running. Press `q` to quit; an API started from the interface stops when you quit.

For a terminal without the interface:

```sh
./run.sh login
./run.sh status
./run.sh serve
```

`serve` starts the API and keeps it running until Ctrl-C. Use `./run.sh --help` for all commands. The launcher selects the pinned Rust toolchain and keeps build files outside this directory.

## Connect a client

The default API base URL is:

```text
http://127.0.0.1:8787/v1
```

It supports `POST /v1/chat/completions`, `POST /v1/responses`, and `GET /v1/models`. Both request formats support text, streaming, and function calls. The Chat Completions route accepts a function result in a later request with the earlier assistant call and its matching `tool_call_id` in the message history. The Responses route accepts the native `function_call_output` item. The caller remains responsible for executing functions and deciding what results to return.

Find the selected model ID:

```sh
curl http://127.0.0.1:8787/v1/models
```

Then send a request, replacing `MODEL_ID` with that ID:

```sh
curl http://127.0.0.1:8787/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"MODEL_ID","messages":[{"role":"user","content":"Say hello."}]}'
```

The listener binds to `127.0.0.1`, so only this computer can connect to it directly. There is no separate API key on the local endpoint; local programs with access to that address can use your signed-in session.

## Choose a model

Use the terminal interface, or set options directly:

```sh
./run.sh config set --model MODEL_ID --effort low --fast off
./run.sh config show
./run.sh update
```

The app checks model and effort choices against the models available to your account. `update` reports a newer model only when the provider advertises a replacement. Restart a separately running API after changing settings; the interface restarts an API that it started itself.

Your sign-in and settings are stored locally under your home directory with restricted file permissions. They are not part of this repository.

## Current scope

API Proxy serves one selected model at a time on your computer. It supports text requests, streaming, and caller-managed function calls through the routes above. It does not provide remote access or execute model-requested functions for you.

## Shared authentication fallback

Every entry point (status, terminal UI, model discovery and inference) uses one resolver. It first tries API Proxy's own credential store (`CODEX_AUTH_HOME`, default `~/.codex-authentication`), then the central Codex store (`CODEX_HOME`, default `~/.codex`). Central credentials remain in their original store; API Proxy does not copy them into its own file. Settings remain in API Proxy's directory.

The central `config.toml` selects `cli_auth_credentials_store` (`file`, `keyring`, `auto`, or `ephemeral`), using Codex's credential loader. A credential must contain a usable ChatGPT access token and account identity. Missing, malformed or expired credentials advance to the next source. Usable credentials retain Codex's guarded proactive refresh. When no source is usable, interactive sign-in saves only to API Proxy's own store. This is a local credential-store integration; it does not read browser cookies or extract credentials from a running conversation.

An upstream HTTP 401 advances once to the next source for that request. The chain is finite: exhaustion reports an authentication failure. Other errors (403 permission restrictions, 429 limits, network failures, model failures) are returned without switching accounts. Streaming is never restarted after output begins.

Central store configuration parse failures stop resolution rather than guessing another storage mode. System-managed Codex policies are not loaded by this standalone proxy; deployments requiring managed authentication policy must use their approved integration.
