import csv
import json
import os
import scrapy
from scrapy.crawler import CrawlerProcess

class foodcom(scrapy.Spider):
    name = 'food-com'
    custom_settings = {"FEEDS": {"recipes.csv": {"format": "csv"}}}

    page = 1
    nxp = 1
    list_url = 'https://www.food.com/ideas/top-healthy-recipes-6926#c-789404'
    start_urls = [list_url + str(page)]

    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"
    }

    try:
        os.remove("recipes.csv")
    except OSError:
        pass

    def parse(self, response):
        recipe_urls = response.xpath('//h2[@class="title"]/a/@href').getall()

        for url in recipe_urls:
            yield scrapy.Request(url=url, callback=self.parse_details)

    def parse_details(self, response):
        res = response.xpath('//script[@type="application/ld+json"]/text()').get()
        recipe = json.loads(res)

        prep_time = response.xpath('//dd[@class="facts__value svelte-1dqq0pw"]/text()').get()

        serves = response.xpath('//span[@class="value svelte-1o10zxc"]/text()').get()


        name = recipe.get('name')

        directions = response.xpath('//ul[@class="direction-list svelte-1dqq0pw"]/li[@class="direction svelte-1dqq0pw"]/text()').getall()


        description = recipe.get('description')


        ingredients = recipe.get('recipeIngredient', [])

        with open('recipes.csv', 'a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Name:', name])
            csv_writer.writerow(['Description:', description])
            csv_writer.writerow(['Ingredients:', ', '.join(ingredients)])
            csv_writer.writerow(['Prep Time:', prep_time])
            csv_writer.writerow(['Serves:', serves])
            csv_writer.writerow(['Directions:'])
            for direction in directions:
                csv_writer.writerow(['- ' + direction.strip()])
            csv_writer.writerow([])


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(foodcom)
    process.start()
