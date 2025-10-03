fn main() {
    // Custom build hooks: Link platform-specific libs if needed
    // Example for Linux hdparm (add to Cargo.toml if using external C libs)
    #[cfg(target_os = "linux")]
    println!("cargo:rustc-link-lib=hdparm");

    // For Windows: Link winapi if added to deps
    #[cfg(target_os = "windows")]
    println!("cargo:rustc-link-lib=advapi32");
}