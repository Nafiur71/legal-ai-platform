import os
import shutil
import asyncio
import subprocess
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self, max_concurrent: int = 3):
        self._max_concurrent = max_concurrent
        self._semaphore = None
        self.browser_exe = self._detect_browser()
        if self.browser_exe:
            logger.info(f"PDFService initialized with browser: {self.browser_exe}")
        else:
            logger.warning("PDFService: No browser executable found initially. Will retry on demand.")

    def _detect_browser(self) -> str | None:
        # 1. Environment variable override
        for env_var in ["CHROME_BIN", "CHROMIUM_PATH", "PUPPETEER_EXECUTABLE_PATH"]:
            val = os.getenv(env_var)
            if val and os.path.exists(val):
                return val

        # 2. Check PATH
        for bin_name in ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome", "msedge"]:
            which_p = shutil.which(bin_name)
            if which_p and os.path.exists(which_p):
                return which_p

        # 3. Known Linux/Docker paths
        linux_paths = [
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/snap/bin/chromium",
            "/usr/local/bin/chromium"
        ]
        for p in linux_paths:
            if os.path.exists(p):
                return p

        # 4. Known Windows paths
        win_paths = [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
            os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'),
            os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe'),
            os.path.expandvars(r'%PROGRAMFILES%\Google\Chrome\Application\chrome.exe'),
        ]
        for p in win_paths:
            if os.path.exists(p):
                return p

        # 5. Known macOS paths
        mac_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        ]
        for p in mac_paths:
            if os.path.exists(p):
                return p

        return None

    def _get_semaphore(self) -> asyncio.Semaphore:
        if self._semaphore is None:
            # Bounded semaphore to prevent browser process storms under high traffic
            self._semaphore = asyncio.Semaphore(self._max_concurrent)
        return self._semaphore

    def _render_sync(self, html_content: str) -> bytes:
        browser = self.browser_exe or self._detect_browser()
        if not browser:
            raise RuntimeError(
                "PDF generation engine could not locate Chromium/Chrome on this server. "
                "Ensure chromium is installed in the Linux environment."
            )
        self.browser_exe = browser

        tmpdir = tempfile.mkdtemp(prefix="legal_pdf_")
        pdf_bytes = None
        try:
            html_file = Path(tmpdir) / "document.html"
            pdf_file = Path(tmpdir) / "document.pdf"
            profile_dir = Path(tmpdir) / "chrome-profile"
            profile_dir.mkdir(exist_ok=True)

            html_file.write_text(html_content, encoding="utf-8")

            cmd = [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-software-rasterizer",
                "--no-margins",
                f"--user-data-dir={str(profile_dir)}",
                "--disable-background-networking",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-breakpad",
                "--disable-client-side-phishing-detection",
                "--disable-component-update",
                "--disable-default-apps",
                "--disable-dev-tools",
                "--disable-domain-reliability",
                "--disable-extensions",
                "--disable-features=AudioServiceOutOfProcess,IsolateOrigins,site-per-process",
                "--disable-hang-monitor",
                "--disable-ipc-flooding-protection",
                "--disable-popup-blocking",
                "--disable-prompt-on-repost",
                "--disable-renderer-backgrounding",
                "--disable-sync",
                "--disable-translate",
                "--metrics-recording-only",
                "--no-first-run",
                "--no-zygote",
                "--run-all-compositor-stages-before-draw",
                "--safebrowsing-disable-auto-update",
                "--mute-audio",
                f"--print-to-pdf={str(pdf_file)}",
                str(html_file)
            ]

            proc = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=35
            )
            if pdf_file.exists() and pdf_file.stat().st_size > 0:
                pdf_bytes = pdf_file.read_bytes()
            else:
                stderr = proc.stderr.decode(errors="ignore") if proc.stderr else "Empty PDF output"
                raise RuntimeError(f"PDF file was not created or is empty. Details: {stderr}")
        except subprocess.CalledProcessError as e:
            err_text = e.stderr.decode(errors="ignore") if e.stderr else str(e)
            logger.error(f"Chromium PDF generation process exited with error: {err_text}")
            raise RuntimeError(f"Chromium PDF process failed: {err_text[:200]}")
        except Exception as e:
            logger.error(f"Browser PDF generation error: {e}")
            raise RuntimeError(f"PDF generation error: {str(e)}")
        finally:
            # Bulletproof cleanup with ignore_errors=True:
            # Prevents [Errno 39] Directory not empty: 'Default' when Chromium still holds socket/cache handles
            try:
                shutil.rmtree(tmpdir, ignore_errors=True)
            except Exception:
                pass

        if pdf_bytes:
            return pdf_bytes
        raise RuntimeError("PDF generation failed: no output data produced.")

    def convert_html_to_pdf(self, html_content: str) -> bytes:
        return self._render_sync(html_content)

    async def convert_html_to_pdf_async(self, html_content: str) -> bytes:
        semaphore = self._get_semaphore()
        async with semaphore:
            return await asyncio.to_thread(self._render_sync, html_content)

    async def warm_up_async(self):
        """Pre-warm Chromium on server startup so the first export is instantaneous."""
        try:
            logger.info("PDFService: Warming up browser engine...")
            dummy = "<!DOCTYPE html><html><body><h1>Warmup</h1></body></html>"
            await self.convert_html_to_pdf_async(dummy)
            logger.info("PDFService: Headless browser is warm and ready.")
        except Exception as e:
            logger.warning(f"PDFService warmup skipped: {e}")

pdf_service = PDFService()
