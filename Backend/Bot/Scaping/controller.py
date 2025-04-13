from flask import request
import aiohttp
from lxml import html
from .helper import embedd
from .pinecone_utils import storeEmbeddings
from playwright.async_api import async_playwright
import asyncio
from Bot.responses import error, success


async def are_urls_valid(urls):
    notOk = []
    print(urls)
    for url in urls:
        async with aiohttp.ClientSession() as session:
            s = await session.get(url)
            if not s.ok:
                notOk.append(url)
    return notOk


async def scraping_logic(urls):
    # url=request.form.get("url")
    print(3, urls)
    scraped_content = {}
    for url in urls:
        print(url)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=10000)
            html_content = await page.content()
        tree = html.fromstring(html_content)
        # text=tree.xpath("//p/text() | //span/text()")
        text = tree.xpath(
            "//text()[not(ancestor::style or ancestor::script or ancestor::br or ancestor::template or normalize-space(.) = '')]"
        )
        data = []
        for el in text:
            txt = el.strip()

            if not txt:
                continue

            parent = el.getparent()
            href = None
            if parent.tag == "a":
                href = parent.get("href")
            if href:
                txt += f" (View More: {href} )"
            data.append(txt)

        scraped_content[url] = data

    return scraped_content


async def scraping_controller():
    if not request.content_type == "application/json":
        return error(400, "content_type", "Json content must be provided")
    data = request.json
    # data={urls:[]}
    urls = data["urls"]
    room = data["roomId"]
    if not len(urls):
        return error(400, "url", "Atleast a url is required.")
    if not room:
        return error(400, "room", "First create a room.")
    print(1)
    invalid_urls = await are_urls_valid(urls)
    if len(invalid_urls) > 0:
        return error(400, "invalid_urls", invalid_urls)
    try:
        print(2)
        scrapedData = await scraping_logic(urls)
        embed_success, data = await asyncio.to_thread(embedd, scrapedData)
        if not embed_success:
            return error(500, "server", data)
        store_success, error = await asyncio.to_thread(
            storeEmbeddings, data, room, urls
        )
        if not store_success:
            return error(500, "server", error)
        return success(200, "Scraping Finished", "Scraping is finished")

    except Exception as e:
        print(e)
        return error(500, "server", "Server error occured")
