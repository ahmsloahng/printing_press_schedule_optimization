# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 09:59:16 2021

@author: Amlan Ghosh
"""

import pandas as pd

def data_reading(data):

    data_machine = pd.read_excel(data, sheet_name = 'Machine')
    data_sku = pd.read_excel(data, sheet_name = 'SKU')
    
    machine = {}
    sku = {}

    '''preparing data for machine'''    
    for row in data_machine.itertuples():
        machine[row[1]] = {
                            'prod_cost': float(row[2]),
                            'maint_cost': int(row[3]),
                            'speed': int(row[4]),
                            'maint_time': float(row[5]),
                            'change_time': float(row[6]),
                            'avail_time': int(row[7])
                            }
        
    ''' preparing data for sku'''
    for row in data_sku.itertuples():
        sku[row[1]] = int(row[2])
    
    return machine, sku




