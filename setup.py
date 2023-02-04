from setuptools import setup, find_packages

with open("requirements.txt", "r") as fh:
    requirements = []
    for line in fh.readlines():
        line = line.strip()
        if line:
            requirements.append(line)

setup(
    name="aliyun_ddns",
    version="1.0",
    author="linweizhe94",
    author_email="linweizhe94@qq.com",
    description="aliyun ddns cli tool",
    url="https://github.com/chenqiaoanying/aliyun_ddns",
    packages=find_packages(),
    install_requires=requirements,
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'aliyun_ddns = aliyun_ddns.__main__:cli',
        ]
    },
    license='MIT',
    python_requires='>=3'
)
