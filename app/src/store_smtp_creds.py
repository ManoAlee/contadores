#!/usr/bin/env python3
"""Utility to store/retrieve SMTP credentials in the OS keyring.

Usage:
  python store_smtp_creds.py set <user>  (will prompt for password)
  python store_smtp_creds.py del <user>
"""
import sys
try:
    import keyring
except Exception:
    keyring = None


def set_cred(user):
    if not keyring:
        print('keyring module not available. Install with: pip install keyring')
        return 1
    import getpass
    pwd = getpass.getpass('Password for %s: ' % user)
    keyring.set_password('contadores_smtp', user, pwd)
    print('Stored in keyring for user', user)
    return 0


def del_cred(user):
    if not keyring:
        print('keyring module not available.')
        return 1
    keyring.delete_password('contadores_smtp', user)
    print('Deleted credentials for', user)
    return 0


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    cmd = sys.argv[1]
    user = sys.argv[2]
    if cmd == 'set':
        sys.exit(set_cred(user))
    if cmd in ('del', 'delete'):
        sys.exit(del_cred(user))
    print('Unknown command')

if __name__ == '__main__':
    main()
