# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class LagouItem(scrapy.Item):
	# define the fields for your item here like:
	# name = scrapy.Field()
	salary = Field()
	positionName = Field()
	positionLables = Field()
	companyFullName = Field()
	companyLabelList = Field()
	companySize = Field()
	city = Field()
	district = Field()
	education = Field()
	firstType = Field()
	industryField = Field()
	jobNature = Field()
	workYear = Field()
