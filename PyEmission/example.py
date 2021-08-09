from pyemission import GV
   
# Create a Gasoline vehicle and read data
g = GV("Data.xlsx", "Driving cycle", mass=1600)

print('\n\nGeneral statistics of the driving cycle\n-------------------------------------------------')
print(f'Distance traveled                       : {g.distance()} km')
print(f'Average speed                           : {g.average_speed()} KMPH')
print(f'Standaed deviation of speed             : {g.speed_std()} KMPH')
print(f'Number of stops per kilometer           : {g.no_of_stops_per_km()}')
print(f'Average acceleration                    : {g.acc_avg()} m/s2')
print(f'Average deceleration                    : {g.dec_avg()} m/s2')
print(f'Percentage of time on acceleration mode : {g.acc_mode()}%')
print(f'Percentage of time on deceleration mode : {g.dec_mode()}%')
print(f'Percetage of time on idling mode        : {g.idling_mode()}%')

print('\n\nStatistics for Gasoline vehicle\n-------------------------------------------------')
print(f'Tailpipe CO2 emission                   : {g.pump_to_wheel_CO2()} grams')
print(f'Tailpipe CO emission                    : {g.pump_to_wheel_CO()} grams')
print(f'Tailpipe NOx emission                   : {g.pump_to_wheel_NOx()} grams')
print(f'Tailpipe HC emission                    : {g.pump_to_wheel_HC()} grams')

print(f'Tailpipe CO2 emission per km            : {g.pump_to_wheel_CO2_per_km()} grams/km')
print(f'Tailpipe CO  emission per km            : {g.pump_to_wheel_CO_per_km()} grams/km')
print(f'Tailpipe NOx emission per km            : {g.pump_to_wheel_NOx_per_km()} grams/km')
print(f'Tailpipe HC  emission per km            : {g.pump_to_wheel_HC_per_km()} grams/km')

print(f'Well to Pump CO2 emission               : {g.well_to_pump_CO2()} grams')
print(f'Well to Wheel CO2 emission              : {g.well_to_wheel_CO2()} grams')
print(f'Well to Wheel CO2 emission per km       : {g.well_to_wheel_CO2_per_km()} grams/km')

print(f'Fuel burnt                              : {g.fuel_burnt()} ml')
print(f'Miles per Gallon (MPG)                  : {g.mpg()}')


#%%

#Time plot of the driving cycle
g.plot_driving_cycle()

#Time plot of the tractive power
g.plot_tractive_power()

#Speed distribution
g.plot_speed_histogram()