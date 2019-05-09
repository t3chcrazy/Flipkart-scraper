# -*- coding: utf-8 -*-
import scrapy
import mysql.connector

class Phone1Spider(scrapy.Spider):
    name = 'phone1'
    allowed_domains = ['flipkart.com']
    start_urls = ['http://flipkart.com/']
    max_entries = 100

    def start_requests(self):
        keywords = ["Samsung"]
        for keyword in keywords:
            url = f"https://www.flipkart.com/search?q={keyword}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"
            yield scrapy.Request(url = url, callback = self.parse, meta = {"q": keyword})

    def parse(self, response):
        links = [self.start_urls[0][:-1]+link for link in response.xpath("//a[@class = '_31qSD5']//@href").extract()]
        for link in links:
            if self.max_entries <= 0:
                break
            else:
                self.max_entries -= 1
                yield scrapy.Request(url = link, callback = self.parse_item)

        next_page = response.xpath("//a[@class = '_3fVaIS']//@href").extract_first()
        if next_page:
            next_page = self.start_urls[0][:-1]+next_page
            yield scrapy.Request(url = next_page, callback = self.parse, dont_filter = True)
        else:
            print("Scraping Done!")
            return

    def parse_item(self, response):
        name = response.xpath("//span[@class = '_35KyD6']//text()").extract_first()
        price = response.xpath("//div[@class = '_1vC4OE _3qQ9m1']//text()").extract_first()[1:].replace(',','')
        description = response.xpath("//div[@class = '_3la3Fn _1zZOAc']//p//text()").extract_first()
        specification = '\n'.join(response.xpath("//div[@class = '_2RngUh']//*").extract())
        mydb = mysql.connector.connect(user = "root", passwd = "", host = "localhost", database = "products")
        cursor = mydb.cursor()
        sql = "INSERT INTO products.phone (NAME,PRICE,DESCRIPTION,SPECIFICATION) VALUES (%s,%s,%s,%s)"
        values = (name,int(price),description,specification)
        cursor.execute(sql, values)
        mydb.commit()
        yield {name:[price, description, specification]}