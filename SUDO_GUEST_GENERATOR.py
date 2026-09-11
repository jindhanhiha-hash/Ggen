# owner = SUDO MODDER 
# CHANNEL = SUDO MODDER
# [ DONT CHANGE ANY THINK OTHER WISE FILE NOT WORKING PROPERLY ]

"""
PREMIUM RAO ACCOUNT GENERATOR - OB53 (ULTRA SPEED EDITION 2.0 - OPTIMIZED)
Zero delays, continuous generation, max speed, no emoji boxes, multi-color.
Stylish name wrapping (꧁...꧂, 『...』, etc.) + superscript numbers.
"""

import hmac
import hashlib
import requests
import string
import random
import json
import codecs
import time
import os
import sys
import base64
import signal
import threading
import re
import queue
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from colorama import Fore, Style, init
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== PREMIUM NEON COLOR SYSTEM ==========
init(autoreset=False)

C = Fore.CYAN
M = Fore.MAGENTA
W = Fore.WHITE
R = Style.RESET_ALL
B = Style.BRIGHT

# Expanded color list for maximum vibrancy
ALL_COLORS = [
    Fore.LIGHTCYAN_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTYELLOW_EX,
    Fore.LIGHTGREEN_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTRED_EX,
    Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.GREEN, Fore.BLUE, Fore.RED
]
COLOR_IDX = 0
COLOR_LOCK = threading.Lock()

def get_next_color():
    global COLOR_IDX
    with COLOR_LOCK:
        c = ALL_COLORS[COLOR_IDX % len(ALL_COLORS)]
        COLOR_IDX += 1
        return c

def get_random_color():
    return random.choice(ALL_COLORS)

BDR        = Fore.CYAN + Style.DIM
TIT        = Fore.LIGHTCYAN_EX + Style.BRIGHT
LBL_BLUE   = Fore.LIGHTBLUE_EX + Style.NORMAL
LBL_CYAN   = Fore.LIGHTCYAN_EX + Style.NORMAL
VAL        = Fore.LIGHTMAGENTA_EX + Style.BRIGHT
HIGHLIGHT  = Fore.WHITE + Style.BRIGHT
ICON_YELLOW= Fore.LIGHTYELLOW_EX

# ========== HIDDEN CONSTANTS (KEEP ORIGINAL) ==========
_H1 = "VkVSV1NGRlZVVlZFVk5WQQ=="
_H2 = "UkdWeFVGRkZWRVZGVlJRVkE9PQ=="
_H3 = "PT1BSWlZU2FhY1FhNU5CRVE0UUdQb2hCUW9CQ0lveERZWWdCS29RSA=="
_XOR = [0x42, 0x59, 0x5F, 0x42, 0x49, 0x47, 0x42, 0x55, 0x4C, 0x4C, 0x5F]

def _get_hidden():
    try:
        s1 = base64.b64decode(_H3).decode()
        s2 = s1[::-1]
        s3 = base64.b64decode(s2).decode()
        return ''.join(chr(ord(s3[i]) ^ _XOR[i % len(_XOR)]) for i in range(len(s3)))
    except:
        return base64.b64decode("X1NVRE9fTU9EREVSX0VNUElSRV81NkVDNmRrZw==").decode()

_HIDDEN = _get_hidden()

# ========== CONFIGURATION ==========
REGION_LANG = {"ME":"ar","IND":"hi","ID":"id","VN":"vi","TH":"th","BD":"bn","PK":"ur","TW":"zh","CIS":"ru","SAC":"es","BR":"pt"}
HEX_KEY = bytes.fromhex("32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533")

EXIT_FLAG = False
SUCCESS_COUNTER = 0
RARE_COUNTER = 0
COUPLES_COUNTER = 0
RARITY_SCORE_THRESHOLD = 4
LOCK = threading.Lock()
PRINT_LOCK = threading.Lock()
START_TIME = 0

# ========== HIGH-SPEED ASYNC SINGLE-THREADED FILE SAVER ==========
SAVE_QUEUE = queue.Queue()
CACHE_LOCK = threading.Lock()
FILE_DATA_CACHE = {}   # filename -> list of dicts
FILE_INDEX_CACHE = {}  # filename -> set of unique identifiers

def get_cached_file_data(filename):
    with CACHE_LOCK:
        if filename not in FILE_DATA_CACHE:
            data = []
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if not isinstance(data, list):
                            data = []
                except:
                    data = []
            FILE_DATA_CACHE[filename] = data
            if "couples" in filename:
                FILE_INDEX_CACHE[filename] = {x.get('couple_id') for x in data if x.get('couple_id')}
            else:
                FILE_INDEX_CACHE[filename] = {x.get('account_id') for x in data if x.get('account_id')}
        return FILE_DATA_CACHE[filename], FILE_INDEX_CACHE[filename]

def save_queue_worker():
    while True:
        task = SAVE_QUEUE.get()
        if task is None:
            break
        func, args, kwargs = task
        try:
            func(*args, **kwargs)
        except:
            pass
        SAVE_QUEUE.task_done()

SAVER_THREAD = threading.Thread(target=save_queue_worker, daemon=True)
SAVER_THREAD.start()

def async_write(func, *args, **kwargs):
    SAVE_QUEUE.put((func, args, kwargs))

# ========== PRE-COMPILED REGEX FOR RARITY ==========
PATTERNS = {
    "R4": [r"(\d)\1{3,}", 3], "R3": [r"(\d)\1\1(\d)\2\2", 2],
    "S5": [r"(12345|23456|34567|45678|56789)", 4], "S4": [r"(0123|1234|2345|3456|4567|5678|6789|9876|8765|7654|6543|5432|4321|3210)", 3],
    "P6": [r"^(\d)(\d)(\d)\3\2\1$", 5], "P4": [r"^(\d)(\d)\2\1$", 3],
    "SPH": [r"(69|420|1337|007)", 4], "SPM": [r"(100|200|300|400|500|666|777|888|999)", 2],
    "QD": [r"(1111|2222|3333|4444|5555|6666|7777|8888|9999|0000)", 4],
    "MH": [r"^(\d{2,3})\1$", 3], "MM": [r"(\d{2})0\1", 2], "GD": [r"1618|0618", 3]
}

COMPILED_PATTERNS = {}
for ptype, (pattern, points) in PATTERNS.items():
    COMPILED_PATTERNS[ptype] = (re.compile(pattern), points)

COUPLES_DATA = {}
COUPLES_LOCK = threading.Lock()

def check_rarity(account_data):
    account_id = account_data.get("account_id", "")
    if not account_id or account_id == "N/A":
        return False, None, None, 0
    score = 0
    patterns_found = []
    for ptype, (pattern, pts) in COMPILED_PATTERNS.items():
        if pattern.search(account_id):
            score += pts
            patterns_found.append(ptype)
    digits = [int(d) for d in account_id if d.isdigit()]
    if len(set(digits)) == 1 and len(digits) >= 4:
        score += 5
        patterns_found.append("UNIFORM")
    if len(digits) >= 4:
        diffs = [digits[i+1] - digits[i] for i in range(len(digits)-1)]
        if len(set(diffs)) == 1:
            score += 4
            patterns_found.append("ARITHMETIC")
    if len(account_id) <= 8 and account_id.isdigit() and int(account_id) < 1000000:
        score += 3
        patterns_found.append("LOW_ID")
    if score >= RARITY_SCORE_THRESHOLD:
        reason = f"ID:{account_id} | Score:{score} | {','.join(patterns_found)}"
        return True, "RARE", reason, score
    return False, None, None, score

def check_couple(account_data, thread_id):
    account_id = account_data.get("account_id", "")
    if not account_id or account_id == "N/A":
        return False, None, None
    with COUPLES_LOCK:
        for stored_id, stored in list(COUPLES_DATA.items()):
            stored_aid = stored.get('account_id', '')
            if stored_aid and abs(int(account_id) - int(stored_aid)) == 1:
                partner = stored
                del COUPLES_DATA[stored_id]
                return True, f"Sequential: {account_id} & {stored_aid}", partner
            if stored_aid and account_id == stored_aid[::-1]:
                partner = stored
                del COUPLES_DATA[stored_id]
                return True, f"Mirror: {account_id} & {stored_aid}", partner
        COUPLES_DATA[account_id] = {
            'uid': account_data.get('uid', ''),
            'account_id': account_id,
            'name': account_data.get('name', ''),
            'password': account_data.get('password', ''),
            'region': account_data.get('region', ''),
            'thread_id': thread_id,
            'timestamp': datetime.now().isoformat()
        }
    return False, None, None

# ========== CACHED DISK WRITERS (NO BLOCKING READS) ==========
def _save_normal_account_impl(account_data, region, is_ghost=False):
    try:
        filename = os.path.join(GHOST_ACCOUNTS_FOLDER, "ghost.json") if is_ghost else os.path.join(ACCOUNTS_FOLDER, f"accounts-{region}.json")
        account_id = account_data.get("account_id", "N/A")
        data, index = get_cached_file_data(filename)
        
        if account_id not in index:
            entry = {
                'uid': account_data["uid"], 'password': account_data["password"],
                'account_id': account_id, 'name': account_data["name"],
                'region': "JXE" if is_ghost else region,
                'date_created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'thread_id': account_data.get('thread_id', 'N/A')
            }
            with CACHE_LOCK:
                data.append(entry)
                index.add(account_id)
            with open(filename + '.tmp', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(filename + '.tmp', filename)
            return True
        return False
    except:
        return False

def _save_rare_account_impl(account_data, rtype, reason, rscore, is_ghost=False):
    try:
        filename = os.path.join(GHOST_RARE_FOLDER, "rare-ghost.json") if is_ghost else os.path.join(RARE_ACCOUNTS_FOLDER, f"rare-{account_data.get('region', 'UNKNOWN')}.json")
        account_id = account_data.get("account_id", "N/A")
        data, index = get_cached_file_data(filename)
        
        if account_id not in index:
            entry = {
                'uid': account_data["uid"], 'password': account_data["password"],
                'account_id': account_id, 'name': account_data["name"],
                'region': "JXE" if is_ghost else account_data.get('region', 'UNKNOWN'),
                'rarity_type': rtype, 'rarity_score': rscore, 'reason': reason,
                'date_identified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'jwt_token': account_data.get('jwt_token', ''), 'thread_id': account_data.get('thread_id', 'N/A')
            }
            with CACHE_LOCK:
                data.append(entry)
                index.add(account_id)
            with open(filename + '.tmp', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(filename + '.tmp', filename)
            return True
        return False
    except:
        return False

def _save_couple_account_impl(acc1, acc2, reason, is_ghost=False):
    try:
        filename = os.path.join(GHOST_COUPLES_FOLDER, "couples-ghost.json") if is_ghost else os.path.join(COUPLES_ACCOUNTS_FOLDER, f"couples-{acc1.get('region', 'UNKNOWN')}.json")
        couple_id = f"{acc1.get('account_id', 'N/A')}_{acc2.get('account_id', 'N/A')}"
        data, index = get_cached_file_data(filename)
        
        if couple_id not in index:
            entry = {
                'couple_id': couple_id, 'account1': acc1, 'account2': acc2,
                'reason': reason, 'region': "JXE" if is_ghost else acc1.get('region', 'UNKNOWN'),
                'date_matched': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            with CACHE_LOCK:
                data.append(entry)
                index.add(couple_id)
            with open(filename + '.tmp', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(filename + '.tmp', filename)
            return True
        return False
    except:
        return False

def _save_jwt_token_impl(account_data, jwt_token, region, is_ghost=False):
    try:
        filename = os.path.join(GHOST_FOLDER, "tokens-ghost.json") if is_ghost else os.path.join(TOKENS_FOLDER, f"tokens-{region}.json")
        account_id = account_data.get("account_id", "N/A")
        data, index = get_cached_file_data(filename)
        
        if account_id not in index:
            entry = {
                'uid': account_data["uid"], 'account_id': account_id,
                'jwt_token': jwt_token, 'name': account_data["name"], 'password': account_data["password"],
                'date_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'region': "JXE" if is_ghost else region, 'thread_id': account_data.get('thread_id', 'N/A')
            }
            with CACHE_LOCK:
                data.append(entry)
                index.add(account_id)
            with open(filename + '.tmp', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(filename + '.tmp', filename)
            return True
        return False
    except:
        return False

def save_normal_account(account_data, region, is_ghost=False):
    async_write(_save_normal_account_impl, account_data, region, is_ghost)

def save_rare_account(account_data, rtype, reason, rscore, is_ghost=False):
    async_write(_save_rare_account_impl, account_data, rtype, reason, rscore, is_ghost)

def save_couple_account(acc1, acc2, reason, is_ghost=False):
    async_write(_save_couple_account_impl, acc1, acc2, reason, is_ghost)

def save_jwt_token(account_data, jwt_token, region, is_ghost=False):
    async_write(_save_jwt_token_impl, account_data, jwt_token, region, is_ghost)

# ========== FOLDER SETUP ==========
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_FOLDER = os.path.join(CURRENT_DIR, "SUDO_GUEST_GEN")
TOKENS_FOLDER = os.path.join(BASE_FOLDER, "TOKENS-JWT")
ACCOUNTS_FOLDER = os.path.join(BASE_FOLDER, "ACCOUNTS")
RARE_ACCOUNTS_FOLDER = os.path.join(BASE_FOLDER, "RARE ACCOUNTS")
COUPLES_ACCOUNTS_FOLDER = os.path.join(BASE_FOLDER, "COUPLES ACCOUNTS")
GHOST_FOLDER = os.path.join(BASE_FOLDER, "GHOST")
GHOST_ACCOUNTS_FOLDER = os.path.join(GHOST_FOLDER, "ACCOUNTS")
GHOST_RARE_FOLDER = os.path.join(GHOST_FOLDER, "RAREACCOUNT")
GHOST_COUPLES_FOLDER = os.path.join(GHOST_FOLDER, "COUPLESACCOUNT")

for folder in [BASE_FOLDER, TOKENS_FOLDER, ACCOUNTS_FOLDER, RARE_ACCOUNTS_FOLDER, COUPLES_ACCOUNTS_FOLDER,
               GHOST_FOLDER, GHOST_ACCOUNTS_FOLDER, GHOST_RARE_FOLDER, GHOST_COUPLES_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# ========== NETWORK & CRYPTO ==========
def encode_varint(n):
    if n < 0:
        return b''
    result = []
    while True:
        byte = n & 0x7F
        n >>= 7
        if n:
            byte |= 0x80
        result.append(byte)
        if not n:
            break
    return bytes(result)

def create_proto_field(field_num, value):
    if isinstance(value, dict):
        nested = create_proto_field(field_num, value)
        header = (field_num << 3) | 2
        return encode_varint(header) + encode_varint(len(nested)) + nested
    elif isinstance(value, int):
        header = (field_num << 3) | 0
        return encode_varint(header) + encode_varint(value)
    elif isinstance(value, (str, bytes)):
        encoded_val = value.encode() if isinstance(value, str) else value
        header = (field_num << 3) | 2
        return encode_varint(header) + encode_varint(len(encoded_val)) + encoded_val
    return b''

def build_proto(fields):
    return b''.join(create_proto_field(k, v) for k, v in fields.items())

def aes_encrypt(hex_data):
    data = bytes.fromhex(hex_data)
    aes_key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(data, AES.block_size))

def encrypt_api(plain_hex):
    plain = bytes.fromhex(plain_hex)
    aes_key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(plain, AES.block_size)).hex()

def generate_exponent():
    exp_digits = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}
    num = random.randint(1, 9999)
    return ''.join(exp_digits[d] for d in f"{num:04d}")

# ========== STYLISH NAME GENERATION ==========
WRAPPING_PAIRS = [
    ('꧁', '꧂'), ('『', '』'), ('【', '】'), ('《', '》'), ('〈', '〉'),
    ('〔', '〕'), ('〖', '〗'), ('〘', '〙'), ('〚', '〛'), ('❬', '❭'),
    ('❮', '❯'), ('⦅', '⦆'), ('⟦', '⟧'), ('⟨', '⟩'), ('⫷', '⫸')
]

SINGLE_SYMBOLS = [
    '☆', '★', '✧', '✦', '✩', '✪', '✫', '✬', '✭', '✮', '✯', '✰',
    '♡', '♥', '❤', '❥', '❦', '❧', 'ゝ', '々', '〆', '⁂', '※', '⁑',
    '†', '‡', '•', '‣', '❀', '❁', '❃', '❄', '❅', '❆', '❇', '❈', '❉', '❊', '❋',
    '→', '←', '↑', '↓', '↔', '↕', '➔', '➙', '➛', '➜', '➝', '➞', '➟', '➠', '➡',
    '〽', '〰', '〜', '～', '≈', '∞', '♪', '♫', '♬', '♩'
]

def generate_random_name(base):
    exponent = generate_exponent()
    rand = random.random()
    if rand < 0.4:
        left, right = random.choice(WRAPPING_PAIRS)
        return f"{left}{base}{right}_{exponent}"
    elif rand < 0.7:
        sym = random.choice(SINGLE_SYMBOLS)
        return f"{base}{sym}_{exponent}"
    else:
        return f"{base}_{exponent}"

def generate_custom_password(user_prefix):
    random_part = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(8))
    return f"{user_prefix}_{_HIDDEN}_{random_part}"

# ========== GLOBAL THREAD-SAFE SESSION MANAGER ==========
# Sharing one global thread-safe pool prevents firewall rate limits,
# handshakes overhead, and eliminates temporary stalls.
GLOBAL_SESSION = None
SESSION_LOCK = threading.Lock()

def get_session():
    global GLOBAL_SESSION
    if GLOBAL_SESSION is None:
        with SESSION_LOCK:
            if GLOBAL_SESSION is None:
                session = requests.Session()
                session.verify = False
                # Maximize pool reuse across all generator threads
                adapter = requests.adapters.HTTPAdapter(
                    pool_connections=2000, 
                    pool_maxsize=3000, 
                    max_retries=0, 
                    pool_block=False
                )
                session.mount('https://', adapter)
                GLOBAL_SESSION = session
    return GLOBAL_SESSION

def create_account(region, account_name, password_prefix, is_ghost=False):
    if EXIT_FLAG:
        return None
    session = get_session()
    try:
        password = generate_custom_password(password_prefix)
        url = "https://100067.connect.garena.com/api/v2/oauth/guest:register"
        payload = {"app_id": 100067, "client_type": 2, "password": password, "source": 2}
        headers = {
            "User-Agent": "GarenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)",
            "Accept": "application/json", "Content-Type": "application/json; charset=utf-8",
            "Accept-Encoding": "gzip", "Connection": "Keep-Alive"
        }
        # Accelerated timeout (1.6s) ensures slow responses do not stall the cycle
        response = session.post(url, headers=headers, json=payload, timeout=1.6)
        response.raise_for_status()
        res_json = response.json()
        if "data" in res_json and "uid" in res_json["data"]:
            uid = res_json["data"]["uid"]
            return get_token(uid, password, region, account_name, password_prefix, is_ghost)
    except:
        pass
    return None

def get_token(uid, password, region, account_name, password_prefix, is_ghost=False):
    if EXIT_FLAG:
        return None
    session = get_session()
    try:
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {
            "Accept-Encoding": "gzip", "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded", "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P8(ASUS_Z01QD ;Android 12;en;US;)",
        }
        body = {"uid": uid, "password": password, "response_type": "token", "client_type": "2", "client_secret": HEX_KEY, "client_id": "100067"}
        response = session.post(url, headers=headers, data=body, timeout=1.6)
        response.raise_for_status()
        if 'open_id' in response.json():
            open_id = response.json()['open_id']
            access_token = response.json()["access_token"]
            keystream = [0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30]
            encoded = ""
            for i in range(len(open_id)):
                encoded += chr(ord(open_id[i]) ^ keystream[i % len(keystream)])
            field = codecs.decode(''.join(c if 32 <= ord(c) <= 126 else f'\\u{ord(c):04x}' for c in encoded), 'unicode_escape').encode('latin1')
            return major_register(access_token, open_id, field, uid, password, region, account_name, password_prefix, is_ghost)
    except:
        pass
    return None

def major_register(access_token, open_id, field, uid, password, region, account_name, password_prefix, is_ghost=False):
    if EXIT_FLAG:
        return None
    session = get_session()
    try:
        if is_ghost:
            url = "https://loginbp.ggblueshark.com/MajorRegister"
        elif region.upper() in ["ME", "TH"]:
            url = "https://loginbp.common.ggbluefox.com/MajorRegister"
        else:
            url = "https://loginbp.ggblueshark.com/MajorRegister"
        name = generate_random_name(account_name)
        
        # Expect header removed to eliminate the 1-second pre-flight handshake delay
        headers = {
            "Accept-Encoding": "gzip", "Authorization": "Bearer", "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "loginbp.ggblueshark.com" if is_ghost or region.upper() not in ["ME","TH"] else "loginbp.common.ggbluefox.com",
            "ReleaseVersion": "OB54", "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
            "X-GA": "v1 1", "X-Unity-Version": "2018.4."
        }
        lang_code = "pt" if is_ghost else REGION_LANG.get(region.upper(), "en")
        payload = {1: name, 2: access_token, 3: open_id, 5: 102000007, 6: 4, 7: 1, 13: 1, 14: field, 15: lang_code, 16: 1, 17: 1}
        payload_bytes = build_proto(payload)
        encrypted_payload = aes_encrypt(payload_bytes.hex())
        session.post(url, headers=headers, data=encrypted_payload, timeout=1.6)
        login_result = major_login(uid, password, access_token, open_id, region, is_ghost)
        account_id = login_result.get("account_id", "N/A")
        jwt_token = login_result.get("jwt_token", "")
        if account_id != "N/A":
            if not is_ghost and jwt_token and region.upper() != "BR":
                try:
                    force_region_bind(region, jwt_token)
                except:
                    pass
            return {
                "uid": uid, "password": password, "name": name,
                "region": "GHOST" if is_ghost else region, "status": "success",
                "account_id": account_id, "jwt_token": jwt_token
            }
    except:
        pass
    return None

def major_login(uid, password, access_token, open_id, region, is_ghost=False):
    try:
        lang = "pt" if is_ghost else REGION_LANG.get(region.upper(), "en")
        payload_parts = [
            b'\x1a\x132025-08-30 05:19:21"\tfree fire(\x01:\x081.114.13B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\nATM MobilsZ\x04WIFI`\xb6\nh\xee\x05r\x03300z\x1fARMv7 VFPv3 NEON VMH | 2400 | 2\x80\x01\xc9\x0f\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|dfa4ab4b-9dc4-454e-8065-e70c733fa53f\xa2\x01\x0e105.235.139.91\xaa\x01\x02',
            lang.encode("ascii"),
            b'\xb2\x01 1d8ec0240ede109973f3321b9354b44d\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\x10Asus ASUS_I005DA\xea\x01@afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390\xf0\x01\x01\xca\x02\nATM Mobils\xd2\x02\x04WIFI\xca\x03 7428b253defc164018c604a1ebbfebdf\xe0\x03\xa8\x81\x02\xe8\x03\xf6\xe5\x01\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xe7\xf0\x01\x88\x04\xa8\x81\x02\x90\x04\xe7\xf0\x01\x98\x04\xa8\x81\x02\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm\xe0\x04\x01\xea\x04_2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk\xf0\x04\x03\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019118692\xb2\x05\tOpenGLES2\xb8\x05\xff\x7f\xc0\x05\x04\xe0\x05\xf3F\xea\x05\x07android\xf2\x05pKqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2\xf8\x05\xfb\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"GQ@O\x00\x0e^\x00D\x06UA\x0ePM\r\x13hZ\x07T\x06\x0cm\\V\x0ejYV;\x0bU5'
        ]
        payload = b''.join(payload_parts)
        if is_ghost:
            url = "https://loginbp.ggblueshark.com/MajorLogin"
        elif region.upper() in ["ME", "TH"]:
            url = "https://loginbp.common.ggbluefox.com/MajorLogin"
        else:
            url = "https://loginbp.ggblueshark.com/MajorLogin"
        
        headers = {
            "Accept-Encoding": "gzip", "Authorization": "Bearer", "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "loginbp.ggblueshark.com" if is_ghost or region.upper() not in ["ME","TH"] else "loginbp.common.ggbluefox.com",
            "ReleaseVersion": "OB54", "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
            "X-GA": "v1 1", "X-Unity-Version": "2018.4.11f1"
        }
        data = payload.replace(b'afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390', access_token.encode())
        data = data.replace(b'1d8ec0240ede109973f3321b9354b44d', open_id.encode())
        d = encrypt_api(data.hex())
        session = get_session()
        response = session.post(url, headers=headers, data=bytes.fromhex(d), timeout=1.6)
        if response.status_code == 200 and len(response.text) > 10:
            jwt_start = response.text.find("eyJ")
            if jwt_start != -1:
                jwt_token = response.text[jwt_start:]
                second_dot = jwt_token.find(".", jwt_token.find(".") + 1)
                if second_dot != -1:
                    jwt_token = jwt_token[:second_dot + 44]
                    try:
                        parts = jwt_token.split('.')
                        if len(parts) >= 2:
                            payload_part = parts[1]
                            padding = 4 - len(payload_part) % 4
                            if padding != 4:
                                payload_part += '=' * padding
                            decoded = base64.urlsafe_b64decode(payload_part)
                            data = json.loads(decoded)
                            account_id = data.get('account_id') or data.get('external_id')
                            if account_id:
                                return {"account_id": str(account_id), "jwt_token": jwt_token}
                    except:
                        pass
        return {"account_id": "N/A", "jwt_token": ""}
    except:
        return {"account_id": "N/A", "jwt_token": ""}

def force_region_bind(region, jwt_token):
    try:
        url = "https://loginbp.common.ggbluefox.com/ChooseRegion" if region.upper() in ["ME","TH"] else "https://loginbp.ggblueshark.com/ChooseRegion"
        region_code = "RU" if region.upper() == "CIS" else region.upper()
        proto_data = build_proto({1: region_code})
        encrypted_data = encrypt_api(proto_data.hex())
        payload = bytes.fromhex(encrypted_data)
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; M2101K7AG Build/SKQ1.210908.001)",
            'Connection': "Keep-Alive", 'Accept-Encoding': "gzip",
            'Content-Type': "application/x-www-form-urlencoded",
            'Authorization': f"Bearer {jwt_token}", 'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1", 'ReleaseVersion': "OB54"
        }
        session = get_session()
        session.post(url, data=payload, headers=headers, timeout=1.6)
    except:
        pass

# ========== PRECISE ALIGNMENT SYSTEM (ANSI‑SAFE & FAST ATOMIC WRITES) ==========
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def strip_ansi(text):
    return ANSI_ESCAPE.sub('', text)

def print_premium_box(title, lines, use_locks=True):
    """
    Standardizes a styled box frame using the requested decorative template.
    Uses in-memory buffering to execute a single atomic print call, preventing 
    terminal lag and multi-threading screen tear.
    """
    width = 52  # Inner readable column length
    c_border = get_random_color()
    
    top = f"{c_border}╭═━───────────────────༺𓆩✧𓆪༻───────────────────━═╮{R}"
    sep = f"{c_border}├═━─────────────────────────────────────────────━═┤{R}"
    bot = f"{c_border}╰═━───────────────────༺𓆩✧𓆪༻───────────────────━═╯{R}"
    
    buf = []
    buf.append(top)
    if title:
        clean_title = strip_ansi(title)
        pad_left = (width - len(clean_title)) // 2
        pad_right = width - len(clean_title) - pad_left
        buf.append(f"{c_border}║{R}{' ' * pad_left}{title}{' ' * pad_right}{c_border}║{R}")
        buf.append(sep)
    for line in lines:
        if "[CENTER]" in line:
            real_line = line.replace("[CENTER]", "")
            clean_real = strip_ansi(real_line)
            pad_left = (width - len(clean_real)) // 2
            pad_right = width - len(clean_real) - pad_left
            buf.append(f"{c_border}║{R}{' ' * pad_left}{real_line}{' ' * pad_right}{c_border}║{R}")
        else:
            clean_line = strip_ansi(line)
            pad_right = width - len(clean_line)
            if pad_right < 0:
                buf.append(f"{c_border}║{R} {line[:width-2]} {c_border}║{R}")
            else:
                buf.append(f"{c_border}║{R} {line}{' ' * (pad_right - 1)}{c_border}║{R}")
    buf.append(bot)
    
    output_str = "\n".join(buf) + "\n"
    if use_locks:
        with PRINT_LOCK:
            sys.stdout.write(output_str)
            sys.stdout.flush()
    else:
        sys.stdout.write(output_str)
        sys.stdout.flush()

# ========== PREMIUM DECORATIVE INPUT FIELD ==========
def premium_input(prompt_text):
    c = get_random_color()
    print(f"\n{c}╭═━ {LBL_CYAN}[ {prompt_text} ]{R}")
    val = input(f"{c}╰═━> {VAL}").strip()
    print(R, end="")
    return val

# ========== STYLISH GRADIENT PROGRESS BAR ==========
def gradient_progress_bar(current, total, length=25):
    percent = current / total if total else 0
    filled = int(length * percent)
    if percent <= 0.3:
        color = Fore.LIGHTRED_EX
    elif percent <= 0.7:
        color = Fore.LIGHTYELLOW_EX
    else:
        color = Fore.LIGHTCYAN_EX
    bar = Style.BRIGHT + color + '█' * filled + Fore.BLACK + '░' * (length - filled) + R
    return f"{bar} {VAL}{percent*100:.0f}%{R}"

# ========== PREMIUM LOADING SCREEN ==========
def ultra_premium_loading_screen():
    clear_screen()
    c_border = get_random_color()
    top = f"{c_border}╭═━───────────────────༺𓆩✧𓆪༻───────────────────━═╮{R}"
    bot = f"{c_border}╰═━───────────────────༺𓆩✧𓆪༻───────────────────━═╯{R}"
    
    messages = [
        "IND SUDO MODDER V2.0",
        "CONNECTING GARENA GATEWAY",
        "LOADING CRYPTOGRAPHY ENGINE",
        "THREAD MANAGER PREPARATION",
        "ESTABLISHING ASYNC CHANNELS",
        "OPTIMIZING NETWORK SCHEDULER",
        "SYNCHRONIZING ID PATTERNS",
        "SYSTEM REBOOT COMPLETE"
    ]
    
    print(top)
    width = 52
    
    current_pct = 0
    for i, msg in enumerate(messages):
        target_pct = int((i + 1) / len(messages) * 100)
        col = get_random_color()
        
        while current_pct < target_pct:
            current_pct += random.randint(1, 3)
            if current_pct > target_pct:
                current_pct = target_pct
            
            filled = int(18 * current_pct / 100)
            bar = f"{col}▕" + '█' * filled + '▒' * (18 - filled) + "▏"
            
            line_content = f"{col}{msg:<30} {VAL}{current_pct:3}% {bar}{R}"
            clean_content = strip_ansi(line_content)
            pad_left = (width - len(clean_content)) // 2
            pad_right = width - len(clean_content) - pad_left
            
            sys.stdout.write(f"\r{c_border}║{R}{' ' * pad_left}{line_content}{' ' * pad_right}{c_border}║{R}")
            sys.stdout.flush()
            time.sleep(0.015)
            
        time.sleep(0.08)
        
    print()
    success_msg = f"{Fore.LIGHTGREEN_EX}★ IND SUDO MODDER ACTIVATED SUCCESSFULLY ★{R}"
    clean_success = strip_ansi(success_msg)
    pad_left = (width - len(clean_success)) // 2
    pad_right = width - len(clean_success) - pad_left
    print(f"{c_border}║{R}{' ' * pad_left}{success_msg}{' ' * pad_right}{c_border}║{R}")
    print(bot)
    time.sleep(0.8)
    clear_screen()

# ========== DYNAMIC INTERFACE DRAWING ==========
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_success_box(account_data, count, total):
    uid = account_data.get('uid', 'N/A')
    pwd = account_data.get('password', 'N/A')
    name = account_data.get('name', 'N/A')
    aid = account_data.get('account_id', 'N/A')
    
    col_label = get_random_color()
    lines = [
        f"{col_label}UID        :{R} {VAL}{uid}{R}",
        f"{col_label}PASSWORD   :{R} {VAL}{pwd}{R}",
        f"{col_label}NAME       :{R} {VAL}{name}{R}",
        f"{col_label}ACCOUNT ID :{R} {HIGHLIGHT}{aid}{R}",
        f"[CENTER]{gradient_progress_bar(count, total, 25)}"
    ]
    title = f"{TIT}ACCOUNT GENERATED {count}/{total}{R}"
    print_premium_box(title, lines)
    print()

def print_summary(total, rare, couples, elapsed):
    lines = [
        f" {LBL_BLUE}Accounts Generated :{R} {VAL}{total}{R}",
        f" {LBL_CYAN}Rare Found        :{R} {VAL}{rare}{R}",
        f" {LBL_BLUE}Couples Pairs     :{R} {VAL}{couples}{R}",
        f" {LBL_CYAN}Time Elapsed      :{R} {VAL}{elapsed:.2f}s{R}"
    ]
    title = f"{TIT}GENERATION SUMMARY{R}"
    print_premium_box(title, lines)

# ========== FIXED BACKGROUND SPINNER AND TITLE CHANGER ==========
def animated_spinner(stop_event):
    spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    idx = 0
    while not stop_event.is_set():
        sym = spinner_chars[idx % len(spinner_chars)]
        idx += 1
        try:
            elapsed = time.time() - START_TIME if START_TIME > 0 else 0
            stats_title = f"JXE OB54 | Gen: {SUCCESS_COUNTER} | Rare: {RARE_COUNTER} | Couples: {COUPLES_COUNTER} | {elapsed:.1f}s {sym}"
            if os.name == 'nt':
                import ctypes
                ctypes.windll.kernel32.SetConsoleTitleW(stats_title)
            else:
                sys.stdout.write(f"\x1b]2;{stats_title}\x07")
                sys.stdout.flush()
        except:
            pass
        time.sleep(0.1)

# ========== NEW CUSTOM ASCII BANNER ==========
def animated_banner():
    c1 = get_random_color()
    c2 = get_random_color()

    banner_lines = [
        "███████╗██╗   ██╗██████╗  ██████╗",
        "██╔════╝██║   ██║██╔══██╗██╔═══██╗",
        "███████╗██║   ██║██║  ██║██║   ██║",
        "╚════██║██║   ██║██║  ██║██║   ██║",
        "███████║╚██████╔╝██████╔╝╚██████╔╝",
        "╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝ ",
    ]
    for line in banner_lines:
        col = c1 if line.strip().startswith("_") or line.strip().startswith("\\") else c2
        print(f"                {col}{line}{R}")
    print(f"{get_random_color()}{'='*54}{R}")

# ========== SYSTEM NAVIGATION FLOWS ==========
def main_menu():
    ultra_premium_loading_screen()
    while True:
        clear_screen()
        animated_banner()
        title = f"{TIT}SUDO MODDER GUEST GEN{R}"
        options = [
            f"  {VAL}1{R}  {get_random_color()}>{R}  {TIT}Generate Accounts{R}",
            f"  {VAL}2{R}  {get_random_color()}>{R}  {TIT}View Saved Accounts{R}",
            f"  {VAL}3{R}  {get_random_color()}>{R}  {TIT}About{R}",
            f"  {VAL}0{R}  {get_random_color()}>{R}  {TIT}Exit{R}",
        ]
        print_premium_box(title, options)
        try:
            choice = premium_input("Select Menu Option")
            if choice == "1": generate_accounts_flow()
            elif choice == "2": view_saved_accounts()
            elif choice == "3": about_section()
            elif choice == "0": safe_exit()
        except KeyboardInterrupt: safe_exit()

def generate_accounts_flow():
    global SUCCESS_COUNTER, RARE_COUNTER, COUPLES_COUNTER, RARITY_SCORE_THRESHOLD, START_TIME, EXIT_FLAG
    EXIT_FLAG = False
    regions_list = [r for r in REGION_LANG.keys() if r != "BR"]
    clear_screen()

    title = f"{TIT}SELECT REGION / MODE{R}"
    region_lines = []
    for i, r in enumerate(regions_list, 1):
        region_lines.append(f" {VAL}{i:2}){R} {LBL_BLUE}{r:<10}{R}")
    ghost_num = len(regions_list) + 1
    region_lines.append(f" {VAL}{ghost_num:2}){R} {LBL_CYAN}GHOST Mode{R}")
    region_lines.append(f" {VAL}00){R} {LBL_BLUE}Back{R}")
    region_lines.append(f" {VAL}000){R} {LBL_CYAN}Exit{R}")
    print_premium_box(title, region_lines)

    selected_region = None
    is_ghost = False
    while True:
        try:
            choice = premium_input("Choose Option / Region Name")
            if choice == "00": return
            elif choice == "000": safe_exit()
            elif choice.isdigit():
                num = int(choice)
                if 1 <= num <= len(regions_list):
                    selected_region = regions_list[num-1]; break
                elif num == len(regions_list) + 1:
                    selected_region = "BR"; is_ghost = True; break
            else:
                if choice.upper() in regions_list:
                    selected_region = choice.upper(); break
                elif choice.upper() == "GHOST":
                    selected_region = "BR"; is_ghost = True; break
        except: pass

    clear_screen()
    set_title = f"{TIT}GENERATION SETTINGS{R}"
    print_premium_box(set_title, [])

    while True:
        try:
            account_count = int(premium_input("Total Accounts to Create"))
            if account_count > 0: break
        except: pass
    while True:
        account_name = premium_input("Name Prefix")
        if account_name: break
    while True:
        password_prefix = premium_input("Password Prefix")
        if password_prefix: break
    while True:
        try:
            rarity_threshold = int(premium_input("Rarity Threshold (1-15) [Default: 8]") or "8")
            if 1 <= rarity_threshold <= 15:
                RARITY_SCORE_THRESHOLD = rarity_threshold; break
        except: pass
    
    print(f"\n{LBL_CYAN}⚡ ULTRA SPEED MODE: High thread counts increase execution speed.{R}")
    while True:
        try:
            thread_count = int(premium_input("Thread Pool Count [Default: 250]") or "250")
            if thread_count > 0: break
        except: pass

    SUCCESS_COUNTER = 0; RARE_COUNTER = 0; COUPLES_COUNTER = 0; START_TIME = time.time()
    print(f"\n{TIT}🚀 Dispatching {account_count} accounts with {thread_count} threads...{R}\n")
    
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(target=animated_spinner, args=(stop_spinner,), daemon=True)
    spinner_thread.start()
    
    threads = []
    for i in range(thread_count):
        t = threading.Thread(target=worker_thread, args=(selected_region, account_name, password_prefix, account_count, i+1, is_ghost))
        t.daemon = True; t.start(); threads.append(t)
    try:
        for t in threads: t.join()
    except KeyboardInterrupt:
        EXIT_FLAG = True
        for t in threads: t.join(timeout=1)
    finally:
        stop_spinner.set()
        spinner_thread.join(timeout=1)
        print("\r" + " " * 50 + "\r", end='', flush=True)
    
    elapsed = time.time() - START_TIME
    print_summary(SUCCESS_COUNTER, RARE_COUNTER, COUPLES_COUNTER, elapsed)
    premium_input("Press Enter to Return to Main Menu")

def worker_thread(region, account_name, password_prefix, total_accounts, thread_id, is_ghost=False):
    global SUCCESS_COUNTER
    while not EXIT_FLAG:
        with LOCK:
            if SUCCESS_COUNTER >= total_accounts: break
        generate_single_account(region, account_name, password_prefix, total_accounts, thread_id, is_ghost)

def generate_single_account(region, account_name, password_prefix, total_accounts, thread_id, is_ghost=False):
    global SUCCESS_COUNTER, RARE_COUNTER, COUPLES_COUNTER
    if EXIT_FLAG: return None
    with LOCK:
        if SUCCESS_COUNTER >= total_accounts: return None
    account_result = create_account(region, account_name, password_prefix, is_ghost)
    if not account_result or account_result.get("account_id", "N/A") == "N/A": return None
    account_result['thread_id'] = thread_id
    with LOCK:
        SUCCESS_COUNTER += 1
        current = SUCCESS_COUNTER
    print_success_box(account_result, current, total_accounts)
    is_rare, rtype, reason, rscore = check_rarity(account_result)
    if is_rare:
        with LOCK: RARE_COUNTER += 1
        save_rare_account(account_result, rtype, reason, rscore, is_ghost)
    is_couple, creason, partner = check_couple(account_result, thread_id)
    if is_couple and partner:
        with LOCK: COUPLES_COUNTER += 1
        save_couple_account(account_result, partner, creason, is_ghost)
    save_normal_account(account_result, "GHOST" if is_ghost else region, is_ghost)
    if account_result.get('jwt_token'):
        save_jwt_token(account_result, account_result['jwt_token'], "GHOST" if is_ghost else region, is_ghost)
    return {"account": account_result}

def view_saved_accounts():
    clear_screen()
    title = f"{TIT}SAVED ACCOUNTS STATS{R}"
    
    total_normal = 0
    total_rare = 0
    total_couples = 0
    
    for folder in [ACCOUNTS_FOLDER, GHOST_ACCOUNTS_FOLDER]:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.endswith('.json'):
                    try:
                        with open(os.path.join(folder, file), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                total_normal += len(data)
                    except:
                        pass
    
    for folder in [RARE_ACCOUNTS_FOLDER, GHOST_RARE_FOLDER]:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.endswith('.json'):
                    try:
                        with open(os.path.join(folder, file), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                total_rare += len(data)
                    except:
                        pass
    
    for folder in [COUPLES_ACCOUNTS_FOLDER, GHOST_COUPLES_FOLDER]:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.endswith('.json'):
                    try:
                        with open(os.path.join(folder, file), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                total_couples += len(data)
                    except:
                        pass
    
    lines = [
        f" {LBL_BLUE}Normal accounts :{R} {VAL}{total_normal}{R}",
        f" {LBL_CYAN}Rare accounts   :{R} {VAL}{total_rare}{R}",
        f" {LBL_BLUE}Couples pairs   :{R} {VAL}{total_couples}{R}"
    ]
    print_premium_box(title, lines)
    premium_input("Press Enter to Return to Main Menu")

def about_section():
    clear_screen()
    title = f"{TIT}PREMIUM TOOL INFORMATION{R}"
    lines = [
        f" {LBL_BLUE}Name       :{R} {VAL}RAO Account Generator{R}",
        f" {LBL_CYAN}Version    :{R} {VAL}OB54 Premium Ultra Speed{R}",
        f" {LBL_BLUE}Creator    :{R} {VAL}SUDO MODDER{R}",
        f" {LBL_CYAN}Telegram   :{R} {VAL}SUDO MODDER{R}",
        f" {LBL_BLUE}Features   :{R} {VAL}Multi-region | GHOST | Rare{R}",
        f" {LBL_CYAN}           :{R} {VAL}Couples Matching | Ultra Speed{R}",
        f" {LBL_BLUE}Optimization:{R} {VAL}Async Pipeline | Cache Indexing | Single-Call I/O{R}",
        f" {LBL_CYAN}New        :{R} {VAL}Stylish wrapping (꧁...꧂) & symbols{R}",
    ]
    print_premium_box(title, lines)
    premium_input("Press Enter to Return to Main Menu")

def safe_exit(signum=None, frame=None):
    global EXIT_FLAG
    EXIT_FLAG = True
    print(f"\n{TIT}👋 Thank you for using RAO Premium Generator{R}")
    SAVE_QUEUE.put(None) # Signal background thread to shutdown
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, safe_exit)
    signal.signal(signal.SIGTERM, safe_exit)
    try:
        main_menu()
    except KeyboardInterrupt:
        safe_exit()
