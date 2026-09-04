import socket
import ssl
import time
import re
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

# نگاشت کدهای دوحرفی به نام کامل کشورها
COUNTRY_MAP = {
    # A
    "AD": "Andorra", "AE": "UAE", "AF": "Afghanistan", "AG": "Antigua and Barbuda",
    "AI": "Anguilla", "AL": "Albania", "AM": "Armenia", "AO": "Angola",
    "AQ": "Antarctica", "AR": "Argentina", "AS": "American Samoa", "AT": "Austria",
    "AU": "Australia", "AW": "Aruba", "AX": "Aland Islands", "AZ": "Azerbaijan",

    # B
    "BA": "Bosnia and Herzegovina", "BB": "Barbados", "BD": "Bangladesh", "BE": "Belgium",
    "BF": "Burkina Faso", "BG": "Bulgaria", "BH": "Bahrain", "BI": "Burundi",
    "BJ": "Benin", "BL": "Saint Barthelemy", "BM": "Bermuda", "BN": "Brunei",
    "BO": "Bolivia", "BQ": "Caribbean Netherlands", "BR": "Brazil", "BS": "Bahamas",
    "BT": "Bhutan", "BV": "Bouvet Island", "BW": "Botswana", "BY": "Belarus",
    "BZ": "Belize",

    # C
    "CA": "Canada", "CC": "Cocos Islands", "CD": "DR Congo", "CF": "Central African Republic",
    "CG": "Republic of the Congo", "CH": "Switzerland", "CI": "Ivory Coast", "CK": "Cook Islands",
    "CL": "Chile", "CM": "Cameroon", "CN": "China", "CO": "Colombia",
    "CR": "Costa Rica", "CU": "Cuba", "CV": "Cape Verde", "CW": "Curacao",
    "CX": "Christmas Island", "CY": "Cyprus", "CZ": "Czech Republic",

    # D
    "DE": "Germany", "DJ": "Djibouti", "DK": "Denmark", "DM": "Dominica",
    "DO": "Dominican Republic", "DZ": "Algeria",

    # E
    "EC": "Ecuador", "EE": "Estonia", "EG": "Egypt", "EH": "Western Sahara",
    "ER": "Eritrea", "ES": "Spain", "ET": "Ethiopia",

    # F
    "FI": "Finland", "FJ": "Fiji", "FK": "Falkland Islands", "FM": "Micronesia",
    "FO": "Faroe Islands", "FR": "France",

    # G
    "GA": "Gabon", "GB": "United Kingdom", "GD": "Grenada", "GE": "Georgia",
    "GF": "French Guiana", "GG": "Guernsey", "GH": "Ghana", "GI": "Gibraltar",
    "GL": "Greenland", "GM": "Gambia", "GN": "Guinea", "GP": "Guadeloupe",
    "GQ": "Equatorial Guinea", "GR": "Greece", "GS": "South Georgia", "GT": "Guatemala",
    "GU": "Guam", "GW": "Guinea-Bissau", "GY": "Guyana",

    # H
    "HK": "Hong Kong", "HM": "Heard Island", "HN": "Honduras", "HR": "Croatia",
    "HT": "Haiti", "HU": "Hungary",

    # I
    "ID": "Indonesia", "IE": "Ireland", "IL": "Israel", "IM": "Isle of Man",
    "IN": "India", "IO": "British Indian Ocean Territory", "IQ": "Iraq", "IR": "Iran",
    "IS": "Iceland", "IT": "Italy",

    # J
    "JE": "Jersey", "JM": "Jamaica", "JO": "Jordan", "JP": "Japan",

    # K
    "KE": "Kenya", "KG": "Kyrgyzstan", "KH": "Cambodia", "KI": "Kiribati",
    "KM": "Comoros", "KN": "Saint Kitts and Nevis", "KP": "North Korea", "KR": "South Korea",
    "KW": "Kuwait", "KY": "Cayman Islands", "KZ": "Kazakhstan",

    # L
    "LA": "Laos", "LB": "Lebanon", "LC": "Saint Lucia", "LI": "Liechtenstein",
    "LK": "Sri Lanka", "LR": "Liberia", "LS": "Lesotho", "LT": "Lithuania",
    "LU": "Luxembourg", "LV": "Latvia", "LY": "Libya",

    # M
    "MA": "Morocco", "MC": "Monaco", "MD": "Moldova", "ME": "Montenegro",
    "MF": "Saint Martin", "MG": "Madagascar", "MH": "Marshall Islands", "MK": "North Macedonia",
    "ML": "Mali", "MM": "Myanmar", "MN": "Mongolia", "MO": "Macau",
    "MP": "Northern Mariana Islands", "MQ": "Martinique", "MR": "Mauritania", "MS": "Montserrat",
    "MT": "Malta", "MU": "Mauritius", "MV": "Maldives", "MW": "Malawi",
    "MX": "Mexico", "MY": "Malaysia", "MZ": "Mozambique",

    # N
    "NA": "Namibia", "NC": "New Caledonia", "NE": "Niger", "NF": "Norfolk Island",
    "NG": "Nigeria", "NI": "Nicaragua", "NL": "Netherlands", "NO": "Norway",
    "NP": "Nepal", "NR": "Nauru", "NU": "Niue", "NZ": "New Zealand",

    # O
    "OM": "Oman",

    # P
    "PA": "Panama", "PE": "Peru", "PF": "French Polynesia", "PG": "Papua New Guinea",
    "PH": "Philippines", "PK": "Pakistan", "PL": "Poland", "PM": "Saint Pierre and Miquelon",
    "PN": "Pitcairn", "PR": "Puerto Rico", "PS": "Palestine", "PT": "Portugal",
    "PW": "Palau", "PY": "Paraguay",

    # Q
    "QA": "Qatar",

    # R
    "RE": "Reunion", "RO": "Romania", "RS": "Serbia", "RU": "Russia",
    "RW": "Rwanda",

    # S
    "SA": "Saudi Arabia", "SB": "Solomon Islands", "SC": "Seychelles", "SD": "Sudan",
    "SE": "Sweden", "SG": "Singapore", "SH": "Saint Helena", "SI": "Slovenia",
    "SJ": "Svalbard", "SK": "Slovakia", "SL": "Sierra Leone", "SM": "San Marino",
    "SN": "Senegal", "SO": "Somalia", "SR": "Suriname", "SS": "South Sudan",
    "ST": "Sao Tome and Principe", "SV": "El Salvador", "SX": "Sint Maarten", "SY": "Syria",
    "SZ": "Eswatini",

    # T
    "TC": "Turks and Caicos Islands", "TD": "Chad", "TF": "French Southern Territories", "TG": "Togo",
    "TH": "Thailand", "TJ": "Tajikistan", "TK": "Tokelau", "TL": "Timor-Leste",
    "TM": "Turkmenistan", "TN": "Tunisia", "TO": "Tonga", "TR": "Turkey",
    "TT": "Trinidad and Tobago", "TV": "Tuvalu", "TW": "Taiwan", "TZ": "Tanzania",

    # U
    "UA": "Ukraine", "UG": "Uganda", "UM": "US Outlying Islands", "US": "United States",
    "UY": "Uruguay", "UZ": "Uzbekistan",

    # V
    "VA": "Vatican City", "VC": "Saint Vincent and the Grenadines", "VE": "Venezuela", "VG": "British Virgin Islands",
    "VI": "US Virgin Islands", "VN": "Vietnam", "VU": "Vanuatu",

    # W
    "WF": "Wallis and Futuna", "WS": "Samoa",

    # Y
    "YE": "Yemen", "YT": "Mayotte",

    # Z
    "ZA": "South Africa", "ZM": "Zambia", "ZW": "Zimbabwe"
}

def is_public_ip(ip_str):
    """بررسی آی‌پی‌های معتبر و عمومی اینترنت"""
    try:
        parts = list(map(int, ip_str.split(":")[0].split(".")))
        if len(parts) != 4: return False
        if parts[0] in [0, 10, 127]: return False
        if parts[0] == 172 and (16 <= parts[1] <= 31): return False
        if parts[0] == 192 and parts[1] == 168: return False
        return True
    except Exception:
        return False

def fetch_proxies():
    """دانلود مستقیم لیست روزانه از مخزن NiREvil و استخراج تمام آی‌پی‌ها"""
    url = "https://raw.githubusercontent.com/NiREvil/vless/main/sub/ProxyIP-Daily.md"
    print(f"Fetching raw list from: {url}")
    
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw_text = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
    
    # استخراج تمام IPv4 ها
    ip_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?::\d{2,5})?\b'
    matches = re.findall(ip_pattern, raw_text)
    
    unique_candidates = set()
    for match in matches:
        if is_public_ip(match):
            target = match if ":" in match else f"{match}:443"
            unique_candidates.add(target)
            
    print(f"Extracted {len(unique_candidates)} unique candidate proxies.")
    return list(unique_candidates)

def test_proxy(target, timeout=2.5):
    """تست اختصاصی برای اطمینان از عدم وقوع ارور SSL روی سایت‌های مستقل جهانی"""
    host, port = target.split(":")
    port = int(port)
    start_time = time.time()
    
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        sock = socket.create_connection((host, port), timeout=timeout)
        
        # تست با یک دامنه جهانی (خارج از کلادفلر) جهت تضمین رد شدن پکت‌های SSL
        test_sni = "www.google.com"
        with ctx.wrap_socket(sock, server_hostname=test_sni) as ssock:
            # ارسال پکت اولیه TLS
            request = (
                f"HEAD / HTTP/1.1\r\n"
                f"Host: {test_sni}\r\n"
                f"User-Agent: Mozilla/5.0\r\n"
                f"Connection: close\r\n\r\n"
            ).encode("utf-8")
            ssock.sendall(request)
            
            # اگر سرور ارور SSL ندهد و دیتایی برگرداند، یعنی پروکسی استاندارد SNI است
            data = ssock.recv(512)
            if not data:
                return None
                
            latency = int((time.time() - start_time) * 1000)
            
        # حالا بررسی کشور از طریق کلادفلر برای تعیین لوکیشن
        sock_loc = socket.create_connection((host, port), timeout=timeout)
        with ctx.wrap_socket(sock_loc, server_hostname="speed.cloudflare.com") as ssock_loc:
            ssock_loc.sendall(b"GET /cdn-cgi/trace HTTP/1.1\r\nHost: speed.cloudflare.com\r\nConnection: close\r\n\r\n")
            loc_data = ssock_loc.recv(1024).decode("utf-8", errors="ignore")
            
            loc = None
            for line in loc_data.splitlines():
                if line.startswith("loc="):
                    loc = line.split("=")[1].strip().upper()
                    break
                    
            if loc:
                return {
                    "ip": target,
                    "loc": loc,
                    "country": COUNTRY_MAP.get(loc, loc),
                    "latency": latency
                }
    except Exception:
        pass
    return None

def main():
    candidates = fetch_proxies()
    valid_proxies = []
    
    print("Testing proxies with live TLS handshakes (50 threads)...")
    # ۵۰ پردازش همزمان جهت بررسی کل آی‌پی‌ها ظرف کمتر از ۳۰ ثانیه
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(test_proxy, ip) for ip in candidates]
        for f in as_completed(futures):
            res = f.result()
            if res:
                valid_proxies.append(res)
                
    print(f"Total alive proxies verified: {len(valid_proxies)}")
    
    # دسته‌بندی بر اساس کشور
    by_country = {}
    for p in valid_proxies:
        c = p["country"]
        if c not in by_country:
            by_country[c] = []
        by_country[c].append(p)
        
    # انتخاب فقط ۱ دونه با بهترین پینگ (کمترین Latency) برای هر کشور
    final_output = []
    for country, items in by_country.items():
        items.sort(key=lambda x: x["latency"])
        best_proxy = items[0]
        print(f"Best for {country}: {best_proxy['ip']} ({best_proxy['latency']}ms)")
        final_output.append({
            "country": country,
            "ip": best_proxy["ip"]
        })
        
    # مرتب‌سازی بر اساس نام کشور
    final_output.sort(key=lambda x: x["country"])
    
    # ذخیره فایل نهایی
    with open("fastest_proxies.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully saved {len(final_output)} country proxies to fastest_proxies.json")

if __name__ == "__main__":
    main()
