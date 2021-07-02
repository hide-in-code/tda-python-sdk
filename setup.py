from setuptools import setup, find_packages
import testindata

filepath = 'README.rst'

setup(
    name="testindata",
    version=testindata.VERSION,
    keywords=["云测", "数据集","yuncedata", "testin", "testindata"],
    description="云测数据 数据集管理平台pythonSDK",
    long_description=open(filepath, encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license="MIT Licence",
    url = "http://ai.testin.cn/",
    author = "hide-in-code",
    author_email = "hejinlong@testin.cn",
    packages=find_packages(),
    entry_points={
      'console_scripts': [
          'tdav = testindata.cli.run:main'
      ]
    },
    include_package_data=True,
    platforms="any",
    install_requires=[
        "click",
        "minio",
        "qiniu",
        "requests",
    ],
    data_files=[filepath],
)
