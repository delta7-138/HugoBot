import requests
import numpy as np 
import cv2 as cv
import json 
from PIL import Image
import os
from math import *

class ImageClass():

    async def mergeImages(self , url1 , url2):
        im1 = Image.open(requests.get(url1 , stream = True).raw)
        im2 = Image.open(requests.get(url2 , stream = True).raw)
        im1 = im1.resize((220 , 220))
        im2 = im2.resize((220 , 220))
        im1.save('1.png')
        im2.save('2.png')
        im1arr = cv.imread('1.png')
        im2arr = cv.imread('2.png')
        res = cv.addWeighted(im2arr , 1 , im1arr , 0.6 , 0)
        cv.imwrite('out.png' , res)
    
    async def getDomninantColor(self , url):
        apiurl = 'http://api.itspacchu.tk/dominant_color'
        im = Image.open(requests.get(url,  stream = True).raw) 
        im = im.resize((45 , 45))
        im.save('tmpim.png')
        files = {'image' : open('tmpim.png' , 'rb')}
        r = requests.post(apiurl , files = files)
        content = json.loads(r.text)
        return content["hexval"]
        
    async def getColorInvert(self , url): 
        im = Image.open(requests.get(url , stream = True).raw)
        im.save('invtmp.png')
        im1arr = cv.imread('invtmp.png' , cv.IMREAD_COLOR)
        imageres = cv.bitwise_not(im1arr)
        cv.imwrite('outpic.png' , imageres)

    async def concatImage(self , l):
        dim = int(floor(sqrt(len(l))))
        finImgList = []
        for i in range(0 , len(l) , dim):
            buffer = []
            for j in range(i , i+dim):
                imtmp = Image.open(requests.get(l[j] , stream = True).raw)
                imtmp.save('concat.png')
                cvobj = cv.imread('concat.png')
                buffer.append(cvobj)
                os.remove('concat.png')
            
            finImgList.append(cv.hconcat(buffer))
        
        finalImage = cv.vconcat(finImgList)
        cv.imwrite('chart.png' , finalImage)        


