from distutils.core import setup
import os


def pip_requirements(extra=None):
    if not os.environ.get('SKIP_INSTALL_REQUIRES'):
        if extra is None:
            requirements_path = "requirements.pip"
        else:
            requirements_path = "requirements.{}.pip".format(extra)
        with open(requirements_path) as f:
            return f.readlines()
    return []


setup(
    name="Skeleton",
    version="0.0.1",
    description="Skeleton",
    author="Joel Watts",
    author_email="joel@joelwatts.com",
    url="http://github.com/jpwatts/aiohttp-skeleton",
    packages=[
        "skeleton",
    ],
    install_requires=pip_requirements(),
    entry_points={
        'console_scripts': [
            'skeleton = skeleton.cli:main',
        ],
    }
)
