from silver_spectacle.library import *
from silver_spectacle.library import _is_iterable
import silver_spectacle.png as png
import io

flatten = lambda *m: (i for n in m for i in (flatten(*n) if _is_iterable(n) else (n,)))
# note: returns a generator, not a list
# pure python array-to-png-bytes function
def array_to_png(array):
    stream = io.BytesIO(b"")
    height = len(array)
    width = len(array[0])
    mode = None
    if not _is_iterable(array[0][0]):
        mode = 'L' # grayscale
        channels = 1
    else:
        channels = len(array[0][0])
        if channels == 2:
            mode = "LA" # grayscale with alpha
        elif channels == 3:
            mode = "RGB"
        elif channels == 4:
            mode = "RGBA"
        else:
            raise Exception(f'I expect an image to be image[height][width][channel] but I got a channel value of {channels} (max value is 4, min value is 1)')
    # reformat into png-library's desired format
    #     "each row being a sequence of values (``width*channels`` in number).
    #     So an RGB image that is 16 pixels high and 8 wide will
    #     occupy a 2-dimensional array that is 16x24"
    size_of_each_row = width * channels
    rows = [tuple([0]*size_of_each_row)]*height
    for row_index in range(0,height):
        rows[row_index] = tuple(flatten(
            reversed(array[row_index][column_index]) for column_index in range(0,width)
        ))
    # writes to btyes object instead of a file
    png.from_array(rows, mode).write(stream)
    png.from_array(rows, mode).save("stream_test.png")
    stream.flush()
    return stream.getvalue()

def register_image(file_as_bytes, file_extension=".png"):
    # remove the dot
    file_extension = file_extension.replace(".", "")
    # create an id
    random_number = random.random()
    data_id = f"{random_number}"
    data_format = f"image/{file_extension}"
    register_large(data_format, data_id, file_as_bytes)
    data_format = data_format.replace("/", r"%2F")
    return f"{data_format}/{data_id}"

# 
# add converter for pure image
# 
unknown_iterable = lambda each: _is_iterable(each) and type(each) != str
def unknown_iterable_init(iterable, *args):
    png_btyes = None
    try:
        png_btyes = array_to_png(iterable)
    except Exception as error:
        print(f'[silver_spectacle] Tried to convert a value to a png image, but failed')
        print(f'[silver_spectacle] Make sure your object follows the same structure opencv images')
        print(f'[silver_spectacle] Argument was {iterable}')
        length = len(iterable)
        print(f'[silver_spectacle] len(Argument) was {length}')
        raise error
    
    url_extension = register_image(png_btyes)
    new_arguments = [ url_extension, *args ]
    special_options = dict()
    return new_arguments, special_options
    
DisplayCard.conversion_table["init"]["quickImage"][unknown_iterable] = unknown_iterable_init
DisplayCard.conversion_table["send"]["quickImage"][unknown_iterable] = lambda arg: (unknown_iterable_init(arg)[0][0], dict())

# 
# add converter for image path as string
# 
import random
import os.path
def image_string_init(file_path, *args):
    # 
    # send image to server
    # 
    _, file_extension = os.path.splitext(file_path)
    file_as_bytes = None
    with open(file_path, 'rb') as in_file:
        file_as_bytes = in_file.read()
    url_extension = register_image(file_as_bytes, file_extension=file_extension)
    new_arguments = [ url_extension, *args ]
    special_options = dict()
    return new_arguments, special_options
DisplayCard.conversion_table["init"]["quickImage"][str] = image_string_init
DisplayCard.conversion_table["send"]["quickImage"][str] = lambda arg: (image_string_init(arg)[0][0], dict())

# # 
# # add converter for pillow
# # 
# try:
#     import PIL
#     from PIL import Image
#     from PIL.ImageFile import ImageFile
#     import numpy
#     DisplayCard.conversion_table["init"]["quickImage"][PIL.ImageFile.ImageFile] = lambda *args: ([ convert_numpy_to_rgba(numpy.array(args[0])), *args[1:] ], dict(bypass_purification=True))
#     DisplayCard.conversion_table["send"]["quickImage"][PIL.ImageFile.ImageFile] = lambda arg: (DisplayCard.conversion_table["init"]["quickImage"][PIL.ImageFile.ImageFile]([arg])[0][0], dict(bypass_purification=True))
# except Exception as error:
#     pass