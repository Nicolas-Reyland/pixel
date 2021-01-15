# Pixel Project C code implementation usage utils
import os
from platform import uname

SRC_CODE_FILE = os.path.join(os.path.abspath(__file__).replace(os.path.basename(__file__), ''), 'pixelf.c')
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
DEFINE_START_LINE = 11

os_name = uname()[0]
if os_name == 'Linux':
	compiler = 'gcc'
	run_prefix = './'
elif os_nme == 'Windows':
	compiler = 'cl'
	run_prefix = ''
else:
	raise NotImplementedError('Only Windows/Linux are supported at the time')

def change_src_code(src_code_file, params):
	src_code = open(src_code_file, 'r')
	lines = src_code.readlines()
	src_code.close()
	# all the #define
	for i in range(DEFINE_START_LINE,DEFINE_START_LINE + 4):
		line = lines[i]
		line = line[8:-1]
		name = line[:line.index(' ')]
		newvalue = params[name]
		lines[i] = '#define {} {}\n'.format(name, newvalue)

	# static const int
	newvalue = '{' + ', '.join(map(str, params['TESTRGB'])) + '}'
	lines[DEFINE_START_LINE + 4] = 'static const int TESTRGB[] = {};\n'.format(newvalue)

	# create path var for new src code file
	src_code_file_basename = os.path.basename(src_code_file)
	src_code_dir = os.path.dirname(src_code_file)
	new_src_code_file = os.path.join(src_code_dir, '_tmp_' + src_code_file_basename)

	# write the new code to it
	new_src_code = open(new_src_code_file, 'w')
	new_src_code.writelines(lines)
	new_src_code.close()

	return new_src_code_file

def compile_c(src_code_file, executable_file, options=''):
	result = os.system('{} {} -o {} {}'.format(compiler, src_code_file, executable_file, options))
	return result

def run_exec(executable_file, options=''):
	if os_name == 'Linux' and executable_file[0] == '/':
		result = os.system('/./' + executable_file[1:] + options)
	else:
		result = os.system(run_prefix + executable_file + options)
	return result

if __name__ == '__main__':
	change_src_code(SRC_CODE_FILE, {
		'SENSITIVITY': 45,
		'SRC_IMG_PATH': '"SRC IMG.dat"',
		'BG_IMG_PATH': '"BG IMG.dat"',
		'RESULT_IMG_PATH': '"RESULT IMG.dat"',
		'TESTRGB': [255,255,255]
	})
