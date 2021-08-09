import pickle
import matplotlib.pyplot as plt
plt.style.use('seaborn')
from matplotlib.gridspec import GridSpec
from utility_functions import read_data, calculate_tractive_power, calculate_vsp, vsp_to_op_mod, op_mod_to_emission_rate, joule_to_kwh, convert_to_overall_mpg, energy_kj_to_ml, vsp_coeff, progress_bar

# generic vehicle class
class Car:

    def __init__(self, excel_file_name, sheet_name, mass, frontal_area, mu_rr, air_density, c_d):
        
        """
            excel_file_name (string)  : name of the excel file which contains the driving cycle data
            sheet_name      (string)  : name of the 'sheet' inside the excel file, which contains the driving cycle data.
                                        The provided excel file format is recommended to use. The 'sheet' should have the below 4 columns-
                                        time: in second
                                        speed: in meter per second
                                        time_unit : use the drop down list to choose the appropriate unit
                                        speed_unit : use the dropdown list to choose the appropriate unit                           
                                                    
        
            mass            (numeric) : vehicle mass with cargo in kg
            frontal_area    (numeric) : vehicle frontal area in square meter
            mu_rr           (numeric) : rolling resistance coefficient between tire and road surface
            air_density     (numeric) : ambient air density in kg/m3
            c_d             (numeric) : aerodynamic drag coefficient
            
        """
        print('Loading Data...\n')
        df = read_data(excel_file_name, sheet_name)
        vehicle = df.vehicle_type[0]
        if vehicle == 'Light commercial truck' :
            try:
                df_emission_rate = pickle.load(open('db.pkl','rb'))[0]
            except:
                print('Could not load the file: db.pkl\nMake sure the working directory contains this file.')
        else:
            try:
                df_emission_rate = pickle.load(open('db.pkl','rb'))[1]
            except:
                print('Could not load the file: db.pkl\nMake sure the working directory contains this file.')
        
        # VSP coefficients
        A, B, C, f = vsp_coeff(vehicle)
        self.df_emission_rate = df_emission_rate
        self.A = A
        self.B = B
        self.C = C
        self.M = mass/1000  # unit: ton
        self.f = f
        
        
        # df = read_data(excel_file_name, sheet_name)
       
        self.t  = df.shape[0] # travel time
        self.m = mass
        self.d = df.speed.sum()/1000 # travelled distance in kilometer
        self.frontal_area = frontal_area
        self.mu_rr = mu_rr
        self.air_density = air_density
        self.c_d = c_d


        print('Application Running...')        
        # add acceleration column to the main df
        print("\nPart [1/3]:")
        v_0 = df.speed[0]     
        for row in df.itertuples():
            idx = row.Index
            v = row.speed
            
            if idx == 0:
                a = 0
            else:
                a = v - v_0
                v_0 = v
            df.loc[idx, "acc"] = a
            
            ##put a progress bar
            total_iteration = self.t
            progress_bar(total_iteration, idx + 1)
        

           

        # add tractive_power columns to the main df
        print("\nPart [2/3]:")     
        for row in df.itertuples():
            idx = row.Index
            v = row.speed
            a = row.acc

            p_tract = calculate_tractive_power (v, a, mass, frontal_area, mu_rr, air_density, c_d)
            df.loc[idx, "p_tract"]                  = p_tract
            
            ##put a progress bar
            total_iteration = self.t
            progress_bar(total_iteration, idx + 1)
            
   
        self.df = df

           
            
    #travelled distance------------------------
    def distance(self):
        """
        Return travelled distance in kilometer
        """
        return round(self.d, 3)
    
    # average speed----------------------------
    def average_speed(self):
        return round( self.d/(self.t/3600), 3)
    
    # stops per kilometer----------------------------
    def no_of_stops_per_km(self):
        no_of_stops = 0
        flag = False
        for v in self.df.speed:
            v_fps = v*3.28084
            if v_fps >= 15:
                flag = True
            if v_fps <10 and flag == True:
                no_of_stops += 1
                flag = False
        return round(no_of_stops/self.d, 3)
    
    # idle time percentage-----------------------------
    def idling_mode(self): 
        idle_time = 0
        for v in self.df.speed:
            if v <= 0.1:
                idle_time += 1
        return round( idle_time*100/self.t, 3 )    

    # average acceleration --------------------------
    def acc_avg(self):
        return round( self.df.acc[ self.df.acc > 0].mean(), 3 )
    
    # average decceleration --------------------------
    def dec_avg(self):
        return round( self.df.acc[ self.df.acc < 0].mean(), 3 )
    
    # acceleration mode percentage --------------------------
    def acc_mode(self):
        return round( self.df.acc[ self.df.acc > 0].count()*100/self.t, 3 )
    
    # deceleration mode percentage --------------------------
    def dec_mode(self):
        return round( self.df.acc[ self.df.acc < 0].count()*100/self.t, 3 )

    # speed standard deviation --------------------------
    def speed_std(self):
        speed_kmph = self.df.speed*3.6
        return round( speed_kmph.std(), 3)
    
    
    def plot_driving_cycle(self):
        
        fig = plt.figure(dpi = 300, constrained_layout=True, figsize=(7,3))
        gs = GridSpec(1, 1, figure=fig)
        ax = fig.add_subplot(gs[0, 0])
        
        font_size=12 #font size
        line_weight=1.5
        
        ax.set_xlabel('Time (s)', fontweight='bold')
        ax.set_ylabel('Speed (KMPH)', color='k', fontweight='bold')
        ax.plot(self.df['time'], self.df['speed']*3.6, color='r', linewidth=line_weight)
        ax.tick_params(axis='y', labelcolor='k')
        ax.set_title('Driving Cycle Plot', color='b', fontsize=font_size, fontweight='bold')
        plt.show()
        
        
    def plot_tractive_power(self):
        fig = plt.figure(dpi = 300, constrained_layout=True, figsize=(9,2))
        gs = GridSpec(1, 1, figure=fig)
        ax = fig.add_subplot(gs[0, 0])
        
        font_size=12 #font size
        alpha = 0.7
        x=self.df['time']
        y=self.df['p_tract']/1000 # convert to kilowatt
        y1 = self.df.speed*0
        
        ax.set_xlabel('Time (s)', fontweight='bold')
        ax.set_ylabel('Tractive power\n(kilowatt)', color='k', fontweight='bold')
        #ax.plot(x, y, color='k', linewidth=.5)
        ax.axhline(color='k', linewidth=.5)
        ax.fill_between(x, y, y1, where=y > y1, facecolor = 'm', interpolate=True, label='Positive tractive power', alpha=alpha)
        ax.fill_between(x, y, y1, where=y < y1, facecolor = 'b',  interpolate=True, label='Negative tractive power', alpha=alpha)
        ax.tick_params(axis='y', labelcolor='k')
        ax.set_title('Tractive power Plot', color='b', fontsize=font_size, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.01, 1.5), loc='upper right', ncol=1)
        plt.show()


    def plot_speed_histogram(self, bins=30):
        """
        bins : number of bins. The default value is set as 30
        """
        fig = plt.figure(dpi = 300, constrained_layout=True, figsize=(5,3))
        gs = GridSpec(1, 1, figure=fig)
        ax = fig.add_subplot(gs[0, 0])
        
        x = self.df.speed*3.6 # converted to kmph from mps
        ax.hist(x, edgecolor='w', bins=bins, density=True, alpha=1)
        ax.set_xlabel('Speed (kmph)', fontweight='bold')
        ax.set_ylabel('Probability density', color='k', fontweight='bold')
        ax.set_title('Distribution of speed', color='b', fontsize=12, fontweight='bold')
        plt.show()
    
#------------------------------------------------------------------------------
# gasoline vehicle class
class GV(Car):

    def __init__(self,
                 excel_file_name = 'Data.xlsx',
                 sheet_name = 'Driving cycle',
                 mass = 1500,
                 frontal_area =2.27,
                 mu_rr =0.0127,
                 air_density =1.18,
                 c_d =0.28,
                 well_to_tank_CO2_emission_factor = 16.79                 
                 ):
        
        """
        excel_file_name (string)  : name of the excel file which contains the driving cycle data
        sheet_name      (string)  : name of the 'sheet' inside the excel file, which contains the driving cycle data.
                                    The provided excel file format is recommended to use. The 'sheet' should have the below 4 columns-
                                    time: in second
                                    speed: in meter per second
                                    time_unit : use the drop down list to choose the appropriate unit
                                    speed_unit : use the dropdown list to choose the appropriate unit                           
                                                
    
        mass                            (numeric) : vehicle mass with cargo in kg
        frontal_area                    (numeric) : vehicle frontal area in square meter
        mu_rr                           (numeric) : rolling resistance coefficient between tire and road surface
        air_density                     (numeric) : ambient air density in kg/m3
        c_d                             (numeric) : aerodynamic drag coefficient
        well_to_tank_CO2_emission_factor (numeric): typical value is 16.79 gm/MJ
            
        """
        
        super().__init__(excel_file_name, sheet_name, mass, frontal_area, mu_rr, air_density, c_d)
        self.well_to_tank_CO2_emission_factor = well_to_tank_CO2_emission_factor
        
        # add vsp, emission, and energy_kj columns to the main df
        print('\nPart [3/3]')
        for row in self.df.itertuples():
            idx = row.Index
            v = row.speed
            a = row.acc

            vsp = calculate_vsp (v, a, self.M, self.A, self.B, self.C, self.f)
            
            # calculate op_mod
            speed_t = v
            acc_t = a
            try:
                acc_t_1 = self.df.acc[idx - 1]
            except:
                acc_t_1 = 0
            try:
                acc_t_2 = self.df.acc[idx - 2]
            except:
                acc_t_2 = 0
            op_mod = vsp_to_op_mod (vsp, speed_t, acc_t, acc_t_1, acc_t_2)
            
            CO2                     = op_mod_to_emission_rate (self.df_emission_rate, op_mod, 'CO2')
            CO                      = op_mod_to_emission_rate (self.df_emission_rate, op_mod, 'CO')
            NOx                     = op_mod_to_emission_rate (self.df_emission_rate, op_mod, 'NOx')
            HC                      = op_mod_to_emission_rate (self.df_emission_rate, op_mod, 'HC')
            PM2_5_elemental_carbon  = op_mod_to_emission_rate (self.df_emission_rate, op_mod, 'PM2.5_elemental_carbon')
            PM2_5_organic_carbon    = op_mod_to_emission_rate (self.df_emission_rate, op_mod, 'PM2.5_organic_carbon')
           
            
            self.df.loc[idx, "vsp"]                      = vsp
            self.df.loc[idx, "op_mod"]                   = op_mod
            self.df.loc[idx, "CO2"]                      = CO2
            self.df.loc[idx, "CO"]                       = CO
            self.df.loc[idx, "NOx"]                      = NOx
            self.df.loc[idx, "HC"]                       = HC
            self.df.loc[idx, "PM2.5_elemental_carbon"]   = PM2_5_elemental_carbon
            self.df.loc[idx, "PM2.5_organic_carbon"]     = PM2_5_organic_carbon

            
            ##put a progress bar
            total_iteration = self.t
            progress_bar(total_iteration, idx + 1)
        
    
        
        
    def pump_to_wheel_CO2(self):
        CO2_sum = self.df.CO2.sum()
        return round(CO2_sum, 3)
    
    def pump_to_wheel_CO(self):
        CO_sum = self.df.CO.sum()
        return round(CO_sum, 3)
    
    def pump_to_wheel_NOx(self):
        NOx_sum = self.df.NOx.sum()
        return round(NOx_sum, 3)
    
    def pump_to_wheel_HC(self):
        HC_sum = self.df.HC.sum()
        return round(HC_sum, 3)
 
    def pump_to_wheel_CO2_per_km(self):
        value = self.pump_to_wheel_CO2()/self.d
        return round(value, 3)    
 
    def pump_to_wheel_CO_per_km(self):
        value = self.pump_to_wheel_CO()/self.d
        return round(value, 3)    
 
    def pump_to_wheel_NOx_per_km(self):
        value = self.pump_to_wheel_NOx()/self.d
        return round(value, 3)   
 
    def pump_to_wheel_HC_per_km(self):
        value = self.pump_to_wheel_HC()/self.d
        return round(value, 3)   
 
    
    def fuel_burnt(self):
        HC = self.pump_to_wheel_NOx()
        CO = self.pump_to_wheel_CO()
        CO2 = self.pump_to_wheel_CO2()
        density = 750
        W_c = 0.866
        fuel_sum = (0.866*HC + 0.429*CO + 0.273*CO2)*1000/(density*W_c)
        return round(fuel_sum, 3)
    
    def mpg(self):
        fuel = self.fuel_burnt()
        value = (self.d/1.60934)/(fuel/3785.412)
        return round(value, 3)


    def well_to_pump_CO2(self):
        gasoline = self.fuel_burnt()
        value = gasoline*34.2*self.well_to_tank_CO2_emission_factor/1000
        return round(value, 3)
        
    def well_to_wheel_CO2(self):
        value = self.pump_to_wheel_CO2() + self.well_to_pump_CO2()
        return round(value, 3)
    
    def well_to_wheel_CO2_per_km(self):
        value = self.well_to_wheel_CO2()/self.d
        return round(value, 3)


     
#------------------------------------------------------------------------------
if __name__ == '__main__':    
    
    g = GV("Data.xlsx", "Driving cycle", mass=2850)
    
    g.plot_driving_cycle()
    g.plot_tractive_power()
    g.plot_speed_histogram()
    
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
    
