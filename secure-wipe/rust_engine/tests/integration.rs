#[cfg(test)]
mod tests {
    use super::lib;  // Access lib.rs functions

    #[test]
    fn test_detect_devices() {
        let devices = lib::detect_devices().unwrap();
        assert!(!devices.is_empty(), "Should detect at least one device/mount point");
    }

    #[test]
    fn test_wipe_mock_device() {
        // Create mock device (temp file)
        use std::fs::{OpenOptions, File};
        use std::io::{Write, Read};
        let mock_path = "mock_device.tmp";
        let mut file = OpenOptions::new().write(true).create(true).open(mock_path).unwrap();
        file.write_all(b"original data to wipe").unwrap();

        // Wipe with 1 pass
        lib::wipe_device(mock_path.to_string(), 1).unwrap();

        // Verify: Should be zeroed
        let mut buf = Vec::new();
        let mut f = File::open(mock_path).unwrap();
        f.read_to_end(&mut buf).unwrap();
        assert!(buf.iter().all(|&b| b == 0), "Mock device should be zeroed after wipe");

        // Cleanup
        std::fs::remove_file(mock_path).unwrap();
    }

    #[test]
    #[cfg(target_os = "linux")]
    fn test_hpa_dco_mock() {
        // Mock: Just check function compiles (real test needs hdparm)
        let result = lib::handle_hpa_dco("/dev/mock".to_string());
        // Expect error for mock path, but no panic
        assert!(result.is_err());
    }
}