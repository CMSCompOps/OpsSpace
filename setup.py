import glob
import setuptools

setuptools.setup(
    name='cmstoolbox',
    version='0.9.2',
    packages=setuptools.find_packages(),
    author='Daniel Abercrombie',
    author_email='dabercro@mit.edu',
    description='Tools used by CMS Computing Operations',
    url='https://github.com/CMSCompOps/OpsSpace',
    install_requires=['testfixtures'],
    scripts=[s for s in glob.glob('bin/*') if not s.endswith('~')]
    )
