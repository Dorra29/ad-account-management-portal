"""
Standalone LDAP bind test — no Django involved.

Run with:  python test_ldap_bind.py
(from the project root, same folder as manage.py, so it can find .env)

This only tests the SERVICE ACCOUNT bind (LDAP_BIND_DN / LDAP_BIND_PASSWORD) —
the same call that's failing in accounts/backends.py at admin_conn = Connection(...).
It does not test any individual user's password.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPBindError, LDAPSocketOpenError

load_dotenv(Path(__file__).resolve().parent / ".env")

LDAP_SERVER = os.environ.get("LDAP_SERVER")
LDAP_PORT = int(os.environ.get("LDAP_PORT", 389))
LDAP_BIND_DN = os.environ.get("LDAP_BIND_DN")
LDAP_BIND_PASSWORD = os.environ.get("LDAP_BIND_PASSWORD")
LDAP_BASE_DN = os.environ.get("LDAP_BASE_DN")

print("Testing service-account bind with:")
print(f"  LDAP_SERVER       = {LDAP_SERVER!r}")
print(f"  LDAP_PORT         = {LDAP_PORT!r}")
print(f"  LDAP_BIND_DN      = {LDAP_BIND_DN!r}")
print(f"  LDAP_BIND_PASSWORD = {'<empty>' if not LDAP_BIND_PASSWORD else '*' * len(LDAP_BIND_PASSWORD)} "
      f"({len(LDAP_BIND_PASSWORD or '')} chars)")
print(f"  LDAP_BASE_DN      = {LDAP_BASE_DN!r}")
print()

if not all([LDAP_SERVER, LDAP_BIND_DN, LDAP_BIND_PASSWORD, LDAP_BASE_DN]):
    print("❌ One or more required .env values is missing/empty.")
    print("   Check that a real .env file exists next to manage.py (not just .env.example),")
    print("   and that every LDAP_* value above is actually filled in.")
    raise SystemExit(1)

try:
    server = Server(LDAP_SERVER, port=LDAP_PORT, get_info=ALL)
    conn = Connection(server, user=LDAP_BIND_DN, password=LDAP_BIND_PASSWORD, auto_bind=True)
    print("✅ Service account bind succeeded.")

    # Bonus: confirm the base DN itself is reachable/correct.
    conn.search(search_base=LDAP_BASE_DN, search_filter="(objectClass=*)", search_scope="BASE")
    if conn.entries:
        print(f"✅ LDAP_BASE_DN ({LDAP_BASE_DN}) is reachable.")
    else:
        print(f"⚠️  Bind worked, but LDAP_BASE_DN ({LDAP_BASE_DN}) returned no entries — "
              f"double check it matches your domain's actual DN.")

    conn.unbind()

except LDAPBindError as e:
    print(f"❌ Bind failed: {e}")
    print()
    print("This means the AD server rejected LDAP_BIND_DN / LDAP_BIND_PASSWORD specifically.")
    print("Most likely causes:")
    print("  - The password in .env doesn't match the account's CURRENT password on the AD server")
    print("    (if you rotated the old leaked 'ITlab123' password on AD, update .env to match)")
    print("  - .env still has the placeholder value from .env.example")
    print("  - LDAP_BIND_DN's CN=/DC= components don't match your lab domain's actual structure")

except LDAPSocketOpenError as e:
    print(f"❌ Couldn't even reach the server: {e}")
    print("Check LDAP_SERVER/LDAP_PORT and that the domain controller is running and reachable"
          " from this machine (VPN/network, firewall, etc).")