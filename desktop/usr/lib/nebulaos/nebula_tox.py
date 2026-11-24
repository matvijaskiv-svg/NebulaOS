"""ctypes wrapper over libtoxcore for Nebula Chat.

Tox is peer-to-peer and end-to-end encrypted: there is no NebulaOS server.
Peers find each other through the public Tox DHT (bootstrap nodes) or on the
local network. Everything runs in the caller's thread: call iterate() from a timer.

Besides text, Nebula Chat sends JSON "data" (profiles, photos, posts, likes,
receipts) over lossless custom packets, split into chunks and reassembled here.
"""
import ctypes as C
import json
import os
import random
import urllib.request
from collections import deque
from pathlib import Path

ADDRESS_SIZE = 38
PUBLIC_KEY_SIZE = 32
CHAT_ID_SIZE = 32
SAVEDATA_TYPE_TOX_SAVE = 1
MESSAGE_TYPE_NORMAL = 0
MAX_MESSAGE = 1372
PRIVACY_PUBLIC, PRIVACY_PRIVATE = 0, 1
ROLE_FOUNDER, ROLE_MODERATOR, ROLE_USER, ROLE_OBSERVER = 0, 1, 2, 3
DATA_FRIEND, DATA_GROUP = 170, 171        # first byte of our custom packets
CHUNK = 1300
MAX_DATA = 12 * 1024 * 1024               # one data item (photo, file) at most 12 MB

NODES_URL = "https://nodes.tox.chat/json"
FALLBACK_NODES = [
    ("tox.abilinski.com", 33445, "10C00EB250C3233E343E2AEBA07115A5C28920E9C8D29492F6D00B29049EDC7E"),
    ("144.217.167.73", 33445, "7E5668E0EE09E19F320AD47902419331FFEE147BB3606769CFBE921A2A2FD34C"),
    ("tox.kurnevsky.net", 33445, "82EF82BA33445A1F91A7DB27189ECFC0C013E06E3DA71F588ED692BED625EC23"),
]

lib = C.CDLL("libtoxcore.so.2") if os.path.exists("/usr/lib/libtoxcore.so.2") else C.CDLL("libtoxcore.so")
P = C.c_void_p
u8p = C.POINTER(C.c_uint8)
ERR = C.POINTER(C.c_int)
U32, SZ, BOOL, BUF = C.c_uint32, C.c_size_t, C.c_bool, C.c_char_p

CB = {
    "friend_request": C.CFUNCTYPE(None, P, u8p, u8p, SZ, P),
    "friend_message": C.CFUNCTYPE(None, P, U32, C.c_int, u8p, SZ, P),
    "self_connection_status": C.CFUNCTYPE(None, P, C.c_int, P),
    "friend_connection_status": C.CFUNCTYPE(None, P, U32, C.c_int, P),
    "friend_name": C.CFUNCTYPE(None, P, U32, u8p, SZ, P),
    "friend_typing": C.CFUNCTYPE(None, P, U32, BOOL, P),
    "friend_read_receipt": C.CFUNCTYPE(None, P, U32, U32, P),
    "friend_lossless_packet": C.CFUNCTYPE(None, P, U32, u8p, SZ, P),
    "group_message": C.CFUNCTYPE(None, P, U32, U32, C.c_int, u8p, SZ, U32, P),
    "group_custom_packet": C.CFUNCTYPE(None, P, U32, U32, u8p, SZ, P),
    "group_invite": C.CFUNCTYPE(None, P, U32, u8p, SZ, u8p, SZ, P),
    "group_peer_join": C.CFUNCTYPE(None, P, U32, U32, P),
    "group_peer_exit": C.CFUNCTYPE(None, P, U32, U32, C.c_int, u8p, SZ, u8p, SZ, P),
    "group_self_join": C.CFUNCTYPE(None, P, U32, P),
}


def _sig(name, res, *args):
    f = getattr(lib, name)
    f.restype = res
    f.argtypes = list(args)
    return f


f = {}
for _name, _res, *_args in [
    ("tox_options_new", P, P), ("tox_options_free", None, P),
    ("tox_options_set_savedata_type", None, P, C.c_int),
    ("tox_options_set_savedata_data", None, P, BUF, SZ),
    ("tox_new", P, P, P), ("tox_kill", None, P),
    ("tox_get_savedata_size", SZ, P), ("tox_get_savedata", None, P, BUF),
    ("tox_bootstrap", BOOL, P, BUF, C.c_uint16, BUF, P),
    ("tox_add_tcp_relay", BOOL, P, BUF, C.c_uint16, BUF, P),
    ("tox_iterate", None, P, P), ("tox_iteration_interval", U32, P),
    ("tox_self_get_address", None, P, BUF), ("tox_self_get_public_key", None, P, BUF),
    ("tox_self_set_name", BOOL, P, BUF, SZ, P),
    ("tox_self_set_status_message", BOOL, P, BUF, SZ, P),
    ("tox_self_set_typing", BOOL, P, U32, BOOL, P),
    ("tox_friend_add", U32, P, BUF, BUF, SZ, ERR),
    ("tox_friend_add_norequest", U32, P, BUF, ERR),
    ("tox_friend_delete", BOOL, P, U32, P),
    ("tox_friend_by_public_key", U32, P, BUF, ERR),
    ("tox_friend_get_public_key", BOOL, P, U32, BUF, P),
    ("tox_friend_send_message", U32, P, U32, C.c_int, BUF, SZ, ERR),
    ("tox_friend_send_lossless_packet", BOOL, P, U32, BUF, SZ, ERR),
    ("tox_self_get_friend_list_size", SZ, P),
    ("tox_self_get_friend_list", None, P, C.POINTER(U32)),
    ("tox_group_new", U32, P, C.c_int, BUF, SZ, BUF, SZ, ERR),
    ("tox_group_join", U32, P, BUF, BUF, SZ, BUF, SZ, ERR),
    ("tox_group_leave", BOOL, P, U32, BUF, SZ, P),
    ("tox_group_send_message", U32, P, U32, C.c_int, BUF, SZ, ERR),
    ("tox_group_send_custom_packet", BOOL, P, U32, BOOL, BUF, SZ, ERR),
    ("tox_group_get_chat_id", BOOL, P, U32, BUF, ERR),
    ("tox_group_get_name_size", SZ, P, U32, ERR),
    ("tox_group_get_name", BOOL, P, U32, BUF, ERR),
    ("tox_group_get_number_groups", U32, P),
    ("tox_group_is_connected", BOOL, P, U32, ERR),
    ("tox_group_kick_peer", BOOL, P, U32, U32, ERR),
    ("tox_group_set_role", BOOL, P, U32, U32, C.c_int, ERR),
    ("tox_group_self_get_role", C.c_int, P, U32, ERR),
    ("tox_group_self_get_peer_id", U32, P, U32, ERR),
    ("tox_group_peer_get_name_size", SZ, P, U32, U32, ERR),
    ("tox_group_peer_get_name", BOOL, P, U32, U32, BUF, ERR),
    ("tox_group_peer_get_public_key", BOOL, P, U32, U32, BUF, ERR),
    ("tox_group_peer_get_role", C.c_int, P, U32, U32, ERR),
    ("tox_group_invite_friend", BOOL, P, U32, U32, ERR),
    ("tox_group_invite_accept", U32, P, U32, BUF, SZ, BUF, SZ, BUF, SZ, ERR),
]:
    f[_name] = _sig(_name, _res, *_args)
for _cb in CB:
    _sig(f"tox_callback_{_cb}", None, P, CB[_cb])


def load_nodes(cache):
    """Bootstrap nodes: fresh list from nodes.tox.chat, else the cached one, else built-in."""
    try:
        with urllib.request.urlopen(NODES_URL, timeout=8) as r:
            data = json.loads(r.read().decode())
        nodes = [(n["ipv4"], int(n["port"]), n["public_key"]) for n in data.get("nodes", [])
                 if n.get("status_udp") and n.get("ipv4") not in ("", "-")]
        if nodes:
            cache.write_text(json.dumps(nodes))
            return nodes[:12]
    except Exception:
        pass
    try:
        return [tuple(n) for n in json.loads(cache.read_text())][:12]
    except Exception:
        return FALLBACK_NODES


def _txt(ptr, length):
    return bytes(ptr[:length]).decode("utf-8", "replace")


class Tox:
    """One Tox profile. Event callbacks (set the ones you need):

    on_request(pk, text)              on_message(pk, text)
    on_online(bool)                   on_friend_status(pk, online)
    on_typing(pk, bool)               on_receipt(pk, message_id)
    on_name(pk, name)                 on_data(pk, obj)            JSON data from a friend
    on_group_message(chat_id, peer_id, peer_pk, peer_name, text)
    on_group_data(chat_id, peer_id, peer_pk, peer_name, obj)
    on_group_invite(friend_pk, invite_bytes, group_name)
    on_group_peer(chat_id, peer_id, peer_pk, peer_name, joined)
    on_group_ready(chat_id)
    """

    def __init__(self, profile: Path, name: str):
        self.profile = profile
        for ev in ("request", "message", "online", "friend_status", "typing", "receipt", "name", "data",
                   "group_message", "group_data", "group_invite", "group_peer", "group_ready"):
            setattr(self, "on_" + ev, None)
        self.name = name
        opts = f["tox_options_new"](None)
        data = profile.read_bytes() if profile.exists() else b""
        if data:
            f["tox_options_set_savedata_type"](opts, SAVEDATA_TYPE_TOX_SAVE)
            f["tox_options_set_savedata_data"](opts, data, len(data))
        self.tox = f["tox_new"](opts, None)
        f["tox_options_free"](opts)
        if not self.tox:
            raise RuntimeError("Tox could not start (is the UDP port free?)")
        self.set_name(name)
        self._cbs = {}
        for cb, handler in [("friend_request", self._req), ("friend_message", self._msg),
                            ("self_connection_status", self._self), ("friend_connection_status", self._fconn),
                            ("friend_name", self._fname), ("friend_typing", self._ftyping),
                            ("friend_read_receipt", self._freceipt), ("friend_lossless_packet", self._fpacket),
                            ("group_message", self._gmsg), ("group_custom_packet", self._gpacket),
                            ("group_invite", self._ginvite), ("group_peer_join", self._gjoin),
                            ("group_peer_exit", self._gexit), ("group_self_join", self._gself)]:
            self._cbs[cb] = CB[cb](handler)       # keep references: C holds the pointers
            getattr(lib, f"tox_callback_{cb}")(self.tox, self._cbs[cb])
        self._incoming = {}                       # (src, msg_id) -> [chunks]
        self._outgoing = deque()                  # (kind, target, packet)
        self.save()

    # ---------- network ----------
    def bootstrap(self, nodes):
        for host, port, key in nodes:
            k = bytes.fromhex(key)
            f["tox_bootstrap"](self.tox, host.encode(), port, k, None)
            f["tox_add_tcp_relay"](self.tox, host.encode(), port, k, None)

    def iterate(self):
        f["tox_iterate"](self.tox, None)
        self._pump()
        return f["tox_iteration_interval"](self.tox)

    def _pump(self):
        """Send queued data chunks until Tox's send queue is full."""
        sent = 0
        while self._outgoing and sent < 200:
            kind, target, packet = self._outgoing[0]
            err = C.c_int(0)
            if kind == "f":
                n = self.friend_number(target)
                if n is None:
                    self._outgoing.popleft()
                    continue
                ok = f["tox_friend_send_lossless_packet"](self.tox, n, packet, len(packet), C.byref(err))
            else:
                g = self.group_number(target)
                if g is None:
                    self._outgoing.popleft()
                    continue
                ok = f["tox_group_send_custom_packet"](self.tox, g, True, packet, len(packet), C.byref(err))
            if not ok:
                if kind == "f" and err.value == 3:        # friend offline: drop, it is resent later
                    self._outgoing.popleft()
                    continue
                break                                     # queue full: try again next iteration
            self._outgoing.popleft()
            sent += 1

    def _queue(self, kind, target, obj):
        raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode()
        if len(raw) > MAX_DATA:
            raise ValueError("too large")
        mid = random.getrandbits(32).to_bytes(4, "big")
        parts = [raw[i:i + CHUNK] for i in range(0, len(raw), CHUNK)] or [b""]
        lead = DATA_FRIEND if kind == "f" else DATA_GROUP
        for i, part in enumerate(parts):
            self._outgoing.append((kind, target, bytes([lead]) + mid + i.to_bytes(2, "big")
                                   + len(parts).to_bytes(2, "big") + part))

    def _assemble(self, src, data):
        if len(data) < 9:
            return None
        mid, idx, total = data[1:5], int.from_bytes(data[5:7], "big"), int.from_bytes(data[7:9], "big")
        if total == 0 or idx >= total or total > MAX_DATA // CHUNK + 1:
            return None
        key = (src, mid)
        parts = self._incoming.setdefault(key, [None] * total)
        if len(parts) != total:
            return None
        parts[idx] = data[9:]
        if any(p is None for p in parts):
            if len(self._incoming) > 64:              # forget stalled transfers
                self._incoming.pop(next(iter(self._incoming)))
            return None
        del self._incoming[key]
        try:
            return json.loads(b"".join(parts).decode())
        except ValueError:
            return None

    # ---------- friend callbacks ----------
    def _req(self, _t, pk, msg, length, _u):
        self.on_request and self.on_request(bytes(pk[:PUBLIC_KEY_SIZE]).hex().upper(), _txt(msg, length))

    def _msg(self, _t, fn, _type, msg, length, _u):
        self.on_message and self.on_message(self.friend_key(fn), _txt(msg, length))

    def _self(self, _t, status, _u):
        self.on_online and self.on_online(status != 0)

    def _fconn(self, _t, fn, status, _u):
        self.on_friend_status and self.on_friend_status(self.friend_key(fn), status != 0)

    def _fname(self, _t, fn, name, length, _u):
        self.on_name and self.on_name(self.friend_key(fn), _txt(name, length))

    def _ftyping(self, _t, fn, typing, _u):
        self.on_typing and self.on_typing(self.friend_key(fn), bool(typing))

    def _freceipt(self, _t, fn, mid, _u):
        self.on_receipt and self.on_receipt(self.friend_key(fn), mid)

    def _fpacket(self, _t, fn, data, length, _u):
        raw = bytes(data[:length])
        if raw and raw[0] == DATA_FRIEND:
            pk = self.friend_key(fn)
            obj = self._assemble(("f", pk), raw)
            if obj is not None and self.on_data:
                self.on_data(pk, obj)

    # ---------- group callbacks ----------
    def _gmsg(self, _t, g, peer, _type, msg, length, _mid, _u):
        if self.on_group_message:
            self.on_group_message(self.chat_id(g), peer, self.peer_key(g, peer), self.peer_name(g, peer), _txt(msg, length))

    def _gpacket(self, _t, g, peer, data, length, _u):
        raw = bytes(data[:length])
        if raw and raw[0] == DATA_GROUP:
            pk = self.peer_key(g, peer)
            obj = self._assemble(("g", self.chat_id(g), pk), raw)
            if obj is not None and self.on_group_data:
                self.on_group_data(self.chat_id(g), peer, pk, self.peer_name(g, peer), obj)

    def _ginvite(self, _t, fn, data, length, name, name_len, _u):
        if self.on_group_invite:
            self.on_group_invite(self.friend_key(fn), bytes(data[:length]), _txt(name, name_len))

    def _gjoin(self, _t, g, peer, _u):
        self.on_group_peer and self.on_group_peer(self.chat_id(g), peer, self.peer_key(g, peer), self.peer_name(g, peer), True)

    def _gexit(self, _t, g, peer, _type, name, name_len, _pm, _pl, _u):
        self.on_group_peer and self.on_group_peer(self.chat_id(g), peer, self.peer_key(g, peer), _txt(name, name_len), False)

    def _gself(self, _t, g, _u):
        self.save()
        self.on_group_ready and self.on_group_ready(self.chat_id(g))

    # ---------- identity ----------
    def address(self):
        buf = C.create_string_buffer(ADDRESS_SIZE)
        f["tox_self_get_address"](self.tox, buf)
        return buf.raw.hex().upper()

    def public_key(self):
        return self.address()[:PUBLIC_KEY_SIZE * 2]

    def set_name(self, name):
        self.name = name
        raw = name.encode()[:128]
        f["tox_self_set_name"](self.tox, raw, len(raw), None)

    def set_status(self, text):
        raw = text.encode()[:1000]
        f["tox_self_set_status_message"](self.tox, raw, len(raw), None)

    # ---------- friends ----------
    def friend_key(self, fn):
        buf = C.create_string_buffer(PUBLIC_KEY_SIZE)
        f["tox_friend_get_public_key"](self.tox, fn, buf, None)
        return buf.raw.hex().upper()

    def friend_number(self, pk_hex):
        err = C.c_int(0)
        n = f["tox_friend_by_public_key"](self.tox, bytes.fromhex(pk_hex), C.byref(err))
        return None if err.value else n

    def friends(self):
        n = f["tox_self_get_friend_list_size"](self.tox)
        arr = (U32 * max(n, 1))()
        f["tox_self_get_friend_list"](self.tox, arr)
        return [self.friend_key(arr[i]) for i in range(n)]

    def add(self, address_hex, text):
        """Send a contact request to a Nebula ID. Returns the friend's public key."""
        err = C.c_int(0)
        raw = text.encode()[:900]
        f["tox_friend_add"](self.tox, bytes.fromhex(address_hex), raw, len(raw), C.byref(err))
        if err.value not in (0, 5):          # 5 = already sent
            raise ValueError(f"contact request failed (code {err.value})")
        self.save()
        return address_hex[:PUBLIC_KEY_SIZE * 2].upper()

    def accept(self, pk_hex):
        err = C.c_int(0)
        f["tox_friend_add_norequest"](self.tox, bytes.fromhex(pk_hex), C.byref(err))
        self.save()

    def remove(self, pk_hex):
        n = self.friend_number(pk_hex)
        if n is not None:
            f["tox_friend_delete"](self.tox, n, None)
            self.save()

    def send(self, pk_hex, text):
        """Message id if handed to Tox (the friend is online), else None."""
        n = self.friend_number(pk_hex)
        if n is None:
            return None
        err = C.c_int(0)
        raw = text.encode()[:MAX_MESSAGE]
        mid = f["tox_friend_send_message"](self.tox, n, MESSAGE_TYPE_NORMAL, raw, len(raw), C.byref(err))
        return mid if err.value == 0 else None

    def typing(self, pk_hex, on):
        n = self.friend_number(pk_hex)
        if n is not None:
            f["tox_self_set_typing"](self.tox, n, on, None)

    def send_data(self, pk_hex, obj):
        self._queue("f", pk_hex, obj)

    # ---------- groups ----------
    def groups(self):
        """{chat_id: group_number} of all groups in this profile."""
        out, n, g = {}, f["tox_group_get_number_groups"](self.tox), 0
        while len(out) < n and g < n + 64:
            cid = self.chat_id(g)
            if cid:
                out[cid] = g
            g += 1
        return out

    def chat_id(self, g):
        buf = C.create_string_buffer(CHAT_ID_SIZE)
        err = C.c_int(0)
        ok = f["tox_group_get_chat_id"](self.tox, g, buf, C.byref(err))
        return buf.raw.hex().upper() if ok else ""

    def group_number(self, chat_id):
        return self.groups().get(chat_id)

    def group_name(self, chat_id):
        g = self.group_number(chat_id)
        if g is None:
            return ""
        size = f["tox_group_get_name_size"](self.tox, g, None)
        buf = C.create_string_buffer(max(size, 1))
        f["tox_group_get_name"](self.tox, g, buf, None)
        return buf.raw[:size].decode("utf-8", "replace")

    def create_group(self, name, public=True):
        err = C.c_int(0)
        gn, me = name.encode()[:48], self.name.encode()[:128]
        g = f["tox_group_new"](self.tox, PRIVACY_PUBLIC if public else PRIVACY_PRIVATE,
                               gn, len(gn), me, len(me), C.byref(err))
        if err.value:
            raise ValueError(f"group could not be created (code {err.value})")
        self.save()
        return self.chat_id(g)

    def join_group(self, chat_id):
        err = C.c_int(0)
        me = self.name.encode()[:128]
        f["tox_group_join"](self.tox, bytes.fromhex(chat_id), me, len(me), None, 0, C.byref(err))
        if err.value:
            raise ValueError(f"could not join (code {err.value})")
        self.save()

    def accept_invite(self, friend_pk, invite):
        n = self.friend_number(friend_pk)
        err = C.c_int(0)
        me = self.name.encode()[:128]
        g = f["tox_group_invite_accept"](self.tox, n, invite, len(invite), me, len(me), None, 0, C.byref(err))
        if err.value:
            raise ValueError(f"could not join (code {err.value})")
        self.save()
        return self.chat_id(g)

    def invite(self, chat_id, friend_pk):
        g, n = self.group_number(chat_id), self.friend_number(friend_pk)
        return g is not None and n is not None and f["tox_group_invite_friend"](self.tox, g, n, None)

    def leave_group(self, chat_id):
        g = self.group_number(chat_id)
        if g is not None:
            f["tox_group_leave"](self.tox, g, None, 0, None)
            self.save()

    def group_send(self, chat_id, text):
        g = self.group_number(chat_id)
        if g is None:
            return False
        err = C.c_int(0)
        raw = text.encode()[:MAX_MESSAGE]
        f["tox_group_send_message"](self.tox, g, MESSAGE_TYPE_NORMAL, raw, len(raw), C.byref(err))
        return err.value == 0

    def group_send_data(self, chat_id, obj):
        self._queue("g", chat_id, obj)

    def group_connected(self, chat_id):
        g = self.group_number(chat_id)
        return g is not None and f["tox_group_is_connected"](self.tox, g, None)

    def peer_key(self, g, peer):
        buf = C.create_string_buffer(PUBLIC_KEY_SIZE)
        f["tox_group_peer_get_public_key"](self.tox, g, peer, buf, None)
        return buf.raw.hex().upper()

    def peer_name(self, g, peer):
        size = f["tox_group_peer_get_name_size"](self.tox, g, peer, None)
        buf = C.create_string_buffer(max(size, 1))
        f["tox_group_peer_get_name"](self.tox, g, peer, buf, None)
        return buf.raw[:size].decode("utf-8", "replace")

    def my_peer_id(self, chat_id):
        g = self.group_number(chat_id)
        return None if g is None else f["tox_group_self_get_peer_id"](self.tox, g, None)

    def my_role(self, chat_id):
        g = self.group_number(chat_id)
        return ROLE_USER if g is None else f["tox_group_self_get_role"](self.tox, g, None)

    def members(self, chat_id, known_peer_ids):
        """[(peer_id, pk, name, role)] for the peer ids seen in this group."""
        g = self.group_number(chat_id)
        out = []
        if g is None:
            return out
        for peer in known_peer_ids:
            err = C.c_int(0)
            role = f["tox_group_peer_get_role"](self.tox, g, peer, C.byref(err))
            if err.value == 0:
                out.append((peer, self.peer_key(g, peer), self.peer_name(g, peer), role))
        return out

    def kick(self, chat_id, peer_id):
        g = self.group_number(chat_id)
        return g is not None and f["tox_group_kick_peer"](self.tox, g, peer_id, None)

    def set_role(self, chat_id, peer_id, role):
        g = self.group_number(chat_id)
        return g is not None and f["tox_group_set_role"](self.tox, g, peer_id, role, None)

    def peer_id_of(self, chat_id, pk, candidates):
        g = self.group_number(chat_id)
        for peer in candidates:
            if g is not None and self.peer_key(g, peer) == pk:
                return peer
        return None

    # ---------- profile file ----------
    def save(self):
        size = f["tox_get_savedata_size"](self.tox)
        buf = C.create_string_buffer(size)
        f["tox_get_savedata"](self.tox, buf)
        self.profile.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.profile.with_suffix(".tmp")
        tmp.write_bytes(buf.raw)
        os.chmod(tmp, 0o600)
        tmp.replace(self.profile)

    def close(self):
        if self.tox:
            self.save()
            f["tox_kill"](self.tox)
            self.tox = None
