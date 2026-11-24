#!/usr/bin/env python3
"""Sign channel/channel.json with the maintainer key → channel/channel.sig.

    python3 tools/admin/sign-channel.py            (key: $NEBULA_ADMIN_KEY or ~/.config/nebulaos/admin.key)
    python3 tools/admin/sign-channel.py --new-key  create the key pair once; KEEP admin.key SECRET

The public key goes to desktop/usr/share/nebulaos/admin.pub (shipped in every NebulaOS).
"""
import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "desktop/usr/lib/nebulaos"))
import nebula_sign  # noqa: E402

key = Path(os.environ.get("NEBULA_ADMIN_KEY", Path.home() / ".config/nebulaos/admin.key"))
pub = root / "desktop/usr/share/nebulaos/admin.pub"
if "--new-key" in sys.argv:
    if key.exists():
        sys.exit(f"{key} already exists — not overwriting it.")
    p, s = nebula_sign.keypair()
    key.parent.mkdir(parents=True, exist_ok=True)
    key.write_text(s + "\n")
    os.chmod(key, 0o600)
    pub.write_text(p + "\n")
    print(f"secret key: {key}  (back it up, never publish it)\npublic key: {pub}")
    sys.exit(0)
secret = key.read_text().strip()
(root / "desktop/usr/share/nebulaos/channel.json").write_bytes((root / "channel/channel.json").read_bytes())
for d in (root / "channel", root / "desktop/usr/share/nebulaos"):
    data = (d / "channel.json").read_bytes()
    (d / "channel.sig").write_text(nebula_sign.sign(secret, data) + "\n")
    assert nebula_sign.verify(pub.read_text().strip(), data, (d / "channel.sig").read_text())
print("channel signed")
