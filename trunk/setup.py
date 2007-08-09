#!/usr/bin/env python

from distutils.core import setup
from distutils.command.install_data import install_data

version = "0.0.1"
api_version = "0.1" # mediamax

setup(name = "mediamax-cache",
      version = version,
      description = "toe compiler toolkit",
      long_description = "toe compiler toolkit",
      author = "Danny Milosavljevic",
      author_email = "danny.milo@scratchpost.org",
      url = "http://www.scratchpost.org/hacks/toe/",
      license="GNU LGPL",
      platforms = ["posix", "win32"],
      packages = [
          "toe",
          "toe.lexer"
      ],
      package_data = { # directory: [ file ... ]
      },
      data_files = [ # [ (directory, [ file ... ]) ]
      ],
      scripts = [
          "lexer/toe-compile-lexer"
      ]
)
