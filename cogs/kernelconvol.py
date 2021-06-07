import numpy as np
from PIL import Image

async def instance_convolve(mainim, kernel):
    """
    inputs -- numpy.ndarray , numpy.ndarray
    output -- numpy.ndarray
    """
    kx, ky = kernel.shape
    ix, iy = mainim.shape
    ox, oy = int(np.floor(kx/2)), int(np.floor(ky/2))
    conv_arr = np.zeros((ix, iy))
    for mi in range(ix):
        for mj in range(iy):
            for i in range(kx):
                for j in range(ky):
                    try:
                        conv_arr[mi][mj] += kernel[i-ox][j-ox] * \
                            mainim[i+mi][j+mj]
                    except IndexError:
                        conv_arr[mi][mj] += 0  # borders are zeros
    return conv_arr


async def normal_2D(x, y, varience=1):
    expr = 1/(2*np.pi*varience**2)*np.exp(-1*(x**2 + y**2)/2*varience**2)
    return expr


async def gaussian_kernel(sx, sy, var):
    testker = np.zeros((sx, sy))
    mulmag = 1/(2*np.pi*var**2)
    for i in range(sx):
        for j in range(sy):
            testker[i][j] = mulmag*normal_2D(i-sx/2, j-sy/2, var)
    return testker
