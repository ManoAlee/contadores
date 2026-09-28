# 🖨️ Contadores Impressoras — Enterprise SNMP Meter Management Console

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![UI: CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter%205.2-1f538d.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Protocol: SNMPv1/v2c](https://img.shields.io/badge/Protocol-SNMP%20v1%2Fv2c-orange.svg)](https://en.wikipedia.org/wiki/Simple_Network_Management_Protocol)
[![Storage: SQLite3](https://img.shields.io/badge/Storage-SQLite3%20WAL-lightgrey.svg)](https://www.sqlite.org/)
[![CI Status](https://github.com/ManoAlee/contadores/actions/workflows/ci.yml/badge.svg)](https://github.com/ManoAlee/contadores/actions)

**An enterprise desktop telemetry console engineered for automated SNMP page count auditing, multi-vendor fleet discovery (Lexmark/HP), historical volume reporting, and secure SMTP email reconciliation.**

[Architecture](#-system-architecture) •
[SNMP MIB Specifications](#-snmp-mib-specifications) •
[Core Modules](#-core-module-index) •
[Database Schema](#-database-schema) •
[Quickstart](#-installation--quickstart) •
[License](#-license)

</div>

---

## 🚀 Overview

**Contadores Impressoras** automates physical page count auditing across networked multi-function printer (MFP) fleets. Built with **CustomTkinter** for modern, high-DPI desktop interfaces and asynchronous SNMP query workers, it eliminates manual billing meter collection by:
1. Scanning networked printer IPs via standard Printer-MIB OIDs.
2. Storing meter readings with atomic timestamps in a local SQLite database.
3. Automatically parsing incoming supplier count audit emails and drafting verified reconciliation reports with OS-level keyring credential security.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph UI["Desktop Client (CustomTkinter)"]
        Nav["Navigation Bar (NavBar)"]
        Dash["Dashboard Frame (KPIs & Monthly Charts)"]
        PrintF["Printers Frame (Fleet Cards & Status)"]
        AlertF["Alerts Frame (Anomalies & Low Toner)"]
        SetF["Settings Frame (SNMP/SMTP Config)"]
        Nav --> Dash
        Nav --> PrintF
        Nav --> AlertF
        Nav --> SetF
    end

    subgraph CoreEngine["Application Core"]
        SNMP["SNMP Polling Worker (snmp_client.py)"]
        DBMgr["Database Manager (db.py)"]
        EmailProc["Email Ingestion & Reply (email_parser.py)"]
        Keyring["OS Keyring (Windows Credential Vault)"]
        Dash --> SNMP
        PrintF --> DBMgr
        SetF --> Keyring
        EmailProc --> DBMgr
    end

    subgraph Network["Hardware Fleet & Communication"]
        Printers["Printer Fleet (Lexmark, HP, Canon, Xerox)"]
        SNMP -->|SNMP Get (Port 161)| Printers
        EmailProc -->|IMAP / SMTP TLS| MailServer["Corporate Mail Server"]
    end
```

---

## 📡 SNMP MIB Specifications

The polling engine retrieves standardized RFC 3805 (Printer MIB v2) and RFC 2790 (Host Resources MIB) object identifiers:

| Metric | Object Identifier (OID) | MIB Reference | Description |
| :--- | :--- | :--- | :--- |
| **Total Page Count** | `1.3.6.1.2.1.43.10.2.1.4.1.1` | `prtMarkerLifeCount` | Lifetime engine print/copy page counter |
| **Printer Serial Number** | `1.3.6.1.2.1.43.5.1.1.17.1` | `prtGeneralSerialNumber` | Manufacturer hardware serial identifier |
| **Physical Entity Serial** | `1.3.6.1.2.1.47.1.1.1.1.11` | `entPhysicalSerialNum` | Entity MIB chassis serial fallback |
| **Model Description** | `1.3.6.1.2.1.47.1.1.1.1.7` | `entPhysicalModelName` | Hardware model string (e.g. Lexmark MS823) |
| **Device Description** | `1.3.6.1.2.1.25.3.2.1.3.1` | `hrDeviceDescr` | Host resources device description string |

---

## 🧩 Core Module Index

- `app/gui_main.py`: Main `ctk.CTk` application window managing navigation and asynchronous frame transitions.
- `app/snmp_client.py`: Thread-safe network poller with exponential backoff (`timeout=2`, `retries=1`).
- `app/db.py`: SQLite abstraction with WAL mode executing thread-safe counter logging and monthly aggregation queries.
- `app/email_parser.py`: Ingestion pipeline parsing inbound count request emails with regex normalization.
- `app/auto_reply_from_email.py`: Autonomous reconciliation engine generating verified count reports.
- `app/send_email.py`: Encrypted SMTP TLS client using Windows Credential Manager (`keyring`) for zero-plaintext password management.

---

## 🗄️ Database Schema

```sql
CREATE TABLE IF NOT EXISTS counters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    printer_id TEXT NOT NULL,
    model TEXT NOT NULL,
    total_pages INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_printer_ts ON counters (printer_id, timestamp);
```

---

## 💻 Installation & Quickstart

### Prerequisites
- Python 3.11 or higher
- Network connectivity to printer subnet (Port 161 UDP)

### Running the Desktop Application

```bash
# Clone the repository
git clone https://github.com/ManoAlee/contadores.git
cd contadores

# Set up virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Launch GUI
python run.py
```

---

## 📄 License

This software is released under the **MIT License** - see [LICENSE](LICENSE) for details.
