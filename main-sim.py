def storage_config(state, storage,dis_left,char_left, proxy_factor):
        #proxy_score = %eff of storage / fullness %
    
    proxy_score = pd.DataFrame({'Name':[],'Efficiency':[],'% Fullness':[],'Interconnector Capacity':[],\
                                'Storage Value':[]})

    state_to_fix = state

    stateus_maximus = [NSW, QLD, VIC ,TAS ,SA]

    for stateus in stateus_maximus:
        max_stor = 0
        if stateus.name_long == state_to_fix:

            cols = [stateus.name + ' fly', stateus.name + ' batt', stateus.name + ' phes',\
                    stateus.name + ' caes', stateus.name + ' hyd']
            
            for idx,stortus in enumerate(cols):
                stor_value = storage[stortus].iloc[-1]
                max_stor = getattr(stateus.stor, stortus[len(stateus.name)+1:])
                stor_perc = stor_value/max_stor
                stor_eff = getattr(stateus.eff, stortus[len(stateus.name)+1:])
                to_append = [stortus, stor_eff,stor_perc,'No',stor_value]
                to_series = pd.Series(to_append,index=proxy_score.columns)
                proxy_score = proxy_score.append(to_series,ignore_index=True)

            if dis_left > 0 :
                inter_possibility = inter_raw.loc[(inter_raw['From'] == state_to_fix)]
                state_to = inter_possibility['To'].unique()
            else:
                inter_possibility = inter_raw.loc[(inter_raw['To'] == state_to_fix)]
                state_to = inter_possibility['From'].unique()

            for stateus_again in stateus_maximus:
                
                if stateus_again.name_long in state_to:

                    cols = [stateus_again.name + ' fly', stateus_again.name + ' batt', stateus_again.name + ' phes',\
                    stateus_again.name + ' caes', stateus_again.name + ' hyd']
                                        
                    if dis_left > 0:
                        inter_cap = inter_possibility.loc[inter_possibility['To']==stateus_again.name_long,\
                                                          'Nominal Capacity'].sum()
                        
                    else:
                        inter_cap = inter_possibility.loc[inter_possibility['From']==stateus_again.name_long,\
                                                          'Nominal Capacity'].sum()
    
                            
                    for stortus in cols:
                        max_stor = storage[stortus].iloc[-1] + max_stor

                    for idx,stortus in enumerate(cols):
                        stor_value = storage[stortus].iloc[-1]
                        max_stor = getattr(stateus_again.stor, stortus[len(stateus_again.name)+1:])
                        stor_perc = stor_value/max_stor
                        stor_eff = getattr(stateus_again.eff, stortus[len(stateus_again.name)+1:])
                        to_append = [stortus, stor_eff,stor_perc,inter_cap,stor_value]
                        to_series = pd.Series(to_append,index=proxy_score.columns)
                        proxy_score = proxy_score.append(to_series,ignore_index=True)

    
    if dis_left > 0 :
        proxy_score['Proxy Score'] = np.where(proxy_score['Interconnector Capacity'] == 'No',\
                                              proxy_score['Efficiency']*proxy_score['% Fullness']*proxy_factor,\
                                              proxy_score['Efficiency']*proxy_score['% Fullness'])
    else:
        proxy_score['Proxy Score'] = np.where(proxy_score['Interconnector Capacity'] == 'No',\
                                              (proxy_score['Efficiency']/proxy_score['% Fullness'])*proxy_factor,\
                                              proxy_score['Efficiency']/proxy_score['% Fullness'])
        
    return(proxy_score.sort_values(['Proxy Score'],ascending=False))


def char_dischar(state, storage, dis_left, char_left,proxy_factor,time_idx):

    loss = 0
    leftover = 0
    end_stor = 0

    state_to_fix = state
    
    if dis_left > 0:
        char_or_dis = 'Discharge'
    else:
        char_or_dis = 'Charge'

    #configuration_raw = configuration_raw.loc[(configuration_raw['State']==state_to_fix) &\
                                              #(configuration_raw['Type']==char_or_dis)]

    #configuration = calc_proxy(configuration_raw,storage,proxy_factor,char_or_dis)
    
    configuration  = storage_config(state, storage,dis_left,char_left, proxy_factor)
    
    configuration['New Storage Value']=0
    
    while dis_left + char_left > 0:
        interconnection = 0
        for index,state_to in configuration.iterrows():
            #Collecting State Name
            state_to_send = state_to['Name'][0:3]
            if state_to_send[-1] == " ":
                state_to_send = state_to_send[:-1]
                
            state_to_send_class = getattr(sys.modules[__name__], state_to_send)

            #Collecting storage type
            storage_type = state_to['Name'][len(state_to_send_class.name)+1:]
            storage_eff = getattr(state_to_send_class.eff, storage_type)
            storage_pwr = getattr(state_to_send_class.pwr, storage_type)
            storage_stor = getattr(state_to_send_class.stor, storage_type)
            storage_value = state_to['Storage Value']

            if state_to['Interconnector Capacity'] == 'No':
                stor_cap = storage_pwr
            else:
                inter_cap = state_to['Interconnector Capacity']
                if inter_cap < storage_pwr:
                    stor_cap = inter_cap
                else: 
                    stor_cap = storage_pwr
                interconnection = interconnection + stor_cap


            if char_left > 0:
                if storage_value < storage_stor:
                    charg = charge(char_left, storage_value, storage_eff,\
                                      storage_stor,\
                                      stor_cap,time_idx)
                    storage_final = charg[0]
                    configuration.loc[index,'New Storage Value'] = storage_final
                    char_left = charg[1]
                    loss = charg[2]
                    
            else:
                if storage_value > 0:
                    discharg = discharge(dis_left, storage_value, storage_eff,\
                                      stor_cap,time_idx)
                    storage_final = discharg[0]
                    configuration.loc[index,'New Storage Value'] = storage_final
                    dis_left = discharg[1]
                    loss = discharg[2]
                    
            leftover = dis_left + char_left
           
            if leftover == 0:
                break
            
        if leftover > 0:
            end_stor = 1
            break
        else:
            leftover = 0

    if end_stor != 1:
        configuration['New Storage Value'] = np.where(configuration['New Storage Value']==0, \
                                                      configuration['Storage Value'],\
                                                      configuration['New Storage Value'])
    return(configuration,leftover,interconnection)

def decide_state_r(state):
    
    if state == 'New South Wales':
        index = 0
    elif state == 'Queensland':
        index = 1
    elif state == 'Victoria':
        index = 2
    elif state == 'Tasmania':
        index = 3
    elif state == 'South Australia':
        index = 4
    return(index)

def decide_state(index):
    if index == 0:
        #Run NSW's Interconnector
        p = 'New South Wales'
    elif index == 1:
        #Run QLD's Interconnector
        p = 'Queensland'
    elif index == 2:
        #Run VIC's Interconnector
        p = 'Victoria'
    elif index == 3:
        #Run VIC's Interconnector
        p = 'Tasmania'
    elif index == 4:
        #Run VIC's Interconnector
        p = 'South Australia'
    return(p)

def discharge(discharge_amt,stor_amt, stor_eff , stor_cap, time_idx):
    
    tt_discharge = discharge_amt * (1 + (1 - stor_eff))

    pwr_cap = stor_cap * time_idx

    if pwr_cap <= tt_discharge:
        new_discharge = pwr_cap
        new_stor_amt = stor_amt - new_discharge
        loss = abs(pwr_cap * (1 + (1 - stor_eff)) - pwr_cap)

        if new_stor_amt < 0 :
            discharge_leftover = stor_amt + new_stor_amt
            new_stor_amt = 0
        else:
            discharge_leftover = discharge_amt - pwr_cap / (1 + (1 - stor_eff))
        
    else:
        new_discharge = tt_discharge
        new_stor_amt = stor_amt - new_discharge
        loss = abs(discharge_amt * (1 + (1 - stor_eff)) - discharge_amt)

        if new_stor_amt < 0:
            discharge_leftover = stor_amt + new_stor_amt
            new_stor_amt = 0

        else: discharge_leftover = 0
    
    return([new_stor_amt, discharge_leftover, loss])

def charge(charge_amt, stor_amt , stor_eff, chargemax, stor_cap, time_idx):

    tt_charge = charge_amt * stor_eff
    
    pwr_cap = stor_cap * time_idx

    if tt_charge >= pwr_cap:
        
        new_charge = pwr_cap
        new_stor_amt = stor_amt + new_charge
        loss = abs(pwr_cap * stor_eff - pwr_cap)

        if new_stor_amt > chargemax:
            
            charge_leftover = new_stor_amt - chargemax
            new_stor_amt = chargemax
            
        else:
            
            charge_leftover = charge_amt - pwr_cap / stor_eff

    else:
        
        new_charge = tt_charge
        new_stor_amt = stor_amt + new_charge
        loss = abs(charge_amt * stor_eff - charge_amt)
        
        if new_stor_amt > chargemax:
            
            charge_leftover = new_stor_amt - chargemax
            new_stor_amt = chargemax
            
        else: charge_leftover = 0
            
    return ([new_stor_amt, charge_leftover, loss])

import numpy as np
import pandas as pd
import sys

xls = pd.ExcelFile('Raw_Data.xlsx')
inter_raw = pd.read_excel(xls, 'Interconnector Raw')
Demand = pd.read_excel(xls, 'Scheduled Demand')
NSW_TGen = pd.read_excel(xls, 'NSW Fuels')
QLD_TGen = pd.read_excel(xls, 'QLD Fuels')
VIC_TGen = pd.read_excel(xls, 'VIC Fuels')
TAS_TGen = pd.read_excel(xls, 'Tas Fuels')
SA_TGen = pd.read_excel(xls, 'SA Fuels')

inter_raw['Nominal Capacity'] = inter_raw['Nominal Capacity'].str.replace('MW','')
inter_raw['Nominal Capacity'] = pd.to_numeric(inter_raw['Nominal Capacity'] )


input_type = ''

re_factor=1.1
power_factor=1
storage_factor=0.6

proxy_factor = 1.5
fly_eff = 0.9
batt_eff = 0.9
phes_eff = 0.8
caes_eff = 0.5
hyd_eff = 0.35

class NSW:
    
    class eff:
        fly = fly_eff
        batt = batt_eff
        phes = phes_eff
        caes = caes_eff
        hyd = hyd_eff
        pass
    class pwr:
        fly = 8000*power_factor #MW
        batt = 8000*power_factor #MW
        phes = 30000*power_factor #MW
        caes = 30000*power_factor #MW
        hyd = 100000*power_factor #MW
        pass
    class stor:
        fly = 1800*1000*storage_factor #MWh
        batt = 3000*1000*storage_factor  #MWh
        phes = 6000*1000*storage_factor  #MWh
        caes = 6000*1000*storage_factor  #MWh
        hyd = 20000*1000*storage_factor  #MWh
        pass   

    init_stor_factor = 1

    re_multiplier = 7.6*re_factor
    
    name = 'NSW'
    
    name_long = 'New South Wales'
    
    pass

class QLD:
    class eff:
        fly = fly_eff
        batt = batt_eff
        phes = phes_eff
        caes = caes_eff
        hyd = hyd_eff
        pass
    class pwr:
        fly = 3000*power_factor #MW
        batt = 7000*power_factor #MW
        phes = 30000*power_factor #MW
        caes = 30000*power_factor #MW
        hyd = 100000*power_factor #MW
        pass
    class stor:
        fly = 2000*1000*storage_factor  #MWh
        batt = 3000*1000*storage_factor  #MWh
        phes = 12000*1000*storage_factor  #MWh
        caes = 12000*1000*storage_factor  #MWh
        hyd = 20000*1000*storage_factor  #MWh
        pass   

    init_stor_factor = 0.7

    re_multiplier = 6.8*re_factor
    
    name = 'QLD'
    
    name_long = 'Queensland'
    
    pass

class VIC:
    class eff:
        fly = fly_eff
        batt = batt_eff
        phes = phes_eff
        caes = caes_eff
        hyd = hyd_eff
        pass
    class pwr:
        fly = 2000*power_factor #MW
        batt = 10000*power_factor #MW
        phes = 20000*power_factor #MW
        caes = 20000*power_factor #MW
        hyd = 20000*power_factor #MW
        pass
    class stor:
        fly = 2000*1000*storage_factor  #MWh
        batt = 3000*1000*storage_factor  #MWh
        phes = 9000*1000*storage_factor  #MWh
        caes = 9000*1000*storage_factor  #MWh
        hyd = 10000*1000*storage_factor  #MWh
        pass   

    init_stor_factor = 0.65

    re_multiplier = 4*re_factor
    
    name = 'VIC'
    
    name_long = 'Victoria'
    
    pass

class TAS:
    class eff:
        fly = fly_eff
        batt = batt_eff
        phes = phes_eff
        caes = caes_eff
        hyd = hyd_eff
        pass
    class pwr:
        fly = 2000*power_factor #MW
        batt = 10000*power_factor #MW
        phes = 20000*power_factor #MW
        caes = 20000*power_factor #MW
        hyd = 20000*power_factor #MW
        pass
    class stor:
        fly = 2000*1000*storage_factor  #MWh
        batt = 3000*1000*storage_factor  #MWh
        phes = 8000*1000*storage_factor  #MWh
        caes = 8000*1000*storage_factor  #MWh
        hyd = 8000*1000*storage_factor  #MWh
        pass

    init_stor_factor = 0.65

    re_multiplier = 4.8*re_factor
    
    name = 'TAS'
    name_long = 'Tasmania'
    
    pass

class SA:
    class eff:
        fly = fly_eff
        batt = batt_eff
        phes = phes_eff
        caes = caes_eff
        hyd = hyd_eff
        pass
    class pwr:
        fly = 2000*power_factor  #MW
        batt = 10000*power_factor #MW
        phes = 20000*power_factor #MW
        caes = 20000*power_factor #MW
        hyd = 20000*power_factor #MW
        pass
    class stor:
        fly = 2000*1000*storage_factor  #MWh
        batt = 3000*1000*storage_factor  #MWh
        phes = 9000*1000*storage_factor  #MWh
        caes = 9000*1000*storage_factor  #MWh
        hyd = 10000*1000*storage_factor  #MWh
        pass   

    init_stor_factor = 0.65

    re_multiplier = 2*re_factor
    
    name = 'SA'
    
    name_long = 'South Australia'
    
    pass

NSW_R_Gen = NSW_TGen[['Time-ending','Rooftop PV','Solar','Wind']]
QLD_R_Gen = QLD_TGen[['Time-ending','Rooftop PV','Solar','Wind']]
VIC_R_Gen = VIC_TGen[['Time-ending','Rooftop PV','Solar','Wind']]
TAS_R_Gen = TAS_TGen[['Time-ending','Rooftop PV','Solar','Wind']]
SA_R_Gen = SA_TGen[['Time-ending','Rooftop PV','Solar','Wind']]

NSW_Demand = Demand[['NSW1 Scheduled Demand']]
QLD_Demand = Demand[['QLD1 Scheduled Demand']]
VIC_Demand = Demand[['VIC1 Scheduled Demand']]
TAS_Demand = Demand[['TAS1 Scheduled Demand']]
SA_Demand = Demand[['SA1 Scheduled Demand']]

NSW_info1 = pd.concat([NSW_R_Gen,NSW_Demand],axis = 1)
NSW_info1.rename(columns={'NSW1 Scheduled Demand': 'Demand'},inplace = True)
NSW_info1['re_multi'] = NSW.re_multiplier

QLD_info1 = pd.concat([QLD_R_Gen,QLD_Demand],axis = 1)
QLD_info1.rename(columns={'QLD1 Scheduled Demand': 'Demand'},inplace = True)
QLD_info1['re_multi'] = QLD.re_multiplier

TAS_info1 = pd.concat([TAS_R_Gen,TAS_Demand],axis = 1)
TAS_info1.rename(columns={'TAS1 Scheduled Demand': 'Demand'},inplace = True)
TAS_info1['re_multi'] = TAS.re_multiplier

SA_info1 = pd.concat([SA_R_Gen,SA_Demand],axis = 1)
SA_info1.rename(columns={'SA1 Scheduled Demand': 'Demand'},inplace = True)
SA_info1['re_multi'] = SA.re_multiplier

VIC_info1 = pd.concat([VIC_R_Gen,VIC_Demand],axis = 1)
VIC_info1.rename(columns={'VIC1 Scheduled Demand': 'Demand'},inplace = True)
VIC_info1['re_multi'] = VIC.re_multiplier

if input_type == 'half':
    time_idx = 1
else:
    time_idx = 0.5




X = [NSW_info1, QLD_info1, VIC_info1, TAS_info1, SA_info1]
Y = pd.DataFrame()
for item in X:
    if str(item) == str(NSW_info1):
        name = 'NSW'
    elif str(item) == str(QLD_info1):
        name = 'QLD'
    elif str(item) == str(VIC_info1):
        name = 'VIC'
    elif str(item) == str(TAS_info1):
        name = 'TAS'
    elif str(item) == str(SA_info1):
        name = 'SA'
        
    for states_col in item.columns:
        if states_col == 'Time-ending':
            continue
        process_array = item[states_col]
        
        if input_type == 'half':
            x = ((process_array + process_array.shift(-1)))[::2]
        else: 
            x = process_array
        Y[name +' ' + states_col] = x

X = [NSW, QLD, VIC, TAS, SA]

states = pd.DataFrame()

for item in X:
    state_name = item.name
    total_renewable = (Y[state_name + ' Rooftop PV'] + Y[state_name +' Solar'] +\
                       Y[state_name +' Wind'])*Y[state_name +' re_multi']
    states[state_name+ ' To_Re']= total_renewable
    Y[state_name+ ' To_Re'] = total_renewable
    states[state_name+' Charge(MWh)'] = np.where(Y[state_name+' Demand']<Y[state_name+' To_Re'], \
                                                 Y[state_name+' To_Re']-Y[state_name+' Demand'],0)
    states[state_name+' Discharge(MWh)'] = np.where(Y[state_name+' Demand']<Y[state_name+' To_Re'],\
                                                    0, Y[state_name+' Demand']-Y[state_name+' To_Re'])


makezeros = [0]*len(states.columns)
b_series = pd.DataFrame(makezeros, index = states.columns)
states = pd.concat([b_series.T,states]).reset_index(drop=True)
print(len(states))


all_storage_raw= pd.DataFrame({'NSW fly' : [] , 'NSW batt':[], \
                               'NSW phes' : [], 'NSW caes' : [],\
                               'NSW hyd' : [], 'NSW Interconnector/s' : [],\
                                'QLD fly' : [] , 'QLD batt':[], \
                               'QLD phes' : [], 'QLD caes' : [],\
                               'QLD hyd' : [], 'QLD Interconnector/s' : [],\
                                'VIC fly' : [] , 'VIC batt':[], \
                               'VIC phes' : [], 'VIC caes' : [],\
                               'VIC hyd' : [], 'VIC Interconnector/s' : [],\
                                 'TAS fly' : [] , 'TAS batt':[], \
                               'TAS phes' : [], 'TAS caes' : [],\
                               'TAS hyd' : [], 'TAS Interconnector/s' : [],\
                                 'SA fly' : [] , 'SA batt':[], \
                               'SA phes' : [], 'SA caes' : [],\
                               'SA hyd' : [], 'SA Interconnector/s' : []})


storage_inter = all_storage_raw.copy()
initial_factor = []

for columns in storage_inter:
    storage_type = columns[4:]
    state_to_send = columns[0:3]
    
    if state_to_send[2:3] == " ":
        state_to_send = columns[0:2]
        storage_type = columns[3:]
        
    if storage_type == 'Interconnector/s':
        stor_init_amt = 0
        
    else:
        state_to_send_class = getattr(sys.modules[__name__], state_to_send)
        stor_stor = getattr(state_to_send_class.stor, storage_type)
        init_factor = state_to_send_class.init_stor_factor
        stor_init_amt = stor_stor*init_factor
    
    initial_factor.append(stor_init_amt)
a_series = pd.Series(initial_factor,index=storage_inter.columns)
storage_inter = storage_inter.append(a_series,ignore_index=True)

#config_X = config.copy()
states2 = states.copy()
total_len = len(states2)
end = 0
storage = storage_inter.copy()

hold = [NSW,QLD,VIC,TAS,SA] # 1 = NSW, 2 = QLD, 3 = VIC, 4 = TAS, 5 = SA

for index, row in states2.iterrows():
    temp_storage = pd.DataFrame(storage.iloc[-1]).T 
    print("I'm still going. Be Patient. I'm at %d/%d"%(index,total_len))
    if index == 0:
        continue
    
    for index_state ,item in enumerate(hold):
                
        target_state = [col for col in states2.columns if item.name in col]
        char_left = row[target_state[1]]
        dis_left = row[target_state[2]]
        reference_idx = char_dischar(item.name_long,temp_storage,dis_left,char_left, proxy_factor,time_idx)
        configuration = reference_idx[0]        
        leftover = reference_idx[1]
        #storing interconnection values
        interconnection_cap = reference_idx[2]
        state_to_interconnect = item.name
        temp_storage[state_to_interconnect + ' Interconnector/s'] = interconnection_cap
                
        for idx, config in configuration.iterrows():
            reference = config['Name']
            temp_storage[reference] = config['New Storage Value']
    
        if leftover>0:
            print('Thats All Folks. The Simulation Failed at %s'%(item.name_long))
            end = 1
            break
            
    if end == 1:
        break

    storage = storage.append(temp_storage).reset_index(drop=True)

state_to_fix = [NSW, QLD, VIC ,TAS ,SA]
stor_info = pd.DataFrame({'No.':['Efficiency (%)', 'Power Capacity (MW)', 'Storage Capacity (MWh)', 'Renewable Factor']})

for states_app in state_to_fix:
    
    parameters = [states_app.eff, states_app.pwr, states_app.stor, states_app.re_multiplier]
    cols = [states_app.name + ' Flywheels', states_app.name + ' Batt', states_app.name + ' PHES',\
                states_app.name + ' CAES', states_app.name + ' Hydrogen', states_app.name + ' Renewable Factor']
    state_storage = pd.DataFrame()
    
    for parameter in parameters:
        
        if parameter == states_app.re_multiplier:
            to_append = [0, 0, 0, 0, 0, states_app.re_multiplier]
        else:
            to_append = [parameter.fly, parameter.batt, parameter.phes, parameter.caes, parameter.hyd,0]
        
                
        if parameter == states_app.stor:
            maxstor = sum(to_append)  
            
        a_series = pd.Series(to_append, index=cols)
        state_storage = state_storage.append(a_series, ignore_index=True, sort=False)
        state_storage = state_storage.reindex(cols, axis=1)
    
    stor_info = pd.concat([stor_info, state_storage], axis=1)
    
stor_info.set_index('No.', inplace = True)

x = NSW_TGen['Time-ending']
storage['TimeDate'] = x
storage = storage.set_index('TimeDate')

stor_info.to_json('Run 6 - Inputs.json',orient='columns')     
storage.to_json('Run 6 - Results.json',orient='columns',date_unit='s', date_format='iso')

