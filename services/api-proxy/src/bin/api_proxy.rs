#[path = "../cli/authenticate.rs"]
mod authenticate;
#[path = "../cli/local_api.rs"]
mod local_api;
#[path = "../cli/tui.rs"]
mod tui;

use clap::{Parser, Subcommand, ValueEnum};
use std::io;

#[derive(Parser)]
#[command(
    name = "api-proxy",
    version,
    about = "Local sign-in and LLM API",
    after_help = "Run api-proxy with no command to open the interactive terminal interface."
)]
struct Cli {
    #[command(subcommand)]
    command: Option<Command>,
}

#[derive(Subcommand)]
enum Command {
    /// Sign in, or confirm the saved sign-in.
    Login {
        /// Print the sign-in URL without opening a browser.
        #[arg(long)]
        no_browser: bool,
    },
    /// Check whether a usable sign-in is saved.
    Status,
    /// Start the local OpenAI-style API; signs in first if needed.
    Serve {
        /// Local port (default: 8787).
        #[arg(long)]
        port: Option<u16>,
    },
    /// Set or show the selected model, effort, and fast mode.
    Config {
        #[command(subcommand)]
        command: ConfigCommand,
    },
    /// Check whether the provider recommends a replacement for the selected model.
    Update,
}

#[derive(Subcommand)]
enum ConfigCommand {
    /// Save one or more settings; unsupported combinations are rejected.
    Set {
        #[arg(long)]
        model: Option<String>,
        #[arg(long)]
        effort: Option<String>,
        #[arg(long)]
        fast: Option<FastSwitch>,
    },
    /// Show the effective settings.
    Show,
}

#[derive(Clone, Copy, ValueEnum)]
enum FastSwitch {
    On,
    Off,
}

#[tokio::main]
async fn main() -> io::Result<()> {
    let cli = Cli::parse();
    match cli.command {
        None => tui::run().await?,
        Some(Command::Login { no_browser }) => {
            authenticate::run(false, !no_browser).await?;
        }
        Some(Command::Status) => {
            if !authenticate::run(true, false).await? {
                std::process::exit(1);
            }
        }
        Some(command) => {
            authenticate::run(false, true).await?;
            let action = match command {
                Command::Serve { port } => local_api::Action::Serve { port, quiet: false },
                Command::Config {
                    command:
                        ConfigCommand::Set {
                            model,
                            effort,
                            fast,
                        },
                } => local_api::Action::Configure {
                    model,
                    effort,
                    fast: fast.map(|value| matches!(value, FastSwitch::On)),
                },
                Command::Config {
                    command: ConfigCommand::Show,
                } => local_api::Action::ShowConfig,
                Command::Update => local_api::Action::CheckUpdate,
                Command::Login { .. } | Command::Status => unreachable!(),
            };
            local_api::run(action).await?;
        }
    }
    Ok(())
}
