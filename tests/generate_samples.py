#!/usr/bin/env python3
"""
Generate practice malware-like samples for testing MalZoo's analysis pipeline.
These are all benign files designed to exercise each worker type.

Usage: python3 tests/generate_samples.py
Output: tests/samples/ directory with test files
"""
import os
import struct
import zipfile

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "samples")


def ensure_dir():
    os.makedirs(SAMPLE_DIR, exist_ok=True)


def create_pe_sample():
    """
    Create a minimal valid PE file (Windows executable header).
    This is a bare-minimum PE that won't execute but is structurally valid
    enough for pefile to parse.
    """
    # DOS Header
    dos_header = bytearray(64)
    dos_header[0:2] = b"MZ"                          # e_magic
    struct.pack_into("<I", dos_header, 60, 64)        # e_lfanew -> PE header at offset 64

    # PE Signature
    pe_sig = b"PE\x00\x00"

    # COFF Header (IMAGE_FILE_HEADER) - 20 bytes
    coff = struct.pack("<HHIIIHH",
        0x014C,   # Machine: i386
        1,        # NumberOfSections
        0x5F3E1000,  # TimeDateStamp (fake compile time)
        0,        # PointerToSymbolTable
        0,        # NumberOfSymbols
        0xE0,     # SizeOfOptionalHeader (PE32)
        0x0102,   # Characteristics: EXECUTABLE_IMAGE | 32BIT_MACHINE
    )

    # Optional Header (PE32) - 224 bytes (0xE0)
    opt = bytearray(0xE0)
    struct.pack_into("<H", opt, 0, 0x10B)       # Magic: PE32
    struct.pack_into("<B", opt, 2, 1)            # MajorLinkerVersion
    struct.pack_into("<I", opt, 16, 0x1000)      # AddressOfEntryPoint
    struct.pack_into("<I", opt, 28, 0x400000)    # ImageBase
    struct.pack_into("<I", opt, 32, 0x1000)      # SectionAlignment
    struct.pack_into("<I", opt, 36, 0x200)       # FileAlignment
    struct.pack_into("<H", opt, 40, 4)           # MajorOSVersion
    struct.pack_into("<H", opt, 44, 4)           # MajorSubsystemVersion
    struct.pack_into("<I", opt, 56, 0x3000)      # SizeOfImage
    struct.pack_into("<I", opt, 60, 0x200)       # SizeOfHeaders
    struct.pack_into("<H", opt, 68, 3)           # Subsystem: CONSOLE
    struct.pack_into("<I", opt, 76, 0x100000)    # SizeOfStackReserve
    struct.pack_into("<I", opt, 80, 0x1000)      # SizeOfStackCommit
    struct.pack_into("<I", opt, 84, 0x100000)    # SizeOfHeapReserve
    struct.pack_into("<I", opt, 88, 0x1000)      # SizeOfHeapCommit
    struct.pack_into("<I", opt, 92, 16)          # NumberOfRvaAndSizes

    # Import Directory RVA (data directory entry 1)
    struct.pack_into("<II", opt, 104, 0x2000, 40)  # RVA, Size

    # Section Header (.text) - 40 bytes
    section = bytearray(40)
    section[0:6] = b".text\x00"
    struct.pack_into("<I", section, 8, 0x1000)    # VirtualSize
    struct.pack_into("<I", section, 12, 0x1000)   # VirtualAddress
    struct.pack_into("<I", section, 16, 0x200)    # SizeOfRawData
    struct.pack_into("<I", section, 20, 0x200)    # PointerToRawData
    struct.pack_into("<I", section, 36, 0xE0000060)  # Characteristics

    # Section data (pad to FileAlignment)
    section_data = b"\xCC" * 0x200  # INT 3 fill

    # Build the PE
    headers = dos_header + pe_sig + coff + bytes(opt) + bytes(section)
    # Pad headers to FileAlignment (0x200 = 512)
    headers = headers.ljust(0x200, b"\x00")

    pe_data = headers + section_data

    path = os.path.join(SAMPLE_DIR, "test_executable.exe")
    with open(path, "wb") as f:
        f.write(pe_data)
    print(f"[+] PE sample: {path} ({len(pe_data)} bytes)")


def create_office_sample():
    """
    Create a minimal OLE2 Compound Document (MS-CFB format).
    This mimics an old-style .doc file enough for oletools to inspect.
    """
    # OLE2 magic + minimal header (512 bytes)
    ole_header = bytearray(512)
    # OLE2 signature
    ole_header[0:8] = b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"
    # Minor version
    struct.pack_into("<H", ole_header, 0x18, 0x003E)
    # Major version (3 = OLE2)
    struct.pack_into("<H", ole_header, 0x1A, 0x0003)
    # Byte order (little-endian)
    struct.pack_into("<H", ole_header, 0x1C, 0xFFFE)
    # Sector size power (9 = 512 bytes)
    struct.pack_into("<H", ole_header, 0x1E, 0x0009)
    # Mini sector size power (6 = 64 bytes)
    struct.pack_into("<H", ole_header, 0x20, 0x0006)
    # Fill remaining with 0xFF (empty FAT entries)
    for i in range(0x44, 0x200):
        ole_header[i] = 0xFF

    path = os.path.join(SAMPLE_DIR, "test_document.doc")
    with open(path, "wb") as f:
        f.write(ole_header)
    print(f"[+] Office sample: {path} ({len(ole_header)} bytes)")


def create_email_sample():
    """Create a simple .eml file with headers, body, and a URL."""
    eml = """\
From: sender@example.com
To: recipient@example.com
Subject: Test Malware Alert
Date: Mon, 30 Mar 2026 12:00:00 +0000
MIME-Version: 1.0
Content-Type: text/html; charset="utf-8"

<html>
<body>
<p>Please review the following suspicious link:</p>
<p><a href="http://malicious-example.test/payload">Click here</a></p>
<p>Additional URL: https://another-suspicious.test/download?id=12345</p>
</body>
</html>
"""
    path = os.path.join(SAMPLE_DIR, "test_email.eml")
    with open(path, "w") as f:
        f.write(eml)
    print(f"[+] Email sample: {path}")


def create_zip_sample():
    """Create a ZIP archive containing a text file."""
    path = os.path.join(SAMPLE_DIR, "test_archive.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("readme.txt", "This is a test file inside a ZIP archive.\n")
        zf.writestr("data/config.ini", "[settings]\nkey = value\n")
    print(f"[+] ZIP sample: {path}")


def create_generic_sample():
    """Create a generic binary file that won't match any specific type."""
    data = bytes(range(256)) * 4  # 1KB of byte patterns
    path = os.path.join(SAMPLE_DIR, "test_generic.bin")
    with open(path, "wb") as f:
        f.write(data)
    print(f"[+] Generic sample: {path} ({len(data)} bytes)")


def create_eicar_sample():
    """
    Create the EICAR anti-malware test file.
    This is the industry-standard test string recognized by AV products.
    It is completely harmless.
    """
    eicar = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    path = os.path.join(SAMPLE_DIR, "eicar.com")
    with open(path, "wb") as f:
        f.write(eicar)
    print(f"[+] EICAR sample: {path}")


if __name__ == "__main__":
    print("[*] Generating test samples...")
    ensure_dir()
    create_pe_sample()
    create_office_sample()
    create_email_sample()
    create_zip_sample()
    create_generic_sample()
    create_eicar_sample()
    print(f"\n[+] All samples written to {SAMPLE_DIR}/")
