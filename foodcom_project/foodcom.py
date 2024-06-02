import csv
import re
import json
import os
import scrapy
from scrapy.crawler import CrawlerProcess

def convert_prep_time(prep_time_str):
    # Regular expression to capture hours and minutes
    hours_pattern = re.compile(r'(\d+)\s*hrs?')
    minutes_pattern = re.compile(r'(\d+)\s*mins?')

    # Initialize hours and minutes to 0
    hours = 0
    minutes = 0

    # Extract hours using the regex pattern
    hours_match = hours_pattern.search(prep_time_str)
    if hours_match:
        hours = int(hours_match.group(1))

    # Extract minutes using the regex pattern
    minutes_match = minutes_pattern.search(prep_time_str)
    if minutes_match:
        minutes = int(minutes_match.group(1))

    # Return the total time in minutes
    return hours * 60 + minutes


class FoodComSpider(scrapy.Spider):
    name = 'food-com'
    custom_settings = {"FEEDS": {"recipes.csv": {"format": "csv"}}}

    page = 1
    list_url = 'https://www.food.com/ideas/top-healthy-recipes-6926#c-789404'
    start_urls = [list_url + str(page)]

    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"
    }

    # Remove the old CSV file if it exists
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
        prep_time_in_minutes = convert_prep_time(prep_time)  # Convert prep time to minutes
        serves = response.xpath('//span[@class="value svelte-1o10zxc"]/text()').get()

        name = recipe.get('name')
        directions = response.xpath('//ul[@class="direction-list svelte-1dqq0pw"]/li[@class="direction svelte-1dqq0pw"]/text()').getall()
        description = recipe.get('description')
        ingredients = recipe.get('recipeIngredient', [])

        nutrition_info = recipe.get('nutrition', {})
        calories = nutrition_info.get('calories', 'N/A')
        fat_content = nutrition_info.get('fatContent', 'N/A')
        saturated_fat_content = nutrition_info.get('saturatedFatContent', 'N/A')
        cholesterol_content = nutrition_info.get('cholesterolContent', 'N/A')
        sodium_content = nutrition_info.get('sodiumContent', 'N/A')
        carbohydrate_content = nutrition_info.get('carbohydrateContent', 'N/A')
        fiber_content = nutrition_info.get('fiberContent', 'N/A')
        sugar_content = nutrition_info.get('sugarContent', 'N/A')
        protein_content = nutrition_info.get('proteinContent', 'N/A')

        with open('recipes.csv', 'a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([name, description, ', '.join(ingredients), prep_time_in_minutes, serves,
                                 '\n'.join(directions), calories, fat_content, saturated_fat_content,
                                 cholesterol_content, sodium_content, carbohydrate_content, fiber_content,
                                 sugar_content, protein_content])

if __name__ == "__main__":
    # Write the header to the CSV file
    with open('recipes.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Name', 'Description', 'Ingredients', 'Prep Time (minutes)', 'Serves',
                             'Directions', 'Calories', 'Fat Content', 'Saturated Fat Content',
                             'Cholesterol Content', 'Sodium Content', 'Carbohydrate Content',
                             'Fiber Content', 'Sugar Content', 'Protein Content'])

    process = CrawlerProcess()
    process.crawl(FoodComSpider)
    process.start()