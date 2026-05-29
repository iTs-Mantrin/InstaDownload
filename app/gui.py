"""Modern GUI for InstaDownload using customtkinter."""

import os
import re
import threading
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .downloader import (
    Downloader,
    DownloadType,
    InstagramType,
    DownloadStatus,
)
from .utils import (
    is_youtube_url,
    is_instagram_url,
    is_valid_url,
    get_default_download_path,
    format_file_size,
    open_folder,
)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# ── Colors ──────────────────────────────────────────────────
BG_FRAME = "#1a1a2e" if ctk.get_appearance_mode() == "Dark" else "#f0f0f5"
ACCENT = "#e1306c"  # Instagram-ish pink


class InstaDownloadApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.title("InstaDownload — Instagram & YouTube Downloader")
        self.geometry("820x680")
        self.minsize(720, 600)

        self.download_path = get_default_download_path()
        os.makedirs(self.download_path, exist_ok=True)

        self.current_downloader: Downloader | None = None
        self.log_lines: list[str] = []

        self._build_ui()

    # ── UI Build ─────────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── Header ───────────────────────────────────────────
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 4))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="📥  InstaDownload",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            header,
            text="Instagram & YouTube Downloader",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        ).pack(side="left", pady=(6, 0))

        # ── Tab View ─────────────────────────────────────────
        self.tab_view = ctk.CTkTabview(self, corner_radius=8)
        self.tab_view.grid(row=1, column=0, sticky="ew", padx=16, pady=(8, 4))

        self.tab_youtube = self.tab_view.add("  YouTube  ")
        self.tab_instagram = self.tab_view.add("  Instagram  ")

        self._build_youtube_tab()
        self._build_instagram_tab()

        # ── Progress & Status (shared) ───────────────────────
        progress_frame = ctk.CTkFrame(self, corner_radius=8)
        progress_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(4, 4))
        progress_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(progress_frame, text="Progress", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, padx=(12, 8), pady=(10, 2), sticky="w"
        )
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=14, corner_radius=6)
        self.progress_bar.grid(row=1, column=0, columnspan=3, sticky="ew", padx=12, pady=(2, 6))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(progress_frame, text="Ready", font=ctk.CTkFont(size=11))
        self.status_label.grid(row=0, column=1, padx=(4, 8), pady=(10, 0), sticky="w")

        self.speed_label = ctk.CTkLabel(progress_frame, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self.speed_label.grid(row=0, column=2, padx=(4, 12), pady=(10, 0), sticky="e")

        # ── Download Path ────────────────────────────────────
        path_frame = ctk.CTkFrame(self, corner_radius=8)
        path_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=(4, 4))
        path_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(path_frame, text="Save to:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, padx=(12, 6), pady=10, sticky="w"
        )
        self.path_var = ctk.StringVar(value=self.download_path)
        self.path_entry = ctk.CTkEntry(
            path_frame, textvariable=self.path_var, state="readonly", height=30
        )
        self.path_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=10)

        self.browse_btn = ctk.CTkButton(
            path_frame, text="Browse", width=80, height=30, command=self._browse_path
        )
        self.browse_btn.grid(row=0, column=2, padx=(4, 6), pady=10)

        self.open_btn = ctk.CTkButton(
            path_frame, text="Open Folder", width=100, height=30, command=self._open_folder
        )
        self.open_btn.grid(row=0, column=3, padx=(0, 12), pady=10)

        # ── Log ──────────────────────────────────────────────
        log_frame = ctk.CTkFrame(self, corner_radius=8)
        log_frame.grid(row=4, column=0, sticky="nsew", padx=16, pady=(4, 12))
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 0))
        log_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(log_header, text="Log", font=ctk.CTkFont(size=12, weight="bold")).pack(
            side="left"
        )
        self.clear_log_btn = ctk.CTkButton(
            log_header, text="Clear", width=60, height=24, font=ctk.CTkFont(size=11),
            command=self._clear_log, fg_color="transparent", border_width=1,
            text_color=("gray20", "gray80"),
        )
        self.clear_log_btn.pack(side="right")

        self.log_text = ctk.CTkTextbox(log_frame, wrap="word", font=ctk.CTkFont(size=11))
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))
        self.log_text.configure(state="disabled")

    # ── YouTube Tab ─────────────────────────────────────────

    def _build_youtube_tab(self):
        self.tab_youtube.grid_columnconfigure(1, weight=1)

        # URL
        ctk.CTkLabel(self.tab_youtube, text="YouTube URL:", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, padx=(16, 8), pady=(20, 6), sticky="w"
        )
        self.yt_url = ctk.CTkEntry(
            self.tab_youtube, placeholder_text="https://youtube.com/watch?v=..."
        )
        self.yt_url.grid(row=0, column=1, columnspan=3, sticky="ew", padx=(0, 16), pady=(20, 6))

        # Download type
        self.yt_dl_type = ctk.StringVar(value="video")
        ctk.CTkLabel(self.tab_youtube, text="Type:", font=ctk.CTkFont(size=13)).grid(
            row=1, column=0, padx=(16, 8), pady=(6, 6), sticky="w"
        )
        type_frame = ctk.CTkFrame(self.tab_youtube, fg_color="transparent")
        type_frame.grid(row=1, column=1, columnspan=3, sticky="w", padx=(0, 16), pady=(6, 6))
        ctk.CTkRadioButton(type_frame, text="Video (MP4)", variable=self.yt_dl_type,
                           value="video", command=self._on_yt_type_change).pack(side="left", padx=(0, 16))
        ctk.CTkRadioButton(type_frame, text="Audio (MP3)", variable=self.yt_dl_type,
                           value="audio", command=self._on_yt_type_change).pack(side="left")

        # Quality
        ctk.CTkLabel(self.tab_youtube, text="Quality:", font=ctk.CTkFont(size=13)).grid(
            row=2, column=0, padx=(16, 8), pady=(6, 6), sticky="w"
        )
        self.yt_quality = ctk.CTkOptionMenu(
            self.tab_youtube,
            values=["Highest", "1080p", "720p", "480p", "360p"],
            width=120,
        )
        self.yt_quality.grid(row=2, column=1, sticky="w", padx=(0, 16), pady=(6, 6))
        self.yt_quality.set("Highest")

        # Audio quality label (hidden initially)
        self.yt_audio_label = ctk.CTkLabel(
            self.tab_youtube, text="MP3 192 kbps",
            font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.yt_audio_label.grid(row=2, column=2, sticky="w", padx=(0, 16), pady=(6, 6))
        self.yt_audio_label.grid_remove()

        # Download button
        self.yt_dl_btn = ctk.CTkButton(
            self.tab_youtube,
            text="⬇  Download YouTube",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._download_youtube,
        )
        self.yt_dl_btn.grid(row=3, column=0, columnspan=4, padx=80, pady=(16, 20), sticky="ew")

        # Info label
        self.yt_info = ctk.CTkLabel(
            self.tab_youtube, text="",
            font=ctk.CTkFont(size=11), text_color="gray", wraplength=600
        )
        self.yt_info.grid(row=4, column=0, columnspan=4, padx=16, pady=(0, 10))

    def _on_yt_type_change(self):
        if self.yt_dl_type.get() == "audio":
            self.yt_quality.grid_remove()
            self.yt_audio_label.grid()
            self.yt_dl_btn.configure(text="⬇  Download Audio (MP3)")
        else:
            self.yt_audio_label.grid_remove()
            self.yt_quality.grid()
            self.yt_dl_btn.configure(text="⬇  Download YouTube")

    # ── Instagram Tab ───────────────────────────────────────

    def _build_instagram_tab(self):
        self.tab_instagram.grid_columnconfigure(1, weight=1)
        self.tab_instagram.grid_rowconfigure(7, weight=1)

        # ── Single URL download section ──────────────────────

        # URL
        ctk.CTkLabel(self.tab_instagram, text="Instagram URL:", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, padx=(16, 8), pady=(20, 6), sticky="w"
        )
        self.ig_url = ctk.CTkEntry(
            self.tab_instagram, placeholder_text="https://www.instagram.com/p/... or /reel/... or /stories/..."
        )
        self.ig_url.grid(row=0, column=1, columnspan=3, sticky="ew", padx=(0, 16), pady=(20, 6))

        # Content type
        ctk.CTkLabel(self.tab_instagram, text="Type:", font=ctk.CTkFont(size=13)).grid(
            row=1, column=0, padx=(16, 8), pady=(12, 12), sticky="w"
        )
        self.ig_type = ctk.StringVar(value="post")
        type_frame = ctk.CTkFrame(self.tab_instagram, fg_color="transparent")
        type_frame.grid(row=1, column=1, columnspan=3, sticky="w", padx=(0, 16), pady=(12, 12))
        ctk.CTkRadioButton(type_frame, text="Post / Reel", variable=self.ig_type,
                           value="post").pack(side="left", padx=(0, 16))
        ctk.CTkRadioButton(type_frame, text="Story", variable=self.ig_type,
                           value="story").pack(side="left")

        # Download button
        self.ig_dl_btn = ctk.CTkButton(
            self.tab_instagram,
            text="⬇  Download Instagram",
            height=40,
            fg_color=ACCENT,
            hover_color="#c62e5c",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._download_instagram,
        )
        self.ig_dl_btn.grid(row=2, column=0, columnspan=4, padx=80, pady=(16, 12), sticky="ew")

        # Info label
        self.ig_info = ctk.CTkLabel(
            self.tab_instagram, text="",
            font=ctk.CTkFont(size=11), text_color="gray", wraplength=600
        )
        self.ig_info.grid(row=3, column=0, columnspan=4, padx=16, pady=(0, 4))

        # ── Separator ────────────────────────────────────────
        sep = ctk.CTkFrame(self.tab_instagram, height=2, fg_color=("gray70", "gray30"))
        sep.grid(row=4, column=0, columnspan=4, sticky="ew", padx=16, pady=(6, 8))

        # ── User search section ──────────────────────────────
        ctk.CTkLabel(
            self.tab_instagram, text="🔍  Search by Username",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=5, column=0, columnspan=4, padx=16, pady=(0, 4), sticky="w")

        # Username entry + search button
        self.ig_username = ctk.CTkEntry(
            self.tab_instagram, placeholder_text="instagram_username"
        )
        self.ig_username.grid(row=6, column=0, columnspan=2, sticky="ew", padx=(16, 4), pady=(4, 6))

        self.ig_search_btn = ctk.CTkButton(
            self.tab_instagram, text="Search", width=80, height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ACCENT, hover_color="#c62e5c",
            command=self._search_instagram_user,
        )
        self.ig_search_btn.grid(row=6, column=2, padx=(0, 4), pady=(4, 6))

        self.ig_search_status = ctk.CTkLabel(
            self.tab_instagram, text="",
            font=ctk.CTkFont(size=11), text_color="gray"
        )
        self.ig_search_status.grid(row=6, column=3, padx=(0, 16), pady=(4, 6), sticky="w")

        # Results list
        self.ig_results = ctk.CTkScrollableFrame(
            self.tab_instagram, corner_radius=6,
        )
        self.ig_results.grid(row=7, column=0, columnspan=4, sticky="nsew", padx=16, pady=(0, 12))

    # ── Download Logic ───────────────────────────────────────

    def _update_progress(self, ds: DownloadStatus):
        """Called from download thread — schedule GUI update."""

        def _update():
            if ds.status == "downloading":
                self.progress_bar.set(ds.percent / 100.0)
                pct = f"{ds.percent:.1f}%"
                speed = ds.speed or ""
                eta = ds.eta or ""
                self.status_label.configure(text=f"Downloading... {pct}")
                self.speed_label.configure(text=f"{speed}  •  ETA {eta}" if speed else "")
            elif ds.status == "processing":
                self.status_label.configure(text="Processing...")
                self.speed_label.configure(text="")
            elif ds.status == "done":
                self.progress_bar.set(1.0)
                self.status_label.configure(text="✅ Download complete!")
                self.speed_label.configure(text="")
                self._enable_buttons()
                self._log(f"Download completed successfully → {self.download_path}")
            elif ds.status == "error":
                err = ds.error_msg
                # Friendlier message for common auth issues
                if "cookies" in err.lower() or "bot" in err.lower() or "sign in" in err.lower():
                    hint = ("Auth required. Try: run with your browser open, "
                            "or use yt-dlp's --cookies-from-browser option.")
                    self.status_label.configure(text=f"❌ Auth error")
                    self._log(f"Auth required. {hint}")
                else:
                    self.status_label.configure(text=f"❌ Error")
                self.speed_label.configure(text="")
                self._enable_buttons()
                self._log(f"ERROR: {err}")

        self.after(0, _update)

    def _download_youtube(self):
        url = self.yt_url.get().strip()
        if not is_valid_url(url) or not is_youtube_url(url):
            messagebox.showwarning("Invalid URL", "Please enter a valid YouTube URL.")
            return

        self._disable_buttons()
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting download...")
        self.speed_label.configure(text="")
        self._log(f"YouTube: {url}")

        dl_type = DownloadType.VIDEO if self.yt_dl_type.get() == "video" else DownloadType.AUDIO
        quality = self.yt_quality.get()

        self.current_downloader = Downloader(
            download_path=self.download_path,
            progress_callback=self._update_progress,
        )
        self.current_downloader.download_youtube(url, dl_type, quality)

    def _download_instagram(self):
        url = self.ig_url.get().strip()
        if not is_valid_url(url) or not is_instagram_url(url):
            messagebox.showwarning("Invalid URL", "Please enter a valid Instagram URL.")
            return

        self._disable_buttons()
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting download...")
        self.speed_label.configure(text="")
        self._log(f"Instagram: {url}")

        ig_type = InstagramType.POST_REEL if self.ig_type.get() == "post" else InstagramType.STORY

        self.current_downloader = Downloader(
            download_path=self.download_path,
            progress_callback=self._update_progress,
        )
        self.current_downloader.download_instagram(url, ig_type)

    # ── Instagram User Search ─────────────────────────────────

    def _search_instagram_user(self):
        """Fetch media items for an Instagram username in a background thread."""
        username = self.ig_username.get().strip()
        if not username:
            messagebox.showwarning("Empty", "Please enter an Instagram username.")
            return

        # Clear previous results
        for w in self.ig_results.winfo_children():
            w.destroy()

        self.ig_search_btn.configure(state="disabled", text="Searching...")
        self.ig_search_status.configure(text="Fetching...")
        self._log(f"Searching Instagram user: @{username}")

        def _run():
            try:
                items, error = Downloader.list_user_media(username)
                self.after(0, self._display_user_results, items, username, error)
            except Exception as e:
                self.after(0, self._search_error, str(e))

        threading.Thread(target=_run, daemon=True).start()

    def _display_user_results(self, items: list[dict], username: str, error: str = ""):
        """Populate the results scrollable frame with media cards."""
        self.ig_search_btn.configure(state="normal", text="Search")
        self.ig_search_status.configure(text="")

        # Clear any previous results
        for w in self.ig_results.winfo_children():
            w.destroy()

        if not items:
            # Log the actual yt-dlp error if we have one
            if error:
                self._log(f"User @{username} search failed: {error}")

            help_text = (
                "Could not fetch posts for this user.\n\n"
                "Instagram's profile extractor is currently disabled in yt-dlp.\n\n"
            )

            if error:
                help_text += (
                    f"yt-dlp error:\n  {error}\n\n"
                )

            help_text += (
                "Options:\n"
                "  • Use the single URL method above — paste each\n"
                "    Instagram post/reel URL directly and click Download\n"
                "  • Login to Instagram in Chrome, then enable cookies\n"
                "    in yt-dlp's settings for profile search to work\n"
                "  • This is an upstream yt-dlp limitation — report at\n"
                "    github.com/yt-dlp/yt-dlp/issues"
            )

            ctk.CTkLabel(
                self.ig_results,
                text=help_text,
                font=ctk.CTkFont(size=12),
                text_color="gray",
                justify="left",
                wraplength=500,
            ).pack(padx=20, pady=30)
            if not error:
                self._log(f"User @{username}: no items found (Instagram blocking)")
            return

        self._log(f"Found {len(items)} items for @{username}")

        # Header count
        ctk.CTkLabel(
            self.ig_results,
            text=f"@{username} — {len(items)} post(s)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray20", "gray80"),
        ).pack(anchor="w", padx=8, pady=(6, 4))

        # Add a card for each item
        for idx, item in enumerate(items):
            self._add_result_card(item, idx)

    def _add_result_card(self, item: dict, idx: int):
        """Build a single result card with title and download button."""
        card = ctk.CTkFrame(self.ig_results, corner_radius=6)
        card.pack(fill="x", padx=6, pady=3)

        title = item.get("title", "Untitled")
        url = item.get("url", "")
        item_id = item.get("id", "")

        # Show a short ID fallback if title is generic
        display = title
        if display == "Untitled" and item_id:
            display = f"Post {item_id}"

        # Truncate for display
        if len(display) > 65:
            display = display[:62] + "..."

        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text=f"{idx + 1}.  {display}",
            font=ctk.CTkFont(size=12),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(10, 6), pady=8)

        ctk.CTkButton(
            card,
            text="⬇  Download",
            width=100,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=ACCENT,
            hover_color="#c62e5c",
            command=lambda u=url: self._download_user_item(u),
        ).grid(row=0, column=1, padx=(4, 10), pady=6)

    def _download_user_item(self, url: str):
        """Download a single item from the user search results."""
        if not url:
            self._log("ERROR: No URL for this item")
            return

        self._log(f"Downloading user item: {url}")
        self._disable_buttons()
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting download...")
        self.speed_label.configure(text="")

        self.current_downloader = Downloader(
            download_path=self.download_path,
            progress_callback=self._update_progress,
        )
        self.current_downloader.download_instagram(url, InstagramType.POST_REEL)

    def _search_error(self, error: str):
        """Handle search failure."""
        self.ig_search_btn.configure(state="normal", text="Search")
        self.ig_search_status.configure(text="Error")
        self._log(f"Search error: {error}")
        ctk.CTkLabel(
            self.ig_results,
            text=f"Search failed.\n{error}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            wraplength=500,
        ).pack(padx=20, pady=30)

    # ── Helpers ──────────────────────────────────────────────

    def _disable_buttons(self):
        self.yt_dl_btn.configure(state="disabled")
        self.ig_dl_btn.configure(state="disabled")
        self.browse_btn.configure(state="disabled")
        self.ig_search_btn.configure(state="disabled")

    def _enable_buttons(self):
        self.yt_dl_btn.configure(state="normal")
        self.ig_dl_btn.configure(state="normal")
        self.browse_btn.configure(state="normal")
        self.ig_search_btn.configure(state="normal")

    def _browse_path(self):
        path = filedialog.askdirectory(initialdir=self.download_path)
        if path:
            self.download_path = path
            self.path_var.set(path)
            self._log(f"Download path changed: {path}")

    def _open_folder(self):
        if os.path.isdir(self.download_path):
            open_folder(self.download_path)

    def _log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}"
        self.log_lines.append(line)
        self.log_text.configure(state="normal")
        self.log_text.insert("end", line + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self.log_lines.clear()


def run():
    app = InstaDownloadApp()
    app.mainloop()
