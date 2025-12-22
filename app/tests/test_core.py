import sys
from pathlib import Path

# garantir import do src
ROOT = Path(__file__).resolve().parents[2]
SRC = str(ROOT / 'app' / 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import pytest

from auto_reply_from_email import normalize_serial, extract_serials
from get_printer_counters import load_ips


def test_normalize_serial():
    assert normalize_serial(' abC-12 ') == 'ABC'
    assert normalize_serial('35P7G10-89-0') == '35P7G10'


def test_extract_serials():
    txt = 'X656 DN – N/S: 79G5C52 – C :\nX464DN – N/S: 35P7G2H'
    serials = extract_serials(txt)
    assert '79G5C52' in serials
    assert '35P7G2H' in serials


def test_load_ips(tmp_path):
    p = tmp_path / 'ips.txt'
    p.write_text('TI,10.0.0.173\n10.0.0.5\n')
    ips = load_ips(str(p))
    assert ('TI', '10.0.0.173') in ips
    assert (None, '10.0.0.5') in ips
