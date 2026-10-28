use async_stream::stream;
use axum::Json;
use axum::Router;
use axum::body::Body;
use axum::extract::State;
use axum::http::{HeaderValue, StatusCode, header};
use axum::response::{IntoResponse, Response};
use axum::routing::{get, post};
use chrono::Utc;
use futures_util::StreamExt;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::io;
use std::io::Write;
use std::path::PathBuf;

const BACKEND: &str = "https://chatgpt.com/backend-api/codex/responses";
const DEFAULT_MODEL: &str = "gpt-6.1-sol";
const MODELS_URL: &str = "https://chatgpt.com/backend-api/codex/models?client_version=1.0.0";
const MAX_BODY: usize = 2 * 1024 * 1024;

#[derive(Clone, Debug, Deserialize, Serialize)]
pub(crate) struct Settings {
    pub(crate) model: String,
    pub(crate) effort: Option<String>,
    pub(crate) fast: bool,
}

pub(crate) struct UiModel {
    pub(crate) name: String,
    pub(crate) efforts: Vec<String>,
    pub(crate) fast: bool,
}

pub(crate) struct UiSnapshot {
    pub(crate) settings: Settings,
    pub(crate) models: Vec<UiModel>,
    pub(crate) replacement: Option<String>,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            model: DEFAULT_MODEL.into(),
            effort: None,
            fast: false,
        }
    }
}

#[derive(Clone)]
struct AppState {
    client: reqwest::Client,
    settings: Settings,
}

pub(crate) enum Action {
    Serve {
        port: Option<u16>,
        quiet: bool,
    },
    Configure {
        model: Option<String>,
        effort: Option<String>,
        fast: Option<bool>,
    },
    ShowConfig,
    CheckUpdate,
}

pub(crate) async fn run(action: Action) -> io::Result<()> {
    let home = auth_home()?;
    if super::authenticate::resolve_after(0).await?.is_none() {
        return Err(io::Error::other("no usable credentials in the authentication chain; run api-proxy login"));
    }
    let client = reqwest::Client::builder()
        .build()
        .map_err(io::Error::other)?;
    let mut settings = read_settings(&home)?;
    if let Action::Configure {
        model,
        effort,
        fast,
    } = &action
    {
        let mut args = Vec::new();
        if let Some(model) = model {
            args.extend(["--model".to_owned(), model.clone()]);
        }
        if let Some(effort) = effort {
            args.extend(["--effort".to_owned(), effort.clone()]);
        }
        if let Some(fast) = fast {
            args.extend([
                "--fast".to_owned(),
                if *fast { "on" } else { "off" }.to_owned(),
            ]);
        }
        apply_config_args(&mut settings, &args)?;
    }
    let catalog = fetch_catalog(&client).await?;
    if matches!(&action, Action::CheckUpdate) {
        return check_update(&settings, &catalog);
    }
    let mut resolved = settings.clone();
    resolve_settings(&mut resolved, &catalog)?;
    if matches!(&action, Action::ShowConfig) {
        println!(
            "{}",
            serde_json::to_string_pretty(&resolved).map_err(io::Error::other)?
        );
        return Ok(());
    }
    if matches!(&action, Action::Configure { .. }) {
        save_settings(&home, &settings)?;
        println!(
            "Saved model={}, effort={}, fast={}",
            resolved.model,
            resolved.effort.as_deref().unwrap_or("default"),
            resolved.fast
        );
        return Ok(());
    }
    settings = resolved;
    let Action::Serve { port, quiet } = action else {
        unreachable!()
    };
    let port = port
        .or_else(|| {
            std::env::var("CODEX_API_PORT")
                .ok()
                .and_then(|s| s.parse().ok())
        })
        .unwrap_or(8787);
    let listener = tokio::net::TcpListener::bind(("127.0.0.1", port)).await?;
    let state = AppState {
        client,
        settings: settings.clone(),
    };
    let app = Router::new()
        .route("/health", get(health))
        .route("/v1/models", get(models))
        .route("/v1/responses", post(responses))
        .route("/v1/chat/completions", post(chat_completions))
        .layer(axum::extract::DefaultBodyLimit::max(MAX_BODY))
        .with_state(state);
    if !quiet {
        println!("Local LLM API: http://127.0.0.1:{port}/v1");
        println!(
            "Model: {}, effort: {}, fast: {}. Press Ctrl-C to stop.",
            settings.model,
            settings.effort.as_deref().unwrap_or("default"),
            settings.fast
        );
        if let Some(replacement) = replacement_model(&settings, &catalog)? {
            println!(
                "Model update available: {} → {}",
                settings.model, replacement
            );
        }
    }
    axum::serve(listener, app).await.map_err(io::Error::other)
}

fn auth_home() -> io::Result<PathBuf> { super::authenticate::auth_home() }

fn read_settings(home: &PathBuf) -> io::Result<Settings> {
    let path = home.join("settings.json");
    match std::fs::read(path) {
        Ok(data) => serde_json::from_slice(&data).map_err(io::Error::other),
        Err(error) if error.kind() == io::ErrorKind::NotFound => Ok(Settings::default()),
        Err(error) => Err(error),
    }
}

fn save_settings(home: &PathBuf, settings: &Settings) -> io::Result<()> {
    std::fs::create_dir_all(home)?;
    let path = home.join("settings.json");
    let bytes = serde_json::to_vec_pretty(settings).map_err(io::Error::other)?;
    let mut options = std::fs::OpenOptions::new();
    options.write(true).create(true).truncate(true);
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        options.mode(0o600);
    }
    let mut file = options.open(&path)?;
    file.write_all(&bytes)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(&path, std::fs::Permissions::from_mode(0o600))?;
    }
    Ok(())
}

fn apply_config_args(settings: &mut Settings, args: &[String]) -> io::Result<()> {
    if args.is_empty() || args.len() % 2 != 0 {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "configure with --model NAME, --effort LEVEL, or --fast on|off",
        ));
    }
    if let Some(model) = args.chunks_exact(2).find(|pair| pair[0] == "--model") {
        if model[1].is_empty() {
            return Err(io::Error::new(
                io::ErrorKind::InvalidInput,
                "model cannot be empty",
            ));
        }
        settings.model = model[1].clone();
        settings.effort = None;
        settings.fast = false;
    }
    for pair in args.chunks_exact(2) {
        match pair[0].as_str() {
            "--model" => {}
            "--effort" => {
                settings.effort = if pair[1] == "default" {
                    None
                } else {
                    Some(pair[1].clone())
                }
            }
            "--fast" => {
                settings.fast = match pair[1].as_str() {
                    "on" => true,
                    "off" => false,
                    _ => {
                        return Err(io::Error::new(
                            io::ErrorKind::InvalidInput,
                            "--fast must be on or off",
                        ));
                    }
                }
            }
            _ => {
                return Err(io::Error::new(
                    io::ErrorKind::InvalidInput,
                    "unknown configuration option",
                ));
            }
        }
    }
    Ok(())
}

async fn fetch_catalog(client: &reqwest::Client) -> io::Result<Value> {
    let mut next=0;
    while let Some(resolved)=super::authenticate::resolve_after(next).await? {
        next=resolved.index+1;
        let token=resolved.auth.get_token()?;
        let account=resolved.auth.get_account_id().ok_or_else(||io::Error::other("account ID unavailable"))?;
        let response=client.get(MODELS_URL).bearer_auth(token).header("chatgpt-account-id",account).header("originator","codex_cli_rs").send().await.map_err(io::Error::other)?;
        if response.status()==reqwest::StatusCode::UNAUTHORIZED { continue; }
        if !response.status().is_success() { return Err(io::Error::other(format!("model catalog request failed: {}",response.status()))); }
        return response.json().await.map_err(io::Error::other);
    }
    Err(io::Error::other("authentication chain exhausted; sign in again"))
}

fn selected_model<'a>(settings: &Settings, catalog: &'a Value) -> io::Result<&'a Value> {
    catalog["models"]
        .as_array()
        .into_iter()
        .flatten()
        .find(|model| model["slug"] == settings.model)
        .ok_or_else(|| {
            io::Error::new(
                io::ErrorKind::InvalidInput,
                format!("model {} is unavailable for this account", settings.model),
            )
        })
}

fn resolve_settings(settings: &mut Settings, catalog: &Value) -> io::Result<()> {
    let model = selected_model(settings, catalog)?;
    if settings.effort.is_none() {
        settings.effort = model["default_reasoning_level"].as_str().map(str::to_owned);
    }
    if let Some(effort) = &settings.effort {
        let supported = model["supported_reasoning_levels"]
            .as_array()
            .into_iter()
            .flatten()
            .any(|item| item["effort"] == *effort);
        if !supported {
            return Err(io::Error::new(
                io::ErrorKind::InvalidInput,
                format!("effort {effort} is unsupported by {}", settings.model),
            ));
        }
    }
    if settings.fast
        && !model["service_tiers"]
            .as_array()
            .into_iter()
            .flatten()
            .any(|tier| tier["id"] == "priority")
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            format!("fast mode is unavailable for {}", settings.model),
        ));
    }
    Ok(())
}

fn replacement_model<'a>(settings: &Settings, catalog: &'a Value) -> io::Result<Option<&'a str>> {
    let model = selected_model(settings, catalog)?;
    Ok(model["upgrade"]["model"].as_str())
}

fn check_update(settings: &Settings, catalog: &Value) -> io::Result<()> {
    if let Some(replacement) = replacement_model(settings, catalog)? {
        println!(
            "Model update available: {} → {}",
            settings.model, replacement
        );
    } else {
        println!("No model update is advertised for {}.", settings.model);
    }
    Ok(())
}

async fn ui_catalog() -> io::Result<Value> {
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(10))
        .build()
        .map_err(io::Error::other)?;
    fetch_catalog(&client).await
}

fn ui_snapshot_from_catalog(mut settings: Settings, catalog: &Value) -> io::Result<UiSnapshot> {
    resolve_settings(&mut settings, catalog)?;
    let replacement = replacement_model(&settings, catalog)?.map(str::to_owned);
    let models = catalog["models"]
        .as_array()
        .into_iter()
        .flatten()
        .filter(|model| model["visibility"] == "list" || model["slug"] == settings.model)
        .filter_map(|model| {
            let name = model["slug"].as_str()?.to_owned();
            let efforts = model["supported_reasoning_levels"]
                .as_array()
                .into_iter()
                .flatten()
                .filter_map(|item| item["effort"].as_str().map(str::to_owned))
                .collect();
            let fast = model["service_tiers"]
                .as_array()
                .into_iter()
                .flatten()
                .any(|tier| tier["id"] == "priority");
            Some(UiModel {
                name,
                efforts,
                fast,
            })
        })
        .collect();
    Ok(UiSnapshot {
        settings,
        models,
        replacement,
    })
}

pub(crate) async fn ui_snapshot() -> io::Result<UiSnapshot> {
    let home = auth_home()?;
    let catalog = ui_catalog().await?;
    ui_snapshot_from_catalog(read_settings(&home)?, &catalog)
}

pub(crate) async fn ui_save(settings: Settings) -> io::Result<UiSnapshot> {
    let home = auth_home()?;
    let catalog = ui_catalog().await?;
    let snapshot = ui_snapshot_from_catalog(settings.clone(), &catalog)?;
    save_settings(&home, &settings)?;
    Ok(snapshot)
}

async fn health(State(_state): State<AppState>) -> impl IntoResponse {
    Json(
        json!({"status": if super::authenticate::resolve_after(0).await.ok().flatten().is_some() { "authenticated" } else { "unauthenticated" }}),
    )
}

async fn models(State(state): State<AppState>) -> impl IntoResponse {
    Json(
        json!({"object":"list","data":[{"id":state.settings.model,"object":"model","owned_by":"codex"}]}),
    )
}

fn error(status: StatusCode, message: &str) -> Response {
    (
        status,
        Json(json!({"error":{"message":message,"type":"invalid_request_error"}})),
    )
        .into_response()
}

fn validate_model(value: &Value, state: &AppState) -> Result<(), Response> {
    match value.get("model").and_then(Value::as_str) {
        Some(model) if model == state.settings.model => Ok(()),
        Some(_) => Err(error(
            StatusCode::BAD_REQUEST,
            "unsupported model; see GET /v1/models or run api-proxy config set",
        )),
        None => Err(error(StatusCode::BAD_REQUEST, "model is required")),
    }
}

async fn send_upstream(state: &AppState, body: Value) -> Result<reqwest::Response, Response> {
    let mut next=0;
    let response=loop {
        let resolved=super::authenticate::resolve_after(next).await
            .map_err(|_|error(StatusCode::UNAUTHORIZED,"authentication source unavailable"))?
            .ok_or_else(||error(StatusCode::UNAUTHORIZED,"authentication chain exhausted; sign in again"))?;
        next=resolved.index+1;
        let token=resolved.auth.get_token().map_err(|_|error(StatusCode::UNAUTHORIZED,"sign-in token unavailable"))?;
        let account=resolved.auth.get_account_id().ok_or_else(||error(StatusCode::UNAUTHORIZED,"account ID unavailable"))?;
        let response=state.client.post(BACKEND).bearer_auth(token).header("chatgpt-account-id",account).header("originator","codex_cli_rs").header(header::ACCEPT,"text/event-stream").json(&body).send().await.map_err(|_|error(StatusCode::BAD_GATEWAY,"upstream connection failed"))?;
        if response.status()==reqwest::StatusCode::UNAUTHORIZED { continue; }
        break response;
    };
    if !response.status().is_success() {
        let status =
            StatusCode::from_u16(response.status().as_u16()).unwrap_or(StatusCode::BAD_GATEWAY);
        let body = response.text().await.unwrap_or_default();
        let message = if body.len() > 1000 {
            &body[..body.floor_char_boundary(1000)]
        } else {
            &body
        };
        return Err(error(status, message));
    }
    Ok(response)
}

fn apply_request_settings(body: &mut Value, settings: &Settings) {
    let obj = body.as_object_mut().expect("request object");
    if let Some(effort) = &settings.effort {
        obj.insert("reasoning".into(), json!({"effort":effort}));
    }
    if settings.fast {
        obj.insert("service_tier".into(), json!("priority"));
    } else {
        obj.remove("service_tier");
    }
}

fn normalize_responses(mut body: Value, settings: &Settings) -> Result<Value, Response> {
    let obj = body
        .as_object_mut()
        .ok_or_else(|| error(StatusCode::BAD_REQUEST, "JSON object required"))?;
    match obj.get("input") {
        Some(Value::String(text)) => {
            let message = json!({"role":"user","content":[{"type":"input_text","text":text}]});
            obj.insert("input".into(), json!([message]));
        }
        Some(Value::Array(_)) => {}
        _ => {
            return Err(error(
                StatusCode::BAD_REQUEST,
                "input must be text or an array",
            ));
        }
    }
    obj.insert("stream".into(), json!(true));
    obj.insert("store".into(), json!(false));
    obj.entry("instructions")
        .or_insert(json!("You are a helpful assistant."));
    obj.entry("tools").or_insert(json!([]));
    obj.entry("tool_choice").or_insert(json!("auto"));
    obj.entry("parallel_tool_calls").or_insert(json!(false));
    obj.entry("include").or_insert(json!([]));
    apply_request_settings(&mut body, settings);
    Ok(body)
}

async fn responses(State(state): State<AppState>, Json(body): Json<Value>) -> Response {
    if let Err(e) = validate_model(&body, &state) {
        return e;
    }
    let wants_stream = body.get("stream").and_then(Value::as_bool).unwrap_or(false);
    let body = match normalize_responses(body, &state.settings) {
        Ok(b) => b,
        Err(e) => return e,
    };
    let upstream = match send_upstream(&state, body).await {
        Ok(r) => r,
        Err(e) => return e,
    };
    if wants_stream {
        let mut response = Response::new(Body::from_stream(upstream.bytes_stream()));
        response.headers_mut().insert(
            header::CONTENT_TYPE,
            HeaderValue::from_static("text/event-stream"),
        );
        response
            .headers_mut()
            .insert(header::CACHE_CONTROL, HeaderValue::from_static("no-cache"));
        return response;
    }
    match collect_completed(upstream).await {
        Ok(value) => Json(value).into_response(),
        Err(message) => error(StatusCode::BAD_GATEWAY, &message),
    }
}

async fn collect_completed(response: reqwest::Response) -> Result<Value, String> {
    let mut stream = response.bytes_stream();
    let mut pending = String::new();
    let mut completed = None;
    while let Some(chunk) = stream.next().await {
        let chunk = chunk.map_err(|e| e.to_string())?;
        pending.push_str(&String::from_utf8_lossy(&chunk));
        while let Some((event, consumed)) = take_event(&pending) {
            if let Some(value) = event_data(&event) {
                if value["type"] == "response.completed" {
                    completed = value.get("response").cloned();
                }
                if value["type"] == "response.failed" {
                    return Err(value.to_string());
                }
            }
            pending.drain(..consumed);
        }
    }
    completed.ok_or_else(|| "upstream ended without a completed response".into())
}

fn take_event(pending: &str) -> Option<(String, usize)> {
    if let Some(end) = pending.find("\n\n") {
        return Some((pending[..end].to_owned(), end + 2));
    }
    if let Some(end) = pending.find("\r\n\r\n") {
        return Some((pending[..end].to_owned(), end + 4));
    }
    None
}

fn event_data(event: &str) -> Option<Value> {
    let data = event
        .lines()
        .filter_map(|line| {
            line.strip_prefix("data: ")
                .or_else(|| line.strip_prefix("data:"))
        })
        .collect::<Vec<_>>()
        .join("\n");
    serde_json::from_str(&data).ok()
}

fn chat_input(body: &Value, settings: &Settings) -> Result<Value, Response> {
    let messages = body
        .get("messages")
        .and_then(Value::as_array)
        .ok_or_else(|| error(StatusCode::BAD_REQUEST, "messages array is required"))?;
    let mut input = Vec::new();
    let mut instructions = Vec::new();
    let mut pending_calls = std::collections::HashSet::new();
    for message in messages {
        let role = message.get("role").and_then(Value::as_str).unwrap_or("");
        match role {
            "system" | "developer" | "user" | "assistant" => {
                if !pending_calls.is_empty() {
                    return Err(error(
                        StatusCode::BAD_REQUEST,
                        "supply all pending tool results before another message",
                    ));
                }
                let content = message.get("content").and_then(Value::as_str);
                if role != "assistant" || content.is_some() {
                    let content = content.ok_or_else(|| {
                        error(
                            StatusCode::BAD_REQUEST,
                            "only text message content is supported",
                        )
                    })?;
                    if role == "system" || role == "developer" {
                        instructions.push(content.to_owned());
                    } else {
                        input.push(json!({"role":role,"content":[{"type":if role == "assistant" {"output_text"} else {"input_text"},"text":content}]}));
                    }
                }
                if let Some(calls) = message.get("tool_calls") {
                    if role != "assistant" {
                        return Err(error(
                            StatusCode::BAD_REQUEST,
                            "only assistant messages may contain tool_calls",
                        ));
                    }
                    let calls = calls
                        .as_array()
                        .filter(|calls| !calls.is_empty())
                        .ok_or_else(|| {
                            error(
                                StatusCode::BAD_REQUEST,
                                "tool_calls must be a non-empty array",
                            )
                        })?;
                    for call in calls {
                        let call_id = call
                            .get("id")
                            .and_then(Value::as_str)
                            .filter(|s| !s.is_empty())
                            .ok_or_else(|| {
                                error(StatusCode::BAD_REQUEST, "tool call ID is required")
                            })?;
                        let function = call.get("function").ok_or_else(|| {
                            error(StatusCode::BAD_REQUEST, "tool call function is required")
                        })?;
                        let name = function
                            .get("name")
                            .and_then(Value::as_str)
                            .filter(|s| !s.is_empty())
                            .ok_or_else(|| {
                                error(StatusCode::BAD_REQUEST, "tool call name is required")
                            })?;
                        let arguments = function
                            .get("arguments")
                            .and_then(Value::as_str)
                            .ok_or_else(|| {
                                error(
                                    StatusCode::BAD_REQUEST,
                                    "tool call arguments must be JSON text",
                                )
                            })?;
                        if call.get("type").and_then(Value::as_str) != Some("function")
                            || serde_json::from_str::<Value>(arguments).is_err()
                            || !pending_calls.insert(call_id.to_owned())
                        {
                            return Err(error(
                                StatusCode::BAD_REQUEST,
                                "invalid or duplicate function call",
                            ));
                        }
                        input.push(json!({"type":"function_call","call_id":call_id,"name":name,"arguments":arguments}));
                    }
                }
            }
            "tool" => {
                let call_id = message
                    .get("tool_call_id")
                    .and_then(Value::as_str)
                    .ok_or_else(|| error(StatusCode::BAD_REQUEST, "tool_call_id is required"))?;
                let output = message
                    .get("content")
                    .and_then(Value::as_str)
                    .ok_or_else(|| error(StatusCode::BAD_REQUEST, "tool result must be text"))?;
                if !pending_calls.remove(call_id) {
                    return Err(error(
                        StatusCode::BAD_REQUEST,
                        "tool result has no pending call",
                    ));
                }
                input
                    .push(json!({"type":"function_call_output","call_id":call_id,"output":output}));
            }
            _ => return Err(error(StatusCode::BAD_REQUEST, "unsupported message role")),
        }
    }
    if !pending_calls.is_empty() {
        return Err(error(
            StatusCode::BAD_REQUEST,
            "supply all pending tool results",
        ));
    }
    if input.is_empty() {
        return Err(error(
            StatusCode::BAD_REQUEST,
            "at least one user or assistant message is required",
        ));
    }
    let tools = chat_tools(body)?;
    let tool_choice = chat_tool_choice(body)?;
    let mut request = json!({
        "model": body["model"], "stream":true, "store":false,
        "instructions": if instructions.is_empty() { "You are a helpful assistant.".to_owned() } else { instructions.join("\n\n") },
        "input":input,"tools":tools,"tool_choice":tool_choice,"parallel_tool_calls":false,"include":[]
    });
    apply_request_settings(&mut request, settings);
    Ok(request)
}

fn chat_tools(body: &Value) -> Result<Vec<Value>, Response> {
    let Some(tools) = body.get("tools") else {
        return Ok(Vec::new());
    };
    let tools = tools
        .as_array()
        .filter(|tools| tools.len() <= 64)
        .ok_or_else(|| {
            error(
                StatusCode::BAD_REQUEST,
                "tools must be an array of at most 64 functions",
            )
        })?;
    let mut names = std::collections::HashSet::new();
    tools.iter().map(|tool| {
        let function = tool.get("function").ok_or_else(|| error(StatusCode::BAD_REQUEST, "function tool definition is required"))?;
        let name = function.get("name").and_then(Value::as_str).filter(|s| !s.is_empty()).ok_or_else(|| error(StatusCode::BAD_REQUEST, "function name is required"))?;
        if tool.get("type").and_then(Value::as_str) != Some("function") || !names.insert(name.to_owned()) {
            return Err(error(StatusCode::BAD_REQUEST, "invalid or duplicate function tool"));
        }
        let parameters = function.get("parameters").cloned().unwrap_or_else(|| json!({"type":"object","properties":{}}));
        if !parameters.is_object() {
            return Err(error(StatusCode::BAD_REQUEST, "function parameters must be an object schema"));
        }
        Ok(json!({"type":"function","name":name,"description":function.get("description").and_then(Value::as_str).unwrap_or(""),"parameters":parameters,"strict":function.get("strict").and_then(Value::as_bool).unwrap_or(false)}))
    }).collect()
}

fn chat_tool_choice(body: &Value) -> Result<Value, Response> {
    let choice = body.get("tool_choice").unwrap_or(&Value::Null);
    if choice.is_null() {
        return Ok(json!("auto"));
    }
    if let Some(value) = choice.as_str() {
        if matches!(value, "auto" | "none" | "required") {
            return Ok(json!(value));
        }
    }
    if choice.get("type").and_then(Value::as_str) == Some("function") {
        if let Some(name) = choice
            .get("function")
            .and_then(|f| f.get("name"))
            .and_then(Value::as_str)
        {
            return Ok(json!({"type":"function","name":name}));
        }
    }
    Err(error(StatusCode::BAD_REQUEST, "unsupported tool_choice"))
}

fn chat_result(response: &Value, model: &str) -> Value {
    let content = response["output"]
        .as_array()
        .into_iter()
        .flatten()
        .flat_map(|item| item["content"].as_array().into_iter().flatten())
        .filter(|part| part["type"] == "output_text")
        .filter_map(|part| part["text"].as_str())
        .collect::<String>();
    let calls = response["output"].as_array().into_iter().flatten()
        .filter(|item| item["type"] == "function_call")
        .map(|item| json!({"id":item["call_id"],"type":"function","function":{"name":item["name"],"arguments":item["arguments"]}}))
        .collect::<Vec<_>>();
    let mut message = json!({"role":"assistant","content":if content.is_empty() { Value::Null } else { json!(content) }});
    if !calls.is_empty() {
        message["tool_calls"] = json!(calls);
    }
    json!({
        "id":response["id"],"object":"chat.completion","created":Utc::now().timestamp(),
        "model":model,"choices":[{"index":0,"message":message,"finish_reason":if calls.is_empty() {"stop"} else {"tool_calls"}}],
        "usage":response["usage"]
    })
}

async fn chat_completions(State(state): State<AppState>, Json(body): Json<Value>) -> Response {
    if let Err(e) = validate_model(&body, &state) {
        return e;
    }
    let wants_stream = body.get("stream").and_then(Value::as_bool).unwrap_or(false);
    let request = match chat_input(&body, &state.settings) {
        Ok(v) => v,
        Err(e) => return e,
    };
    let upstream = match send_upstream(&state, request).await {
        Ok(r) => r,
        Err(e) => return e,
    };
    if wants_stream {
        return chat_stream(upstream, state.settings.model);
    }
    match collect_completed(upstream).await {
        Ok(response) => Json(chat_result(&response, &state.settings.model)).into_response(),
        Err(message) => error(StatusCode::BAD_GATEWAY, &message),
    }
}

fn chat_stream(upstream: reqwest::Response, model: String) -> Response {
    let mut bytes = upstream.bytes_stream();
    let output = stream! {
        let mut pending = String::new();
        let id = format!("chatcmpl-{}", Utc::now().timestamp_millis());
        let created = Utc::now().timestamp();
        yield Ok::<_, io::Error>(format!("data: {}\n\n", json!({"id":id,"object":"chat.completion.chunk","created":created,"model":model,"choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]})));
        while let Some(chunk) = bytes.next().await {
            let Ok(chunk) = chunk else { break; };
            pending.push_str(&String::from_utf8_lossy(&chunk));
            while let Some((event, consumed)) = take_event(&pending) {
                if let Some(value) = event_data(&event) {
                    if value["type"] == "response.output_text.delta" {
                        if let Some(delta) = value["delta"].as_str() {
                            yield Ok(format!("data: {}\n\n", json!({"id":id,"object":"chat.completion.chunk","created":created,"model":model,"choices":[{"index":0,"delta":{"content":delta},"finish_reason":null}]})));
                        }
                    }
                    if value["type"] == "response.completed" {
                        let result = chat_result(&value["response"], &model);
                        let calls = result["choices"][0]["message"]["tool_calls"].as_array();
                        if let Some(calls) = calls {
                            for (index, call) in calls.iter().enumerate() {
                                yield Ok(format!("data: {}\n\n", json!({"id":id,"object":"chat.completion.chunk","created":created,"model":model,"choices":[{"index":0,"delta":{"tool_calls":[{"index":index,"id":call["id"],"type":"function","function":call["function"]}]},"finish_reason":null}]})));
                            }
                        }
                        yield Ok(format!("data: {}\n\n", json!({"id":id,"object":"chat.completion.chunk","created":created,"model":model,"choices":[{"index":0,"delta":{},"finish_reason":result["choices"][0]["finish_reason"]}]})));
                    }
                }
                pending.drain(..consumed);
            }
        }
        yield Ok("data: [DONE]\n\n".to_owned());
    };
    let mut response = Response::new(Body::from_stream(output));
    response.headers_mut().insert(
        header::CONTENT_TYPE,
        HeaderValue::from_static("text/event-stream"),
    );
    response
        .headers_mut()
        .insert(header::CACHE_CONTROL, HeaderValue::from_static("no-cache"));
    response
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn chat_request_maps_roles_and_text() {
        let body = json!({"model":"gpt-test","messages":[{"role":"system","content":"Be concise"},{"role":"user","content":"hi"}]});
        let mapped = chat_input(&body, &Settings::default()).unwrap();
        assert_eq!(mapped["instructions"], "Be concise");
        assert_eq!(mapped["input"][0]["content"][0]["text"], "hi");
        assert_eq!(mapped["stream"], true);
        assert_eq!(mapped["store"], false);
    }
    #[test]
    fn chat_function_exchange_maps_to_responses() {
        let tool = json!({"type":"function","function":{"name":"get_number","description":"Return a number","parameters":{"type":"object","properties":{}}}});
        let body = json!({"model":"gpt-test","tools":[tool],"messages":[
            {"role":"user","content":"What is the number?"},
            {"role":"assistant","content":null,"tool_calls":[{"id":"call_1","type":"function","function":{"name":"get_number","arguments":"{}"}}]},
            {"role":"tool","tool_call_id":"call_1","content":"42"}
        ]});
        let mapped = chat_input(&body, &Settings::default()).unwrap();
        assert_eq!(mapped["tools"][0]["name"], "get_number");
        assert_eq!(mapped["input"][1]["type"], "function_call");
        assert_eq!(mapped["input"][2]["type"], "function_call_output");
        assert_eq!(mapped["input"][2]["output"], "42");
        let result = chat_result(
            &json!({"id":"r1","output":[{"type":"function_call","call_id":"call_2","name":"get_number","arguments":"{}"}]}),
            "gpt-test",
        );
        assert_eq!(result["choices"][0]["finish_reason"], "tool_calls");
        assert_eq!(
            result["choices"][0]["message"]["tool_calls"][0]["id"],
            "call_2"
        );
    }
    #[test]
    fn chat_rejects_unmatched_tool_results() {
        let body = json!({"model":"gpt-test","messages":[{"role":"user","content":"hi"},{"role":"tool","tool_call_id":"unknown","content":"42"}]});
        assert!(chat_input(&body, &Settings::default()).is_err());
    }
    #[test]
    fn event_parser_reads_completed_event() {
        let raw = "event: response.completed\ndata: {\"type\":\"response.completed\",\"response\":{\"id\":\"r1\"}}\n\n";
        let (event, size) = take_event(raw).unwrap();
        assert_eq!(size, raw.len());
        assert_eq!(event_data(&event).unwrap()["response"]["id"], "r1");
    }

    #[test]
    fn configured_effort_and_fast_mode_reach_both_request_formats() {
        let settings = Settings {
            model: "gpt-test".into(),
            effort: Some("high".into()),
            fast: true,
        };
        let response =
            normalize_responses(json!({"model":"gpt-test","input":"hi"}), &settings).unwrap();
        let chat = chat_input(
            &json!({"model":"gpt-test","messages":[{"role":"user","content":"hi"}]}),
            &settings,
        )
        .unwrap();
        for request in [response, chat] {
            assert_eq!(request["reasoning"]["effort"], "high");
            assert_eq!(request["service_tier"], "priority");
        }
    }

    #[test]
    fn catalog_rejects_unsupported_configuration() {
        let catalog = json!({"models":[{"slug":"gpt-test","default_reasoning_level":"low","supported_reasoning_levels":[{"effort":"low"}],"service_tiers":[]}]});
        let mut settings = Settings {
            model: "gpt-test".into(),
            effort: Some("high".into()),
            fast: false,
        };
        assert!(resolve_settings(&mut settings, &catalog).is_err());
        settings.effort = None;
        settings.fast = true;
        assert!(resolve_settings(&mut settings, &catalog).is_err());
        settings.fast = false;
        resolve_settings(&mut settings, &catalog).unwrap();
        assert_eq!(settings.effort.as_deref(), Some("low"));
    }

    #[test]
    fn update_requires_explicit_provider_replacement() {
        let settings = Settings {
            model: "old-model".into(),
            effort: None,
            fast: false,
        };
        let catalog = json!({"models":[{"slug":"old-model","upgrade":{"model":"new-model"}}]});
        assert_eq!(
            replacement_model(&settings, &catalog).unwrap(),
            Some("new-model")
        );
        let catalog = json!({"models":[{"slug":"old-model"},{"slug":"new-model"}]});
        assert_eq!(replacement_model(&settings, &catalog).unwrap(), None);
    }

    #[test]
    fn configuration_flags_work_in_any_order() {
        let mut settings = Settings::default();
        let args =
            ["--effort", "high", "--fast", "on", "--model", "gpt-6-astra"].map(str::to_owned);
        apply_config_args(&mut settings, &args).unwrap();
        assert_eq!(settings.model, "gpt-6-astra");
        assert_eq!(settings.effort.as_deref(), Some("high"));
        assert!(settings.fast);
    }
}
