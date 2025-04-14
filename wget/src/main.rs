use std::{error::Error, str::Bytes};

use clap::Parser;
use reqwest::{Client, header::CONTENT_LENGTH};
use tokio::{fs::File, io::AsyncWriteExt};

/// Wget clone written in Rust
#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// Url to download
    #[arg()]
    url: String,
}

async fn download(target: &str) -> Result<(), Box<dyn Error>> {
    let client = Client::new();

    let mut res = client.get(target).send().await?;

    if !res.status().is_success() {
        return Err("Unable to download".into());
    }

    let mut buf = Vec::new();
    while let Some(chunk) = res.chunk().await? {
        buf.extend_from_slice(&chunk);
    }
    let fname = target.split("/").last().unwrap();
    save_to_file(buf, fname).await?;
    Ok(())
}
async fn save_to_file(buffer: Vec<u8>, file_path: &str) -> Result<(), Box<dyn Error>> {
    let mut file = File::create(file_path).await?; // Creates or overwrites the file
    file.write_all(&buffer).await?;
    Ok(())
}

#[tokio::main]
async fn main() {
    let args = Args::parse();
    let res = download(args.url.as_str()).await;
    match res {
        Ok(_) => println!("Downloaded"),
        Err(_) => println!("Something went wrong"),
    }
}
