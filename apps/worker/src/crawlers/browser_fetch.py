"""Fetch page HTML via Playwright (for JS-rendered pages). Browser is reused per process."""

import logging
from typing import Any

logger = logging.getLogger(__name__)

_browser: Any = None
_playwright: Any = None

BROWSER_TIMEOUT_MS = 30_000
BODY_SELECTOR = "article, main, [role='main']"
BODY_WAIT_TIMEOUT_MS = 15_000


def _get_browser():
    global _browser, _playwright
    if _browser is not None:
        return _browser
    try:
        from playwright.sync_api import sync_playwright
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(headless=True)
        return _browser
    except Exception as e:
        logger.warning("Playwright browser start failed: %s", e)
        return None


def fetch_page_with_browser(url: str, timeout_ms: int = BROWSER_TIMEOUT_MS) -> str:
    """
    Load url in headless Chromium, wait for main content if possible, return page HTML.
    Returns empty string on failure. Reuses a single browser instance per process.
    """
    browser = _get_browser()
    if browser is None:
        return ""
    try:
        context = browser.new_context(
            user_agent="MultiAssetInvestWorker/1.0",
            ignore_https_errors=True,
        )
        page = context.new_page()
        try:
            page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            try:
                page.wait_for_selector(BODY_SELECTOR, timeout=BODY_WAIT_TIMEOUT_MS)
            except Exception:
                pass
            return page.content()
        finally:
            page.close()
            context.close()
    except Exception as e:
        logger.warning("Browser fetch failed for %s: %s", url, e)
        return ""


def close_browser() -> None:
    """Close the shared browser; call on process shutdown if desired."""
    global _browser, _playwright
    if _browser:
        try:
            _browser.close()
        except Exception:
            pass
        _browser = None
    if _playwright:
        try:
            _playwright.stop()
        except Exception:
            pass
        _playwright = None
