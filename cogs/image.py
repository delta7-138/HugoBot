import requests
import numpy as np 
import cv2 as cv
from PIL import Image

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
    

