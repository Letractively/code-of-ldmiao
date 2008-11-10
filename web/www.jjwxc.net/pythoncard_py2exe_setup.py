from distutils.core import setup 
 
# py2exe stuff 
import py2exe, os 
# find pythoncard resources, to add as 'data_files' 
pycard_resources=['icon.ico'] 
for filename in os.listdir('.'): 
    if filename.find('.rsrc.')>-1: 
        pycard_resources+=[filename] 
 
# includes for py2exe 
includes=[] 
for comp in ['button','statictext','textarea','textfield','gauge']: 
    includes += ['PythonCard.components.'+comp] 
print 'includes',includes 
 
opts = { 'py2exe': { 'includes':includes } } 
print 'opts',opts 
# end of py2exe stuff 
 
setup(name='blarg', 
    version='0.1', 
    url='http://ldmiao.riit.tsinghua.edu.cn', 
    author='ldmiao', 
    author_email='ldmiao@gmail.com', 
    package_dir={'jjwxc':'.'}, 
    packages=[], 
    data_files=[('.',pycard_resources)], 
	windows = [
		{
			"script": "jjwxc.pyw",
			"icon_resources": [(1, "icon.ico")]
		}
	],
    options=opts 
    ) 