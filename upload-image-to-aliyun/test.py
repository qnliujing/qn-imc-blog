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

filename = "2018-5-2_DSC_0006.JPG"
date_str, info = filename.split("_DSC_")
info, _ = info.split(".")
date = datetime.strptime(date_str, "%Y-%m-%d")
print(date)