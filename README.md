# Getting started: Connection to the MAC local DB

This documentation pertains to this project: https://github.com/kai-ucsb/Gantry

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
  - Save the CERN IDs of your technicians in `Operators.txt` one person per line with no trailing spaces.
  - Set the Python 3 version under `Python.txt`.
    - You will require Python 3.6 and greater.
    - Please install [`asyncpg`](https://pypi.org/project/asyncpg/) for this python version.
    - Please read the instructions on [Automatic Protomodule Naming](https://github.com/kai-ucsb/Gantry/blob/main/README.md#automatic-protomodule-naming) when using for the first time.

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
- Open the project Assembly.lvproj
- Under `Main VIs`, open `Manual Assembly DB.vi`.

![image](https://github.com/user-attachments/assets/ecb34a19-4e8a-4fb5-a8d2-d61a54c10104)

![image](https://github.com/user-attachments/assets/7cf8146d-eb93-4480-a4f5-45348839fc6d)
Submitting the tile selections at `Initiate Assembly.vi` writes to the local database. The user can then select the routine they want to run. If the program is aborted at this stage, there will still be an entry in the database. If you don't want to keep those entries, please delete them with pgAdmin.
![image](https://github.com/user-attachments/assets/143eae7c-d0d5-4435-97d6-c84926c5100c)

# Automatic Protomodule Naming
The program automatically figures our the serial number for an assembled protomodule. It does so by incrementing the serial number of last assembled protomodule of that by 1. The first time you run this program, it will save a protomodule with serial number 1 for that type, i.e. `320-PX-XXXX-XX-0001`. However, at the time this code is being deployed, we assume MACs have already assembled multiple protomodules and would like to ensure we have the right serial number sequence. We recommend opening the `proto_assembly` table in pgAdmin and editing that entry to reflect the correct protomodule name. Please do not change the naming convention, i.e. prefixes and dashes. The next time you assemble a protomodule of that type, it should have the correct and desired name. To find the table in pgAdmin: `hgcdb` -> `Schemas` -> `Tables` -> `proto_assembly`. Right-click and select `View/Edit Data`.

![image](https://github.com/user-attachments/assets/0e86ef37-8087-46fd-a3ab-8047269b9300)

![image](https://github.com/user-attachments/assets/7540e9c2-5339-43e7-a84d-7cd251f331eb)

![image](https://github.com/user-attachments/assets/0d2896db-1d70-4e43-ad5a-88607c2c7da8)

![image](https://github.com/user-attachments/assets/7e575ec3-d750-4686-b238-fd562b0f5392)


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
- **Test connection with LabVIEW**: Run `Main VIs/python_db/check_db_conn.vi` to troubleshoot python, database, and LabVIEW interconnection.

# Debugging
- Run `Database Entry.lvclass:Initiate Assembly.vi` with `Database Entry.lvclass:Write to DB.vi` open. The error will be displayed in `error out py` in the latter's front panel.
- Additional debugging tools present for tables in `Main VIs/python_db/upload_data_db.vi`.

## Instruction to set up a local DB:
https://github.com/cmu-hgc-mac/HGC_DB_postgres/

<!--## Instructions, Documentation, and Developer Notes:--->
<!--https://github.com/cmu-hgc-mac/HGC_DB_postgres/blob/main/documentation/gantry/README.md-->

