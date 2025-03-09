import streamlit as st
from langchain.llms import Ollama
import sqlite3
import pandas as pd
import plotly.express as px

# Database path
database_path = 'tml_cesl_final_data_acsentsarthi.db'

# Prompt template for the LLM
prompt_template = """
You are an expert SQL developer and data visualization specialist. Your role is to accurately translate user questions into optimized SQL queries and recommend the best visualization type for effective data interpretation. The database, named `tml_cesl_final_data_acsentsarthi.db`, contains the following three key tables:

Your task is to convert a natural language request into an optimized SQL query. The query should strictly follow SQL syntax and best practices while handling missing fields and edge cases effectively.
 
Guidelines:
Understand the User's Intent
 
Carefully analyze the request to identify the required fields, filters, conditions, and operators.
Distinguish between search, aggregation, and filtering tasks.
SQL Query Construction
 
 1. Use standard SQL syntax without backticks (\\) around field names.
 2. Use SQL features such as DISTINCT, JOIN, LAG, LEAD and SUBQUERIES.
 3. If uniqueness is required, use **'GROUP BY'** or **'DISTINCT'**.
 4. Use SELECT statements to fetch relevant fields.
 5. Apply filtering conditions correctly using WHERE.
 6. Implement aggregations (e.g., AVG(), SUM(), COUNT(), MIN(), MAX()) following Elasticsearch SQL standards.
 7. The output should contain **only one** valid ELK SQL query without additional text.
 8. Use 'date_histogram' aggregation to group data by month.
 9. Return only aggregated results without individual documents.
 10. Optionally, allow filtering for a specific year.
 11. The output should be the ELK SQL query that starts with **SELECT...**
 
 ### **Output Format:**
 Generate a single, valid SQL query with no additional text or explanations.
 
 Following is the Table Schema:
 
Table Name: energy_data
Columns Name:                            Description
- A_KWh_Remain_End                       Energy efficiency of category A (kWh per km) at the end of a trip.
- A_KWh_Remain_start                     Energy efficiency of category A (kWh per km) at the start of a trip.
- B_KWh_Remain_End                       Energy efficiency of category B (kWh per km) at the end of a trip.
- B_KWh_Remain_start                     Energy efficiency of category B (kWh per km) at the start of a trip.
- C_KWh_Remain_End                       Energy efficiency of category C (kWh per km) at the end of a trip
- C_KWh_Remain_start                     Energy efficiency of category C (kWh per km) at the start of a trip.
- DLR_NAME                               Name of the dealer associated with the vehicle                                  
- DLR_ORG_CITY                           City where the dealer is located.
- DLR_REGION                             Region of the dealer
- DLR_STATE                              State of the dealer
- D_KWh_Remain_End                       Energy efficiency of category D (kWh per km) at the end of a trip
- D_KWh_Remain_start                     Energy efficiency of category C (kWh per km) at the start of a trip
- Depot_Name                             Name of the vehicle's depot.
- FIRST_SALE_DT                          Date when the vehicle was first sold.
- LOB                                    Line of Business.
- NetkWh                                 Net energy consumption in kWh.
- PL                                     Product Line.
- PPL                                    Parent Product Line.
- Range                                  Estimated remaining range of the vehicle  
- Smart_City                             indicates if the vehicle is part of a smart city initiative
- VCU_BMS_No_of_Packs                    Number of battery packs in the vehicle.
- acConsumption                          Air conditioning power consumption
- acConsumption_Fr                       Air conditioning power consumption (fractional value).
- acConsumption_km                       Air conditioning power consumption per km
- acLoadDrive                            AC load while driving.                            
- acLoadDrive_km                         AC load per km while driving.
- acLoadIdle                             AC load while idle.
- acLoadIdle_km                          AC load per km while idle.
- air_ventilation                        Air ventilation system status or consumption.
- aux1Load                               Auxiliary Load 1 consumption and efficiency
- aux1Load_Fr                            Auxiliary Load 1 consumption and efficiency fractional load                          
- aux1Load_km                            Auxiliary Load 1 consumption and efficiency per km
- aux2Load                               Auxiliary Load 2 consumption and efficiency
- aux2Load_Fr                            Auxiliary Load 1 consumption and efficiency fractional load
- aux2Load_km                            Auxiliary Load 1 consumption and efficiency per km
- bcs1Load                               Battery Charging System 1 load and efficiency
- bcs1Load_Fr                            Battery Charging System 1 load and efficiency fractional load
- bcs1Load_km                            Battery Charging System 1 load and efficiency per km                                            
- bcs2Load                               Battery Charging System 2 load and efficiency                              
- bcs2Load_Fr                            Battery Charging System 2 load and efficiency fractional load                                                                                
- bcs2Load_km                            Battery Charging System 2 load and efficiency per km                        
- dataCons_kWh                           Total data consumption in kWh                          
- dataCons_kWh_Fr                        Fractional data consumption in kWh  
- dataCons_kWh_km                        Data consumption per km in kWh
- dataNet_kWh                            Net data energy usage in kWh  
- dataNet_kWh_km                         Net data energy usage per km
- dataRegen_kWh                          Total regenerated energy in kWh  
- dataRegen_kWh_Fr                       Fractional regenerated energy in kWh
- dataRegen_kWh_km                       Regenerated energy per km in kWh  
- dcdcLoad                               DC-DC converter load
- dcdcLoad_Fr                            DC-DC converter fractional load  
- dcdcLoad_km                            DC-DC converter load per km
- deltaDte                               Time difference between two events.
- dischargeSoc                           Battery discharge during the trip  
- distanceInKM                           Total distance traveled during the trip (in km)
- endDte                                 End date of the trip  
- endOdo                                 Odometer reading at the end of the trip
- endSoc                                 Battery state of charge (SOC) at the end of the trip  
- endTime                                End time of the trip
- error                                  Error codes or messages related to vehicle operation
- errorDte                               Date of the error occurrence  
- eventdate                              Date of the event logged in the system
- kwh_km                                 Energy consumption in kWh per km
- monthId                                Identifier for the month of the trip
- motorConsumption                       Total motor power consumption
- motorConsumption_Fr                    Fractional motor power consumption
- motorConsumption_km                    Motor power consumption per km  
- product_line                           Specific category of the product    
- remLoad                                Remaining load  
- remLoad_km                             Remaining load per km
- rn                                     Record number or unique row identifier
- startDte                               Start date of the trip
- startOdo                               Odometer reading at the start of the trip  
- startSoc                               Battery state of charge (SOC) at the start of the trip
- startTime                              Start time of the trip  
- totalTimeInSec                         Total duration of the trip in seconds
- unique_id                              Unique identifier for the record  
- vehicleId                              Unique identifier for the vehicle  
- vehicle_registration_number            Registration number of the vehicle          
- whPerKM                                Energy consumption in watt-hours per km  


Table: discharge_table
Contains energy discharge details.
Columns Name                          Description
- A_KWh_Remain_End                       Energy efficiency of category A (kWh per km) at the end of a trip.
- A_KWh_Remain_start                     Energy efficiency of category A (kWh per km) at the start of a trip.
- B_KWh_Remain_End                       Energy efficiency of category B (kWh per km) at the end of a trip.
- B_KWh_Remain_start                     Energy efficiency of category B (kWh per km) at the start of a trip.
- C_KWh_Remain_End                       Energy efficiency of category C (kWh per km) at the end of a trip
- C_KWh_Remain_start                     Energy efficiency of category C (kWh per km) at the start of a trip.
- DLR_NAME                               Name of the dealer associated with the vehicle                                  
- DLR_ORG_CITY                           City where the dealer is located.
- DLR_REGION                             Region of the dealer
- DLR_STATE                              State of the dealer
- D_KWh_Remain_End                       Energy efficiency of category D (kWh per km) at the end of a trip
- D_KWh_Remain_start                     Energy efficiency of category C (kWh per km) at the start of a trip
- Depot_Name                             Name of the vehicle’s depot.
- FIRST_SALE_DT                          Date when the vehicle was first sold.
- LOB                                    Line of Business.
- NetkWh                                 Net energy consumption in kWh.
- PL                                     Product Line.
- PPL                                    Parent Product Line.
- Range                                  Estimated remaining range of the vehicle  
- Smart_City                             indicates if the vehicle is part of a smart city initiative
- VCU_BMS_No_of_Packs                    Number of battery packs in the vehicle.
- air_ventilation                        Air ventilation system status or consumption 
- dataCons_kWh                           Total data consumption in kWh                          
- dataCons_kWh_Fr                        Fractional data consumption in kWh  
- dataCons_kWh_km                        Data consumption per km in kWh 
- dataNet_kWh                            Net data energy usage in kWh  
- dataNet_kWh_km                         Net data energy usage per km 
- dataRegen_kWh                          Total regenerated energy in kWh  
- dataRegen_kWh_km                       Regenerated energy per km in kWh 
- deltaDte                               Time difference between two events.
- dischargeSoc                           Battery discharge during the trip  
- distanceInKM                           Total distance traveled during the trip (in km) 
- endDte                                 End date of the trip  
- endOdo                                 Odometer reading at the end of the trip 
- endSoc                                 Battery state of charge (SOC) at the end of the trip   
- endTime                                End time of the trip 
- errorDte                               Date of the error occurrence 
- eventdate                              Date of the event logged in the system
- monthId                                Identifier for the month of the trip 
- product_line                           Specific category of the product    
- rn                                     Record number or unique row identifier
- startDte                               Start date of the trip 
- startOdo                               Odometer reading at the start of the trip  
- startSoc                               Battery state of charge (SOC) at the start of the trip
- startTime                              Start time of the trip  
- totalTimeInSec                         Total duration of the trip in seconds 
- unique_id                              Unique identifier for the record  
- vehicleId                              Unique identifier for the vehicle  
- vehicle_registration_number            Registration number of the vehicle           
- whPerKM                                Energy consumption in watt-hours per km  

Table Name: charging_table
Contains charging session details.
Columns Name                          Description

- A_KWh_Remain_start                     Category A energy efficiency at the start (kWh per km)  
- A_KWh_Remain_End                       Category A energy efficiency at the end (kWh per km)  
- A_Max_Cell_Temp                        Maximum cell temperature in category A  
- A_Max_Cell_Volt                        Maximum cell voltage in category A  
- A_Min_Cell_Volt                        Minimum cell voltage in category A  
- B_KWh_Remain_start                     Category B energy efficiency at the start (kWh per km)  
- B_KWh_Remain_End                       Category B energy efficiency at the end (kWh per km)  
- B_Max_Cell_Temp                        Maximum cell temperature in category B  
- B_Max_Cell_Volt                        Maximum cell voltage in category B  
- B_Min_Cell_Volt                        Minimum cell voltage in category B  
- C_KWh_Remain_start                     Category C energy efficiency at the start (kWh per km)  
- C_KWh_Remain_End                       Category C energy efficiency at the end (kWh per km)  
- C_Max_Cell_Temp                        Maximum cell temperature in category C  
- C_Max_Cell_Volt                        Maximum cell voltage in category C  
- C_Min_Cell_Volt                        Minimum cell voltage in category C  
- DLR_NAME                               Name of the dealer associated with the vehicle                                  
- DLR_ORG_CITY                           City where the dealer is located.
- DLR_REGION                             Region of the dealer
- DLR_STATE                              State of the dealer
- D_KWh_Remain_start                     Category D energy efficiency at the start (kWh per km)  
- D_KWh_Remain_End                       Category D energy efficiency at the end (kWh per km)  
- D_Max_Cell_Temp                        Maximum cell temperature in category D  
- D_Max_Cell_Volt                        Maximum cell voltage in category D  
- D_Min_Cell_Volt                        Minimum cell voltage in category D 
- Depot_Name                             Name of the vehicle’s depot.
- FIRST_SALE_DT                          Date when the vehicle was first sold.
- InterruptDuration                      Total duration of charging interruptions  
- InterruptDurationInMin                 Charging interruption duration in minutes
- LOB                                    Line of Business.
- NoOfInterrupt                          Total number of charging interruptions  
- NoOfInterrupt_in                       Internal count of interruptions 
- LastChargeTime                         Timestamp of the last completed charge  
- LastInterrupttime                      Timestamp of the last charging interruption 
- PL                                     Product Line category  
- PPL                                    Parent Product Line  
- Smart_City                             Indicates if the vehicle is part of a smart city initiative  
- air_ventilation                        Air ventilation system status or consumption  
- avgChargingCurrent                     Average charging current during the session  
- chargeDurationInMin                    Total charging duration in minutes  
- delta_soc                              Change in state of charge during charging  
- eventdate                              Date of the charging event  
- fistChargeTime                         Timestamp of the first charge event  
- fullcharge                             Flag indicating if the battery was fully charged  
- fullcharge_old                         Previous full charge status  
- gunAfterfullcharge                     Time elapsed after full charge before unplugging  
- gunAfterfullchargeInMin                Time elapsed (in minutes) after full charge  
- gunAfterfullchargeInMin_old            Previous time elapsed after full charge  
- gunAfterfullcharge_old                 Previous full charge unplugging status  
- gunDurationInMin                       Total duration of charging gun being connected  
- gun_end                                Timestamp when charging gun was removed  
- gun_start                              Timestamp when charging gun was plugged in  
- kwhCharged                             Total energy charged in kilowatt-hours (kWh)  
- monthId                                Identifier for the month of the charging event  
- product_line                           Specific category of the product  
- rn                                     Record number or unique row identifier  
- roc                                    Rate of charge change  
- signal_occurence_count                 Number of times a signal occurred during charging  
- signal_occurence_name                  Name of the signal occurrence  
- soc_end                                Battery state of charge (SOC) at the end of charging  
- soc_start                              Battery state of charge (SOC) at the start of charging  
- unique_id                              Unique identifier for the record  
- vehicleId                              Unique identifier for the vehicle  
- vehicle_registration_number            Registration number of the vehicle 

Table Name: soh_table
Contains State of Health (SOH) data of vehicle batteries.

Columns Name                        Description
- A_SOH_Value                          State of Health (SOH) value for Pack A  
- Avg_of_Pack_A_Charge_Temp            Average charging temperature of Pack A  
- Avg_of_Pack_A_Discharge_Temp         Average discharging temperature of Pack A  
- Avg_of_Pack_B_Charge_Temp            Average charging temperature of Pack B  
- Avg_of_Pack_B_Discharge_Temp         Average discharging temperature of Pack B  
- Avg_of_Pack_C_Charge_Temp            Average charging temperature of Pack C  
- Avg_of_Pack_C_Discharge_Temp         Average discharging temperature of Pack C  
- Avg_of_Pack_D_Charge_Temp            Average charging temperature of Pack D  
- Avg_of_Pack_D_Discharge_Temp         Average discharging temperature of Pack D  
- B_SOH_Value                          State of Health (SOH) value for Pack B  
- C_SOH_Value                          State of Health (SOH) value for Pack C  
- DLR_NAME                             Name of the dealer associated with the vehicle  
- DLR_ORG_CITY                         City where the dealer is located  
- DLR_REGION                           Region of the dealer  
- DLR_STATE                            State of the dealer  
- D_SOH_Value                          State of Health (SOH) value for Pack D  
- Depot_Name                           Name of the vehicle’s depot  
- Energy_consumption                   Total energy consumed by the vehicle  
- FIRST_SALE_DT                        Date when the vehicle was first sold  
- LOB                                  Line of Business the vehicle belongs to  
- Median_of_Max_Pack_A_Charge_Temp     Median of the maximum charging temperature for Pack A  
- Median_of_Max_Pack_A_Discharge_Temp  Median of the maximum discharging temperature for Pack A  
- Median_of_Max_Pack_B_Charge_Temp     Median of the maximum charging temperature for Pack B  
- Median_of_Max_Pack_B_Discharge_Temp  Median of the maximum discharging temperature for Pack B  
- Median_of_Max_Pack_C_Charge_Temp     Median of the maximum charging temperature for Pack C  
- Median_of_Max_Pack_C_Discharge_Temp  Median of the maximum discharging temperature for Pack C  
- Median_of_Max_Pack_D_Charge_Temp     Median of the maximum charging temperature for Pack D  
- Median_of_Max_Pack_D_Discharge_Temp  Median of the maximum discharging temperature for Pack D  
- Net_consumption                      Net energy consumed after regeneration  
- NetkWh                               Net kilowatt-hours consumed  
- PL                                   Product Line category  
- PPL                                  Parent Product Line  
- Pack_A_Total_KWH_Charged             Total energy charged for Pack A  
- Pack_A_Total_KWH_Discharged          Total energy discharged for Pack A  
- Pack_B_Total_KWH_Charged             Total energy charged for Pack B  
- Pack_B_Total_KWH_Discharged          Total energy discharged for Pack B  
- Pack_C_Total_KWH_Charged             Total energy charged for Pack C  
- Pack_C_Total_KWH_Discharged          Total energy discharged for Pack C  
- Pack_D_Total_KWH_Charged             Total energy charged for Pack D  
- Pack_D_Total_KWH_Discharged          Total energy discharged for Pack D  
- Regeneration                         Amount of energy regenerated during operation  
- Regeneration_fraction                Fraction of energy recovered through regeneration  
- Smart_City                           Indicates if the vehicle is part of a smart city initiative  
- air_ventilation                      Air ventilation system status or consumption  
- endOdo                               Odometer reading at the end of the session  
- eventdate                            Date of the event  
- kwhCharged_cycles                    Total kilowatt-hours charged over multiple cycles  
- min_value                            Minimum recorded value of relevant data  
- product_line                         Specific category of the product  
- rn                                   Record number or unique row identifier  
- total_charged_cycle                  Total number of charge cycles completed  
- total_full_charged_cycles            Total number of full charge cycles completed  
- unique_id                            Unique identifier for the record  
- vehicleId                            Unique identifier for the vehicle  
- vehicle_registration_number          Registration number of the vehicle  
- vehicle_type                         Type of vehicle  
 
Table Name: vehicle_table
Contains vehicle details.

Columns Name                          Description
- DLR_NAME                              Name of the dealer associated with the vehicle  
- DLR_ORG_CITY                          City where the dealer is located  
- DLR_REGION                            Region of the dealer  
- DLR_STATE                             State of the dealer  
- Depot_Name                            Name of the vehicle’s depot  
- FIRST_SALE_DT                         Date when the vehicle was first sold  
- LOB                                   Line of Business the vehicle belongs to  
- PL                                    Product Line category  
- PPL                                   Parent Product Line  
- Smart_City                            Indicates if the vehicle is part of a smart city initiative  
- air_ventilation                       Air ventilation system status or consumption  
- eventdate                             Date of the event  
- monthId                               Unique identifier for the month  
- month_year                            Month and year of the record  
- product_line                          Specific category of the product  
- rn                                    Record number or unique row identifier  
- unique_id                             Unique identifier for the record  
- vehicleId                             Unique identifier for the vehicle  
- vehicle_registration_number           Registration number of the vehicle  
 
 
Example SQL Queries & Visualizations
 
- total Energy Consumption per Vehicle
SELECT vehicleId, SUM(NetkWh) AS total_energy_consumedFROM energy_dataGROUP BY vehicleIdORDER BY total_energy_consumed DESC;
 
 
- Average Energy Efficiency by Dealer Region
SELECT DLR_REGION, AVG(NetkWh / distanceInKM) AS avg_energy_efficiency FROM energy_data WHERE distanceInKM > 0 GROUP BY DLR_REGION ORDER BY avg_energy_efficiency DESC;

- Total Energy Consumption by Product Line
SELECT PL, SUM(NetkWh) AS Total_Energy_Consumption FROM discharge_table  GROUP BY PL ORDER BY Total_Energy_Consumption DESC;

- Average Energy Efficiency of Categories (A, B, C, D) Per Km
SELECT AVG(A_KWh_Remain_End - A_KWh_Remain_start) AS Avg_A_Efficiency,AVG(B_KWh_Remain_End - B_KWh_Remain_start) AS Avg_B_Efficiency,AVG(C_KWh_Remain_End - C_KWh_Remain_start) AS Avg_C_Efficiency,AVG(D_KWh_Remain_End - D_KWh_Remain_start) AS Avg_D_Efficiency FROM discharge_table;

- Top 5 Dealers by Total Distance Covered
SELECT DLR_NAME, SUM(distanceInKM) AS Total_Distance FROM discharge_table GROUP BY DLR_NAME ORDER BY Total_Distance DESC LIMIT 5;

- Relationship Between Number of Battery Packs and Net Energy Usage
SELECT VCU_BMS_No_of_Packs, AVG(NetkWh) AS Avg_Energy_Usage FROM discharge_table GROUP BY VCU_BMS_No_of_Packs ORDER BY VCU_BMS_No_of_Packs;

- Vehicle Performance by Region
SELECT DLR_REGION, AVG(whPerKM) AS Avg_Energy_Consumption FROM discharge_table GROUP BY DLR_REGION ORDER BY Avg_Energy_Consumption;

- Average Distance Traveled by Smart City vs. Non-Smart City Vehicles
SELECT Smart_City, AVG(distanceInKM) AS Avg_Distance FROM discharge_table GROUP BY Smart_City;

- Vehicles with the Highest Regenerated Energy
SELECT vehicle_registration_number, SUM(dataRegen_kWh) AS Total_Regen_Energy FROM discharge_table GROUP BY vehicle_registration_number ORDER BY Total_Regen_Energy DESC LIMIT 10;

- Retrieve the dealer name, city, and region along with the total energy consumption (NetkWh) from both tables for each vehicle.
SELECT e.vehicleId, e.DLR_NAME, e.DLR_ORG_CITY, e.DLR_REGION, e.NetkWh AS EnergyData_NetkWh, d.NetkWh AS DischargeTable_NetkWh FROM energy_data e JOIN discharge_table d ON e.vehicleId = d.vehicleId;

- Find the average energy consumption per km (whPerKM) for each vehicle by taking the mean from both tables.
SELECT e.vehicleId, (e.whPerKM + d.whPerKM) / 2 AS Avg_whPerKM FROM energy_data e JOIN discharge_table d ON e.vehicleId = d.vehicleId;

- Find dealers with the highest total energy consumption (NetkWh) across all vehicles.
SELECT e.DLR_NAME, SUM(e.NetkWh + d.NetkWh) AS Total_NetkWh FROM energy_data e JOIN discharge_table d ON e.vehicleId = d.vehicleId GROUP BY e.DLR_NAME ORDER BY Total_NetkWh DESC LIMIT 10;

- Retrieve the total energy charged per vehicle
SELECT vehicleId, SUM(kwhCharged) AS total_energy_charged FROM charging_table GROUP BY vehicleId ORDER BY total_energy_charged DESC;

- Find the average charging duration per depot
SELECT Depot_Name, AVG(chargeDurationInMin) AS avg_charge_duration FROM charging_table GROUP BY Depot_Name ORDER BY avg_charge_duration DESC;

- Get the count of vehicles that had at least one charging interruption
SELECT COUNT(DISTINCT vehicleId) AS vehicles_with_interruptions FROM charging_table WHERE NoOfInterrupt > 0;

- Identify the top 5 dealers with the highest total energy charged
SELECT DLR_NAME, SUM(kwhCharged) AS total_energy_charged FROM charging_table GROUP BY DLR_NAME ORDER BY total_energy_charged DESC LIMIT 5;

- Get the total number of charging events for each region
SELECT DLR_REGION, COUNT(*) AS total_charging_events FROM charging_table GROUP BY DLR_REGION ORDER BY total_charging_events DESC;

- Get the maximum cell temperature recorded for each category
SELECT MAX(A_Max_Cell_Temp) AS max_temp_A, MAX(B_Max_Cell_Temp) AS max_temp_B, MAX(C_Max_Cell_Temp) AS max_temp_C, MAX(D_Max_Cell_Temp) AS max_temp_D FROM charging_table;

- Find the average change in state of charge (SOC) per vehicle
SELECT vehicleId, AVG(delta_soc) AS avg_soc_change FROM charging_table GROUP BY vehicleId ORDER BY avg_soc_change DESC;
 
- Get Vehicle Energy Consumption and Discharge Details
SELECT e.vehicleId, e.vehicle_registration_number, e.NetkWh AS Energy_Consumption, d.dischargeSoc AS Battery_Discharge, e.distanceInKM AS Distance_Travelled FROM energy_data e JOIN discharge_table d ON e.vehicleId = d.vehicleId AND e.unique_id = d.unique_id;

- Find Vehicles with the Highest Net Energy Consumption and Distance Traveled
SELECT e.vehicleId, e.vehicle_registration_number, e.NetkWh, e.distanceInKM, d.dischargeSoc FROM energy_data e JOIN discharge_table d ON e.vehicleId = d.vehicleId ORDER BY e.NetkWh DESC, e.distanceInKM DESC LIMIT 10;

- Find Charging Sessions with Corresponding Discharge Data
SELECT c.vehicleId, c.vehicle_registration_number, c.kwhCharged, d.dischargeSoc AS Battery_Discharge_Before_Charging, c.soc_start, c.soc_end FROM charging_table c JOIN discharge_table d ON c.vehicleId = d.vehicleId AND c.unique_id = d.unique_id;

- Find Vehicles with the Most Charging Events
SELECT c.vehicleId, e.vehicle_registration_number, COUNT(c.vehicleId) AS Total_Charging_SessionsFROM charging_table c JOIN energy_data e ON c.vehicleId = e.vehicleId GROUP BY c.vehicleId, e.vehicle_registration_number ORDER BY Total_Charging_Sessions DESC LIMIT 10;

- Find the number of vehicles sold per dealer.
SELECT DLR_NAME, COUNT(*) AS vehicle_count FROM vehicle_table GROUP BY DLR_NAME;

- Find dealers operating in more than one region.
SELECT DLR_NAME, COUNT(DISTINCT DLR_REGION) AS region_count FROM vehicle_table GROUP BY DLR_NAME HAVING region_count > 1;

- Find the top 5 dealers with the highest number of vehicle sales.
SELECT DLR_NAME, COUNT(*) AS vehicle_count FROM vehicle_table GROUP BY DLR_NAME ORDER BY vehicle_count DESC LIMIT 5;
 
- Retrieve charging details along with energy consumption for each vehicle.
SELECT e.vehicleId, c.kwhCharged, e.NetkWh, c.soc_start, c.soc_end FROM energy_data e INNER JOIN charging_table c  ON e.vehicleId = c.vehicleId AND e.unique_id = c.unique_id;

- Find vehicles with their energy, charging, and SOH details.
SELECT e.vehicleId, e.NetkWh, c.kwhCharged, c.soc_start, c.soc_end, s.SOH FROM energy_data e INNER JOIN charging_table c ON e.vehicleId = c.vehicleId INNER JOIN soh_table s ON e.vehicleId = s.vehicleId;

- Find vehicles that have charging but no discharge records
SELECT c.vehicleId, c.kwhCharged, c.soc_end FROM charging_table c LEFT JOIN discharge_table d  ON c.vehicleId = d.vehicleId WHERE d.vehicleId IS NULL;

- Retrieve energy, discharge, and charging details together
SELECT e.vehicleId, e.NetkWh, d.dischargeSoc, d.distanceInKM, c.kwhCharged, c.soc_end FROM energy_data e INNER JOIN discharge_table d ON e.vehicleId = d.vehicleId INNER JOIN charging_table c ON e.vehicleId = c.vehicleId;

- Retrieve a comprehensive view of vehicle energy efficiency, including energy usage, discharge, and charging stats.
SELECT ed.vehicleId, ed.vehicle_registration_number, ed.distanceInKM, ed.kwh_km, dt.NetkWh AS discharge_energy, dt.dischargeSoc, ct.kwhCharged AS charged_energy, ct.soc_start, ct.soc_end, ct.chargeDurationInMin FROM energy_data ed JOIN discharge_table dt ON ed.vehicleId = dt.vehicleId JOIN charging_table ct ON ed.vehicleId = ct.vehicleId;

- Retrieve vehicle health data along with energy consumption for analysis
SELECT ed.vehicleId, ed.vehicle_registration_number, ed.NetkWh, ed.kwh_km, soh.SOH_Percentage, soh.Last_SOH_Update FROM energy_data ed JOIN soh_table soh ON ed.vehicleId = soh.vehicleId;

- Get a complete overview of vehicle energy usage, charging, and battery health.
SELECT ed.vehicleId, ed.vehicle_registration_number, ed.DLR_NAME, ed.distanceInKM, ed.NetkWh AS energy_consumed, dt.dischargeSoc, dt.NetkWh AS discharge_energy, ct.kwhCharged, ct.chargeDurationInMin, ct.soc_start, ct.soc_end, soh.SOH_Percentage, soh.Last_SOH_Update FROM energy_data ed JOIN discharge_table dt ON ed.vehicleId = dt.vehicleId JOIN charging_table ct ON ed.vehicleId = ct.vehicleId JOIN soh_table soh ON ed.vehicleId = soh.vehicleId;

- Identify vehicles where there is a significant difference between charged energy and discharged
SELECT ed.vehicleId, vt.vehicle_registration_number, ct.kwhCharged AS charged_energy, dt.NetkWh AS discharged_energy, (ct.kwhCharged - dt.NetkWh) AS energy_loss FROM energy_data ed JOIN vehicle_table vt ON ed.vehicleId = vt.vehicleId JOIN charging_table ct ON ed.vehicleId = ct.vehicleId JOIN discharge_table dt ON ed.vehicleId = dt.vehicleId ORDER BY energy_loss DESC LIMIT 10;

- Find cases where SOC drops significantly between charge and discharge.
SELECT ed.vehicleId, vt.vehicle_registration_number, ct.soc_end AS charging_soc, dt.dischargeSoc AS discharge_soc, (ct.soc_end - dt.dischargeSoc) AS soc_difference FROM energy_data ed JOIN vehicle_table vt ON ed.vehicleId = vt.vehicleId JOIN charging_table ct ON ed.vehicleId = ct.vehicleId JOIN discharge_table dt ON ed.vehicleId = dt.vehicleId WHERE (ct.soc_end - dt.dischargeSoc) > 30 ORDER BY soc_difference DESC;

- Write an SQL query to find the total energy discharged from discharge_table and the total energy charged from charging_table for each vehicle.
SELECT d.vehicleId,SUM(d.NetkWh) AS total_energy_discharged,SUM(c.kwhCharged) AS total_energy_charged FROM discharge_table d JOIN charging_table c ON d.vehicleId = c.vehicleId GROUP BY d.vehicleId;

- Find the average state of charge (SOC) before and after charging for each vehicle
SELECT d.vehicleId,AVG(d.startSoc) AS avg_discharge_start_soc,AVG(c.soc_end) AS avg_charge_end_soc FROM discharge_table d JOIN charging_table c ON d.vehicleId = c.vehicleId GROUP BY d.vehicleId;

- Find vehicles that had more than 5 charging interruptions
SELECT c.vehicleId,SUM(c.NoOfInterrupt) AS total_interruptions FROM charging_table c GROUP BY c.vehicleId HAVING SUM(c.NoOfInterrupt) > 5;




- Retrieve the vehicle ID, dealer name, and net energy consumption from both tables.
SELECT d.vehicleId, d.DLR_NAME, d.NetkWh AS discharge_netkwh, s.NetkWh AS soh_netkwh FROM discharge_table d JOIN soh_table s ON d.vehicleId = s.vehicleId;

- Find the total energy consumption per dealer.
SELECT d.DLR_NAME, SUM(d.NetkWh) AS total_discharge_energy, SUM(s.NetkWh) AS total_soh_energy FROM discharge_table d JOIN soh_table s ON d.vehicleId = s.vehicleId GROUP BY d.DLR_NAME;

- Find the number of vehicles operating under the Smart City initiative.
SELECT COUNT(DISTINCT d.vehicleId) AS smart_city_vehicles FROM discharge_table d JOIN soh_table s ON d.vehicleId = s.vehicleId WHERE d.Smart_City = 'Yes' AND s.Smart_City = 'Yes';

- Get the list of vehicles with their first sale date and total energy consumption.
SELECT d.vehicleId, d.FIRST_SALE_DT, SUM(d.NetkWh) AS total_energy_consumed FROM discharge_table d JOIN soh_table s ON d.vehicleId = s.vehicleId GROUP BY d.vehicleId, d.FIRST_SALE_DT;


- Retrieve the vehicle registration number, dealer name, depot name, net energy consumption, and total distance traveled for each trip.
SELECT d.vehicle_registration_number, d.DLR_NAME, d.Depot_Name, d.NetkWh, d.distanceInKM FROM discharge_table d JOIN vehicle_table v ON d.vehicleId = v.vehicleId;

- Get a list of vehicles that are part of the Smart City initiative along with their energy consumption details.
SELECT d.vehicle_registration_number, d.Smart_City, d.NetkWh, d.distanceInKM FROM discharge_table d JOIN vehicle_table v ON d.vehicleId = v.vehicleId WHERE v.Smart_City = 'Yes';

- Retrieve details of vehicles that have consumed more than 100 kWh in a single trip.
SELECT d.vehicle_registration_number, d.NetkWh, d.distanceInKM, d.DLR_NAME FROM discharge_table d JOIN vehicle_table v ON d.vehicleId = v.vehicleId WHERE d.NetkWh > 100;

- Find the total energy consumption for each product line.
SELECT v.product_line, SUM(d.NetkWh) AS total_energy_consumed FROM discharge_table d JOIN vehicle_table v ON d.vehicleId = v.vehicleId GROUP BY v.product_line;



- Retrieve the total energy charged and net energy consumption for each vehicle
SELECT c.vehicleId, c.kwhCharged, e.NetkWh FROM charging_table c JOIN energy_data e ON c.vehicleId = e.vehicleId;

- Get the list of dealers and their associated regions along with the last charge time
SELECT c.DLR_NAME, c.DLR_REGION, c.LastChargeTime FROM charging_table c JOIN energy_data e ON c.DLR_NAME = e.DLR_NAME;

- Find vehicles with the highest charging interruptions along with their trip energy efficiency
SELECT c.vehicleId, c.NoOfInterrupt, c.InterruptDurationInMin, e.kwh_km FROM charging_table c JOIN energy_data e  ON c.vehicleId = e.vehicleId ORDER BY c.NoOfInterrupt DESC;



- Retrieve Charging and SOH Details for Each Vehicle
SELECT c.vehicleId, c.vehicle_registration_number, c.kwhCharged, c.soc_start, c.soc_end, c.chargeDurationInMin,s.A_SOH_Value, s.B_SOH_Value, s.C_SOH_Value, s.D_SOH_Value FROM charging_table c JOIN soh_table s ON c.vehicleId = s.vehicleId;

-  Find Total Energy Charged and Discharged per Vehicle
SELECT c.vehicleId, c.vehicle_registration_number,SUM(c.kwhCharged) AS Total_KWh_Charged,SUM(s.Pack_A_Total_KWH_Discharged + s.Pack_B_Total_KWH_Discharged + s.Pack_C_Total_KWH_Discharged + s.Pack_D_Total_KWH_Discharged) AS Total_KWh_Discharged FROM charging_table c JOIN soh_table s ON c.vehicleId = s.vehicleId GROUP BY c.vehicleId, c.vehicle_registration_number;

- Identify Dealers with High Charging Activity and Vehicle Health
SELECT c.DLR_NAME, c.DLR_ORG_CITY, c.DLR_STATE,COUNT(DISTINCT c.vehicleId) AS Total_Vehicles_Charged,AVG(s.A_SOH_Value + s.B_SOH_Value + s.C_SOH_Value + s.D_SOH_Value) / 4 AS Avg_SOH FROM charging_table c JOIN soh_table s ON c.vehicleId = s.vehicleId GROUP BY c.DLR_NAME, c.DLR_ORG_CITY, c.DLR_STATE ORDER BY Total_Vehicles_Charged DESC;


- Get the total energy charged for each vehicle along with dealer and depot details.
SELECT c.vehicleId,v.DLR_NAME,v.Depot_Name,SUM(c.kwhCharged) AS total_energy_charged FROM charging_table c JOIN vehicle_table v ON c.vehicleId = v.vehicleId GROUP BY c.vehicleId, v.DLR_NAME, v.Depot_Name;

-  Identify vehicles that had more than 3 charging interruptions in any session.
SELECT c.vehicleId,c.vehicle_registration_number,c.eventdate,c.NoOfInterrupt FROM charging_table c JOIN vehicle_table v ON c.vehicleId = v.vehicleId WHERE c.NoOfInterrupt > 3;

- Find vehicles that had a full charge and the time taken to fully charge.
SELECT c.vehicleId,c.vehicle_registration_number,c.eventdate,c.chargeDurationInMin FROM charging_table c JOIN vehicle_table v ON c.vehicleId = v.vehicleId WHERE c.fullcharge = 'Yes';



- Find the vehicles with the lowest SOH value and their total energy consumption.
SELECT s.vehicleId,s.vehicle_registration_number,LEAST(s.A_SOH_Value, s.B_SOH_Value, s.C_SOH_Value, s.D_SOH_Value) AS Min_SOH_Value,e.NetkWh FROM soh_table s JOIN energy_data e ON s.vehicleId = e.vehicleId ORDER BY Min_SOH_Value ASC;

- Identify vehicles with high energy consumption but low regeneration efficiency.
SELECT s.vehicleId,s.vehicle_registration_number,e.NetkWh,s.Regeneration_fraction FROM soh_table s JOIN energy_data e ON s.vehicleId = e.vehicleId WHERE e.NetkWh > 500 AND s.Regeneration_fraction < 0.1;

 

- Get the SOH values of all vehicles along with their dealer name and city.
SELECT s.vehicleId, s.A_SOH_Value, s.B_SOH_Value, s.C_SOH_Value, s.D_SOH_Value, v.DLR_NAME, v.DLR_ORG_CITY FROM soh_table s JOIN vehicle_table v ON s.vehicleId = v.vehicleId;

- Get the average charging temperature of all packs along with their dealer region and state.
SELECT s.vehicleId, s.Avg_of_Pack_A_Charge_Temp, s.Avg_of_Pack_B_Charge_Temp, s.Avg_of_Pack_C_Charge_Temp, s.Avg_of_Pack_D_Charge_Temp,v.DLR_REGION, v.DLR_STATE FROM soh_table s JOIN vehicle_table v ON s.vehicleId = v.vehicleId;

- Get the highest charging temperature recorded for Pack A along with vehicle registration number and dealer name
SELECT s.vehicleId, s.vehicle_registration_number, s.Median_of_Max_Pack_A_Charge_Temp, v.DLR_NAME FROM soh_table s JOIN vehicle_table v ON s.vehicleId = v.vehicleId ORDER BY s.Median_of_Max_Pack_A_Charge_Temp DESC LIMIT 1;

- Get all vehicles along with their total energy consumption (NetkWh)
SELECT vt.vehicleId, vt.vehicle_registration_number, vt.DLR_NAME, vt.LOB, vt.PL, ed.NetkWh, ed.Range, ed.kwh_km FROM vehicle_table vt JOIN energy_data ed ON vt.vehicleId = ed.vehicleId AND vt.vehicle_registration_number = ed.vehicle_registration_number;

- Find vehicles with the highest energy consumption per km (kwh_km)
SELECT vt.vehicleId, vt.vehicle_registration_number, vt.DLR_NAME, vt.LOB, vt.PL, ed.kwh_km, ed.NetkWh FROM vehicle_table vt JOIN energy_data ed ON vt.vehicleId = ed.vehicleId ORDER BY ed.kwh_km DESC LIMIT 10;

- Find dealers (DLR_NAME) operating in multiple regions (DLR_REGION)
SELECT DLR_NAME, COUNT(DISTINCT DLR_REGION) AS unique_regions FROM vehicle_table GROUP BY DLR_NAME HAVING COUNT(DISTINCT DLR_REGION) > 1;


- Find vehicles that had charging interruptions greater than 30 minutes
SELECT v.vehicleId, v.vehicle_registration_number, v.DLR_NAME AS dealer_name, v.Depot_Name, c.InterruptDurationInMin FROM vehicle_table v JOIN charging_table c ON v.vehicleId = c.vehicleId AND v.vehicle_registration_number = c.vehicle_registration_number WHERE c.InterruptDurationInMin > 30 ORDER BY c.InterruptDurationInMin DESC;

- Get the latest charging session details for each vehicle
SELECT v.vehicleId, v.vehicle_registration_number, v.DLR_NAME AS dealer_name, v.DLR_STATE AS dealer_state, c.kwhCharged, c.chargeDurationInMin, c.soc_start, c.soc_end, c.eventdate FROM vehicle_table v JOIN charging_table c ON v.vehicleId = c.vehicleId AND v.vehicle_registration_number = c.vehicle_registration_number WHERE c.eventdate = (SELECT MAX(eventdate) FROM charging_table c2 WHERE c2.vehicleId = c.vehicleId) ORDER BY c.eventdate DESC;

- Count the number of charging sessions per vehicle
SELECT v.vehicleId, v.vehicle_registration_number, v.DLR_NAME AS dealer_name, v.DLR_STATE AS dealer_state, COUNT(c.unique_id) AS charging_sessions FROM vehicle_table v JOIN charging_table c ON v.vehicleId = c.vehicleId AND v.vehicle_registration_number = c.vehicle_registration_number GROUP BY v.vehicleId, v.vehicle_registration_number, v.DLR_NAME, v.DLR_STATE ORDER BY charging_sessions DESC;

-  Find depots with the most charging sessions
SELECT v.Depot_Name, COUNT(c.unique_id) AS total_charging_sessions FROM vehicle_table v JOIN charging_table c ON v.vehicleId = c.vehicleId AND v.vehicle_registration_number = c.vehicle_registration_number GROUP BY v.Depot_Name ORDER BY total_charging_sessions DESC;
 
Question: {question}
Query Language:SQL
Answer:
 
[The output should be a single, valid SQL query in one line, without line breaks or additional text.]
"""

def get_ollama_response(question, prompt):
    llm = Ollama(model="mistral")
    response = llm.invoke(f"{prompt}\nQuestion: {question}\nAnswer:")
    return response

def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error reading SQL query: {e}")
        return pd.DataFrame()

def get_sql_query_from_response(response):
    try:
        query_start = response.index('SELECT')
        query_end = response.index(';') + 1
        sql_query = response[query_start:query_end]
        return sql_query
    except ValueError:
        st.error("Could not extract SQL query from the response.")
        return None

def determine_chart_type(df):
    if df.empty:
        return None

    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    cat_cols = df.select_dtypes(include=['object', 'category']).columns

    if len(df.columns) == 2 and len(num_cols) == 1 and len(cat_cols) == 1 and len(df) <= 10:
        return 'pie'
    if len(df.columns) >= 2 and len(num_cols) > 0:
        time_columns = [col.lower() for col in df.columns]
        if any(word in time_columns for word in ['month', 'year', 'date', 'time', 'day']):
            return 'line'
    if len(num_cols) >= 2:
        return 'scatter'
    if len(df.columns) == 1 and len(num_cols) == 1:
        return 'histogram'
    if len(df.columns) > 1 and len(num_cols) == len(df.columns):
        return 'heatmap'
    if len(num_cols) >= 3:
        return 'bubble'
    if len(df.columns) > 2 and len(num_cols) > 1 and len(cat_cols) == 1:
        return 'radar'
    if (len(df.columns) == 2 and len(num_cols) == 1 and len(cat_cols) == 1) or \
       (len(df.columns) > 2 and len(cat_cols) > 0 and len(num_cols) > 0):
        return 'bar'
    if (len(df.columns) == 2 and len(num_cols) == 1 and len(cat_cols) == 1) or \
       (len(df.columns) > 2 and len(num_cols) > 0):
        return 'area'
    if len(df.columns) == 2 and len(num_cols) == 1 and len(cat_cols) == 1:
        return 'dot'
    if len(df.columns) == 2 and len(num_cols) == 1 and len(cat_cols) == 1:
        return 'treemap'
    if len(df.columns) == 2 and len(num_cols) == 1 and len(cat_cols) == 1 and len(df) <= 5:
        return 'gauge'

    return None

def generate_chart(df, chart_type, title=None, x_axis_label=None, y_axis_label=None, color_scale=None, bin_size=None):
    if chart_type is None:
        st.write("No suitable chart type determined for this data.")
        return

    if df.empty:
        st.write("The input DataFrame is empty.")
        return

    if chart_type == 'bar':
        fig = px.bar(df, x=df.columns[0], y=df.columns[1],
                     title=title if title else f"{df.columns[0]} vs. {df.columns[1]}",
                     template="plotly_white", color=df.columns[0])
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'pie':
        fig = px.pie(df, names=df.columns[0], values=df.columns[1],
                     title=title if title else f"Distribution of {df.columns[0]}",
                     template="plotly_white")
    elif chart_type == 'line':
        fig = px.line(df, x=df.columns[0], y=df.columns[1],
                      title=title if title else f"{df.columns[1]} Over {df.columns[0]}",
                      template="plotly_white", markers=True)
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'scatter':
        fig = px.scatter(df, x=df.columns[0], y=df.columns[1],
                         title=title if title else f"{df.columns[0]} vs. {df.columns[1]}",
                         template="plotly_white")
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'heatmap':
        fig = px.imshow(df.pivot_table(index=df.columns[0], columns=df.columns[1], values=df.columns[2]),
                         text_auto=True,
                         title=title if title else f"Heatmap of {df.columns[0]} vs. {df.columns[1]}",
                         template="plotly_white",
                         color_continuous_scale=color_scale if color_scale else "Viridis")
    elif chart_type == 'histogram':
        fig = px.histogram(df, x=df.columns[0],
                           title=title if title else f"Histogram of {df.columns[0]}",
                           template="plotly_white",
                           nbins=bin_size if bin_size else 10)
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
    elif chart_type == 'boxplot':
        fig = px.box(df, x=df.columns[0], y=df.columns[1],
                     title=title if title else f"Boxplot of {df.columns[0]} vs. {df.columns[1]}",
                     template="plotly_white")
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'violinplot':
        fig = px.violin(df, x=df.columns[0], y=df.columns[1],
                        title=title if title else f"Violinplot of {df.columns[0]} vs. {df.columns[1]}",
                        template="plotly_white")
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'densityplot':
        fig = px.density_heatmap(df, x=df.columns[0], y=df.columns[1],
                                 title=title if title else f"Densityplot of {df.columns[0]} vs. {df.columns[1]}",
                                 template="plotly_white")
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'treemap':
        fig = px.treemap(df, names=df.columns[0], parents=df.columns[1], values=df.columns[2],
                         title=title if title else f"Treemap of {df.columns[0]} vs. {df.columns[1]}",
                         template="plotly_white")
    elif chart_type == 'sunburst':
        fig = px.sunburst(df, names=df.columns[0], parents=df.columns[1], values=df.columns[2],
                          title=title if title else f"Sunburst of {df.columns[0]} vs. {df.columns[1]}",
                          template="plotly_white")
    elif chart_type == 'waterfall':
        fig = px.waterfall(df, x=df.columns[0], y=df.columns[1],
                            title=title if title else f"Waterfall of {df.columns[0]} vs. {df.columns[1]}",
                            template="plotly_white")
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'funnel':
        fig = px.funnel(df, x=df.columns[0], y=df.columns[1],
                         title=title if title else f"Funnel of {df.columns[0]} vs. {df.columns[1]}",
                         template="plotly_white")
        fig.update_xaxes(title=x_axis_label if x_axis_label else df.columns[0])
        fig.update_yaxes(title=y_axis_label if y_axis_label else df.columns[1])
    elif chart_type == 'sankey':
        fig = px.sankey(df, source=df.columns[0], target=df.columns[1], value=df.columns[2],
                         title=title if title else f"Sankey of {df.columns[0]} vs. {df.columns[1]}",
                         template="plotly_white")

    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

st.set_page_config(page_title="SQL Query Retrieval App", layout="wide")

st.markdown("""
    <h1 style="color: purple; text-align: center;">
        📊 DataQuery Pro: Insights at Your Command 📊
    </h1>
    """, unsafe_allow_html=True)

with st.container():
    st.subheader("What are you looking for?")

    col1, col2 = st.columns([3, 1], gap="small")

    with col1:
        question = st.text_input("Input your question here:", key="input", placeholder="Type here...")

    with col2:
        st.write("")
        submit = st.button("Retrieve Data", help="Click to submit your question.")

if submit and question:
    response = get_ollama_response(question, prompt_template)
    sql_query = get_sql_query_from_response(response)

    if sql_query:
        st.code(sql_query, language='sql')
        df = read_sql_query(sql_query, database_path)

        if not df.empty:
            col_data, col_chart = st.columns(2)
            with col_data:
                st.subheader("Query Results:")
                st.dataframe(df)
            chart_type = determine_chart_type(df)

            if chart_type:
                with col_chart:
                    st.subheader("Visualization:")
                    generate_chart(df, chart_type)
        else:
            st.write("No results found for the given query.")
    else:
        st.write("No valid SQL query could be extracted from the response.")
