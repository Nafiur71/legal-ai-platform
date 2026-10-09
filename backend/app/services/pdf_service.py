import os
import shutil
import subprocess
import tempfile
from pathlib import Path

class PDFService:
    def __init__(self):
        self.browser_exe = self._detect_browser()

    def _detect_browser(self):
        # 1. Check environment variable override
        env_path = os.getenv("CHROME_BIN") or os.getenv("BROWSER_PATH")
        if env_path and os.path.exists(env_path):
            return env_path

        # 2. Check system PATH via shutil.which
        for name in ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "msedge"]:
            found = shutil.which(name)
            if found:
                return found

        # 3. Check known standard filesystem locations
        known_paths = [
            # Linux / Docker
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/snap/bin/chromium",
            # Windows
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            # macOS
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        ]

        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            known_paths.append(os.path.join(local_app_data, r"Google\Chrome\Application\chrome.exe"))

        for p in known_paths:
            if os.path.exists(p):
                return p

        return None

    def convert_html_to_pdf(self, html_content: str) -> bytes:
        browser = self.browser_exe or self._detect_browser()
        if not browser:
            raise RuntimeError("PDF generation engine could not find a browser (Chrome/Edge/Chromium).")

        with tempfile.TemporaryDirectory() as tmpdir:
            html_file = Path(tmpdir) / "document.html"
            pdf_file = Path(tmpdir) / "document.pdf"

            html_file.write_text(html_content, encoding="utf-8")

            cmd = [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--no-margins",
                f"--print-to-pdf={str(pdf_file)}",
                str(html_file)
            ]
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25)
                if pdf_file.exists():
                    return pdf_file.read_bytes()
            except Exception as e:
                print(f"Browser PDF generation error: {e}")

            raise RuntimeError("PDF generation engine failed to render document.")

pdf_service = PDFService()
