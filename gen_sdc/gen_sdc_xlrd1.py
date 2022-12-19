#!/home/andyzhao/project/ENTER/bin/python

import xlrd
import os
import sys
import re



data = xlrd.open_workbook(r'Analog_Timing_Table.xlsx')

table = data.sheet_by_name("Shee1_R1")
nrows = table.nrows
ncols = table.ncols
print("rows : {}".format(nrows))
print("cols : {}".format(ncols))

#获得第一行的所有item
list_header = [str(table.cell_value(0, i)) for i in range(0, ncols)]

new_header = []

time_unit_dict = {}

#clock definition
create_clock = {}

#input cap
input_cap_max = {}
input_cap_min = {}

#input transition
input_rise_trans_max = {}
input_fall_trans_max = {}
input_rise_trans_min = {}
input_fall_trans_min = {}

#related clock for input/output delay
related_clock = {}

#output load
load_max = {}

#output transition
output_rise_trans_max = {} 
output_rise_trans_min = {}

#output delay 
output_delay_max = {}               
output_delay_min = {}      

#input delay
input_delay_max = {}         
input_delay_min = {}

for item in list_header:
    #duty cycle
    if re.fullmatch(r'(\w+) (\w+)',item):
        m = re.fullmatch(r'(\w+) (\w+)',item)
        new_item = m.group(1)+"_"+m.group(2)
        new_header.append(new_item)    
    #eq driver name
    elif re.fullmatch(r'(\w+) (\w+) (\w+)',item):
        m = re.fullmatch(r'(\w+) (\w+) (\w+)',item)
        new_item = m.group(1)+"_"+m.group(2)+"_"+m.group(3)
        new_header.append(new_item)
    #output load (min) (fF)
    elif re.fullmatch(r'(\w+) (\w+) \((\w+)\) \((\w+)\)',item):
        m = re.fullmatch(r'(\w+) (\w+) \((\w+)\) \((\w+)\)',item)
        new_item = m.group(1)+"_"+m.group(2)+"_"+m.group(3)
        time_unit_dict[new_item] = m.group(4)
        new_header.append(new_item)       
    #Trise (min) (ps)
    elif re.fullmatch(r'(\w+) \((\w+)\) \((\w+)\)',item):
        m = re.fullmatch(r'(\w+) \((\w+)\) \((\w+)\)',item)
        new_item = m.group(1)+"_"+m.group(2)
        #print("Trise (min) (ps) is {} {} {} {}".format(m.group(1),m.group(2),m.group(3),new_item))
        time_unit_dict[new_item] = m.group(3)
        new_header.append(new_item)      
    #clock period (ns)
    
    elif re.fullmatch(r'(\w+) (\w+) \((\w+)\)',item):
        m = re.fullmatch(r'(\w+) (\w+) \((\w+)\)',item)
        new_item = m.group(1)+"_"+m.group(2)
        time_unit_dict[new_item] = m.group(3)
        new_header.append(new_item)
    else :
        new_header.append(item)        
print("list_header：{}".format(list_header))
print("new_header：{}".format(new_header))

if time_unit_dict["OUTPUT_LOAD_max"] == "fF":
   output_load_max_pF = 0.001
else:
    print("please provide the right format for OUTPUT_LOAD_max unit")
    sys.exit()
    
if time_unit_dict["OUTPUT_LOAD_min"] == "fF":
   output_load_min_pF = 0.001  
else:
    print("please provide the right format for OUTPUT_LOAD_min unit")
    sys.exit()
    
if time_unit_dict["Trise_max"] == "ps":
   Trise_max_ns = 0.001
else:
    print("please provide the right format for Trise_max unit")
    sys.exit()
   
if time_unit_dict["Trise_min"] == "ps":
   Trise_min_ns = 0.001
else:
    print("please provide the right format for Trise_min unit")
    sys.exit()
    
if time_unit_dict["Tfall_max"] == "ps":
   Tfall_max_ns = 0.001
else:
    print("please provide the right format for Tfall_max unit")
    sys.exit()   
    
if time_unit_dict["Tfall_min"] == "ps":
   Tfall_min_ns = 0.001   
else:
    print("please provide the right format for Tfall_min unit")
    sys.exit()
    
if time_unit_dict["TCO_max"] == "ps":
   tco_max_ns = 0.001
else:
    print("please provide the right format for TCO_max unit")
    sys.exit()   
    
if time_unit_dict["TCO_min"] == "ps":
   tco_min_ns = 0.001
else:
    print("please provide the right format for TCO_min unit")
    sys.exit()

if time_unit_dict["CLOCK_PERIOD"] == "ns":
   clock_period_ns = 1
else:
    print("please provide the right format for CLOCK_PERIOD unit")
    sys.exit()

if time_unit_dict["Tsetup_max"] == "ps":
   tsetup_max_ns = 0.001
else:
    print("please provide the right format for Tsetup_max unit")
    sys.exit()
    
if time_unit_dict["Thold_min"] == "ps":
   thold_min_ns = 0.001
else:
    print("please provide the right format for Thold_min unit")
    sys.exit()

if time_unit_dict["INPUT_LOAD"] == "fF":
   input_load_pF = 0.001
else:
    print("please provide the right format for INPUT_LOAD unit")
    sys.exit()
   
#print("time_unit_dict: {}".format(time_unit_dict))

line_dict = {}

with open("temp1.log","w") as fout1:
    #print("time_unit_dict : {}".format(time_unit_dict),file=fout)
    for i in range(1,nrows):
#        for item in sht.range(f'A{i}:V{i}').value:
        #line = sht.range(f'A{i}:T{i}').value
        line = [table.cell_value(i, col) for col in range(0, ncols)]
        j = 0
        for item in new_header:
            line_dict[item] = line[j]
            j = j + 1
        #collect analog output clock pin's attribute,the analog output pin maps the input pin of SOC
        if line_dict["PIN_TYPE"]=="CO":
            clock_pin_name = line_dict["PIN_NAME"]
            clock_period = line_dict["CLOCK_PERIOD"]*clock_period_ns
            clock_duty_cycle = line_dict["Duty_Cycle"]
            if re.fullmatch(r'(\w+)ID_(\w+)',line_dict["PIN_NAME"]):
                m = re.fullmatch(r'(\w+)ID_(\w+)',line_dict["PIN_NAME"])
                if m.group(1) == "GEPHY":
                    for k in range(0,8):
                        clock_pin_name = m.group(1)+str(k)+"_"+m.group(2)
                        create_clock[clock_pin_name] = [clock_pin_name,clock_period,clock_duty_cycle]
                        input_cap_max[clock_pin_name] = float(line_dict["OUTPUT_LOAD_max"])*output_load_max_pF
                        input_cap_min[clock_pin_name] = float(line_dict["OUTPUT_LOAD_min"])*output_load_min_pF
                        input_rise_trans_max[clock_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                        input_rise_trans_min[clock_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                        input_fall_trans_max[clock_pin_name] = float(line_dict["Tfall_max"])*Tfall_max_ns
                        input_fall_trans_min[clock_pin_name] = float(line_dict["Tfall_min"])*Tfall_min_ns
                elif m.group(1) == "GEPLL":
                    for k in range(0,2):
                        clock_pin_name = m.group(1)+str(k)+"_"+m.group(2)
                        create_clock[clock_pin_name] = [clock_pin_name,clock_period,clock_duty_cycle]
                        input_cap_max[clock_pin_name] = float(line_dict["OUTPUT_LOAD_max"])*output_load_max_pF
                        input_cap_min[clock_pin_name] = float(line_dict["OUTPUT_LOAD_min"])*output_load_min_pF
                        input_rise_trans_max[clock_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                        input_rise_trans_min[clock_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                        input_fall_trans_max[clock_pin_name] = float(line_dict["Tfall_max"])*Tfall_max_ns
                        input_fall_trans_min[clock_pin_name] = float(line_dict["Tfall_min"])*Tfall_min_ns
                elif m.group(1) == "SDSPHY":
                    for k in range(0,2):
                        clock_pin_name = m.group(1)+str(k)+"_"+m.group(2)
                        create_clock[clock_pin_name] = [clock_pin_name,clock_period,clock_duty_cycle]
                        input_cap_max[clock_pin_name] = float(line_dict["OUTPUT_LOAD_max"])*output_load_max_pF
                        input_cap_min[clock_pin_name] = float(line_dict["OUTPUT_LOAD_min"])*output_load_min_pF
                        input_rise_trans_max[clock_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                        input_rise_trans_min[clock_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                        input_fall_trans_max[clock_pin_name] = float(line_dict["Tfall_max"])*Tfall_max_ns
                        input_fall_trans_min[clock_pin_name] = float(line_dict["Tfall_min"])*Tfall_min_ns
            else:                        
                create_clock[clock_pin_name] = [clock_pin_name,clock_period,clock_duty_cycle]
                input_cap_max[clock_pin_name] = float(line_dict["OUTPUT_LOAD_max"])*output_load_max_pF
                input_cap_min[clock_pin_name] = float(line_dict["OUTPUT_LOAD_min"])*output_load_min_pF
                input_rise_trans_max[clock_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                input_rise_trans_min[clock_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                input_fall_trans_max[clock_pin_name] = float(line_dict["Tfall_max"])*Tfall_max_ns
                input_fall_trans_min[clock_pin_name] = float(line_dict["Tfall_min"])*Tfall_min_ns
        #collect analog output data pin's attribute, the analog output pin maps the input pin of SOC
        if line_dict["PIN_TYPE"]=="O":
            #judge data width
            m1 = re.fullmatch(r'(\w+)+<(\d+):(\d+)>',line_dict["PIN_NAME"]) #bus data
            m2 = re.fullmatch(r'(\w+)+<(\d+)>',line_dict["PIN_NAME"]) #1 bit data
            if m1:# bus data
                real_pin_name = m1.group(1)
                bus_msb = int(m1.group(2))
                bus_lsb = int(m1.group(3))
            elif m2: #1 bit data
                real_pin_name = m1.group(1)
                bus_msb = int(m1.group(2))
                bus_lsb = int(m1.group(2))
            else: #1bit data without <>
                real_pin_name = line_dict["PIN_NAME"]
                bus_msb = "None"
                bus_lsb = "None"
            print("real_pin_name : {}".format(real_pin_name))
            print("bus_msb : {}".format(bus_msb))
            print("bus_lsb : {}".format(bus_lsb))
            #judge PHYID/SDSPHYID
            m3 = re.fullmatch(r'(\w+)ID_(\w+)',real_pin_name)
            #get PHYID/SDSPHYID clock
            m4 = re.fullmatch(r'(\w+)ID_(\w+)',line_dict["CLOCK_DOMAIN"])            
            if m3: #PHYID/SDSPHYID
                pin_name_part1 = m3.group(1)
                pin_name_part2 = m3.group(2)  
                if pin_name_part1 == "GEPHY":
                    for k in range(0,8): #ID from 0~7
                        if bus_msb != "None" and bus_lsb != "None":
                            for h in range(bus_lsb,bus_msb+1): #bus width
                                data_pin_name = pin_name_part1+str(k)+"_"+pin_name_part2+"["+str(h)+"]"                                
                                if m4:
                                    related_clock[data_pin_name] = m4.group(1)+str(k)+"_"+m4.group(2)
                                    input_cap_max[data_pin_name] = float(line_dict["OUTPUT_LOAD_max"])*output_load_max_pF
                                    input_cap_min[data_pin_name] = float(line_dict["OUTPUT_LOAD_min"])*output_load_min_pF
                                    input_rise_trans_max[data_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                                    input_rise_trans_min[data_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                                    input_fall_trans_max[data_pin_name] = float(line_dict["Tfall_max"])*Tfall_max_ns
                                    input_fall_trans_min[data_pin_name] = float(line_dict["Tfall_min"])*Tfall_min_ns
                                    input_delay_max[data_pin_name] = [float(line_dict["TCO_max"])*tco_max_ns,line_dict["Edge"]]         
                                    input_delay_min[data_pin_name] = [float(line_dict["TCO_min"])*tco_min_ns,line_dict["Edge"]]
                        elif bus_msb == "None" and bus_lsb == "None": #1bit data without <>
                            data_pin_name = pin_name_part1+str(k)+"_"+pin_name_part2
                            if m4:
                                related_clock[data_pin_name] = m4.group(1)+str(k)+"_"+m4.group(2)
                                input_cap_max[data_pin_name] = float(line_dict["OUTPUT_LOAD_max"])*output_load_max_pF
                                input_cap_min[data_pin_name] = float(line_dict["OUTPUT_LOAD_min"])*output_load_min_pF
                                input_rise_trans_max[data_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                                input_rise_trans_min[data_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                                input_fall_trans_max[data_pin_name] = float(line_dict["Tfall_max"])*Tfall_max_ns
                                input_fall_trans_min[data_pin_name] = float(line_dict["Tfall_min"])*Tfall_min_ns
                                input_delay_max[data_pin_name] = [float(line_dict["TCO_max"])*tco_max_ns,line_dict["Edge"]]         
                                input_delay_min[data_pin_name] = [float(line_dict["TCO_min"])*tco_min_ns,line_dict["Edge"]]                            
                elif pin_name_part1 == "SDSPHY":
                    for k in range(0,2): #ID from 0~1
                        if bus_msb != "None" and bus_lsb != "None":
                            for h in range(bus_lsb,bus_msb+1): #bus width
                                data_pin_name = pin_name_part1+str(k)+"_"+pin_name_part2+"["+str(h)+"]"
                                if m4:
                                    related_clock[data_pin_name] = m4.group(1)+str(k)+"_"+m4.group(2)
                                    input_cap_max[data_pin_name] = float(line_dict["OUTPUT_LOAD_max"])*output_load_max_pF
                                    input_cap_min[data_pin_name] = float(line_dict["OUTPUT_LOAD_min"])*output_load_min_pF
                                    input_rise_trans_max[data_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                                    input_rise_trans_min[data_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                                    input_fall_trans_max[data_pin_name] = float(line_dict["Tfall_max"])*Tfall_max_ns
                                    input_fall_trans_min[data_pin_name] = float(line_dict["Tfall_min"])*Tfall_min_ns
                                    input_delay_max[data_pin_name] = [float(line_dict["TCO_max"])*tco_max_ns,line_dict["Edge"]]         
                                    input_delay_min[data_pin_name] = [float(line_dict["TCO_min"])*tco_min_ns,line_dict["Edge"]]
                        elif bus_msb == "None" and bus_lsb == "None": #1bit data without <>
                            data_pin_name = pin_name_part1+str(k)+"_"+pin_name_part2
                            if m4:
                                related_clock[data_pin_name] = m4.group(1)+str(k)+"_"+m4.group(2)
                                input_cap_max[data_pin_name] = float(line_dict["OUTPUT_LOAD_max"])*output_load_max_pF
                                input_cap_min[data_pin_name] = float(line_dict["OUTPUT_LOAD_min"])*output_load_min_pF
                                input_rise_trans_max[data_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                                input_rise_trans_min[data_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                                input_fall_trans_max[data_pin_name] = float(line_dict["Tfall_max"])*Tfall_max_ns
                                input_fall_trans_min[data_pin_name] = float(line_dict["Tfall_min"])*Tfall_min_ns
                                input_delay_max[data_pin_name] = [float(line_dict["TCO_max"])*tco_max_ns,line_dict["Edge"]]         
                                input_delay_min[data_pin_name] = [float(line_dict["TCO_min"])*tco_min_ns,line_dict["Edge"]]                                    
            elif m1:# without ID flag
                if bus_msb != "None" and bus_lsb != "None":
                    for h in range(bus_lsb,bus_msb+1): #bus width
                        data_pin_name = real_pin_name+"["+str(h)+"]"                                
                        related_clock[data_pin_name] = line_dict["CLOCK_DOMAIN"]
                        input_cap_max[data_pin_name] = float(line_dict["OUTPUT_LOAD_max"])*output_load_max_pF
                        input_cap_min[data_pin_name] = float(line_dict["OUTPUT_LOAD_min"])*output_load_min_pF
                        input_rise_trans_max[data_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                        input_rise_trans_min[data_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                        input_fall_trans_max[data_pin_name] = float(line_dict["Tfall_max"])*Tfall_max_ns
                        input_fall_trans_min[data_pin_name] = float(line_dict["Tfall_min"])*Tfall_min_ns
                        input_delay_max[data_pin_name] = [float(line_dict["TCO_max"])*tco_max_ns,line_dict["Edge"]]         
                        input_delay_min[data_pin_name] = [float(line_dict["TCO_min"])*tco_min_ns,line_dict["Edge"]]
                elif bus_msb == "None" and bus_lsb == "None": #1bit data without <>
                    data_pin_name = real_pin_name
                    related_clock[data_pin_name] = line_dict["CLOCK_DOMAIN"]
                    input_cap_max[data_pin_name] = float(line_dict["OUTPUT_LOAD_max"])*output_load_max_pF
                    input_cap_min[data_pin_name] = float(line_dict["OUTPUT_LOAD_min"])*output_load_min_pF
                    input_rise_trans_max[data_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                    input_rise_trans_min[data_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                    input_fall_trans_max[data_pin_name] = float(line_dict["Tfall_max"])*Tfall_max_ns
                    input_fall_trans_min[data_pin_name] = float(line_dict["Tfall_min"])*Tfall_min_ns
                    input_delay_max[data_pin_name] = [float(line_dict["TCO_max"])*tco_max_ns,line_dict["Edge"]]         
                    input_delay_min[data_pin_name] = [float(line_dict["TCO_min"])*tco_min_ns,line_dict["Edge"]]                

                    
        #collect analog input data pin's attribute, the analog input pin maps the output pin of SOC
        if line_dict["PIN_TYPE"]=="I":
            #judge data width
            m1 = re.fullmatch(r'(\w+)<(\d+):(\d+)>',line_dict["PIN_NAME"]) #bus data
            m2 = re.fullmatch(r'(\w+)<(\d+)>',line_dict["PIN_NAME"]) #1 bit data
            if m1:# bus data
                real_pin_name = m1.group(1)
                bus_msb = int(m1.group(2))
                bus_lsb = int(m1.group(3))
            elif m2: #1 bit data
                real_pin_name = m1.group(1)
                bus_msb = int(m1.group(2))
                bus_lsb = int(m1.group(2))
            else: #1bit data without <>
                real_pin_name = line_dict["PIN_NAME"]
                bus_msb = "None"
                bus_lsb = "None"
            #judge PHYID/SDSPHYID
            m3 = re.fullmatch(r'(\w+)ID_(\w+)',real_pin_name)
            #get PHYID/SDSPHYID clock
            m4 = re.fullmatch(r'(\w+)ID_(\w+)',line_dict["CLOCK_DOMAIN"])
            if m3: #PHYID/SDSPHYID
                pin_name_part1 = m3.group(1)
                pin_name_part2 = m3.group(2)
                if pin_name_part1 == "GEPHY":
                    for k in range(0,8): #ID from 0~7
                        if bus_msb != "None" and bus_lsb != "None":
                            for h in range(bus_lsb,bus_msb+1): #bus width
                                data_pin_name = pin_name_part1+str(k)+"_"+pin_name_part2+"["+str(h)+"]"                                
                                if m4:
                                    related_clock[data_pin_name] = m4.group(1)+str(k)+"_"+m4.group(2)
                                    load_max[data_pin_name] = float(line_dict["INPUT_LOAD"])*input_load_pF
                                    output_rise_trans_max[data_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                                    output_rise_trans_min[data_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                                    output_delay_max[data_pin_name] = [float(line_dict["Tsetup_max"])*tsetup_max_ns,line_dict["Edge"]]         
                                    output_delay_min[data_pin_name] = [float(line_dict["Thold_min"])*thold_min_ns,line_dict["Edge"]]
                        elif bus_msb == "None" and bus_lsb == "None": #1bit data without <>
                            data_pin_name = pin_name_part1+str(k)+"_"+pin_name_part2
                            if m4:
                                related_clock[data_pin_name] = m4.group(1)+str(k)+"_"+m4.group(2)
                                load_max[data_pin_name] = float(line_dict["INPUT_LOAD"])*input_load_pF
                                output_rise_trans_max[data_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                                output_rise_trans_min[data_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                                output_delay_max[data_pin_name] = [float(line_dict["Tsetup_max"])*tsetup_max_ns,line_dict["Edge"]]         
                                output_delay_min[data_pin_name] = [float(line_dict["Thold_min"])*thold_min_ns,line_dict["Edge"]]                            
                elif pin_name_part1 == "SDSPHY":
                    for k in range(0,2): #ID from 0~1
                        if bus_msb != "None" and bus_lsb != "None":
                            for h in range(bus_lsb,bus_msb+1): #bus width
                                data_pin_name = pin_name_part1+str(k)+"_"+pin_name_part2+"["+str(h)+"]"
                                if m4:
                                    related_clock[data_pin_name] = m4.group(1)+str(k)+"_"+m4.group(2)
                                    load_max[data_pin_name] = float(line_dict["INPUT_LOAD"])*input_load_pF
                                    output_rise_trans_max[data_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                                    output_rise_trans_min[data_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                                    output_delay_max[data_pin_name] = [float(line_dict["Tsetup_max"])*tsetup_max_ns,line_dict["Edge"]]         
                                    output_delay_min[data_pin_name] = [float(line_dict["Thold_min"])*thold_min_ns,line_dict["Edge"]]
                        elif bus_msb == "None" and bus_lsb == "None": #1bit data without <>
                            data_pin_name = pin_name_part1+str(k)+"_"+pin_name_part2
                            if m4:
                                related_clock[data_pin_name] = m4.group(1)+str(k)+"_"+m4.group(2)
                                load_max[data_pin_name] = float(line_dict["INPUT_LOAD"])*input_load_pF
                                output_rise_trans_max[data_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                                output_rise_trans_min[data_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                                output_delay_max[data_pin_name] = [float(line_dict["Tsetup_max"])*tsetup_max_ns,line_dict["Edge"]]         
                                output_delay_min[data_pin_name] = [float(line_dict["Thold_min"])*thold_min_ns,line_dict["Edge"]]                                    
            elif m1:# without ID flag
                if bus_msb != "None" and bus_lsb != "None":
                    for h in range(bus_lsb,bus_msb+1): #bus width
                        data_pin_name = real_pin_name+"["+str(h)+"]"                                
                        related_clock[data_pin_name] = line_dict["CLOCK_DOMAIN"]
                        load_max[data_pin_name] = float(line_dict["INPUT_LOAD"])*input_load_pF
                        output_rise_trans_max[data_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                        output_rise_trans_min[data_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                        output_delay_max[data_pin_name] = [float(line_dict["Tsetup_max"])*tsetup_max_ns,line_dict["Edge"]]         
                        output_delay_min[data_pin_name] = [float(line_dict["Thold_min"])*thold_min_ns,line_dict["Edge"]]
                elif bus_msb == "None" and bus_lsb == "None": #1bit data without <>
                    data_pin_name = real_pin_name
                    related_clock[data_pin_name] = line_dict["CLOCK_DOMAIN"]
                    load_max[data_pin_name] = float(line_dict["INPUT_LOAD"])*input_load_pF
                    output_rise_trans_max[data_pin_name] = float(line_dict["Trise_max"])*Trise_max_ns
                    output_rise_trans_min[data_pin_name] = float(line_dict["Trise_min"])*Trise_min_ns
                    output_delay_max[data_pin_name] = [float(line_dict["Tsetup_max"])*tsetup_max_ns,line_dict["Edge"]]         
                    output_delay_min[data_pin_name] = [float(line_dict["Thold_min"])*thold_min_ns,line_dict["Edge"]]
        print("line_dict             : {}".format(line_dict),file=fout1)
        
        
with open("temp2.log","w+") as fout2:
    print("create_clock          : {}".format(create_clock),file=fout2)
    print("input_cap_max         : {}".format(input_cap_max),file=fout2)
    print("input_cap_min         : {}".format(input_cap_min),file=fout2)
    print("input_rise_trans_max  : {}".format(input_rise_trans_max),file=fout2)
    print("input_fall_trans_max  : {}".format(input_fall_trans_max),file=fout2)
    print("input_rise_trans_min  : {}".format(input_rise_trans_min),file=fout2)
    print("input_fall_trans_min  : {}".format(input_fall_trans_min),file=fout2)
    print("related_clock         : {}".format(related_clock),file=fout2)
    print("load_max              : {}".format(load_max),file=fout2)
    print("output_rise_trans_max : {}".format(output_rise_trans_max),file=fout2)
    print("output_rise_trans_min : {}".format(output_rise_trans_min),file=fout2)
    print("output_delay_max      : {}".format(output_delay_max),file=fout2)         
    print("output_delay_min      : {}".format(output_delay_min),file=fout2)
    print("input_delay_max       : {}".format(input_delay_max),file=fout2)  
    print("input_delay_min       : {}".format(input_delay_min),file=fout2)

    
