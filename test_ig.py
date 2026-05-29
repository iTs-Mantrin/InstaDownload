"""Test: Instagram Ajax endpoint with POST."""
import json
import re
import urllib.request
import urllib.error
import ssl

USERNAME = "nasa"
url = f"https://www.instagram.com/{USERNAME}/"
ctx = ssl.create_default_context()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5",
}

# Get initial page, CSRF, and extract XHR endpoint
print("Step 1: Get initial page and XHR endpoint...")
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
    html = resp.read().decode("utf-8", errors="replace")
    cookies = resp.headers.get_all("Set-Cookie") or []
    csrf = ""
    all_cookies = {}
    for c in cookies:
        parts = c.split(";")[0]
        if "=" in parts:
            k, v = parts.split("=", 1)
            all_cookies[k] = v
            if k == "csrftoken":
                csrf = v
    print(f"CSRF: {csrf[:20]}...")
    print(f"Cookies: mid={all_cookies.get('mid','')[:10]}... ig_nrcb={all_cookies.get('ig_nrcb','')[:10]}...")

    # Find XHR endpoint from page
    xhr_matches = re.findall(
        r'{"u":"([^"]+)","e":"(\d+)","s":"XPolarisProfileController"[^}]*}',
        html
    )
    if xhr_matches:
        endpoint = xhr_matches[0][0].replace("\\/", "/")
        print(f"XHR Endpoint: {endpoint}")
    else:
        endpoint = None
        print("No XHR endpoint found")

# Step 2: POST to Polaris XHR endpoint
if endpoint:
    print(f"\nStep 2: POST to {endpoint}...")
    try:
        full_url = f"https://www.instagram.com{endpoint}"
        post_data = json.dumps({
            "variables": json.dumps({"after": None, "first": 12})
        }).encode()

        ajax_headers = {
            **headers,
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrf,
            "X-FB-LSD": re.search(r'"LSD",\[\],{"token":"([^"]+)"}', html).group(1) if re.search(r'"LSD",\[\],{"token":"([^"]+)"}', html) else "",
            "Referer": url,
            "Origin": "https://www.instagram.com",
        }
        if all_cookies:
            ajax_headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in all_cookies.items())

        # Try GET first
        print("  Trying GET...")
        get_req = urllib.request.Request(full_url, headers=ajax_headers)
        with urllib.request.urlopen(get_req, context=ctx, timeout=15) as r:
            print(f"  GET Status: {r.status}")
            raw = r.read()
            print(f"  Response (first 500): {raw.decode('utf-8',errors='replace')[:500]}")

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        print(f"  HTTP {e.code}: {body}")

    # Try Facebook's Ajax format
    try:
        print("\n  Trying Facebook Ajax POST...")
        fb_endpoint = endpoint.split("?")[0]
        fb_params = endpoint.split("?")[1] if "?" in endpoint else ""
        fb_data = f"__user=0&__a=1&__comet_req=7&__dyn=7xe6E5Z3W2Fz81bxPS5&__req=1&__hs=19003.HYP:instagram_www_pkg.2.1..0.0&__hsi=0&__csr=&__ajax__=1"

        post_req = urllib.request.Request(
            f"https://www.instagram.com{fb_endpoint}",
            data=fb_data.encode(),
            headers={**ajax_headers, "Content-Type": "application/x-www-form-urlencoded"},
            method="POST"
        )
        with urllib.request.urlopen(post_req, context=ctx, timeout=15) as r:
            print(f"  POST Status: {r.status}")
            raw = r.read()
            text = raw.decode("utf-8", errors="replace")
            print(f"  Response (first 500): {text[:500]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        print(f"  HTTP {e.code}: {body}")
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")
