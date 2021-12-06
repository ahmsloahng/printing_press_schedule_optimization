# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 16:49:25 2021

@author: Amlan Ghosh
"""

from data_reading import *
from mip_model import *

data = 'Data.xlsx'

machine, sku = data_reading(data)
print('data reading completed')

print('starting to solve...')
solution = model(machine,sku)