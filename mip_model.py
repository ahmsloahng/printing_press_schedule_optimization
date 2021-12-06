# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 16:25:14 2021

@author: Amlan Ghosh
"""

from pulp import *
import pandas as pd

def model(machine, sku):
    
    '''defining the model'''
    model = LpProblem('printing_press_cost_optimization', sense = LpMinimize)
    
    '''defining the variables'''
    
    var_volume_sku_machine = {} #integer variable: number of volumes of a sku is printed in a machine
    for i in sku:
        for j in machine:
            var_volume_sku_machine[(i,j)] = LpVariable('volume_'+i+'_'+j, lowBound = 0, upBound = sku[i], cat = LpInteger)
    
    #binary variable: if a given sku is printed in a machine
    var_used_sku_machine = LpVariable.dicts('used', ((i,j) for i in sku 
                                                            for j in machine),
                                            cat = LpBinary)
    
    #binary variable: if a machine is used
    var_used_machine = LpVariable.dicts('machine', ((j) for j in machine), cat = LpBinary)
    
    #integer variable: number of changeovers in a machine
    var_change_machine = LpVariable.dicts('change', ((i) for i in machine), lowBound = 0, cat = LpInteger)
    print ('defining variables is successful')
    
    '''defining the constraints'''
    #total hours (including changeover time, maintenance time, running time) should be less than available hours 
    for j in machine:
        model += (lpSum([var_volume_sku_machine[i,j]*(1/machine[j]['speed']) for i in sku]) 
                + var_change_machine[j]*machine[j]['change_time']
                + machine[j]['maint_time'] <= machine[j]['avail_time'])
    
    #volumes of a sku will be printed in a machine if and only if the machine is used by that sku
    for i in sku:
        for j in machine:
            model += var_volume_sku_machine[i,j] >= var_used_sku_machine[i,j]
            model += var_volume_sku_machine[i,j] <= var_used_sku_machine[i,j]*sku[i]
    
    #for a sku, total printed volumes accross all machines must equal demand
    for i in sku:
        model += lpSum([var_volume_sku_machine[i,j] for j in machine]) == sku[i]
    
    #a machine is used if any sku has been printed in that machine
    for j in machine:
        for i in sku:
            model += var_used_machine[j] >= var_used_sku_machine[i,j]
    
    #number of changeovers
    for j in machine:
        model += var_change_machine[j] >= sum([var_used_sku_machine[i,j] for i in sku]) - 1
    print ('building constraints is successful')
            
    '''defining the objective'''    
    model += (lpSum([var_volume_sku_machine[i,j]*machine[j]['prod_cost'] for j in machine for i in sku]) #production cost 
                  + lpSum([var_used_machine[j]*machine[j]['maint_cost'] for j in machine])) #maintenance cost

    print ('successfully defined objective')
    
    '''solving the problem'''
    model.solve()
    print ('solved') 
    
    '''printing the solution'''
    status = LpStatus[model.status]
    print ('problem status is: ' + str(status))
    
    '''printing the solution'''
    if status == 'Optimal':
        machine_list = [j for j in machine]
        sku_list = [i for i in sku]
        
        sku_allocation = {}
        for i in sku_list:
            sku_allocation[i] = []
            for j in machine_list:
                sku_allocation[i].append(round(var_volume_sku_machine[i,j].varValue/machine[j]['speed'],2))
            sku_allocation[i].append(sum([var_volume_sku_machine[i,j].varValue for j in machine_list]))
            sku_allocation[i].append('')

        prod_cost = []
        for j in machine_list:
            prod_cost.append(sum([var_volume_sku_machine[i,j].varValue*machine[j]['prod_cost'] for i in sku_list]))
        prod_cost.append(sum(prod_cost))
        prod_cost.append('')
        
        maint_cost = [var_used_machine[j].varValue*machine[j]['maint_cost'] for j in machine_list]
        maint_cost.append(sum(maint_cost))
        maint_cost.append('')
        
        sku_allocation[sku_list[0]][-1] = prod_cost[-2] + maint_cost[-2]
        
        run_time = []
        for j in machine_list:
            run_time.append(sum([var_volume_sku_machine[i,j].varValue/machine[j]['speed'] for i in sku_list]) 
                            + max(0, sum([var_used_sku_machine[i,j].varValue for i in sku])-1)*machine[j]['change_time']
                            + machine[j]['maint_time'])
        run_time.append('Total Cost')
        run_time.append('')
        
        df = pd.DataFrame(sku_allocation, index = [j for j in machine_list] + ['Total Volume', 'Total Overall Cost'])
        df['Changeover Time'] = [max(0, sum([var_used_sku_machine[i,j].varValue for i in sku])-1)*machine[j]['change_time'] for j in machine]+ ['']*2
        df['Maintenance Time'] = [machine[j]['maint_time'] for j in machine_list] + ['']*2
        df['Running Time'] = run_time
        df['Production Cost'] = prod_cost
        df['Maintainance Cost'] = maint_cost
        df.to_excel('Optimal Schedule.xlsx')
        print ('output files generated')
        
    
    