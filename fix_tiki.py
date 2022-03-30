# thư viện requests đọc dữ liệu khi crawl về
import requests
# jsson chuyển file lấy từ web về đọc dữ liệu
import json
#lưu vào csv truyền vào database
import csv
import numpy as np
#pandas đọc ghi file nhanh
import pandas as pd

from bs4 import BeautifulSoup

# truyền api + page
nhacuadoisong_page_url="https://tiki.vn/api/v2/products?limit=12&include=advertisement&is_mweb=1&aggregations=1&trackity_id=494fc1f6-6f99-5f80-8f98-2154b6a13c2f&src=c.1883.hamburger_menu_fly_out_banner&urlKey=nha-cua-doi-song&categoryId=1883&category=1883&page=1"
product_url="https://tiki.vn/api/v2/products/{}"
rating_url="https://tiki.vn/api/v2/reviews?spid=46648924&product_id=46648921&limit=18&sort=score%7Cdesc&seller_id=1764"


product_id_file="./data/product-id.txt"
product_file ="./data/product.txt"
product_file2="./data/product-detail.txt"
rating_file="./data/rating.csv"

# bước 1 lấy id của product đó
def crawl_product_id():
	product_list = np.array([])
	i = 1
	while( i < 22) :
		payload = {}
		headers = {
			'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"}
		params = {
			'page': i
		}
		i += 1
		respone = requests.request(
			# câu lệnh lấy đọc từ link về respone
			"GET", nhacuadoisong_page_url,headers=headers,data=payload,params=params
			)
		print(respone)
		print("page",i)
		# chuyển respone về file json
		y = respone.json()
		print(len(y["data"]))
		for j in range (len(y["data"])):
			idproduct = y["data"][j]['id']
			product_list=np.append(product_list,[idproduct],axis=0)
	
	product_list = product_list.astype(int)
	print('product_list',product_list)
	return product_list



def write_csv_file(data_matrix,file_path,mode='w'):
 	df = pd.DataFrame(data=data_matrix)
 	# coluoms userid itemid rating timestamp comment
 	df.to_csv(file_path,sep='\t',encoding='utf-8',header=False,index=False, mode=mode)








def read_matrix_file(file_path):
 	f = pd.read_csv(
 			file_path, sep='t',encoding='utf-8',headers=None)
 	f = f.to_numpy()
 	return f

def crawl_product(product_list):
 	product_detail_list = np .array(
 		[['id','ten','gia','phanloai','thuonghieu','xuatxu','xuatxuthuonghieu','sku','mota']])
 	print('product_detail_list',product_detail_list)
 	for product_id in product_list:
 		id = -1
 		ten = -1
 		gia = -1
 		phanloai = -1
 		thuonghieu = -1
 		xuatxu = -1
 		xuatxuthuonghieu = -1
 		sku = -1
 		mota = -1
 		print("product_id",product_id)
 		payload ={}
 		headers = {
 			'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"}
 		respone = requests.get(product_url.format(
 		product_id),headers=headers,data=payload)
 		y = respone.json()
 		if(respone.status_code == 200):
 			id = y['id']
 			ten = y['name']
 			gia = y['price']
 			sku = y['sku']
 			phanloai = y['productset_group_name']
 			thuonghieu = y ['brand']['name']
 			for i in range( len(y['specifications'][0]['attributes'])):
 			 	 if (y['specifications'][0]['attributes'][i]['name'] == "Xuất xứ"):
 			 	 		xuatxu = y['specifications'][0]['attributes'][i]['value']
 			 	 if (y['specifications'][0]['attributes'][i]['name'] == "Xuất xứ thương hiệu"):
 			 	 		xuatxuthuonghieu = y['specifications'][0]['attributes'][i]['value']	
 				
 			mota = BeautifulSoup(y['description'],'html.parser').get('text')
 		product_detail_list = np .append(
 			product_detail_list,[[id,ten,phanloai,gia,thuonghieu,xuatxu,xuatxuthuonghieu,sku,mota]],axis=0)
 	return product_detail_list
def crawl_rating(product_list):
 	for product_id in product_list:
  		userid = -1
  		itemid = -1
  		rating = -1
  		timestamp = -1
  		i = 1
  		print("product_id",product_id)
  		payload = {}
  		params ={"page": i}
  		headers = {
 			'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"}
  		respone = requests.get(rating_url.format(
  			product_id),headers=headers, data=payload, params=params)
  		print("respone",respone)
  		y = respone.json()
  		total_page = y["paging"]["last_page"]
  		if(y["paging"]["total"] > 0):
  			while(i<= total_page):
  				payload={}
  				params ={"page":i}
  				headers = {
 					'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"}
  				res = requests.get(rating_url.format(
  					product_id),headers=headers, data=payload,params=params)
  				x = res.json()
  				for j in range(len(x["data"])):
  					userid = x["data"][j]['customer_id']
  					itemid = product_id
  					rating = x["data"][j]['created_at']
  					comment = x["data"][j]['content']
  					rating_list = np.array(
  						[[userid,itemid,rating,timestamp,comment]])
  					write_csv_file(rating_list,rating_file,mode='a')
  			i += 1
  #return 1

  	#crawl id tất cả sản phẩm 
product_list = crawl_product_id()

  	#ghi file các id vua crawl vào dile product-id txt
write_csv_file(product_list, product_id_file,mode='w+')

  	# đọc danh sach id de crawl  chi tet sp + rating
product_detail_list = crawl_product(product_list)
write_csv_file(product_list,product_file2,mode ='w+')

  	#crawl tat ca ghi vao file rating
rating_list = crawl_rating(product_list)


