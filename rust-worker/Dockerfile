# Build stage com imagem completa do Rust
FROM rust:1.75-alpine AS builder
WORKDIR /usr/src/app
RUN apk add --no-cache musl-dev
COPY . .
RUN cargo build --release

# Runtime stage ultra-leve (Alpine puro para o binário compilado)
FROM alpine:3.19
WORKDIR /app
RUN apk add --no-cache libgcc ffmpeg
COPY --from=builder /usr/src/app/target/release/drift-rust-worker /app/drift-rust-worker

CMD ["./drift-rust-worker"]

