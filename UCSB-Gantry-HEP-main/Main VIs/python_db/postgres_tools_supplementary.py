import numpy as np
from datetime import datetime
import asyncio, asyncpg, traceback #, sys, os


###################################################################################
########################### GET PARTS DATA FROM DATABASE #########################
#################################################################################

def get_offsets_from_db(conn_info = [], ass_type = 'module', date_since = '2026-04-01', no_of_parts = 16):
    if ass_type in ['proto', 'module']:
        header = ["name", "assembly_date", "x_offset_mu", "y_offset_mu", "ang_offset_deg"]
        limit_clause = f"LIMIT {no_of_parts}" if no_of_parts else ""
        query = f"""SELECT * FROM (
                    SELECT mi.{ass_type}_name,
                    ma.ass_run_date,
                    mi.x_offset_mu,
                    mi.y_offset_mu,
                    mi.ang_offset_deg
                    FROM {ass_type}_inspect mi
                    JOIN {ass_type}_assembly ma ON mi.{ass_type}_name = ma.{ass_type}_name
                    WHERE ma.ass_run_date > '{date_since}'
                    ORDER BY ma.ass_run_date DESC, mi.{ass_type}_name DESC
                    {limit_clause}
                    ) sub
                    ORDER BY ass_run_date ASC, {ass_type}_name ASC"""
                    
    try:
        rows = asyncio.run(read_val_from_db(conn_info, query=query))
    except:
        rows = (asyncio.get_event_loop()).run_until_complete(read_val_from_db(conn_info, query=query))
    
    if type(rows) is list:
        return [header] + [[row[f'{ass_type}_name'], row['ass_run_date'].strftime('%Y-%m-%d'), str(row['x_offset_mu']), str(row['y_offset_mu']), str(np.round(row['ang_offset_deg'], 6))] for row in rows]
    return [header]


def get_temperature_humidity_from_db(conn_info = [], log_location = ''):
    
    query = f"""SELECT log_timestamp, temp_c, rel_hum 
                FROM temp_humidity
                WHERE log_location = '{log_location}'
                ORDER BY log_no DESC LIMIT 1"""
    try:
        rows = asyncio.run(read_val_from_db(conn_info, query=query))
    except:
        rows = (asyncio.get_event_loop()).run_until_complete(read_val_from_db(conn_info, query=query))
    if rows:
        return [[row['log_timestamp'].strftime('%Y-%m-%d'),str(row["temp_c"]), str(row["rel_hum"])] for row in rows][0]  ### convert 2D list to 1D list
    return ["", "", ""]


async def read_val_from_db(conn_info=[], query = '', val = []):
    try:
        conn = await init_conn(conn_info)  
        if val:
            rows = await conn.fetch(query, list(val))
        else:
            rows = await conn.fetch(query)
        print(f'Query executed successfully: {query}')
        await conn.close() ## outside the loop
        return rows
    except Exception as e:
        print(f"Error during query execution: {str(e)}")
        return None

async def init_pool(conn_info):
    pool = await asyncpg.create_pool(
        host=conn_info[0],
        database=conn_info[1],
        user=conn_info[2],
        password=conn_info[3],
        min_size=10,  # minimum number of connections in the pool
        max_size=30)  # maximum number of connections in the pool
    print('Connection successful. \n')
    return pool

async def init_conn(conn_info):
    conn = await asyncpg.connect(
        host=conn_info[0],
        database=conn_info[1],
        user=conn_info[2],
        password=conn_info[3],)
    print('Connection successful. \n')
    return conn

##########################################################################
############################# DEBUGGING TOOLS ################################
#########################################################################

def db_conn_debugger(conn_info=[]):
    try:
        try:
            conn = asyncio.run(asyncpg.connect(
                host=conn_info[0],
                database=conn_info[1],
                user=conn_info[2],
                password=conn_info[3]))
            return "Connection successful! (Py 3.7)"
        except:
            conn = (asyncio.get_event_loop()).run_until_complete(asyncpg.connect(
                host=conn_info[0],
                database=conn_info[1],
                user=conn_info[2],
                password=conn_info[3]))
            return "Connection successful! (Py 3.6)"
    except:
        return "Connection failed!"

if __name__ == "__main__":
    import os
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    conn_file_path = os.path.join(current_script_dir, "..", "..", "Assembly Data", "Database Config", "conn.txt")
    conn_file_path = os.path.normpath(conn_file_path)

    with open(conn_file_path, 'r') as file:
        conn_info = [line.strip() for line in file]
        
    print("Connection info:", conn_info)
    conn_message = db_conn_debugger(conn_info)
    print(conn_message)
    # print(cmd_debugger(conn_info))
