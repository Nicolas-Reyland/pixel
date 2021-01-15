# Pixel Project - C implementation use through this file
import sys, os
import imageio
import numpy as np
from PIL import Image
import pixelf_c_utils as pcu
'''
Usage: python3 pixel-use.py "path-to-src-image" "path-to-bg-image" "path-to-result-image" SENSITIVITY=... SRC_IM... (all are mandatory, none default)
You must also give the args in this order (file-order is as-is, C-args-order is not important, as long as they are all there)
The TESTRGB value is expected as TESTRGB=123,45,12 (raw ints, separated by comma)

Will resize the background-image if there is a need to resize
'''

# nice images to try this with
'''
img_src = '/home/ilu_vatar_/Pictures/Nic Ames/nick-ames-aftermath-noise-bright.jpg'
bg_img = '/home/ilu_vatar_/Pictures/giant_wave_girl_resized.jpg'
ouput_img = '/home/ilu_vatar_/Pictures/output.jpg'
'''

resize = lambda img, size: np.array(Image.fromarray(img).resize(size[::-1]))
load_img = lambda path: imageio.imread(open(path, 'rb'))
save_img = lambda array, path: Image.fromarray(array, mode='RGB').save(path, format='BMP')


def main(return_img=True, compile_args='', run_args=''):
	args = sys.argv[1:]
	assert len(args) == 5 # 3 for image-paths + 5 for params - 3 for PATHS = 8

	# settings args
	src_path, bg_path, result_path = args[:3]
	assert os.path.isfile(src_path)
	assert os.path.isfile(bg_path)

	# check image-sizes and resize if needed
	img1 = load_img(src_path)
	img2 = load_img(bg_path)
	if img1.shape != img2.shape:
		#if img1.shape[0] * img1.shape[1] > img2.shape[0] * img2.shape[1]:
		img2 = resize(img2, img1.shape[:2])
		extension = '.' + bg_path[::-1].split('.')[0][::-1]
		bg_path = bg_path[:-len(extension)] + '-resized' + extension
		save_img(img2, bg_path)
		resized = bg_path
	else:
		resized = ''

	# init params etc.
	params = {}
	check_list = ['SENSITIVITY', 'TESTRGB']
	for arg in args[3:]:
		print(arg)
		name, value = arg.split('=')
		assert name in check_list # name exists/no duplicates
		if name == 'TESTRGB':
			value = list(map(int, value.split(','))) # technically yes, there is a converting-to-and-back but idc rn bc it allows more flexibility
		else:
			# the rest (only sensitivity :D) are all integers
			value = int(value)
		params[name] = value
		check_list.remove(name)
	assert len(check_list) == 0 # there should be no elements left to declare
	params['SRC_IMG_PATH'] = f'"{src_path}"'
	params['BG_IMG_PATH'] = f'"{bg_path}"'
	params['RESULT_IMG_PATH'] = f'"{result_path}"'

	# creating new c file
	src_code_file = pcu.change_src_code(pcu.SRC_CODE_FILE, params)

	# compiling new c file
	exec_file = os.path.join(pcu.WORK_DIR, '_tmp_exec')
	result = pcu.compile_c(src_code_file, exec_file, options=compile_args)
	print('Result for compiling code: {}'.format(result))

	# running executable (+ make sure everything went OK)
	result = pcu.run_exec(exec_file, options=run_args)
	print('Result for running code: {}'.format(result))

	# cleaning up the mess (generated code + tmp compiled)
	#os.remove(src_code_file) # keep for debugging :D
	#os.remove(exec_file)

	if resized != '':
		os.remove(resized)

if __name__ == '__main__':
	main(return_img=False, compile_args='-lm', run_args='')
