#!/usr/bin/env python3
# ultra_login.py – Ultra‑fast Free Fire launcher with rate‑limit handling & live counter

import os
import sys
import time
import json
import socket
import threading
import urllib3
import http.client
import ssl
import gzip
import random
import base64
import binascii
from io import BytesIO
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import requests
import jwt
from google.protobuf.timestamp_pb2 import Timestamp
from protobuf_decoder.protobuf_decoder import Parser

# ---------- protobuf message definition (from xKEys.py) ----------
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5, 27, 2, '',
    'my_message.proto'
)
_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x10my_message.proto\">\n\tMyMessage\x12\x0f\n\x07\x66ield21\x18\x15 \x01(\x03\x12\x0f\n\x07\x66ield22\x18\x16 \x01(\x0c\x12\x0f\n\x07\x66ield23\x18\x17 \x01(\x0c\x62\x06proto3'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'my_message_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_MYMESSAGE']._serialized_start = 20
    _globals['_MYMESSAGE']._serialized_end = 82

# ---------- Crypto & Protocol functions (from byte.py) ----------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

Key, Iv = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56]), bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

def EnC_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return cipher.encrypt(pad(bytes.fromhex(HeX), AES.block_size)).hex()

def DEc_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return unpad(cipher.decrypt(bytes.fromhex(HeX)), AES.block_size).hex()

def EnC_PacKeT(HeX, K, V):
    return AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(HeX), 16)).hex()

def DEc_PacKeT(HeX, K, V):
    return unpad(AES.new(K, AES.MODE_CBC, V).decrypt(bytes.fromhex(HeX)), 16).hex()

def EnC_Uid(H, Tp):
    e, H = [], int(H)
    while H:
        e.append((H & 0x7F) | (0x80 if H > 0x7F else 0))
        H >>= 7
    return bytes(e).hex() if Tp == 'Uid' else None

def EnC_Vr(N):
    if N < 0:
        return ''
    H = []
    while True:
        BesTo = N & 0x7F
        N >>= 7
        if N:
            BesTo |= 0x80
        H.append(BesTo)
        if not N:
            break
    return bytes(H)

def DEc_Uid(H):
    n = s = 0
    for b in bytes.fromhex(H):
        n |= (b & 0x7F) << s
        if not b & 0x80:
            break
        s += 7
    return n

def CrEaTe_VarianT(field_number, value):
    field_header = (field_number << 3) | 0
    return EnC_Vr(field_header) + EnC_Vr(value)

def CrEaTe_LenGTh(field_number, value):
    field_header = (field_number << 3) | 2
    encoded_value = value.encode() if isinstance(value, str) else value
    return EnC_Vr(field_header) + EnC_Vr(len(encoded_value)) + encoded_value

def CrEaTe_ProTo(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, dict):
            nested_packet = CrEaTe_ProTo(value)
            packet.extend(CrEaTe_LenGTh(field, nested_packet))
        elif isinstance(value, int):
            packet.extend(CrEaTe_VarianT(field, value))
        elif isinstance(value, str) or isinstance(value, bytes):
            packet.extend(CrEaTe_LenGTh(field, value))
    return packet

def DecodE_HeX(H):
    R = hex(H)
    F = str(R)[2:]
    if len(F) == 1:
        F = "0" + F
        return F
    else:
        return F

def Fix_PackEt(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {}
        field_data['wire_type'] = result.wire_type
        if result.wire_type == "varint":
            field_data['data'] = result.data
        if result.wire_type == "string":
            field_data['data'] = result.data
        if result.wire_type == "bytes":
            field_data['data'] = result.data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = Fix_PackEt(result.data.results)
        result_dict[result.field] = field_data
    return result_dict

def DeCode_PackEt(input_text):
    try:
        parsed_results = Parser().parse(input_text)
        parsed_results_objects = parsed_results
        parsed_results_dict = Fix_PackEt(parsed_results_objects)
        json_data = json.dumps(parsed_results_dict)
        return json_data
    except Exception as e:
        return None

def xMsGFixinG(n):
    return '🗿'.join(str(n)[i:i + 3] for i in range(0, len(str(n)), 3))

# ---------- Packet generation helpers ----------
ULTRA_GLOW_COLORS = [
    "FF0040", "FF2200", "FF3300", "FF4400", "FF5500", "FF6600",
    "FF7700", "FF8800", "FF9900", "FFAA00", "FFBB00", "FFCC00",
    "FFDD00", "FFEE00", "FFFF00",
    "FF00AA", "FF00CC", "FF00EE", "FF00FF",
    "00FF00", "00FF44", "00FF88", "00FFCC", "00FFFF",
    "0044FF", "0088FF", "00CCFF",
    "4400FF", "8800FF", "CC00FF",
    "FFAAFF", "AAFFFF", "FFCCAA", "AAFFCC", "FFAACC", "CCFFAA",
    "FF0055", "FF0066", "FF0077", "FF0088", "FF0099", "FF00AA",
    "FF00BB", "FF00CC", "FF00DD", "FF00EE", "FF00FF",
    "FF1100", "FF2200", "FF4400", "FF8800", "FFCC00",
    "00FFAA", "00FFDD", "00BBFF", "00AAFF", "0088FF",
    "AA00FF", "BB00FF", "DD00FF", "EE00FF",
]

def ArA_CoLor():
    return random.choice(ULTRA_GLOW_COLORS)

def xBunnEr():
    return random.choice([902050001])

def GenResponsMsg(Msg, Tp, Tp2, id, K, V):
    fields = {
        1: id,
        2: Tp2,
        3: Tp,
        4: Msg,
        5: 1735129800,
        7: 2,
        9: {
            1: "xBesTo - C4­",
            2: xBunnEr(),
            3: 901048018,
            4: 330,
            5: 909000014,
            8: "xBesTo - C4",
            10: 1,
            11: random.choice([1]),
            13: {1: 2, 2: 1},
            14: {1: 1158053040, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0015\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}
        },
        10: "en",
        13: {2: 1, 3: 1},
        14: {}
    }
    Pk = str(CrEaTe_ProTo(fields).hex())
    Pk = "080112" + EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return GeneRaTePk(str(Pk), '1215', K, V)

def GeneRaTePk(Pk, N, K, V):
    PkEnc = EnC_PacKeT(Pk, K, V)
    _ = DecodE_HeX(int(len(PkEnc) // 2))
    if len(_) == 2:
        HeadEr = N + "000000"
    elif len(_) == 3:
        HeadEr = N + "00000"
    elif len(_) == 4:
        HeadEr = N + "0000"
    elif len(_) == 5:
        HeadEr = N + "000"
    return bytes.fromhex(HeadEr + _ + PkEnc)

# ---------- Dummy for ChEck_The_Uid (unused) ----------
def ChEck_The_Uid(uid):
    return False

# ---------- Global counters ----------
total_accounts = 0
online_count = 0
counter_lock = threading.Lock()
online_accounts = []

def increment_online(uid):
    global online_count, online_accounts
    with counter_lock:
        online_count += 1
        online_accounts.append(uid)
        print(f"[✅] Account {uid} is online – {online_count}/{total_accounts} online")

def print_status():
    with counter_lock:
        print(f"[STATUS] Online: {online_count}/{total_accounts} accounts online")
        if online_accounts:
            print(f"         Online IDs: {', '.join(online_accounts[:5])}{' ...' if len(online_accounts) > 5 else ''}")

# ---------- Account loader ----------
def load_accounts():
    accounts = []
    if os.path.exists("accounts.json"):
        try:
            with open("accounts.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for entry in data:
                        uid = str(entry.get("uid", ""))
                        password = entry.get("password", "")
                        if uid and password:
                            accounts.append({"id": uid, "password": password})
                print(f"[+] Loaded {len(accounts)} accounts from accounts.json")
                return accounts
        except Exception as e:
            print(f"[-] Error reading accounts.json: {e}")

    try:
        with open("accs.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if ":" in line:
                        parts = line.split(":", 1)
                        if len(parts) >= 2:
                            accounts.append({"id": parts[0].strip(), "password": parts[1].strip()})
                    else:
                        accounts.append({"id": line.strip(), "password": ""})
        print(f"[+] Loaded {len(accounts)} accounts from accs.txt")
    except FileNotFoundError:
        print("[-] No accounts file found (tried accounts.json and accs.txt)")
    except Exception as e:
        print(f"[-] Error reading accs.txt: {e}")
    return accounts

# ---------- FF_CLient (ultra‑fast login core with rate‑limit handling) ----------
class FF_CLient:
    def __init__(self, id, password):
        self.id = id
        self.password = password
        self.DaTa2 = None
        self.Get_FiNal_ToKen_0115()

    def Connect_SerVer_OnLine(self, Token, tok, host, port, key, iv, host2, port2):
        try:
            self.AutH_ToKen_0115 = tok
            self.CliEnts2 = socket.create_connection((host2, int(port2)))
            self.CliEnts2.send(bytes.fromhex(self.AutH_ToKen_0115))
        except Exception as e:
            print(f"[-] {self.id} – secondary server error: {e}")
            return

        while True:
            try:
                self.DaTa2 = self.CliEnts2.recv(99999)
                if self.DaTa2 and len(self.DaTa2) > 0:
                    hex_data = self.DaTa2.hex()
                    if '0500' in hex_data[0:4] and len(hex_data) > 30:
                        try:
                            self.packet = json.loads(DeCode_PackEt(f'08{hex_data.split("08", 1)[1]}'))
                            if '5' in self.packet and 'data' in self.packet['5']:
                                self.AutH = self.packet['5']['data']['7']['data']
                                print(f"[+] {self.id} – auth updated")
                        except Exception:
                            pass
            except Exception as e:
                print(f"[-] {self.id} – recv error: {e}")
                time.sleep(0.5)

    def Connect_SerVer(self, Token, tok, host, port, key, iv, host2, port2):
        if port is None or port2 is None or host is None or host2 is None:
            print(f"[-] {self.id} – invalid ports, retrying...")
            time.sleep(1)
            self.Get_FiNal_ToKen_0115()
            return

        self.AutH_ToKen_0115 = tok
        try:
            self.CliEnts = socket.create_connection((host, int(port)))
            self.CliEnts.send(bytes.fromhex(self.AutH_ToKen_0115))
            self.DaTa = self.CliEnts.recv(1024)
        except Exception as e:
            print(f"[-] {self.id} – main server error: {e}")
            time.sleep(0.5)
            self.Connect_SerVer(Token, tok, host, port, key, iv, host2, port2)
            return

        threading.Thread(target=self.Connect_SerVer_OnLine,
                         args=(Token, tok, host, port, key, iv, host2, port2),
                         daemon=True).start()
        self.Exemple = xMsGFixinG('12345678')
        self.key = key
        self.iv = iv

        print(f"[+] {self.id} – online")
        increment_online(self.id)

        while True:
            try:
                self.DaTa = self.CliEnts.recv(1024)
                if len(self.DaTa) == 0:
                    self.CliEnts.close()
                    if hasattr(self, 'CliEnts2'):
                        self.CliEnts2.close()
                    self.Connect_SerVer(Token, tok, host, port, key, iv, host2, port2)
                    continue

                if '1200' in self.DaTa.hex()[0:4] and 900 > len(self.DaTa.hex()) > 100:
                    if b"***" in self.DaTa:
                        self.DaTa = self.DaTa.replace(b"***", b"106")
                    try:
                        self.BesTo_data = json.loads(DeCode_PackEt(self.DaTa.hex()[10:]))
                        self.input_msg = 'besto_love' if '8' in self.BesTo_data["5"]["data"] else self.BesTo_data["5"]["data"]["4"]["data"]
                    except:
                        self.input_msg = None
                    self.DeCode_CliEnt_Uid = self.BesTo_data["5"]["data"]["1"]["data"]
                    self.CliEnt_Uid = EnC_Uid(self.DeCode_CliEnt_Uid, Tp='Uid')

                if self.input_msg and 'besto_love' in self.input_msg[:10]:
                    self.CliEnts.send(GenResponsMsg(f'''@Telegram:@bigbullghost999''', 2,
                                                    self.DeCode_CliEnt_Uid, self.DeCode_CliEnt_Uid, key, iv))
                    time.sleep(0.1)
                    self.CliEnts.close()
                    if hasattr(self, 'CliEnts2'):
                        self.CliEnts2.close()
                    self.Connect_SerVer(Token, tok, host, port, key, iv, host2, port2)

                if self.input_msg and (b'@help ' in self.DaTa or b'@help' in self.DaTa or 'en' in self.input_msg[:2]):
                    self.CliEnts.send(GenResponsMsg(f'''@Telegram:@bigbullghost999''', 2,
                                                    self.DeCode_CliEnt_Uid, self.DeCode_CliEnt_Uid, key, iv))

            except Exception as e:
                print(f"[-] {self.id} – main loop error: {e}")
                try:
                    self.CliEnts.close()
                    if hasattr(self, 'CliEnts2'):
                        self.CliEnts2.close()
                except:
                    pass
                time.sleep(0.5)
                self.Connect_SerVer(Token, tok, host, port, key, iv, host2, port2)

    # ----- helper methods with rate‑limit handling -----
    def GeT_Key_Iv(self, serialized_data):
        from google.protobuf.timestamp_pb2 import Timestamp
        my_message = _globals['MyMessage']()
        my_message.ParseFromString(serialized_data)
        timestamp, key, iv = my_message.field21, my_message.field22, my_message.field23
        timestamp_obj = Timestamp()
        timestamp_obj.FromNanoseconds(timestamp)
        timestamp_seconds = timestamp_obj.seconds
        timestamp_nanos = timestamp_obj.nanos
        combined_timestamp = timestamp_seconds * 1_000_000_000 + timestamp_nanos
        return combined_timestamp, key, iv

    def Guest_GeneRaTe(self, uid, password, retry_count=0):
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {
            "Host": "100067.connect.garena.com",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close",
        }
        data = {
            "uid": f"{uid}",
            "password": f"{password}",
            "response_type": "token",
            "client_type": "2",
            "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            "client_id": "100067",
        }
        try:
            resp = requests.post(url, headers=headers, data=data, timeout=5).json()
            if 'access_token' in resp and 'open_id' in resp:
                self.Access_ToKen, self.Access_Uid = resp['access_token'], resp['open_id']
                print(f"[+] Starting account: {uid}")
                return self.ToKen_GeneRaTe(self.Access_ToKen, self.Access_Uid)
            else:
                # Check for rate limit error
                if resp.get('error') == 'error_too_many_requests' or resp.get('code') == 1006:
                    wait = min(2 ** retry_count, 32)  # exponential backoff: 2,4,8,16,32
                    print(f"[-] Rate limit for {uid}, waiting {wait}s before retry...")
                    time.sleep(wait)
                    return self.Guest_GeneRaTe(uid, password, retry_count + 1)
                else:
                    print(f"[-] Guest token failed for {uid}: {resp}")
                    return None
        except Exception as e:
            print(f"[-] Token error for {uid}: {e}")
            return None

    def ToKen_GeneRaTe(self, Access_ToKen, Access_Uid):
        try:
            self.PLaFTrom = "4"
            self.Version, self.V = '2024010012', '1.126.2'

            self.PyL = {
                3: str(datetime.now())[:-7],
                4: "free fire",
                5: 2,
                7: self.V,
                8: "Android OS 11 / API-30 (RQ3A.210805.001)",
                9: "Handheld",
                10: "Verizon",
                11: "WIFI",
                12: 1080,
                13: 2400,
                14: "440",
                15: "ARMv8",
                16: 6144,
                17: "Adreno (TM) 650",
                18: "OpenGL ES 3.2 V@1.50",
                19: "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57",
                20: "",
                21: "en",
                22: Access_Uid,
                23: self.PLaFTrom,
                24: "Handheld",
                25: "google G011A",
                29: Access_ToKen,
                30: 3,
                41: "Verizon",
                42: "WIFI",
                57: "1ac4b80ecf0478a44203bf8fac6120f5",
                60: 32966,
                61: 29779,
                62: 2479,
                63: 914,
                64: 31176,
                65: 32966,
                66: 31176,
                67: 32966,
                70: 4,
                73: 2,
                74: "/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/lib/arm",
                76: 1,
                77: "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/base.apk",
                78: 6,
                79: 1,
                81: "64",
                83: self.Version,
                86: "OpenGLES3",
                87: 255,
                88: self.PLaFTrom,
                89: "J\u0003FD\u0004\r_UH\u0003\u000b\u0016_\u0003D^J>\u000fWT\u0000\\=\nQ_;\u0000\r;Z\u0005a",
                90: "Phoenix",
                91: "AZ",
                92: 10214,
                93: "3rd_party",
                94: "KqsHT7gtKWkK0gY/HwmdwXIhSiz4fQldX3YjZeK86XBTthKAf1bW4Vsz6Di0S8vqr0Jc4HX3TMQ8KaUU3GeVvYzWF9I=",
                95: 111207,
                97: 1,
                98: 1,
                99: f"{self.PLaFTrom}",
                100: f"{self.PLaFTrom}"
            }

            self.PyL = CrEaTe_ProTo(self.PyL).hex()
            self.PaYload = bytes.fromhex(EnC_AEs(self.PyL))

            context = ssl._create_unverified_context()
            conn = http.client.HTTPSConnection("loginbp.ggpolarbear.com", context=context, timeout=5)
            headers = {
                'X-Unity-Version': '2018.4.11f1',
                'ReleaseVersion': 'OB54',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-GA': 'v1 1',
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
                'Host': 'loginbp.ggpolarbear.com',
                'Connection': 'Keep-Alive',
                'Accept-Encoding': 'gzip'
            }

            conn.request("POST", "/MajorLogin", body=self.PaYload, headers=headers)
            response = conn.getresponse()
            raw_data = response.read()
            if response.getheader('Content-Encoding') == 'gzip':
                with gzip.GzipFile(fileobj=BytesIO(raw_data)) as f:
                    raw_data = f.read()

            if response.status not in [200, 201]:
                print("[-] MajorLogin failed")
                return None

            self.BesTo_data = json.loads(DeCode_PackEt(raw_data.hex()))
            self.JwT_ToKen = self.BesTo_data['8']['data']
            self.combined_timestamp, self.key, self.iv = self.GeT_Key_Iv(raw_data)

            ip, port, ip2, port2 = self.GeT_LoGin_PorTs(self.JwT_ToKen, self.PaYload)
            if ip is None or port is None or ip2 is None or port2 is None:
                print("[-] Failed to get valid ports from GetLoginData")
                return None
            return self.JwT_ToKen, self.key, self.iv, self.combined_timestamp, ip, port, ip2, port2
        except Exception as e:
            print(f"[-] Token generation error: {e}")
            return None

    def GeT_LoGin_PorTs(self, JwT_ToKen, PayLoad):
        url = 'https://client.ind.freefiremobile.com/GetLoginData'
        headers = {
            'Expect': '100-continue',
            'Authorization': f'Bearer {JwT_ToKen}',
            'X-Unity-Version': '2018.4.11f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': 'OB54',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)',
            'Host': 'client.ind.freefiremobile.com',
            'Connection': 'close',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        try:
            resp = requests.post(url, headers=headers, data=PayLoad, verify=False, timeout=5)
            decoded = DeCode_PackEt(resp.content.hex())
            if not decoded:
                print("[-] Failed to decode GetLoginData response")
                return None, None, None, None

            data = json.loads(decoded)
            if '32' not in data or '14' not in data:
                print(f"[-] Missing port data: {data.keys()}")
                return None, None, None, None

            address, address2 = data['32']['data'], data['14']['data']
            if not address or not address2:
                print("[-] Empty address received")
                return None, None, None, None

            ip, port = address.rsplit(":", 1)
            ip2, port2 = address2.rsplit(":", 1)
            if not ip or not port or not ip2 or not port2:
                print("[-] Invalid address format")
                return None, None, None, None

            print(f"[+] Got ports: Chat={ip}:{port}, Game={ip2}:{port2}")
            return ip, int(port), ip2, int(port2)
        except Exception as e:
            print(f"[-] GetLoginData error: {e}")
            return None, None, None, None

    def Get_FiNal_ToKen_0115(self):
        token_res = self.Guest_GeneRaTe(self.id, self.password)
        if not token_res:
            print(f"[-] {self.id} – token generation failed, retrying...")
            time.sleep(1)
            self.Get_FiNal_ToKen_0115()
            return

        token, key, iv, timestamp, ip, port, ip2, port2 = token_res
        self.JwT_ToKen = token
        try:
            self.AfTer_DeC_JwT = jwt.decode(token, options={"verify_signature": False})
            self.AccounT_Uid = self.AfTer_DeC_JwT.get('account_id')
            self.EncoDed_AccounT = hex(self.AccounT_Uid)[2:]
            self.HeX_VaLue = DecodE_HeX(timestamp)
            self.TimE_HEx = self.HeX_VaLue
            self.JwT_ToKen_ = token.encode().hex()
        except Exception as e:
            print(f"[-] JWT decode error: {e}")
            time.sleep(1)
            self.Get_FiNal_ToKen_0115()
            return

        try:
            self.Header = hex(len(EnC_PacKeT(self.JwT_ToKen_, key, iv)) // 2)[2:]
            length = len(self.EncoDed_AccounT)
            self.__ = '00000000'
            if length == 9:
                self.__ = '0000000'
            elif length == 8:
                self.__ = '00000000'
            elif length == 10:
                self.__ = '000000'
            elif length == 7:
                self.__ = '000000000'
            else:
                print('[-] Unexpected account id length')
                time.sleep(1)
                self.Get_FiNal_ToKen_0115()
                return
            self.Header = f'0115{self.__}{self.EncoDed_AccounT}{self.TimE_HEx}00000{self.Header}'
            self.FiNal_ToKen_0115 = self.Header + EnC_PacKeT(self.JwT_ToKen_, key, iv)
        except Exception as e:
            print(f"[-] Final token error: {e}")
            time.sleep(1)
            self.Get_FiNal_ToKen_0115()
            return

        self.AutH_ToKen = self.FiNal_ToKen_0115
        self.Connect_SerVer(self.JwT_ToKen, self.AutH_ToKen, ip, port, key, iv, ip2, port2)

# ---------- Start accounts with staggered launch ----------
def start_account(account):
    try:
        FF_CLient(account['id'], account['password'])
    except Exception as e:
        print(f"❌ Failed to start {account['id']}: {e}")
        time.sleep(0.5)
        start_account(account)

# ---------- Summary thread (every 5 seconds) ----------
def print_summary():
    while True:
        time.sleep(5)
        print_status()

# ---------- Main ----------
if __name__ == '__main__':
    accounts = load_accounts()
    if not accounts:
        print("[-] No accounts to start. Exiting.")
        sys.exit(1)

    total_accounts = len(accounts)
    print(f"[+] Total accounts loaded: {total_accounts}")
    print("[+] Starting accounts with staggered launch (0.3s gap) to avoid rate limits...")

    threading.Thread(target=print_summary, daemon=True).start()

    # Use ThreadPoolExecutor but submit each account with a small delay between submissions
    with ThreadPoolExecutor(max_workers=total_accounts) as executor:
        futures = []
        for acc in accounts:
            futures.append(executor.submit(start_account, acc))
            time.sleep(0.3)  # stagger submissions to avoid rate limit

        # Wait for all to complete (they run forever)
        for f in futures:
            try:
                f.result()
            except Exception as e:
                print(f"Error in thread: {e}")

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print(f"\n[!] Shutting down... Final online: {online_count}/{total_accounts}")
        sys.exit(0)