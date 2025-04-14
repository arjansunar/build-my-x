use clap::Parser;

/// Wget clone written in Rust
#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// Url to download
    #[arg(short, long)]
    url: String,
}

fn main() {
    let args = Args::parse();
    println!("Hello {}!", args.url);
}
