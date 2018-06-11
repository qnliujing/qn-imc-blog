#coding: utf-8
from PIL import Image
import oss2
from itertools import islice
import os
import sys
import json
from datetime import datetime
from ImageProcess import Graphics

# 定义压缩比，数值越大，压缩越小
SIZE_normal = 1.0
SIZE_small = 1.5
SIZE_more_small = 2.0
SIZE_more_small_small = 3.0


def make_directory(directory):
    """创建目录"""
    os.makedirs(directory)

def directory_exists(directory):
    """判断目录是否存在"""
    if os.path.exists(directory):
        return True
    else:
        return False

def list_img_file(directory):
    """列出目录下所有文件，并筛选出图片文件列表返回"""
    old_list = sorted(os.listdir(directory), reverse=True)
    print(old_list)
    new_list = []
    for filename in old_list:
        name, fileformat = filename.split(".")
        if fileformat.lower() == "jpg" or fileformat.lower() == "png" or fileformat.lower() == "gif" or fileformat.lower() == "jpeg":
            new_list.append(filename)
    # print new_list
    return new_list

def compress(choose, des_dir, src_dir, file_list):
    """压缩算法，img.thumbnail对图片进行压缩，
    
    参数
    -----------
    choose: str
            选择压缩的比例，有4个选项，越大压缩后的图片越小
    """
    if choose == '1':
        scale = SIZE_normal
    if choose == '2':
        scale = SIZE_small
    if choose == '3':
        scale = SIZE_more_small
    if choose == '4':
        scale = SIZE_more_small_small
    for infile in file_list:
        img = Image.open(src_dir+infile)
        # size_of_file = os.path.getsize(infile)
        w, h = img.size
        img.thumbnail((int(w/scale), int(h/scale)))
        img.save(des_dir + infile)
def compress_photo():
    '''调用压缩图片的函数
    '''
    src_dir, des_dir = "photos/", "min_photos/"
    
    if directory_exists(src_dir):
        if not directory_exists(src_dir):
            make_directory(src_dir)
        # business logic
        file_list_src = list_img_file(src_dir)
    if directory_exists(des_dir):
        if not directory_exists(des_dir):
            make_directory(des_dir)
        file_list_des = list_img_file(des_dir)
        # print file_list
    '''如果已经压缩了，就不再压缩'''
    for i in range(len(file_list_des)):
        if file_list_des[i] in file_list_src:
            file_list_src.remove(file_list_des[i])
    compress('4', des_dir, src_dir, file_list_src)

def handle_photo():
    '''
    更新json文件
    
    '''
    endpoint = 'https://oss-cn-hangzhou.aliyuncs.com'
    auth = oss2.Auth('LTAIL0n5voZi5lJB', 'UIFXKBRPWluGsUQuALDiLdb1KpKDW7')
    bucket = oss2.Bucket(auth, endpoint, 'imc-img')
    file_list = []
    objs=islice(oss2.ObjectIterator(bucket,prefix='photos/20',delimiter=''),None)
    for obj in objs:
        file_list.append(obj.key.replace("photos/",""))
    print(file_list)
    list_info = []
    for i in range(len(file_list)):
        filename = file_list[i]
        date_str, info = filename.split("DSC_")
        info, _ = info.split(".")
        date = datetime.strptime(date_str, "%Y-%m-%d")
        year_month = date_str[0:7]            
        if i == 0:  # 处理第一个文件
            new_dict = {"date": year_month, "arr":{'year': date.year,
                                                                   'month': date.month,
                                                                   'link': [filename],
                                                                   'text': [info],
                                                                   'type': ["image"]
                                                                   }
                                        } 
            list_info.append(new_dict)
        elif year_month != list_info[-1]['date']:  # 不是最后的一个日期，就新建一个dict
            new_dict = {"date": year_month, "arr":{'year': date.year,
                                                   'month': date.month,
                                                   'link': [filename],
                                                   'text': [info],
                                                   'type': ["image"]
                                                   }
                        }
            list_info.append(new_dict)
        else:  # 同一个日期
            list_info[-1]['arr']['link'].append(filename)
            list_info[-1]['arr']['text'].append(info)
            list_info[-1]['arr']['type'].append("image")
    list_info.reverse()  # 翻转
    tmp = bubbleYear(list_info)
    bubble(tmp)
    final_dict = {"list": list_info}
    with open("../themes/next/source/lib/album/data.json","w") as fp:
        json.dump(final_dict, fp)

def cut_photo():
    """裁剪算法
    
    ----------
    调用Graphics类中的裁剪算法，将src_dir目录下的文件进行裁剪（裁剪成正方形）
    """
    src_dir = "photos/"
    if directory_exists(src_dir):
        if not directory_exists(src_dir):
            make_directory(src_dir)
        # business logic
        file_list = list_img_file(src_dir)
        # print file_list
        if file_list:
            for infile in file_list:
                img = Image.open(src_dir+infile)
                Graphics(infile=src_dir+infile, outfile=src_dir + infile).cut_by_ratio()            
        else:
            pass
    else:
        print("source directory not exist!")     



def aliyun_operation():
    '''
    上传图片
    '''
    endpoint = 'https://oss-cn-hangzhou.aliyuncs.com'
    auth = oss2.Auth('LTAIL0n5voZi5lJB', 'UIFXKBRPWluGsUQuALDiLdb1KpKDW7')
    bucket = oss2.Bucket(auth, endpoint, 'imc-img')
    dir_list={ 'min_photos/', 'photos/'}
    for dir in dir_list:
    	file_list = list_img_file(dir)
    	if file_list:
    			for infile in file_list:
    				key2 = dir+infile
    				key1 = dir+infile
    				result = bucket.put_object_from_file(key1,key2)
    				if result.status == 200:
    					print ("upload success")
    	else:
    		pass



def bubble(bubbleList):
    listLength = len(bubbleList)
    while listLength > 0:
        for i in range(listLength - 1):    # 这个循环负责设置冒泡排序进行的次数
            # print(bubbleList[i])
            for j in range(listLength-i-1):  # ｊ为列表下标
                if(bubbleList[j].get('arr').get('year') == bubbleList[j+1].get('arr').get('year')):
                    if bubbleList[j].get('arr').get('month') < bubbleList[j+1].get('arr').get('month'):
                
                        bubbleList[j], bubbleList[j+1] = bubbleList[j+1], bubbleList[j]
        return bubbleList

    
        # for i in range(listLength - 1):
        #     if(bubbleList[i].get('arr').get('year') == bubbleList[i+1].get('arr').get('year')):
        #         if bubbleList[i].get('arr').get('month') > bubbleList[i+1].get('arr').get('month'):
        #             bubbleList[i] = bubbleList[i] + bubbleList[i+1]
        #             bubbleList[i+1] = bubbleList[i] - bubbleList[i+1]
        #             bubbleList[i] = bubbleList[i] - bubbleList[i+1]
        # listLength -= 1
    
def bubbleYear(bubbleList):
    listLength = len(bubbleList)
    while listLength > 0:
        for i in range(listLength - 1):
            for j in range(listLength-i-1):
                if bubbleList[j].get('arr').get('year') < bubbleList[j+1].get('arr').get('year'):
                    
                    bubbleList[j], bubbleList[j+1] = bubbleList[j+1], bubbleList[j]
        # print(bubbleList)
        return bubbleList


if __name__ == "__main__":
		cut_photo()        # 裁剪图片，裁剪成正方形，去中间部分
		compress_photo()   # 压缩图片，并保存到mini_photos文件夹下
		aliyun_operation() # 提交到阿里云OSS服务器
		handle_photo()     # 将文件处理成json格式，存到博客仓库中
