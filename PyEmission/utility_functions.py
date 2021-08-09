
import pandas as pd


#%%
# Read data with columns 'time' and 'speed'
def read_data(excel_file_name, sheet_name):
    try:
        df = pd.read_excel(io = excel_file_name,
                           sheet_name= sheet_name,
                           header=0)
    
        #convert speed to 'meter per second' if it is in another unit
        conversion_factor_dict = {
          "meter per second": 1,
          "kilometer per hour": 0.277778,
          "mile per hour": 0.44704
        }
        
        conversion_factor = conversion_factor_dict[df.speed_unit[0]]  
        df.speed = df.speed*conversion_factor
        
        print('Loading data was successful\n')
        return df
    
    except:
        print('''** WARNING:
              UNABLE TO READ THE INPUT DATA FILE.
              PLEASE USE THE PROVIDED EXCEL FILE FORMAT AND
              CLOSE THE EXCEL FILE BEFORE RUNNING THE PROGRAM.\n\n\n\n\n''')


#%%
# Meter per second to mile per hour
def mps_to_mph (mps):
    mph = 2.23694 * mps
    return mph

# acceleration m/s^2 to mph/s
def mps2_to_mph_per_sec (mps2):
    mph_per_sec =  2.23694 * mps2
    return mph_per_sec

def energy_kj_to_ml (energy_kj):
    value = 3785.41/131760
    return value
    
#%%
def calculate_tractive_power (v, a, mass, frontal_area, mu_rr, air_density, c_d):
    
    tractive_power = v*mass*(a + mu_rr*9.81) + 0.5*air_density*c_d*frontal_area*pow(v, 3)  
    
    return tractive_power


#%%
def calculate_vsp (v, a, mass, A, B, C, f):
    
    vsp = (A*v + B*v**2 + C*v**3 + mass*a*v)/f
    
    return vsp


#%%
def vsp_to_op_mod (vsp, speed_t, acc_t, acc_t_1, acc_t_2):
    
    speed_t = mps_to_mph(speed_t)
    acc_t = mps2_to_mph_per_sec(acc_t)
    acc_t_1 = mps2_to_mph_per_sec(acc_t_1)
    acc_t_1 = mps2_to_mph_per_sec(acc_t_2)
    
    if acc_t <= -2 or (acc_t <= -1 and acc_t_1 <= -1 and acc_t_2 <= -1):
        op_mod = 0
    elif speed_t < 1:
        op_mod = 1
    else:
        if speed_t <= 25:
            if vsp < 0:
                op_mod = 11
            elif 0 <= vsp < 3:
                op_mod = 12
            elif 3 <= vsp < 6:
                op_mod = 13
            elif 6 <= vsp < 9:
                op_mod = 14
            elif 9 <= vsp < 12:
                op_mod = 15
            else:
                op_mod = 16
        elif 25 < speed_t <= 50:
            if vsp < 0:
                op_mod = 21
            elif 0 <= vsp < 3:
                op_mod = 22
            elif 3 <= vsp < 6:
                op_mod = 23
            elif 6 <= vsp < 9:
                op_mod = 24
            elif 9 <= vsp < 12:
                op_mod = 25
            elif 12 <= vsp < 18:
                op_mod = 27
            elif 18 <= vsp < 24:
                op_mod = 28
            elif 24 <= vsp < 30:
                op_mod = 29
            else:
                op_mod = 30
        else:
            if vsp < 6:
                op_mod = 33
            elif 6 <= vsp < 12:
                op_mod = 35
            elif 12 <= vsp < 18:
                op_mod = 37
            elif 18 <= vsp < 24:
                op_mod = 38
            elif 24 <= vsp < 30:
                op_mod = 39
            else:
                op_mod = 40
                
    return op_mod

#%%
def op_mod_to_emission_rate (df_emission_rate, op_mod, pollutant_name):
    
    value = df_emission_rate.loc[op_mod, pollutant_name]
    
    return value  
                   

#%%
def joule_to_kwh(joule):
    
    return joule/(3.6*pow(10, 6))

#%%
def convert_to_overall_mpg(distance, gasoline_ml, electricity_kwh):
    
    gallon_to_kwh = 33.7	#https://www.fueleconomy.gov/feg/noframes/41133.shtml
    
    return (distance/1.60934)/(gasoline_ml/3785.412 + electricity_kwh/gallon_to_kwh)


#%%
def vsp_coeff(vehicle_type):
    if vehicle_type == 'Passenger car':
        A = 0.156461	
        B = 0.002002	
        C = 0.000493	
        f = 1.4788

    elif vehicle_type == 'Passenger truck' or 'SUV':
        A = 0.22112	
        B = 0.002838	
        C = 0.000698	
        f = 1.86686
    # elif vehicle_type == 'Light commercial truck':
    else:
        A = 0.235008	
        B = 0.003039	
        C = 0.000748	
        f = 2.05979
    return A, B, C, f


#%%

# create a progress bar
import sys
# import time


def progress_bar(total_iteration, current_iteration):

    barLength = 50
    status = "complete"
    current_iteration = float(current_iteration) / float(total_iteration)
    if current_iteration >= 1.:
        current_iteration, status = 1, "\r\n"
    block = int(round(barLength * current_iteration))
    text = "\rProgress: [{}] {:.0f}% {}".format(
        "#" * block + "-" * (barLength - block), round(current_iteration * 100, 0),
        status)
    sys.stdout.write(text)
    sys.stdout.flush()





