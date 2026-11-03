/**
 * CutWire Drift - High-Performance Bare-Metal Rust Media Engine (drift-rust-worker).
 * Consumes audiovisual tasks dispatched by Fastify via Redis/BullMQ.
 * Executes FFmpeg processing at native metal speed with <20MB RAM and zero GC pauses.
 */
use std::env;
use std::process::Stdio;
use tokio::process::Command;
use tokio::time::{sleep, Duration};
use serde::{Deserialize, Serialize};
use tracing::{info, warn, error};

#[derive(Debug, Serialize, Deserialize)]
struct MediaJobPayload {
    #[serde(rename = "inputUrl")]
    input_url: String,
    #[serde(default = "default_profile")]
    profile: String,
    #[serde(default)]
    created_at: Option<String>,
}

fn default_profile() -> String {
    "proxy-light".to_string()
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Inicialização do logger leve estruturado
    tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env())
        .init();

    info!("[Drift-Rust Engine] Worker audiovisual de alta performance iniciado no metal.");

    let redis_url = env::var("REDIS_URL").unwrap_or_else(|_| "redis://localhost:6379".to_string());
    info!("[Drift-Rust Engine] Conectando ao Redis: {}", redis_url);

    // Loop assíncrono de escuta com captura de sinais de encerramento gracioso
    let mut shutdown_signal = std::pin::pin!(tokio::signal::ctrl_c());

    loop {
        tokio::select! {
            _ = &mut shutdown_signal => {
                info!("[Drift-Rust Engine] Sinal de encerramento recebido. Finalizando tarefas ativas...");
                break;
            }
            res = process_queue_cycle(&redis_url) => {
                if let Err(e) = res {
                    warn!("[Drift-Rust Engine] Ciclo de escuta ocioso ou Redis desconectado: {}", e);
                    sleep(Duration::from_millis(2000)).await;
                } else {
                    sleep(Duration::from_millis(500)).await;
                }
            }
        }
    }

    info!("[Drift-Rust Engine] Worker finalizado com sucesso.");
    Ok(())
}

async fn process_queue_cycle(redis_url: &str) -> Result<(), Box<dyn std::error::Error>> {
    let client = redis::Client::open(redis_url)?;
    let mut con = client.get_multiplexed_async_connection().await?;

    // Consumo reativo da fila Redis BullMQ
    let job_opt: Option<(String, String)> = redis::cmd("BLPOP")
        .arg("bull:drift-heavy-tasks:wait")
        .arg(1) // Timeout de 1 segundo para manter o loop reativo
        .query_async(&mut con)
        .await
        .ok();

    if let Some((_queue, job_data)) = job_opt {
        info!("[Drift-Rust Engine] Job capturado da fila. Iniciando decodificação...");
        if let Ok(payload) = serde_json::from_str::<MediaJobPayload>(&job_data) {
            execute_ffmpeg_job(&payload).await?;
        }
    }

    Ok(())
}

async fn execute_ffmpeg_job(payload: &MediaJobPayload) -> Result<(), Box<dyn std::error::Error>> {
    info!(
        "[Drift-Rust Engine] Processando vídeo: {} [Perfil: {}]",
        payload.input_url, payload.profile
    );

    let output_path = format!("{}_processed.mp4", payload.input_url);

    // 1. Tentar render acelerado por hardware NVIDIA (NVENC)
    let nvenc_status = if payload.profile == "proxy-light" {
        Command::new("ffmpeg")
            .args([
                "-y",
                "-hwaccel", "cuda",
                "-i", &payload.input_url,
                "-c:v", "h264_nvenc",
                "-preset", "p4",
                "-vf", "scale=-2:720",
                "-b:v", "2M",
                "-c:a", "aac",
                &output_path,
            ])
            .stdout(Stdio::null())
            .stderr(Stdio::piped())
            .status()
            .await
    } else {
        Command::new("ffmpeg")
            .args([
                "-y",
                "-hwaccel", "cuda",
                "-i", &payload.input_url,
                "-c:v", "h264_nvenc",
                "-preset", "p6",
                "-c:a", "aac",
                &output_path,
            ])
            .stdout(Stdio::null())
            .stderr(Stdio::piped())
            .status()
            .await
    };

    match nvenc_status {
        Ok(status) if status.success() => {
            info!("[Drift-Rust Engine] Render NVENC concluído com sucesso: {}", output_path);
            Ok(())
        }
        _ => {
            // 2. Fallback automático transparente por CPU (libx264)
            warn!("[Drift-Rust Engine] GPU NVENC indisponível. Executando fallback em CPU...");
            let cpu_status = Command::new("ffmpeg")
                .args([
                    "-y",
                    "-i", &payload.input_url,
                    "-c:v", "libx264",
                    "-preset", "veryfast",
                    "-vf", "scale=-2:720",
                    "-b:v", "2M",
                    "-c:a", "aac",
                    &output_path,
                ])
                .status()
                .await?;

            if cpu_status.success() {
                info!("[Drift-Rust Engine] Render CPU Fallback concluído com sucesso: {}", output_path);
                Ok(())
            } else {
                error!("[Drift-Rust Engine] Falha ao executar FFmpeg via CPU.");
                Err("FFmpeg execution failed".into())
            }
        }
    }
}

