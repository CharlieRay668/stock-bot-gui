from PIL import Image
import numpy as np 
from matplotlib import image
import matplotlib.pyplot as plt
import io
from io import StringIO, BytesIO
import os


image = Image.open('option_chain.PNG')

data = np.array(image)
data = np.delete(data, range(347, 351), 1)
chunks = []
chunk = []
chunk2 = []
for index, item in enumerate(data):
    if index%16 == 0:
        chunks.append(chunk)
        chunks.append(chunk2)
        chunk = []
        chunk2 =[]
    for pixindex, pix in enumerate(item):
        if data[index, pixindex].tolist() == [0,59,90,255]:
            data[index, pixindex] = [47,47,47,255]
        if pixindex <= 76:
            chunk.append([index, pixindex])
        elif pixindex >= 272:
            chunk2.append([index, pixindex])

def highlight_green(x, red=False, data=data):
    new_data = np.copy(data)
    for pix in chunks[x]:
        curr_c = new_data[pix[0], pix[1]]
        if red:
            new_data[pix[0], pix[1]] = [curr_c[0]+50,curr_c[1],curr_c[2],curr_c[3]]
        else:
            new_data[pix[0], pix[1]] = [curr_c[0],curr_c[1]+50,curr_c[2],curr_c[3]]
    return new_data

def highlight_red(x, data=data):
    return highlight_green(x, True, data=data)

def highlight_border(x, data=data):
    max_x = -1
    max_y = -1
    min_x = 100000
    min_y = 100000
    for pix in chunks[x]:
        px = pix[0]
        py = pix[1]
        if px > max_x:
            max_x = px
        elif px < min_x:
            min_x = px
        if py > max_y:
            max_y = py
        elif py < min_y:
            min_y = py
    new_data = np.copy(data)
    for pix in chunks[x]:
        curr_c = new_data[pix[0], pix[1]]
        if pix[0] == max_x or pix[0] == min_x or pix[1] == max_y or pix[1] == min_y:
            new_data[pix[0], pix[1]] = [curr_c[0],curr_c[1],255,curr_c[3]]
    return new_data

def get_edit_data(edits):
    new_data = np.copy(data)
    for edit in edits:
        x  = int(edit.replace('C', '').replace('P', '').replace('B', '').replace('S', ''))
        string = ''.join([i for i in edit if not i.isdigit()])
        if 'B' in string:
            new_data = highlight_green(x, data=new_data)
        else:
            new_data = highlight_red(x, data=new_data)
    x  = int(edits[-1].replace('C', '').replace('P', '').replace('B', '').replace('S', ''))
    new_data = highlight_border(x, data=new_data)
    return new_data

def serve_pil_image(pil_img):
    pil_img = pil_img.convert('RGB')
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return img_io

def create_pil_img(data):
    return Image.fromarray(data)    

def defaultdata():
    return np.copy(data)

# imgplot = plt.imshow(highlight_green(12, data=highlight_red(6, data=highlight_border(12))))
# plt.show()
# serve_pil_image(create_pil_img(data))
# create Pillow image
#image2 = Image.fromarray(data)



# import numpy as np

# image = image.imread('option_chain.PNG')
# # summarize shape of the pixel array
# print(image.dtype)
# print(image.shape)
# # display the array of pixels as an image
# pyplot.imshow(image)
# pyplot.show()