use chrono::Duration;
use chrono::Utc;
use codex_http_client::HttpClientFactory;
use codex_http_client::OutboundProxyPolicy;
use codex_login::AuthCredentialsStoreMode;
use codex_login::AuthKeyringBackendKind;
use codex_login::AuthManager;
use codex_login::AuthRouteConfig;
use codex_login::LoginSuccessPage;
use codex_login::ServerOptions;
use codex_login::load_auth_dot_json;
use codex_login::oauth_client_id;
use codex_login::run_login_server;
use codex_login::token_data::parse_jwt_expiration;
use std::io;
use std::path::Path;
use std::path::PathBuf;
use std::sync::Arc;

// A dedicated 0600 credential file keeps this program's login across runs.
const STORE_MODE: AuthCredentialsStoreMode = AuthCredentialsStoreMode::File;

pub(crate) async fn run(status_only: bool, open_browser: bool) -> io::Result<bool> {
    let home = auth_home()?;
    let keyring = AuthKeyringBackendKind::default();
    let route = AuthRouteConfig::from_http_client_factory(HttpClientFactory::new(
        OutboundProxyPolicy::ReqwestDefault,
    ));

    if let Some(resolved) = resolve_after(0).await? {
        println!("Authenticated using {}{}.", resolved.source, resolved.identity);
        return Ok(true);
    }

    if status_only {
        println!("Not authenticated.");
        return Ok(false);
    }

    if open_browser {
        println!("Not authenticated. Opening your browser to sign in...");
    } else {
        println!("Not authenticated. Open the URL below to sign in.");
    }
    let mut options = ServerOptions::new(
        home.clone(),
        oauth_client_id(),
        None,
        STORE_MODE,
        keyring,
        route.clone(),
    );
    options.open_browser = open_browser;
    options.login_success_page = LoginSuccessPage::AuthenticationOnly;
    let login = run_login_server(options)?;
    if open_browser {
        println!("If the browser did not open, visit:\n{}", login.auth_url);
    } else {
        println!("Visit:\n{}", login.auth_url);
    }
    login.block_until_done().await?;

    match current_identity(&home, keyring, &route).await? {
        Some(identity) => {
            println!("Authenticated{identity}.");
            Ok(true)
        }
        None => Err(io::Error::other(
            "sign-in finished, but no usable credentials were saved",
        )),
    }
}

pub(crate) async fn identity() -> io::Result<Option<String>> {
    Ok(resolve_after(0).await?.map(|resolved| resolved.identity.trim_start_matches(" as ").to_owned()))
}

#[derive(Clone)]
pub(crate) struct ResolvedAuth {
    pub(crate) auth: codex_login::CodexAuth,
    pub(crate) index: usize,
    pub(crate) source: &'static str,
    identity: String,
}

#[derive(Default, serde::Deserialize)]
struct CentralConfig {
    #[serde(default)]
    cli_auth_credentials_store: AuthCredentialsStoreMode,
}

fn central_store(home: &Path) -> io::Result<AuthCredentialsStoreMode> {
    match std::fs::read_to_string(home.join("config.toml")) {
        Ok(text) => toml::from_str::<CentralConfig>(&text)
            .map(|config| config.cli_auth_credentials_store)
            .map_err(|_| io::Error::other("central Codex authentication configuration is invalid")),
        Err(error) if error.kind() == io::ErrorKind::NotFound => Ok(AuthCredentialsStoreMode::File),
        Err(_) => Err(io::Error::other("central Codex authentication configuration could not be read")),
    }
}

fn central_home() -> io::Result<PathBuf> {
    if let Some(path) = std::env::var_os("CODEX_HOME") {
        return Ok(PathBuf::from(path));
    }
    let home=std::env::var_os("HOME").or_else(|| std::env::var_os("USERPROFILE"))
        .ok_or_else(|| io::Error::other("home directory is unavailable"))?;
    Ok(PathBuf::from(home).join(".codex"))
}

pub(crate) async fn resolve_after(start: usize) -> io::Result<Option<ResolvedAuth>> {
    resolve_paths(&auth_home()?, &central_home()?, start).await
}

async fn resolve_paths(own: &Path, central: &Path, start: usize) -> io::Result<Option<ResolvedAuth>> {
    let route=AuthRouteConfig::from_http_client_factory(HttpClientFactory::new(OutboundProxyPolicy::ReqwestDefault));
    let keyring=AuthKeyringBackendKind::default();
    for index in start..2 {
        let (home,mode,source)=if index==0 {
            (own, STORE_MODE, "API Proxy credentials")
        } else {
            if own==central { continue; }
            (central, central_store(central)?, "central Codex credentials")
        };
        if let Some((auth,identity))=load_candidate(home,mode,keyring,&route).await? {
            return Ok(Some(ResolvedAuth{auth,index,source,identity}));
        }
    }
    Ok(None)
}

pub(crate) fn auth_home() -> io::Result<PathBuf> {
    if let Some(path) = std::env::var_os("CODEX_AUTH_HOME") {
        return Ok(PathBuf::from(path));
    }
    let home = std::env::var_os("HOME")
        .or_else(|| std::env::var_os("USERPROFILE"))
        .ok_or_else(|| io::Error::other("home directory is unavailable"))?;
    Ok(PathBuf::from(home).join(".codex-authentication"))
}

async fn current_identity(
    home: &Path,
    keyring: AuthKeyringBackendKind,
    route: &AuthRouteConfig,
) -> io::Result<Option<String>> {
    Ok(load_candidate(home, STORE_MODE, keyring, route).await?.map(|(_,identity)|identity))
}

async fn load_candidate(home: &Path, mode: AuthCredentialsStoreMode, keyring: AuthKeyringBackendKind, route: &AuthRouteConfig) -> io::Result<Option<(codex_login::CodexAuth,String)>> {
    match load_auth_dot_json(home, mode, keyring) {
        Ok(Some(saved)) => {
            // Expired local access tokens are unavailable for selection. The shared
            // AuthManager still owns proactive refresh of usable credentials.
            let usable=saved.tokens.as_ref().and_then(|tokens|parse_jwt_expiration(&tokens.access_token).ok().flatten())
                .is_some_and(|expiry|expiry > Utc::now()+Duration::seconds(30));
            if !usable { return Ok(None); }
        }
        Ok(None) => return Ok(None),
        Err(_) => {
            eprintln!("A saved credential source could not be read; trying the next source.");
            return Ok(None);
        }
    }
    let manager=Arc::new(AuthManager::new(home.to_path_buf(),false,mode,None,None,keyring,route.clone()).await);
    let Some(auth)=manager.auth().await else{return Ok(None)};
    let Ok(tokens)=auth.get_token_data() else{return Ok(None)};
    let Ok(Some(expiry))=parse_jwt_expiration(&tokens.access_token) else{return Ok(None)};
    if expiry<=Utc::now()+Duration::seconds(30) || auth.get_account_id().is_none() { return Ok(None); }
    let identity=auth.get_account_email().map(|email|format!(" as {email}")).unwrap_or_default();
    Ok(Some((auth,identity)))
}

#[cfg(test)]
mod tests {
    use super::*;
    use base64::Engine;
    use codex_login::AuthDotJson;
    use codex_login::TokenData;
    use codex_login::save_auth;
    use codex_login::token_data::parse_chatgpt_jwt_claims;
    use codex_protocol::auth::AuthMode;

    fn jwt(payload: serde_json::Value) -> String {
        let encoded = base64::engine::general_purpose::URL_SAFE_NO_PAD
            .encode(serde_json::to_vec(&payload).expect("JSON payload"));
        format!("e30.{encoded}.signature")
    }

    fn route() -> AuthRouteConfig {
        AuthRouteConfig::from_http_client_factory(HttpClientFactory::new(
            OutboundProxyPolicy::ReqwestDefault,
        ))
    }

    #[tokio::test]
    async fn saved_login_is_found_on_a_later_check() {
        let dir = tempfile::tempdir().expect("temporary credential directory");
        let id_token = jwt(serde_json::json!({"email": "user@example.com"}));
        let access_token = jwt(serde_json::json!({
            "exp": (Utc::now() + Duration::hours(1)).timestamp()
        }));
        let auth = AuthDotJson {
            auth_mode: Some(AuthMode::Chatgpt),
            openai_api_key: None,
            tokens: Some(TokenData {
                id_token: parse_chatgpt_jwt_claims(&id_token).expect("ID token"),
                access_token,
                refresh_token: "test-refresh-token".to_string(),
                oauth_provenance: None,
                login_owner_id: None,
                account_id: Some("test-account".into()),
            }),
            last_refresh: Some(Utc::now()),
            agent_identity: None,
            personal_access_token: None,
            bedrock_api_key: None,
            bedrock_access_keys: None,
        };
        save_auth(
            dir.path(),
            &auth,
            STORE_MODE,
            AuthKeyringBackendKind::default(),
        )
        .expect("save credentials");

        let identity = current_identity(dir.path(), AuthKeyringBackendKind::default(), &route())
            .await
            .expect("read credentials");
        assert_eq!(identity.as_deref(), Some(" as user@example.com"));
    }

    #[tokio::test]
    async fn no_saved_login_is_not_authenticated() {
        let dir = tempfile::tempdir().expect("temporary credential directory");
        let identity = current_identity(dir.path(), AuthKeyringBackendKind::default(), &route())
            .await
            .expect("read credentials");
        assert_eq!(identity, None);
    }

    #[tokio::test]
    async fn damaged_saved_login_allows_a_new_sign_in() {
        let dir = tempfile::tempdir().expect("temporary credential directory");
        std::fs::write(dir.path().join("auth.json"), "not JSON")
            .expect("write damaged credentials");
        let identity = current_identity(dir.path(), AuthKeyringBackendKind::default(), &route())
            .await
            .expect("read credentials");
        assert_eq!(identity, None);
    }
}

#[cfg(test)]
mod fallback_tests {
    use super::*;
    use base64::Engine;
    use codex_login::{AuthDotJson, TokenData, save_auth};
    use codex_login::token_data::parse_chatgpt_jwt_claims;
    use codex_protocol::auth::AuthMode;

    fn jwt(payload:serde_json::Value)->String {
        format!("e30.{}.signature",base64::engine::general_purpose::URL_SAFE_NO_PAD.encode(serde_json::to_vec(&payload).unwrap()))
    }
    fn save(home:&Path,email:&str,expiry:i64) {
        let auth=AuthDotJson {
            auth_mode:Some(AuthMode::Chatgpt),openai_api_key:None,
            tokens:Some(TokenData{id_token:parse_chatgpt_jwt_claims(&jwt(serde_json::json!({"email":email}))).unwrap(),access_token:jwt(serde_json::json!({"exp":expiry})),refresh_token:"fixture-refresh".into(),oauth_provenance:None,login_owner_id:None,account_id:Some("fixture-account".into())}),
            last_refresh:Some(Utc::now()),agent_identity:None,personal_access_token:None,bedrock_api_key:None,bedrock_access_keys:None,
        };
        save_auth(home,&auth,STORE_MODE,AuthKeyringBackendKind::default()).unwrap();
    }
    #[tokio::test]
    async fn own_usable_credentials_win_without_reading_central_configuration() {
        let own=tempfile::tempdir().unwrap();let central=tempfile::tempdir().unwrap();
        save(own.path(),"own@example.test",(Utc::now()+Duration::hours(1)).timestamp());
        std::fs::write(central.path().join("config.toml"),"invalid = [").unwrap();
        assert_eq!(resolve_paths(own.path(),central.path(),0).await.unwrap().unwrap().index,0);
    }
    #[tokio::test]
    async fn missing_own_uses_central_without_copying_credentials() {
        let own=tempfile::tempdir().unwrap();let central=tempfile::tempdir().unwrap();
        save(central.path(),"central@example.test",(Utc::now()+Duration::hours(1)).timestamp());
        let before=std::fs::read(central.path().join("auth.json")).unwrap();
        let resolved=resolve_paths(own.path(),central.path(),0).await.unwrap().unwrap();
        assert_eq!(resolved.index,1);assert_eq!(resolved.identity," as central@example.test");
        assert!(!own.path().join("auth.json").exists());
        assert_eq!(before,std::fs::read(central.path().join("auth.json")).unwrap());
    }
    #[tokio::test]
    async fn expired_own_uses_central_and_rejected_source_can_be_skipped() {
        let own=tempfile::tempdir().unwrap();let central=tempfile::tempdir().unwrap();
        save(own.path(),"own@example.test",(Utc::now()-Duration::hours(1)).timestamp());
        save(central.path(),"central@example.test",(Utc::now()+Duration::hours(1)).timestamp());
        assert_eq!(resolve_paths(own.path(),central.path(),0).await.unwrap().unwrap().index,1);
        save(own.path(),"own@example.test",(Utc::now()+Duration::hours(1)).timestamp());
        assert_eq!(resolve_paths(own.path(),central.path(),1).await.unwrap().unwrap().index,1);
        assert!(resolve_paths(own.path(),central.path(),2).await.unwrap().is_none());
    }
    #[tokio::test]
    async fn damaged_own_falls_back_but_ephemeral_central_never_reads_stale_file() {
        let own=tempfile::tempdir().unwrap();let central=tempfile::tempdir().unwrap();
        std::fs::write(own.path().join("auth.json"),"damaged").unwrap();
        save(central.path(),"central@example.test",(Utc::now()+Duration::hours(1)).timestamp());
        assert_eq!(resolve_paths(own.path(),central.path(),0).await.unwrap().unwrap().index,1);
        std::fs::write(central.path().join("config.toml"),"cli_auth_credentials_store = 'ephemeral'").unwrap();
        assert!(resolve_paths(own.path(),central.path(),0).await.unwrap().is_none());
    }
}
