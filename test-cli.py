#!/usr/bin/env python3

from app import get_data
from json import dumps

data = get_data()

print(dumps(data))