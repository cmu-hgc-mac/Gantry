import numpy as np
from datetime import datetime
import asyncio, asyncpg #, sys, os

def assembly_data(conn_info=[], ass_type = '', geometry= '', resolution= '', base_layer_id = '', top_layer_id = '', bl_position=None, tl_position=None, put_position=None, region = None, ass_tray_id= '', comp_tray_id= '', put_id= '', ass_run_date= '', ass_time_begin= '', ass_time_end= '', operator= '', tape_batch = None, glue_batch = None, stack_name = 'test'):
    try:
        ass_run_date = datetime.strptime(ass_run_date, '%Y-%m-%d')
    except:
        ass_run_date = datetime.now().date()
    
    try:
        ass_time_begin = datetime.strptime(ass_time_begin, '%H:%M:%S')
        ass_time_end = datetime.strptime(ass_time_end, '%H:%M:%S')
    except:
        ass_time_begin = datetime.now().time()
        ass_time_end = datetime.now().time()
    
    inst_code = 'CM'
    #conn = asyncio.run(get_conn(*conn_info))
    #conn_info = ['cmsmac04.phys.cmu.edu', 'hgcdb', 'postgres', 'hgcal']
    if ass_type == 'proto':
        db_upload = [stack_name, geometry, resolution, base_layer_id, top_layer_id, str(bl_position), str(tl_position), str(put_position), str(region), str(ass_tray_id), str(comp_tray_id), str(put_id), tape_batch, glue_batch, ass_run_date, ass_time_begin, ass_time_end, operator]
        db_table_name = 'proto_assembly'
    elif ass_type == 'module':
        db_upload = [stack_name, geometry, resolution, base_layer_id, top_layer_id, str(bl_position), str(tl_position), str(put_position), str(region), str(ass_tray_id), str(comp_tray_id), str(put_id), tape_batch, glue_batch, ass_run_date, ass_time_begin, ass_time_end, operator]
        db_table_name = 'module_assembly'
    
    try:
        return asyncio.run(upload_PostgreSQL(conn_info, db_table_name, db_upload))
    except:
        temp = (asyncio.get_event_loop()).run_until_complete(upload_PostgreSQL(conn_info, db_table_name, db_upload))
        return temp
    #except:
    #    return conn_info[1]
    
def cmd_debugger():
    ass_type, base_layer_id, top_layer_id = 'proto', 'BA_123_test', 'SL_123_test'
    ass_type, base_layer_id, top_layer_id = 'module', 'PL_123_test', 'HB_123_test'
    geometry, resolution = 'Full', 'LD'
    bl_position, tl_position, put_position, region = 1, 1, 1, 1
    ass_tray_id, comp_tray_id, put_id = '1', 2, 1
    ass_run_date = '2012-07-04'
    ass_time_begin = '12:01:00.123'
    ass_time_end = '12:03:59.456'
    operator = 'cmuperson'
    tape_batch, glue_batch = None, None
    conn_info = ['cmsmac04.phys.cmu.edu', 'hgcdb', 'postgres', 'hgcal']
    t = assembly_data(ass_type, geometry, resolution, base_layer_id, top_layer_id, str(bl_position), str(tl_position), str(put_position), region, ass_tray_id, comp_tray_id, put_id, ass_run_date, ass_time_begin, ass_time_end, operator, tape_batch, glue_batch)
    print(t)
    
def get_query_write(table_name):
    if table_name == 'module_assembly':
        pre_query = f""" 
        INSERT INTO {table_name} 
        (module_name, geometry, resolution, proto_name, hxb_name, pml_position, hxb_position, put_position, region, ass_tray_id, hxb_tray_id, hxb_put_id, tape_batch, glue_batch, ass_run_date, ass_time_begin, ass_time_end, operator)
        VALUES """
    elif table_name == 'proto_assembly':
        pre_query = f""" 
        INSERT INTO {table_name} 
        (proto_name, geometry, resolution, bp_name, sen_name, bp_position, sen_position, put_position, region, ass_tray_id, sen_tray_id, sen_put_id, tape_batch, glue_batch, ass_run_date, ass_time_begin, ass_time_end, operator)
        VALUES  """
    data_placeholder = ', '.join(['${}'.format(i) for i in range(1, len(pre_query.split(','))+1)])
    query = f"""{pre_query} {'({})'.format(data_placeholder)}"""
    return query

comptable = {'baseplate':{'prefix': 'bp'},'hexaboard':{'prefix': 'hxb'},'protomodule':{'prefix': 'proto'},'module':{'prefix': 'module'}}
def get_query_read(component_type, part_name = None, comptable=comptable):
    if part_name is None:
        query = f"""SELECT {comptable[component_type]['prefix']}_name FROM {comptable[component_type]['prefix']}_inspect ORDER BY {comptable[component_type]['prefix']}_row_no DESC LIMIT 10;"""
    else:
        query = f"""SELECT hexplot FROM {comptable[component_type]['prefix']}_inspect WHERE {comptable[component_type]['prefix']}_name = '{part_name}'"""
    return query

async def upload_PostgreSQL(conn_info, table_name, db_upload_data):
    conn = await asyncpg.connect(
        host=conn_info[0],
        database=conn_info[1],
        user=conn_info[2],
        password=conn_info[3])
    print('Connection successful. \n')
    schema_name = 'public'
    table_exists_query = """
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = $1 
        AND table_name = $2
    );
    """
    table_exists = await conn.fetchval(table_exists_query, schema_name, table_name)  ### Returns True/False
    if table_exists:
        query = get_query_write(table_name)
        await conn.execute(query, *db_upload_data)
        print(f'Executing query: {query}')
        print(f'Data successfully uploaded to the {table_name}!')
    else:
        print(f'Table {table_name} does not exist in the database.')
    await conn.close()
    return 'Upload Success'

async def fetch_PostgreSQL(conn_info, component_type, bp_name = None):
    conn = ''
    result = await conn.fetch(get_query_read(component_type, bp_name ))
    await conn.close()
    return result


def debugprint(test=[], news=''):
    return test[2]
#print((cmd_debugger()))

