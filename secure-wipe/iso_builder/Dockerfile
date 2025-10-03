# Minimal Alpine Linux with Rust for building the ISO environment
FROM rust:1.70-alpine AS builder

# Install build deps
RUN apk add --no-cache grub grub-mkrescue xorriso syslinux

# Copy Rust CLI source
WORKDIR /app
COPY ../rust_engine /app/rust_engine
RUN cd rust_engine && cargo build --release --bin wipe_cli

# Final stage: Create ISO
FROM alpine:latest
RUN apk add --no-cache grub grub-mkrescue xorriso syslinux
COPY --from=builder /app/rust_engine/target/release/wipe_cli /boot/wipe_cli
COPY grub.cfg /boot/grub/grub.cfg
COPY isolinux/isolinux.bin /boot/isolinux.bin

# Build ISO (run in container)
CMD ["sh", "-c", "grub-mkrescue -o /output/secure_wipe.iso /boot"]