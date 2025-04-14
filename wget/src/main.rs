use std::error::Error;

use clap::Parser;
use reqwest::{Client, Response};
use tokio::{fs::File, io::AsyncWriteExt};

/// Wget clone written in Rust
#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// Url to download
    #[arg()]
    url: String,

    /// Flog to enable download
    #[arg(short, default_value_t = false)]
    download: bool,
}

async fn make_req(target: &str) -> Result<Response, Box<dyn Error>> {
    let client = Client::new();
    let res = client.get(target).send().await?;
    if !res.status().is_success() {
        return Err("Unable to request to provided url".into());
    }
    Ok(res)
}

async fn collect_buf(res: &mut Response) -> Result<Vec<u8>, Box<dyn Error>> {
    let mut buf = Vec::new();
    while let Some(chunk) = res.chunk().await? {
        buf.extend_from_slice(&chunk);
    }
    Ok(buf)
}
async fn save_to_file(buffer: Vec<u8>, file_path: &str) -> Result<(), Box<dyn Error>> {
    let mut file = File::create(file_path).await?;
    file.write_all(&buffer).await?;
    Ok(())
}

#[tokio::main]
async fn main() {
    let args = Args::parse();
    let res = make_req(args.url.as_str()).await;
    if args.download {
        let fname = args.url.split("/").last().unwrap_or("Download");
        if let Ok(mut r) = res {
            let buf = collect_buf(&mut r).await.expect("Unable to collect buffer");
            save_to_file(buf, fname)
                .await
                .expect("Unable to save to file");
        }
    } else if let Ok(r) = res {
        let txt = r.text().await;
        if let Ok(txt) = txt {
            println!("{}", txt)
        }
    }
}
