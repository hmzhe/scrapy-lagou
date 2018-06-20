# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import quote
from lagou.items import LagouItem
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request, FormRequest
import time
import hashlib
import re
import sys
from bs4 import BeautifulSoup
from scrapy.shell import inspect_response
import json
import math

class PositionSpider(scrapy.Spider):
	name = 'position'
	allowed_domains = ['lagou.com']
	start_url = 'https://www.lagou.com/jobs/positionAjax.json?city=%s&needAddtionalResult=false' % (quote('深圳'))
	headers = {
    #'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
	}
	curPage = 1
	job_name = 'java php 大数据'
	
	
	def get_token(self,response):
		#print(response.text)
		match_obj = re.search(r".*window.X_Anti_Forge_Token = '(.*?)'.*window.X_Anti_Forge_Code = '(.*?)'", response.text, re.S)
		if match_obj:
			Forge_Token = match_obj.group(1)
			Forge_Code = match_obj.group(2)
			#print(Forge_Token, Forge_Code)
			return Forge_Token, Forge_Code
	
	def start_requests(self):
		return [Request(url='https://passport.lagou.com/login/login.html?ts=1529408383229&serviceId=lagou&service=https%253A%252F%252Fwww.lagou.com%252F&action=login&signature=BBA48197F5CD74DC673F8E17BD880F80',
			headers=self.headers,meta = {'cookiejar':1}, 
			callback = self.post_login)]
	
	def post_login(self, response):
		def hash(value):
			#调用hashlib中的md5()生成一个md5 hash对象
			m = hashlib.md5()
			# print(m)#<md5 HASH object @ 0x0000000002938B48>
			#用update方法对字符串进行md5加密的更新处理
			m.update(bytes(value,encoding='utf-8')) 
			#加密后的十六进制结果
			sign = m.hexdigest()
			#返回解密后的16进制结果
			return sign

		pwd = hash('459693361zhe')
		pwd_str = 'veenike' + pwd + 'veenike'
		pwd_str = hash(pwd_str)
		forge_toekn, forge_code = self.get_token(response)
		self.login_headers = self.headers.copy()
		self.login_headers.update({'X-Requested-With': 'XMLHttpRequest',
									'X-Anit-Forge-Token':forge_toekn,
									'X-Anit-Forge-Code':forge_code,
									'Referer':'https://passport.lagou.com/login/login.html?ts=1529408383229&serviceId=lagou&service=https%253A%252F%252Fwww.lagou.com%252F&action=login&signature=BBA48197F5CD74DC673F8E17BD880F80'})
		print('Preparing login')
		data = {
			'isValidate':'true',
			'username':'13415488394',
			'password':pwd_str,
			'request_form_verifyCode': '',
			'submit': ''}
		return FormRequest(
							url = 'https://passport.lagou.com/login/login.json',
							meta = {'cookiejar':response.meta['cookiejar']},
							headers = self.login_headers,
							formdata = data,
							callback = self.next_request)
	
	#def after_login(self, response):
	#	print(response.text)

	def next_request(self, response):
		print(response.text)
		print("lagou page:" + str(self.curPage))
		if self.curPage == 1:
			first = 'true'
		else:
			first = 'false'
		Referer = "https://www.lagou.com/jobs/list_java%20php%20%E5%A4%A7%E6%95%B0%E6%8D%AE?labelWords=&fromSearch=true&suginput="
		self.headers.update({'Referer':Referer})
		yield FormRequest(url=self.start_url, formdata={'pn': str(self.curPage), 'kd': 'java php 大数据','first':first},
								  method='POST',
								  headers=self.headers, 
								  meta={'page': self.curPage, 'kd': self.job_name,'cookiejar':response.meta['cookiejar']},
								  callback=self.parse)
	
	def parse(self, response):
		#inspect_response(response, self)
		print("request -> " + response.url)
		html = json.loads(response.text)
		#except ValueError:
			#yield self.next_request(response)
		if (html.get("success")):
			if html.get('content').get('positionResult').get('resultSize') != 0:
				results = html.get('content').get('positionResult').get('result')
				print('lagou Nums:' + str(len(results)))
			for result in results:
				item = LagouItem()
				item['salary'] = result.get('salary').replace("k", "K")
				item['positionName'] = result.get('positionName')
				item['positionLables'] = result.get('positionLables')
				item['companyFullName'] = result.get('companyFullName')
				item['companyLabelList'] = result.get('companyLabelList')
				item['companySize'] = result.get('companySize')
				item['city'] = result.get('city')
				item['district'] = result.get('district')
				item['education'] = result.get('education')
				item['firstType'] = result.get('firstType')
				item['industryField'] = result.get('industryField')
				item['jobNature'] = result.get('jobNature')
				item['workYear'] = result.get('workYear')
				yield item
			totalPage = math.floor(int(html.get('content').get('positionResult').get("totalCount")) / int(
					html.get('content').get("pageSize")))
			self.curPage = self.curPage + 1
			if (self.curPage <= totalPage):
				yield self.next_request(response)
		else:
			time.sleep(60)
			yield self.next_request(response)
			