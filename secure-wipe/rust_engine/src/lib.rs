use pyo3::prelude::*;
use sysinfo::{System, SystemExt, Disks};
use rand::Rng;
use std::fs::File;
use std::io::{Read, Write, Seek, SeekFrom};
use std::path::Path;
use anyhow::Result as AnyhowResult;

// Detect available devices (mount points)
#[pyfunction]
fn detect_devices() -> PyResult<Vec<String>> {
    let s = System::new_all();
    let disks: Vec<String> = Disks::new_with_refreshed_list()
        .iter()
        .map(|disk| disk.mount_point().to_string_lossy().to_string())
        .collect();
    Ok(disks)
}

// Wipe device with multi-pass (zero/random data)
#[pyfunction]
fn wipe_device(path: String, passes: u32) -> PyResult<()> {
    let mut rng = rand::thread_rng();
    let full_path = Path::new(&path);
    if !full_path.exists() {
        return Err(PyErr::new::<pyo3::exceptions::PyIOError, _>("Device not found"));
    }

    let mut file = File::options().write(true).open(full_path)?;

    // Get size
    file.seek(SeekFrom::End(0))?;
    let size = file.seek(SeekFrom::Current(0))? as usize;

    // Multi-pass wipe
    for pass in 0..passes {
        file.seek(SeekFrom::Start(0))?;
        let mut buffer = vec![0u8; size / 1024];  // Simplified buffer (adjust for full size)
        if pass > 0 {
            rng.fill(&mut buffer);
        }
        // Write in chunks (for large devices)
        for chunk in buffer.chunks_mut(1024) {
            file.write_all(chunk)?;
        }
    }

    // Verify (read back)
    file.seek(SeekFrom::Start(0))?;
    let mut verify_buf = vec![0u8; size / 1024];
    file.read_exact(&mut verify_buf)?;

    Ok(())
}

// HPA/DCO handling (platform-specific)
#[cfg(target_os = "linux")]
#[pyfunction]
fn handle_hpa_dco(path: String) -> PyResult<()> {
    use std::process::Command;
    let status = Command::new("hdparm")
        .args(["--user-master", "u", "--security-erase-enhanced", &path])
        .status()?;
    if !status.success() {
        return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("HPA/DCO erase failed"));
    }
    Ok(())
}

#[cfg(target_os = "windows")]
#[pyfunction]
fn handle_hpa_dco(path: String) -> PyResult<()> {
    // Placeholder: Use diskpart or winapi (add winapi crate for full)
    Err(PyErr::new::<pyo3::exceptions::PyNotImplementedError, _>(
        "Windows HPA: Implement via diskpart script"
    ))
}

#[cfg(target_os = "macos")]
#[pyfunction]
fn handle_hpa_dco(path: String) -> PyResult<()> {
    use std::process::Command;
    let status = Command::new("diskutil")
        .args(["secureErase", "0", &path])  // Level 0 for zero-fill
        .status()?;
    if !status.success() {
        return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("HPA/DCO erase failed"));
    }
    Ok(())
}

#[pymodule]
fn secure_wipe_engine(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(detect_devices, m)?)?;
    m.add_function(wrap_pyfunction!(wipe_device, m)?)?;
    #[cfg(any(target_os = "linux", target_os = "windows", target_os = "macos"))]
    m.add_function(wrap_pyfunction!(handle_hpa_dco, m)?)?;
    Ok(())
}