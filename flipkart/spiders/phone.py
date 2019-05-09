# -*- coding: utf-8 -*-
import scrapy
import mysql.connector

class PhoneSpider(scrapy.Spider):
    name = 'phone'
    allowed_domains = ['flipkart.com']
    start_urls = ['http://flipkart.com/']

    def start_requests(self):
        keywords = ["Samsung"]
        for keyword in keywords:
            url = f"https://www.flipkart.com/search?q={keyword}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"
            yield scrapy.Request(url = url, callback = self.parse, meta = {"q": keyword})

    def parse(self, response):
        itemblocks = response.xpath("//div[contains(@class,'_1HmYoV')]").xpath("//div[contains(@class,'bhgxx2')]")
        item_names = itemblocks.xpath("//div[@class = '_3wU53n']//text()").extract()
        item_prices = itemblocks.xpath("//div[@class = '_1vC4OE _2rQ-NK']//text()").extract()
        i = 1
        mydb = mysql.connector.connect(host = "localhost",user = "root",passwd = "", database = "products")
        cursor = mydb.cursor()
        with open("phone_data.csv","a") as csvfile:
            csvfile.write("ID,Name,Price\n")
            for item, price in zip(item_names,item_prices):
                yield {item:price}
                item = item.replace(",","")
                price = price.replace(",","")
                csvfile.write(','.join([str(i),item,price[1:]])+"\n")
                sql = "INSERT INTO phone (ID,NAME,PRICE) VALUES (%s,%s,%s)"
                val = (i,item,int(price[1:]))
                cursor.execute(sql,val)
                mydb.commit()
                i+=1