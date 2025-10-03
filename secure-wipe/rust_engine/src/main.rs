use std::env;
use std::process;

mod lib;  // Import functions from lib.rs

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: wipe_cli <device_path> <passes>");
        process::exit(1);
    }

    let path = &args[1];
    let passes: u32 = args[2].parse().expect("Invalid passes number");

    match lib::wipe_device(path.to_string(), passes) {
        Ok(_) => {
            println!("Wipe completed on {}", path);
            // Handle HPA/DCO
            #[cfg(any(target_os = "linux", target_os = "macos"))]
            if let Err(e) = lib::handle_hpa_dco(path.to_string()) {
                eprintln!("HPA/DCO warning: {}", e);
            }
        }
        Err(e) => {
            eprintln!("Wipe failed: {}", e);
            process::exit(1);
        }
    }
}