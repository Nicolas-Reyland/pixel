# Pixel Project - C functions FFI file
import os, sys
import numpy as np
from PIL import Image
from typing import Union

ROOT_DIR : str = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pixel-f')
sys.path.insert(0, ROOT_DIR)
from pixelfuse import main as c_rciibi_function

save = lambda array,path: Image.fromarray(array, mode='RGB').save(path, format='BMP')

def replace_color_in_image_by_image(base_image : np.array, background_image : np.array, target_color : Union[list, np.array], tolerance : int) -> np.array:
    os.chdir(ROOT_DIR)
    save(base_image, '_tmp_img_base.bmp')
    save(background_image, '_tmp_img_bg.bmp')
    test_rgb = ','.join(map(str,target_color))
    result : np.array = c_rciibi_function(
            return_img = True,
            compile_args = '-lm',
            run_args = '',
            args = [
                os.path.join(ROOT_DIR, '_tmp_img_base.bmp'),
                os.path.join(ROOT_DIR, '_tmp_img_bg.bmp'),
                os.path.join(ROOT_DIR, '_tmp_img_res.bmp'),
                f'SENSITIVITY={tolerance}',
                f'TESTRGB={test_rgb}'
                ]
            )
    os.chdir('..')
    return result
