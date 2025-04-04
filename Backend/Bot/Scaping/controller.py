from flask import request
import aiohttp
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import asyncio
from Bot.responses import error,success

async def are_urls_valid(urls):
    notOk=[]
    for url in urls:
        async with aiohttp.ClientSession() as session:
            s= await session.get(url)
            if not s.ok:
                notOk.append(url)
    return notOk    

async def scraping_logic(urls):
    # url=request.form.get("url")
    scraped_content={}
    for url in urls:
        async with async_playwright() as p:
            browser=await p.chromium.launch(headless=True)
            page=await browser.new_page()
            await page.goto(url,timeout=10000)
            html=await page.content()
        parse=BeautifulSoup(html,"html.parser")
        text=parse.get_text("\n",True).split("\n")
        links=[link["href"] for link in parse.find_all("a")]
        scraped_content[url]={
            "text":text,"links":links
        }
    return scraped_content
        
def scraping_controller():
    if not request.content_type=="application/json":
        return error(400,"content_type","Json content must be provided")
    data=request.json
    #data={urls:[]}
    urls=data["urls"]
    if not len(urls):
        return error(400,"url","Atleast a url is required.")
    invalid_urls=asyncio.run(are_urls_valid(urls))
    if len(invalid_urls)>0:
        return error(400,"invalid_urls",invalid_urls)
    try:
        scrapedData=asyncio.run(scraping_logic(urls))
    except Exception as e:
        print(e)
        return error(500,"server","Server error occured")
    else:
        return success(200,"scraping_finished",scrapedData)
