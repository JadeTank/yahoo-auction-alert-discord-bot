import requests, json
from logging import info
from easygoogletranslate import EasyGoogleTranslate
from bs4 import BeautifulSoup
from lightbulb import BotApp
from hikari import Embed, Color


async def check_yahoo_auctions(
    bot: BotApp, translator: EasyGoogleTranslate, alert: dict
) -> None:
    res = requests.get(
        f"https://zenmarket.jp/en/yahoo.aspx/getProducts?q={alert['name']}&sort=new&order=desc",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    )

    items = BeautifulSoup(res.content, 'html.parser').find_all('div', class_='yahoo-search-result')

    for item in items:
        itemCode = str(item.find('a', class_='auction-url')['href']).split('itemCode=')[1]
        title = item.find('a', class_='auction-url').decode_contents()
        image = item.find('img')['src']
        instant_price = item.find('div', class_='auction-blitzprice')
        bid_price = item.find('div', class_='auction-price').span['data-usd']

        if bot.d.synced.find_one(name=itemCode):
            info("[yahoo] already synced — up to date")
            continue

        embed = Embed()
        embed.color = Color(0x09B1BA)
        embed.title = translator.translate(title) or title or "Unknown"

        if itemCode:
            embed.url = "https://zenmarket.jp/en/yahoo.aspx/auction.aspx?itemCode=" + itemCode + "&skipqproc=true"

        if image:
            embed.set_image(image)

        if instant_price:
            embed.add_field("Instant price", instant_price.span['data-usd'])

        if bid_price:
            embed.add_field("Bid price", bid_price)

        embed.set_footer(f"Source: Yahoo Auction — #{itemCode}")

        await bot.rest.create_message(alert["channel_id"], embed=embed)
        bot.d.synced.insert({"name": itemCode})
