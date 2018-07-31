import setuptools

setuptools.setup(
    name='cmstoolbox',
    version='0.9.1',
    packages=setuptools.find_packages(),
    author='Daniel Abercrombie',
    author_email='dabercro@mit.edu',
    description='Tools used by CMS Computing Operations',
    url='https://github.com/CMSCompOps/OpsSpace',
    install_requires=['testfixtures']
    )
