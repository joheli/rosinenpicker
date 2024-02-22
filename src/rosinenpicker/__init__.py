import os
import site

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(BASE_PATH)