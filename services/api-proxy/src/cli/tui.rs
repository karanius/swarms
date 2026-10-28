use std::io::{self, IsTerminal};
use std::time::Duration;

use crossterm::event::{self, Event, KeyCode, KeyEventKind, KeyModifiers};
use ratatui::layout::{Constraint, Direction, Layout};
use ratatui::style::{Color, Modifier, Style};
use ratatui::widgets::{Block, List, ListItem, ListState, Paragraph, Wrap};
use ratatui::{DefaultTerminal, Frame};
use tokio::task::JoinHandle;

use super::{authenticate, local_api};

#[derive(Clone, Copy, PartialEq, Eq)]
enum View {
    Home,
    Models,
    Efforts,
}

struct App {
    identity: Option<String>,
    snapshot: Option<local_api::UiSnapshot>,
    view: View,
    selected: usize,
    choice: usize,
    server: Option<JoinHandle<io::Result<()>>>,
    server_ready: bool,
    external_server: bool,
    message: String,
}

impl App {
    fn new() -> Self {
        Self {
            identity: None,
            snapshot: None,
            view: View::Home,
            selected: 0,
            choice: 0,
            server: None,
            server_ready: false,
            external_server: false,
            message: "Use ↑/↓ and Enter. Press q to quit.".into(),
        }
    }

    async fn refresh(&mut self) {
        match authenticate::identity().await {
            Ok(identity) => self.identity = identity,
            Err(error) => {
                self.identity = None;
                self.message = format!("Sign-in check failed: {error}");
            }
        }
        if self.identity.is_some() {
            match local_api::ui_snapshot().await {
                Ok(snapshot) => self.snapshot = Some(snapshot),
                Err(error) => {
                    self.snapshot = None;
                    self.message = format!("Could not load models: {error}");
                }
            }
        } else {
            self.snapshot = None;
        }
        if self.server.is_none() {
            self.external_server = api_responds().await;
        }
    }

    fn current_model(&self) -> Option<&local_api::UiModel> {
        let snapshot = self.snapshot.as_ref()?;
        snapshot
            .models
            .iter()
            .find(|model| model.name == snapshot.settings.model)
    }

    fn choices(&self) -> Vec<String> {
        match self.view {
            View::Home => {
                let (model, effort, fast) = self.snapshot.as_ref().map_or_else(
                    || ("—".to_owned(), "—".to_owned(), "—".to_owned()),
                    |snapshot| {
                        (
                            snapshot.settings.model.clone(),
                            snapshot
                                .settings
                                .effort
                                .clone()
                                .unwrap_or_else(|| "default".into()),
                            if snapshot.settings.fast { "on" } else { "off" }.into(),
                        )
                    },
                );
                let api = if self.server.is_some() {
                    "Stop local API"
                } else if self.external_server {
                    "Local API already running"
                } else {
                    "Start local API"
                };
                vec![
                    "Sign in / refresh status".into(),
                    format!("Model             {model}"),
                    format!("Effort            {effort}"),
                    format!("Fast mode         {fast}"),
                    "Check model update".into(),
                    api.into(),
                    "Quit".into(),
                ]
            }
            View::Models => self.snapshot.as_ref().map_or_else(Vec::new, |snapshot| {
                snapshot
                    .models
                    .iter()
                    .map(|model| model.name.clone())
                    .collect()
            }),
            View::Efforts => self
                .current_model()
                .map_or_else(Vec::new, |model| model.efforts.clone()),
        }
    }

    fn move_selection(&mut self, direction: isize) {
        let len = self.choices().len();
        if len > 0 {
            self.choice = match self.view {
                View::Home => self.selected,
                _ => self.choice,
            };
            let next = (self.choice as isize + direction).rem_euclid(len as isize) as usize;
            if self.view == View::Home {
                self.selected = next;
            } else {
                self.choice = next;
            }
        }
    }

    async fn save(&mut self, settings: local_api::Settings) {
        match local_api::ui_save(settings).await {
            Ok(snapshot) => {
                self.snapshot = Some(snapshot);
                self.message = "Settings saved.".into();
                if self.server.is_some() {
                    self.stop_server().await;
                    self.start_server().await;
                    self.message = "Settings saved. Local API restarted.".into();
                } else if self.external_server {
                    self.message =
                        "Settings saved. Restart the separately running API to apply them.".into();
                }
            }
            Err(error) => self.message = format!("Could not save settings: {error}"),
        }
    }

    async fn start_server(&mut self) {
        if self.server.is_some() {
            return;
        }
        if api_responds().await {
            self.external_server = true;
            self.message = "An API is already running at http://127.0.0.1:8787/v1".into();
            return;
        }
        self.external_server = false;
        self.server_ready = false;
        self.server = Some(tokio::spawn(local_api::run(local_api::Action::Serve {
            port: Some(8787),
            quiet: true,
        })));
        self.message = "Starting local API at http://127.0.0.1:8787/v1…".into();
    }

    async fn stop_server(&mut self) {
        if let Some(server) = self.server.take() {
            server.abort();
            let _ = server.await;
            self.server_ready = false;
            self.message = "Local API stopped.".into();
        }
    }

    async fn poll_server(&mut self) {
        if self.server.is_some() && !self.server_ready && api_responds().await {
            self.server_ready = true;
            self.message = "Local API running at http://127.0.0.1:8787/v1".into();
        }
        if self.server.as_ref().is_some_and(JoinHandle::is_finished) {
            if let Some(server) = self.server.take() {
                self.server_ready = false;
                self.message = match server.await {
                    Ok(Ok(())) => "Local API stopped.".into(),
                    Ok(Err(error)) => format!("Local API failed: {error}"),
                    Err(error) => format!("Local API stopped: {error}"),
                };
            }
        }
    }

    async fn activate(&mut self, terminal: &mut DefaultTerminal) -> io::Result<bool> {
        if self.view == View::Models {
            if let Some(name) = self.choices().get(self.choice).cloned() {
                if let Some(snapshot) = &self.snapshot {
                    let mut settings = snapshot.settings.clone();
                    settings.model = name;
                    settings.effort = None;
                    settings.fast = false;
                    self.save(settings).await;
                }
            }
            self.view = View::Home;
            return Ok(false);
        }
        if self.view == View::Efforts {
            if let Some(effort) = self.choices().get(self.choice).cloned() {
                if let Some(snapshot) = &self.snapshot {
                    let mut settings = snapshot.settings.clone();
                    settings.effort = Some(effort);
                    self.save(settings).await;
                }
            }
            self.view = View::Home;
            return Ok(false);
        }
        if self.selected == 0 {
            if self.identity.is_some() {
                self.refresh().await;
                self.message = "Authentication is ready.".into();
                return Ok(false);
            }
            ratatui::try_restore()?;
            let result = authenticate::run(false, true).await;
            *terminal = ratatui::try_init()?;
            terminal.clear()?;
            self.message = match result {
                Ok(true) => "Authentication is ready.".into(),
                Ok(false) => "Not authenticated.".into(),
                Err(error) => format!("Sign-in failed: {error}"),
            };
            self.refresh().await;
        } else if self.identity.is_none() {
            self.message = "Sign in first.".into();
        } else if self.snapshot.is_none() {
            self.message = "Model catalog unavailable. Select sign in / refresh to retry.".into();
        } else {
            match self.selected {
                1 => {
                    self.view = View::Models;
                    self.choice = self
                        .snapshot
                        .as_ref()
                        .and_then(|snapshot| {
                            snapshot
                                .models
                                .iter()
                                .position(|model| model.name == snapshot.settings.model)
                        })
                        .unwrap_or(0);
                }
                2 => {
                    self.view = View::Efforts;
                    self.choice = self
                        .current_model()
                        .and_then(|model| {
                            let effort = self.snapshot.as_ref()?.settings.effort.as_deref()?;
                            model.efforts.iter().position(|item| item == effort)
                        })
                        .unwrap_or(0);
                }
                3 => {
                    if self.current_model().is_some_and(|model| model.fast) {
                        let mut settings = self.snapshot.as_ref().unwrap().settings.clone();
                        settings.fast = !settings.fast;
                        self.save(settings).await;
                    } else {
                        self.message = "Fast mode is unavailable for this model.".into();
                    }
                }
                4 => {
                    self.refresh().await;
                    if let Some(snapshot) = &self.snapshot {
                        self.message = snapshot.replacement.as_ref().map_or_else(
                            || {
                                format!(
                                    "No model update is advertised for {}.",
                                    snapshot.settings.model
                                )
                            },
                            |replacement| {
                                format!(
                                    "Model update available: {} → {replacement}",
                                    snapshot.settings.model
                                )
                            },
                        );
                    }
                }
                5 => {
                    if self.server.is_some() {
                        self.stop_server().await;
                    } else {
                        self.start_server().await;
                    }
                }
                6 => return Ok(true),
                _ => {}
            }
        }
        Ok(false)
    }
}

async fn api_responds() -> bool {
    let Ok(client) = reqwest::Client::builder()
        .timeout(Duration::from_millis(500))
        .build()
    else {
        return false;
    };
    client
        .get("http://127.0.0.1:8787/health")
        .send()
        .await
        .is_ok_and(|response| response.status().is_success())
}

fn render(frame: &mut Frame, app: &App) {
    let area = frame.area();
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),
            Constraint::Length(7),
            Constraint::Min(10),
            Constraint::Length(3),
        ])
        .split(area);
    frame.render_widget(
        Paragraph::new(" API PROXY ")
            .style(
                Style::default()
                    .fg(Color::Black)
                    .bg(Color::Cyan)
                    .add_modifier(Modifier::BOLD),
            )
            .block(Block::bordered()),
        chunks[0],
    );
    let identity = app.identity.as_deref().unwrap_or("Not authenticated");
    let api = if app.server_ready {
        "Running in this TUI"
    } else if app.server.is_some() {
        "Starting"
    } else if app.external_server {
        "Running separately"
    } else {
        "Stopped"
    };
    let status = format!(
        "Authentication: {identity}\nLocal API:       {api}\nEndpoint:        http://127.0.0.1:8787/v1"
    );
    frame.render_widget(
        Paragraph::new(status).block(Block::bordered().title("Status")),
        chunks[1],
    );
    let title = match app.view {
        View::Home => "Actions",
        View::Models => "Choose a model",
        View::Efforts => "Choose an effort",
    };
    let items = app
        .choices()
        .into_iter()
        .map(ListItem::new)
        .collect::<Vec<_>>();
    let list = List::new(items)
        .block(Block::bordered().title(title))
        .highlight_symbol("▶ ")
        .highlight_style(
            Style::default()
                .fg(Color::Black)
                .bg(Color::Cyan)
                .add_modifier(Modifier::BOLD),
        );
    let mut state = ListState::default();
    state.select(Some(if app.view == View::Home {
        app.selected
    } else {
        app.choice
    }));
    frame.render_stateful_widget(list, chunks[2], &mut state);
    let help = if app.view == View::Home {
        "↑/↓ move  •  Enter select  •  q quit"
    } else {
        "↑/↓ move  •  Enter save  •  Esc back  •  q quit"
    };
    frame.render_widget(
        Paragraph::new(format!("{}\n{}", app.message, help))
            .wrap(Wrap { trim: true })
            .block(Block::bordered().title("Message")),
        chunks[3],
    );
}

pub(crate) async fn run() -> io::Result<()> {
    if !io::stdin().is_terminal() || !io::stdout().is_terminal() {
        return Err(io::Error::other(
            "interactive terminal required; use api-proxy --help for commands",
        ));
    }
    let mut app = App::new();
    app.refresh().await;
    let mut terminal = ratatui::try_init()?;
    let result = run_loop(&mut app, &mut terminal).await;
    app.stop_server().await;
    let restore = ratatui::try_restore();
    result.and(restore)
}

async fn run_loop(app: &mut App, terminal: &mut DefaultTerminal) -> io::Result<()> {
    loop {
        app.poll_server().await;
        terminal.draw(|frame| render(frame, &app))?;
        if event::poll(Duration::from_millis(120))? {
            if let Event::Key(key) = event::read()? {
                if key.kind != KeyEventKind::Press {
                    continue;
                }
                match key.code {
                    KeyCode::Char('c') if key.modifiers.contains(KeyModifiers::CONTROL) => {
                        return Ok(());
                    }
                    KeyCode::Char('q') => return Ok(()),
                    KeyCode::Esc => {
                        app.view = View::Home;
                    }
                    KeyCode::Up | KeyCode::Char('k') => app.move_selection(-1),
                    KeyCode::Down | KeyCode::Char('j') => app.move_selection(1),
                    KeyCode::Enter => {
                        if app.activate(terminal).await? {
                            return Ok(());
                        }
                    }
                    _ => {}
                }
            }
        }
    }
}
