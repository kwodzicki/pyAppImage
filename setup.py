#!/usr/bin/env python
from setuptools import setup, find_packages, convert_path

NAME     = 'appimage'

main_ns  = {}
ver_path = convert_path( "{}/version.py".format(NAME) )
with open(ver_path) as ver_file:
  exec(ver_file.read(), main_ns)

setup(
  name                 = NAME,
  description          = "For installing and updating AppImages",
  url                  = "https://github.com/kwodzicki/pyAppImage",
  author               = "Kyle R. Wodzicki",
  author_email         = "krwodzicki@gmail.com",
  version              = main_ns['__version__'],
  packages             = find_packages(),
  install_requires     = [ "watchdog" ],
  scripts              = ['bin/appimaged'],
  package_data         = {},
  include_package_date = True,
  zip_safe             = False,
)
