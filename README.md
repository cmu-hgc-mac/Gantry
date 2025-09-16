# Getting started: Connection to the MAC local DB

This documentation pertains to this project: https://github.com/cmu-hgc-mac/Gantry

# Getting started: Connecting to the local DB
1. Under `UCSB-Gantry-HEP-main/Assembly Data/Database Config/type_at_institutions`, verify that the correct types of modules are present for you institution.
2. Under `UCSB-Gantry-HEP-main/Assembly Data/Database Config/`, open `conn.txt` preferably in Excel or VS Code. Set database connection info in the following order while carefully avoiding trailing spaces.
     1. database IP address
     2.  database name (default: `hgcdb`)
     3.  user (`gantry_user`)
     4.  password
### Example for `conn.txt`
```
dbase.phys.school.edu
hgcdb
gantry_user
user_password
```


3. Under `UCSB-Gantry-HEP-main/Assembly Data/Controllers`:
  - Verify the region numbers in `Regions.txt`.
  - Edit `Institution.txt` with the abbreviation of your institution (`CMU`, `IHEP`, `NTU`, `TTU`, `TIFR`, `UCSB`).
  - Save the CERN IDs (or `FirstnameLastname` if CERN ID is not available) of your technicians in `Operators.txt` one person per line with no trailing spaces.
  - Set the Python 3 version under `Python.txt`.
    - You will require Python 3.6 and greater.
    - Please install [`asyncpg`](https://pypi.org/project/asyncpg/) for this python version.
    - ~~Please read the instructions on [Automatic Protomodule Naming](https://github.com/kai-ucsb/Gantry/blob/main/README.md#automatic-protomodule-naming) when using for the first time.~~

# Getting Started: Fitting LabVIEW to your MAC
1. Under `UCSB-Gantry-HEP-main/Assembly Data/Controllers`:
  - Open Dispenser.txt and change COM4 to the USB port connected to the dispenser. To verify the port, go to Device Manager and look for Ports (COM & LPT). Unplug and then reinsert the dispenser’s USB. Change the VISA resource name to the COM that shows up in the Device Manager as a result.
  - Open Sensors.txt and Valves.txt and change the inputs to match your MAC's setup. [CMU example here.](https://docs.google.com/presentation/d/18fChS6HMetSQ2EqdEWxNJkBMLUD8UyrRc5J06kykISw/edit#slide=id.g2587e3c00b2_0_69)
2. Open the project: UCSB-Gantry-HEP-main/Projects/Assembly.lvproj
  - If prompted to locate the file Aerotech.A3200.dll, select the file located under C:\Program Files (x86)\Aerotech\A3200\LabVIEW\2010\Bin. This DLL file links your gantry to the LV files.
  - Camera Setup: Refer to [slides 5 through 13 for details.](https://docs.google.com/presentation/d/18fChS6HMetSQ2EqdEWxNJkBMLUD8UyrRc5J06kykISw/edit#slide=id.g2587e3bfd54_0_32) In the Controllers folder, open Screen.txt. Change these values to match the result of camera calibration.
3. Assembly Tray inputs: Refer to slides 18 and 19.
4. Pick Up Tool (PUT) locations
  - Each PUT has three spacers with pins for loading. Place the PUT over its designated loading pins and ensure that the pins are flush with the PUT. If not, loosen the spacers a little. Place the PUT on the pins and align with the locator blocks.
  - Use Joystick and Camera.vi to obtain XYZ coordinates of the three pins. Find the average X, Y, and Z of each PUT loading area.
  - Refer to Readme in Assembly Data\Coordinate Data\Pick Up Tool Fixture to use these average values as inputs in Region3.txt.
5. Tool Offsets: Refer to [slides 22 and 23.](https://docs.google.com/presentation/d/18fChS6HMetSQ2EqdEWxNJkBMLUD8UyrRc5J06kykISw/edit#slide=id.g2587e3c00b2_0_257)


# Using the database
See [Documentation section](#more-documentation) below for debugging tips.
- Open the project Assembly.lvproj
- Under `Main VIs`, open `Manual Assembly DB.vi`. This also opens `Initiate multi-module assembly.vi`.
- The user can make selections in the drop-down menus and select tiles to populate data in `Data entry form multi-module.vi`. The module-module data form checks if the parts match the assembly type. It also formats the sensor ID input to match CERN convention.
- If parts have been locally inspected and the values are avilable in postgres, LabVIEW will pull those values. When applicable, the user can select between `avg_thickness` and `max_thickness` and even modify the values for setting dispense height. The default is `0.0` for dummies and will need to be set manually.
- **The parts get written to the local database after clicking `Submit thickness` in `Check parts acceptable.vi`.** The user can then select the routine they want to run. **If the program is aborted at this stage, there will still be an entry in the database.** If you don't want to keep those entries, please delete them with pgAdmin4.
- Post-assembly, the user will have an opportunity to submit additional comments that get appeneded to existing comments. This form can be used without assembly at a later time as long as the correct part names are provided.

![image](https://github.com/user-attachments/assets/4a74bae4-2c4c-465e-8c2d-ba301616a946)

![image](https://github.com/user-attachments/assets/49dabd94-95ea-46bd-8ab5-6b99fbf8dbdf)

![image](https://github.com/user-attachments/assets/11327ffc-dea5-4c77-ae31-e7ef2da281be)

![image](https://github.com/user-attachments/assets/df50784f-a07e-4722-ac79-06f84f4615ec)

![image](https://github.com/user-attachments/assets/6885cd48-6f5e-4298-a31b-8a18edd8f835)

![image](https://github.com/user-attachments/assets/d62e2eec-1ed4-4df9-a09d-d073d561c20d)


# More Documentation
- Database queries are in `UCSB-Gantry-HEP-main/Main VIs/python_db/postgres_tools.py`.
- Protomodules and modules are declared with `Stack.lvclass` and database entries are tracked with `Database Entry.lvclass`.
- [Developer notes here - Google Slides](https://docs.google.com/presentation/d/1HBvVTkyuiU_mZnNuGw4U_Wn2-F3KMbM-lAi5Qyut9t0/edit#slide=id.p)

# Test connection
- **Test connection**: Run the following in `python3` on the gantry python installation with the appropriate **database hostname and password**.
<pre>
import asyncpg, asyncio
conn = asyncio.run(asyncpg.connect(
        host=<b>'db_hostname.phys.school.edu'</b>,
        password=<b>'gantry_user_password'</b>,
        database='hgcdb',
        user='gantry_user'))
print('Connection successful!')
</pre>
- **Test connection with LabVIEW**: Open `Main VIs/python_db/check_db_conn.vi` from the `Assembly.lvproj` Project Explorer and run it to troubleshoot python, database, and LabVIEW interconnection.
- To check if the config file path is being read in correctly, run `Main VIs\python_db\postgres_tools.py`.

# Debugging
- Run `Database Entry.lvclass:Initiate Assembly.vi` with `Database Entry.lvclass:Write to DB.vi` open. The error will be displayed in `error out py` in the latter's front panel.
- Additional debugging tools present for tables in `Main VIs/python_db/upload_data_db.vi`.


## Instruction to set up a local DB:
https://github.com/cmu-hgc-mac/HGC_DB_postgres/



# Automatic Protomodule Naming (Obsolete)
**This has been made obsolete. It is not recommended to generate module serial number automatically. Please follow the serial number on the module QR codes.**

There is a field to enter the full stack name (eg. 320PHF2WXCM0006 or 320MHF2WXCM0006, etc). If that field is left empty, the protomodule ID will be automatically determined by LabVIEW based on the types of components and existing protomodules of that sequence in your database. The module ID will be determined by protomodule ID provided. 

It is recommended to use the text box for the first protomodule of you build for a given type. This is so because the program automatically figures out the next serial number by incrementing the serial number of last initialted protomodule of that type. If that type does not exist in the database, LabVIEW will save the next protomodule as a CuW PL by default `320PLF2WXXX0001`. Once a type of protomodule has been saved in the database, the subsequent modules can be automated, i.e. you do not need to provide a serial number for the stack. 

Stack names and routines are assigned in the order of tray numbers followed by positions regardless of the order in which they were initiated in the program. For example, if you initiate `tray 2 pos 1` followed by `tray 1 pos 2`, the module IDs assigned and the assembly excecution will start at `tray 1 pos 2` followed `tray 2 pos 1`.

Please check the database for this after protomodule assembly and before the module assembly step and correct it with the right bp type and index if needed. To find the table in pgAdmin: `hgcdb` -> `Schemas` -> `Tables` -> `proto_assembly`. Right-click and select `View/Edit Data`. Similarly, please monitor the `module_assembly` table.

![image](https://github.com/user-attachments/assets/0e86ef37-8087-46fd-a3ab-8047269b9300)

![image](https://github.com/user-attachments/assets/7540e9c2-5339-43e7-a84d-7cd251f331eb)

![image](https://github.com/user-attachments/assets/0d2896db-1d70-4e43-ad5a-88607c2c7da8)

![image](https://github.com/user-attachments/assets/7e575ec3-d750-4686-b238-fd562b0f5392)


<!--## Instructions, Documentation, and Developer Notes:--->
<!--https://github.com/cmu-hgc-mac/HGC_DB_postgres/blob/main/documentation/gantry/README.md-->

