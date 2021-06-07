import numpy as np
from PIL import Image
import requests
import shutil # idk how else i'd stream images from web without corrupted images?
import time
import os
import tqdm #this is for progress bars remove it here and line 32 replace tqdm.tqdm(range()) --> range()

def process_image_to_numpy_array(Img,mode='L'):
    """
    Processes image to numpy array
    """
    imag = np.asarray(Img)
    img = None
    if(mode == 'L'):
        img = (imag[:, :, 0] + imag[:, :, 1] + imag[:, :, 2])/3
    elif(mode == 'RGB'):
        img = (imag[:, :, 0] , imag[:, :, 1] , imag[:, :, 2])
    return img
 
 
#should be really running on GPU using ```pip install cupy``` but well xD
def instance_convolve(mainim, kernel):
    """
    inputs -- numpy.ndarray , numpy.ndarray
    output -- numpy.ndarray
    """
    kx, ky = kernel.shape
    ix, iy = mainim.shape
    ox, oy = int(np.floor(kx/2)), int(np.floor(ky/2))
    conv_arr = np.zeros((ix, iy))
    for mi in tqdm.tqdm(range(ix)): 
        for mj in range(iy):
            for i in range(kx):
                for j in range(ky):
                    try:
                        conv_arr[mi][mj] += kernel[i-ox][j-ox] * \
                            mainim[i+mi][j+mj]
                    except IndexError:
                        conv_arr[mi][mj] += 0  # borders are zeros
    return conv_arr


def normal_2D(x, y, varience=1):
    expr = 1/(2*np.pi*varience**2)*np.exp(-1*(x**2 + y**2)/2*varience**2)
    return expr


def gaussian_kernel(sx, sy, var):
    testker = np.zeros((sx, sy))
    mulmag = 1/(2*np.pi*var**2)
    for i in range(sx):
        for j in range(sy):
            testker[i][j] = mulmag*normal_2D(i-sx/2, j-sy/2, var)
    return testker


#Kernels
EDGE_DETECT_KERNEL = np.array([
    [0, -1, 0],
    [-1, 4, -1],
    [0, -1, 0]
])

DEFAULT_GAUSSIAN_KERNEL = gaussian_kernel(5, 5, 1)

BOX_BLUR_KERNEL = np.array([
    [1/9, 1/9, 1/9],
    [1/9, 1/9, 1/9],
    [1/9, 1/9, 1/9]
])

HORIZONTAL_KERNEL = np.array([
    [-1,-1,-1],
    [2,2,2],
    [-1,-1,-1]
])

VERTICAL_KERNEL = HORIZONTAL_KERNEL.transpose()

#some functions being added from https://github.com/itspacchu/pacchubot 

def better_send(ctx, content=None, embed=None, file=None):
    try:
        try:
            return ctx.reply(content, embed=embed, file=file)
        except:
            return ctx.send(content, embed=embed, file=file)
    except:
        return ctx.send("Coudn't send the message.. something went wrong!!")


async def downloadFileFromUrl(something: str, name: str)->str:
    response = requests.get(something, stream=True)
    with open(f'{name}.png', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    return name
