import asyncio
from urllib.parse import urljoin

from playwright.async_api import async_playwright


class WebScraperEngine:
    def __init__(self, headless: bool = True):
        self.headless = headless

    async def scrape_quotes(self, limit: int = 5) -> list[dict[str, str]]:
        """
        Scrapes quote data as a standardized test pipeline target.
        """
        if limit < 1:
            raise ValueError("limit must be at least 1.")

        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            try:
                page = await browser.new_page()
                await page.goto(
                    "https://quotes.toscrape.com/",
                    wait_until="domcontentloaded",
                )

                while len(results) < limit:
                    quotes = await page.query_selector_all(".quote")
                    for quote in quotes:
                        if len(results) >= limit:
                            break

                        text_el = await quote.query_selector(".text")
                        author_el = await quote.query_selector(".author")
                        tags_els = await quote.query_selector_all(".tag")

                        text = await text_el.inner_text() if text_el else ""
                        author = await author_el.inner_text() if author_el else ""
                        tags = [await tag.inner_text() for tag in tags_els]

                        results.append({
                            "quote": text.replace("“", "").replace("”", ""),
                            "author": author,
                            "tags": ", ".join(tags),
                        })

                    if len(results) >= limit:
                        break

                    next_link = await page.query_selector("li.next a")
                    if next_link is None:
                        break

                    next_url = urljoin(
                        page.url,
                        await next_link.get_attribute("href") or "",
                    )
                    await page.goto(next_url, wait_until="domcontentloaded")
            finally:
                await browser.close()

        return results


# Verification Test
if __name__ == "__main__":
    scraper = WebScraperEngine(headless=True)
    data = asyncio.run(scraper.scrape_quotes(limit=3))
    print("Scraped Data Sample:", data)