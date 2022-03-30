# thư viện requests đọc dữ liệu khi crawl về
import requests
# jsson chuyển file lấy từ web về đọc dữ liệu
import json
#lưu vào csv truyền vào database
import csv
import numpy as np
#pandas đọc ghi file nhanh
import pandas as pd
import pymysql
from bs4 import BeautifulSoup
#selenium
#TF-IDF
# truyền api + page
nhacuadoisong_page_url="https://tiki.vn/api/v2/products?limit=12&include=advertisement&is_mweb=1&aggregations=1&trackity_id=494fc1f6-6f99-5f80-8f98-2154b6a13c2f&src=c.1883.hamburger_menu_fly_out_banner&urlKey=nha-cua-doi-song&categoryId=1883&category=1883&page=1"
product_url="https://tiki.vn/api/v2/products/{}"

#https%3A%2F%2Ftiki.vn%2Fapi%2Fv2%2Fproducts%3Flimit%3D2%26include%3Dadvertisement%26aggregations%3D1%26trackity_id%3D754ce305-af8e-5347-e963-7cd559144973%26category%3D1789%26page%3D1%26src%3Dc.1789.hamburger_menu_fly_out_banner%26urlKey%3Ddien-thoai-may-tinh-bang%26fbclid%3DIwAR08jx6mMUybx9_m3gttyM0EAhu1p5VjgwjmPleeQFoPlcLf4Tm8SIt3ESE&h=AT3P6MePpkZoA_ZPdDddv77_jmOlY9xJY51YIYNpREZG2Gg_152iR025YMHYHxb1l8qKUR_WXmAYKi7oGjdM8RkXIPgWiNvH_fPBLehsuinK1c3RX1ug8IPcyrqc99aljqJj3ELzrzc66Mwn0PXQSw
product_id_file="./data/product-id.txt"
product_file ="./data/product.txt"
product_file2="./data/product-detail.txt"
product_file3="./data/product.csv"
proimage ="./data/image.csv"
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
   
    response = requests.request(
      # câu lệnh lấy đọc từ link về respone
      "GET", nhacuadoisong_page_url,headers=headers,data=payload,params=params
      )
    print(response)
    print("page",i)
    # chuyển respone về file json
    y = response.json()
    print(len(y["data"]))
    for j in range (len(y["data"])):
      idproduct = y["data"][j]['id']
      product_list=np.append(product_list,[idproduct],axis=0)
    i += 1
  product_list = product_list.astype(int)
  print('product_list',product_list)
  return product_list

# ghi file csv
def write_csv_file(data_matrix,file_path,mode='a'):
  df = pd.DataFrame(data=data_matrix) 
  df.to_csv(file_path,sep='\t',encoding='utf-8',header=False,index=False, mode=mode)
  
def read_matrix_file(file_path):
  f = pd.read_csv(
      file_path, sep='\t',encoding='utf-8',header=None)
  f = f.to_numpy()
  return f
def crawl_product(product_list):
  product_detail_list = np .array(
    [['id','ten','gia','review_count', 'phanloai','thuonghieu','sku','mota','url_image']])
  print('product_detail_list',product_detail_list)
  for product_id in product_list:
    id = -1
    ten = -1
    gia = -1
    review_count = -1
    phanloai = -1
    thuonghieu = -1
    sku = -1
    mota = -1
    print("product_id",product_id)
    payload = {}
    headers = {
      'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"}
    response = requests.get(product_url.format(
    product_id),headers=headers,data=payload)
    y = response.json()
    if(response.status_code == 200):
      id = y['id']
      ten = y['name']
      gia = y['price']
      review_count = y['review_count']
      phanloai = y['productset_group_name']
      thuonghieu = y['brand']['name']
      sku = y['sku']
      url_image = y['thumbnail_url']
      print(id)
      print("\tName:",ten)
      print("\t Price:",gia)
      print("\t",review_count)
      print("\t",phanloai)
      print("\t",thuonghieu)
      print("t", url_image)
      mota = BeautifulSoup(y['description'],'html.parser').get('text')
    product_detail_list = np .append(
      product_detail_list,[[id, ten, gia,review_count,phanloai, thuonghieu,sku, mota, url_image]],axis=0)




        #  vừa craw vừa lưu
    conn= pymysql.connect(host="localhost", user="root", passwd="", db="tiki2")                          
    myCur = conn.cursor()
    sql= "INSERT INTO product(id, ten, gia, thuonghieu, review_count, phanloai, url_image) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val= (id, ten, gia, thuonghieu, review_count, phanloai, url_image)
    myCur.execute(sql, val)
    conn.commit()
    conn.close()

  return product_detail_list
    #crawl id tất cả sản phẩm 





product_list = crawl_product_id()
    #ghi file các id vua crawl vào dile product-id txt
write_csv_file(product_list, product_id_file,mode='w+')
# đọc danh sách id sản phẩm để tieessn hình crawl và ratings
product_list = read_matrix_file(product_id_file).flatten()

  # chi tiết sản phẩm vào file product.csv
product_detail_list = crawl_product(product_list)
write_csv_file(product_detail_list,product_file2,mode ='w+')
write_csv_file(product_detail_list,product_file,mode ='w+')
write_csv_file(product_detail_list,product_file3,mode ='w')




