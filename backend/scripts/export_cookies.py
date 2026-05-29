"""Export browser cookies for yt-dlp (YouTube/Instagram).

Chrome/Edge lock their cookie database while running on Windows.
This script detects if the browser is open and either:
  - Warns and exits (safe mode)
  - Closes it for you (--force mode)
  - Uses browser-cookie3 (--no-close) — works WITHOUT closing browser

Usage:
  python scripts/export_cookies.py               # warns if browser open
  python scripts/export_cookies.py --force        # closes Chrome for you
  python scripts/export_cookies.py --browser edge # use Edge instead
  python scripts/export_cookies.py --no-close     # use browser-cookie3 (no close needed)
  python scripts/export_cookies.py --verify       # check existing cookies

Output: backend/cookies.txt (read by YT_DLP_COOKIES_FILE env var)
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


COOKIES_PATH = Path(__file__).resolve().parent.parent / "cookies.txt"


def is_running(name: str) -> bool:
    try:
        r = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {name}"],
            capture_output=True, text=True, timeout=5,
        )
        return name in r.stdout
    except Exception:
        return False


def close_browser(name: str):
    print(f"  Closing {name}...")
    r = subprocess.run(
        ["taskkill", "/F", "/IM", name],
        capture_output=True, text=True, timeout=10,
    )
    if r.returncode == 0:
        print(f"  [OK] {name} closed. Tabs will restore when reopened.")
    else:
        print(f"  [!] Could not close: {r.stderr.strip()}")


def export_cookies_ytdlp(browser: str) -> bool:
    """Export via yt-dlp --cookies-from-browser (requires browser closed on Windows)."""
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--cookies-from-browser", browser,
        "--cookies", str(COOKIES_PATH),
        "--skip-download",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    ]
    print(f"  Exporting from {browser} (via yt-dlp)...")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        print(f"  [FAIL] Export failed: {r.stderr.strip()[-200:]}")
        return False
    return True


def export_cookies_browsercookie3(browser: str) -> bool:
    """Export via browser-cookie3 library (works with browser open)."""
    print(f"  Exporting from {browser} (via browser-cookie3)...")
    try:
        import browser_cookie3
        cookiejar = getattr(browser_cookie3, browser, browser_cookie3.chrome)(cookie_file=None)
    except ImportError:
        print("  [FAIL] browser-cookie3 not installed. Run: pip install browser-cookie3")
        return False
    except Exception as e:
        print(f"  [FAIL] Could not load {browser} cookies: {e}")
        return False

    yt_domain_cookies = [c for c in cookiejar if "youtube.com" in c.domain]
    if not yt_domain_cookies:
        print("  [FAIL] No YouTube cookies found. Make sure you're logged into YouTube.")
        return False

    # Write in Netscape format
    with open(COOKIES_PATH, "w") as f:
        f.write("# Netscape HTTP Cookie File\n")
        f.write("# Exported via browser-cookie3\n\n")
        for c in yt_domain_cookies:
            domain = c.domain
            flag = "TRUE" if domain.startswith(".") else "FALSE"
            path = c.path
            secure = "TRUE" if c.secure else "FALSE"
            expires = str(int(c.expires)) if c.expires else "0"
            name = c.name
            value = c.value
            f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")

    print(f"  [OK] Exported {len(yt_domain_cookies)} YouTube cookies.")
    return True


def verify_cookies() -> bool:
    if not COOKIES_PATH.exists():
        print(f"  [FAIL] {COOKIES_PATH} not found.")
        return False
    content = COOKIES_PATH.read_text(encoding="utf-8")
    lines = [l.strip() for l in content.split("\n") if l.strip() and not l.startswith("#")]
    has_sid = any("SID" in l or "PSID" in l or "SSID" in l or "APISID" in l or "SAPISID" in l for l in lines)
    has_yt = any("youtube.com" in l for l in lines)
    print(f"  Cookies: {len(lines)} total, YouTube: [{'OK' if has_yt else 'NO'}]"
          f", Logged-in session: [{'YES' if has_sid else 'NO'}]")
    return has_sid and has_yt


def main():
    parser = argparse.ArgumentParser(description="Export browser cookies for yt-dlp")
    parser.add_argument("--force", action="store_true", help="Close browser automatically if running")
    parser.add_argument("--browser", default="chrome", choices=["chrome", "edge", "firefox", "brave", "opera"], help="Browser (default: chrome)")
    parser.add_argument("--no-close", action="store_true", help="Use browser-cookie3 (no need to close browser)")
    parser.add_argument("--verify", action="store_true", help="Check existing cookies file and exit")
    args = parser.parse_args()

    exe_map = {"chrome": "chrome.exe", "edge": "msedge.exe", "firefox": "firefox.exe", "brave": "brave.exe", "opera": "opera.exe"}

    print(f"\n  [InstaDownload Cookie Exporter]\n")

    if args.verify:
        valid = verify_cookies()
        if valid:
            print(f"  [OK] Cookies are valid (includes logged-in session).\n")
        else:
            print(f"  [FAIL] Cookies missing or incomplete. Re-export with a logged-in YouTube session.\n")
        return 0 if COOKIES_PATH.exists() else 1

    # ── Export via browser-cookie3 (--no-close) ─────────────────
    if args.no_close:
        print(f"  Using browser-cookie3 (browser can stay open)...\n")
        ok = export_cookies_browsercookie3(args.browser)
        if not ok:
            print(f"\n  [!] browser-cookie3 failed. Try without --no-close to use yt-dlp method.\n")
            return 1
        print()
        verify_cookies()
        print(f"\n  [OK] Cookies saved to: {COOKIES_PATH}")
        print(f"  Restart the backend to pick them up.\n")
        return 0

    # ── Export via yt-dlp (--cookies-from-browser) ──────────────
    browser_exe = exe_map[args.browser]
    running = is_running(browser_exe)

    if running:
        print(f"  [!] {args.browser.title()} is running. Windows locks the cookie DB while open.")
        if not args.force:
            print(f"\n  Options:")
            print(f"    1. Close {args.browser.title()} and re-run")
            print(f"    2. Run: python scripts/export_cookies.py --force")
            print(f"    3. Run: python scripts/export_cookies.py --no-close (browser-cookie3, keeps browser open)")
            return 1
        close_browser(browser_exe)

    print()
    ok = export_cookies_ytdlp(args.browser)
    if not ok:
        print(f"\n  Try: python scripts/export_cookies.py --browser edge\n")
        print(f"  Or: python scripts/export_cookies.py --no-close (uses browser-cookie3)\n")
        return 1

    print()
    verify_cookies()
    print(f"\n  [OK] Cookies saved to: {COOKIES_PATH}")
    print(f"  Restart the backend to pick them up.\n")
    return 0


if __name__ == "__main__":
    exit(main())
