import requests, json
from logging import info
from bs4 import BeautifulSoup
from lightbulb import BotApp
from hikari import Embed, Color


async def check_mercari(bot: BotApp, alert: dict) -> None:
    res = requests.get(
        f"https://zenmarket.jp/en/mercari.aspx/getProducts?q={alert['name']}&sort=new&order=desc",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    )

    items = BeautifulSoup(res.content, 'html.parser').find_all('a', class_='product-item')

    for item in items:
        itemCode=str(item['href']).split('itemCode=')[1]
        image = item.find('img')['src']
        price = item.find('span', class_='amount')['data-usd']

        if bot.d.synced.find_one(name=itemCode):
            info("[mercari] already synced — up to date")
            continue

        embed = Embed()
        embed.color = Color(0x09B1BA)
        embed.title = item.find('h3',class_='item-title')['title'] or "Unknown"

        if itemCode:
            embed.url = "https://zenmarket.jp/en/mercariproduct.aspx?itemCode=" + itemCode + "&skipqproc=true"

        if image:
            embed.set_image(image)

        if price:
            embed.add_field("Price", price)

        embed.set_footer(f"Source: Mercari — #{itemCode}")

        await bot.rest.create_message(alert["channel_id"], embed=embed)
        bot.d.synced.insert({"name": itemCode})
