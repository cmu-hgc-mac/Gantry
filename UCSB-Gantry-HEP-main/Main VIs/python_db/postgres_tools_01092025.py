import numpy as np
from datetime import datetime
import asyncio, asyncpg, traceback #, sys, os

def post_assembly_data(conn_info=[], ass_type='', stack_name='test', ass_time_end='', comment=None):
    try:
        ass_time_end = datetime.strptime(ass_time_end, '%H:%M:%S').time()
    except:
        ass_time_end = datetime.now().time()

    if len(str(stack_name)) != 0:
        stack_name = stack_name.replace('-','')
        comment = f"{comment}; " if comment else None
        db_table_name = 'proto_assembly' if ass_type == 'proto' else 'module_assembly'

        if comment:
            post_ass_update_query = f""" UPDATE {db_table_name} 
                    SET ass_time_end = $2, comment = COALESCE(comment, '') || $3
                    WHERE REPLACE({"proto_name" if ass_type == "proto" else "module_name"},'-','') = $1;"""
            db_upload_val = (stack_name, ass_time_end, comment)
        else:
            post_ass_update_query = f""" UPDATE {db_table_name} 
                    SET ass_time_end = $2
                    WHERE REPLACE({"proto_name" if ass_type == "proto" else "module_name"},'-','') = $1;"""
            db_upload_val = (stack_name, ass_time_end)

        try:
            return asyncio.run(post_assembly_update(conn_info, post_ass_update_query=post_ass_update_query, db_upload_val=db_upload_val))
        except:
            return (asyncio.get_event_loop()).run_until_complete(post_assembly_update(conn_info, post_ass_update_query=post_ass_update_query, db_upload_val=db_upload_val))
    return "Dummy run. Data not saved."


def assembly_data_as_list(conn_info=[], ass_data_list = []):   
    #### The order of values in db_data_cols must match the order of values in Data cluster in Stack.lvclass: Get stack data.vi ###
    #### The variable names below correspond to postgres col name. LV does not neet to match the col numes but just the values. ###
    #### Right-click on the Data cluster on the front panel and click on 'reorder controls' to verify the order is correct in the code. 
    #### The physical position of the fields is different from the actual position.
    db_data_cols = ["ass_type", 
                    "geometry", 
                    "resolution", 
                    "base_layer_id", 
                    "top_layer_id", 
                    "bl_position", 
                    "tl_position", 
                    "put_position", 
                    "region", 
                    "ass_tray_id", 
                    "comp_tray_id", 
                    "put_id", 
                    "ass_run_date", 
                    "ass_time_begin", 
                    "ass_time_end", 
                    "operator", 
                    "tape_batch", 
                    "glue_batch", 
                    "stack_name", 
                    "adhesive", 
                    "comment", 
                    "temp_c", 
                    "rel_hum"]
    
    if ass_data_list:
        dictinit = {db_data_cols[i] : ass_data_list[i] for i in range(len(ass_data_list))}
        if (len(str(dictinit['base_layer_id'])) != 0) and (len(str(dictinit['top_layer_id'])) != 0):  ### dummy runs don't get saved
            try:
                dictinit['ass_run_date'] = datetime.strptime(dictinit['ass_run_date'], '%Y-%m-%d')
            except:
                dictinit['ass_run_date'] = datetime.now().date()
            
            try:
                dictinit['ass_time_begin'] = datetime.strptime(dictinit['ass_time_begin'], '%H:%M:%S')
                dictinit['ass_time_end'] = datetime.strptime(dictinit['ass_time_end'], '%H:%M:%S')
            except:
                dictinit['ass_time_begin'] = datetime.now().time()
                dictinit['ass_time_end'] = datetime.now().time()
            
            inst_code_dict = {'CM':'CMU', 'SB':'UCSB','IH':'IHEP', 'NT':'NTU', 'TI':'TIFR', 'TT':'TTU'}
            sensor_thickness_dict = {'1': 120, '2': 200, '3': 300}
            bp_material_dict = {'W': 'CuW', 'P': 'PCB', 'T': 'Titanium', 'C': 'Carbon fiber'}
            roc_version_dict = {'X': 'Preseries', '2': 'HGCROCV3b-2', '4': 'HGCROCV3b-4','C': 'HGCROCV3c',}
            
            pos_col, pos_row = get_col_row(int(dictinit['bl_position']))
            dictinit['comment'] = f"{dictinit['comment']}; " if dictinit['comment'] else None

            db_upload = {'geometry' : dictinit['geometry'], 
                        'resolution': dictinit['resolution'], 
                        'ass_run_date': dictinit['ass_run_date'], 
                        'ass_time_begin': dictinit['ass_time_begin'], 
                        'ass_time_end': dictinit['ass_time_end'], 
                        'pos_col': pos_col,
                        'pos_row': pos_row,
                        'adhesive': dictinit['adhesive'],
                        'operator': dictinit['operator'],
                        'comment': dictinit['comment'],
                        'temp_c': dictinit['temp_c'],
                        'rel_hum': dictinit['rel_hum'],}

            if dictinit['ass_type'] == 'proto':
                db_table_name = 'proto_assembly'
                db_upload.update({
                        'proto_name': dictinit['stack_name'], 
                        'bp_name': dictinit['base_layer_id'], 
                        'sen_name': dictinit['top_layer_id'], 
                        'bp_position': str(dictinit['bl_position']), 
                        'sen_position': str(dictinit['tl_position']), 
                        'put_position': str(dictinit['put_position']), 
                        'region': str(dictinit['region']), 
                        'ass_tray_id': str(dictinit['ass_tray_id']), 
                        'sen_tray_id': str(dictinit['comp_tray_id']), 
                        'sen_put_id': str(dictinit['put_id']), 
                        'tape_batch': dictinit['tape_batch'], 
                        'glue_batch': dictinit['glue_batch']})

                try:
                    return asyncio.run(proto_assembly_seq(conn_info, db_table_name, db_upload))
                except:
                    return (asyncio.get_event_loop()).run_until_complete(proto_assembly_seq(conn_info, db_table_name, db_upload))
                
            elif dictinit['ass_type'] == 'module':
                db_table_name = 'module_assembly'
                db_upload.update({
                        'module_name': dictinit['stack_name'], 
                        'proto_name': dictinit['base_layer_id'], 
                        'hxb_name': dictinit['top_layer_id'], 
                        'pml_position': str(dictinit['bl_position']), 
                        'hxb_position': str(dictinit['tl_position']), 
                        'put_position': str(dictinit['put_position']), 
                        'region': str(dictinit['region']), 
                        'ass_tray_id': str(dictinit['ass_tray_id']), 
                        'hxb_tray_id': str(dictinit['comp_tray_id']), 
                        'hxb_put_id': str(dictinit['put_id']), 
                        'tape_batch': dictinit['tape_batch'], 
                        'glue_batch': dictinit['glue_batch']})
                db_upload_info = {'module_name': dictinit['stack_name'], 
                                'proto_name': dictinit['base_layer_id'], 
                                'hxb_name': dictinit['top_layer_id'], 
                                'geometry' : dictinit['geometry'], 
                                'resolution': dictinit['resolution'],
                                'assembled': dictinit['ass_run_date']}
                try:
                    db_upload_info.update({'bp_material': bp_material_dict[(dictinit['stack_name'].replace("-",""))[7]],
                                        'sen_thickness': sensor_thickness_dict[(dictinit['stack_name'].replace("-",""))[6]],
                                        'institution': inst_code_dict[(dictinit['stack_name'].replace("-",""))[9:11]],   
                                        'roc_version': roc_version_dict[(dictinit['stack_name'].replace("-",""))[8]]})
                except: print('Check module name again. Code incomplete.')
                db_upload_dict = {db_table_name: db_upload, 'module_info': db_upload_info}
            try:
                return asyncio.run(module_assembly_seq(conn_info, db_upload_dict))
            except:
                return (asyncio.get_event_loop()).run_until_complete(module_assembly_seq(conn_info, db_upload_dict))
        
    return "Dummy run. Data not saved."


def get_thickness_from_db(conn_info = [], base_layer_ids = [], ass_type = 'module'):
    row = []
    if ass_type == 'proto':
        prefix = 'bp'
        cols = [f'{prefix}_name', 'thickness', 'flatness', 'grade']
        def_data = ['', 0.0, 0.0, False]
    elif ass_type == 'module':
        prefix = 'proto'
        cols = [f'{prefix}_name', 'thickness', 'ave_thickness', 'max_thickness', 'flatness', 'x_offset_mu', 'y_offset_mu', 'ang_offset_deg', 'grade']
        def_data = ['', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, False]
    
    def_return = {col: [str(def_data[c]) for part in base_layer_ids] for c, col in enumerate(cols)}
    
    base_layer_ids = [i.replace('-','') for i in base_layer_ids]
    query = f"""SELECT DISTINCT ON (REPLACE({prefix}_name,'-','')) REPLACE({prefix}_name,'-','') as {prefix}_name, {', '.join([col for col in cols[1:]])}
        FROM {prefix}_inspect WHERE REPLACE({prefix}_name,'-','') = ANY($1) ORDER BY {prefix}_name, {prefix}_row_no DESC;"""

    try:
        rows = asyncio.run(read_val_from_db(conn_info, query=query, val=base_layer_ids))
    except:
        rows = (asyncio.get_event_loop()).run_until_complete(read_val_from_db(conn_info, query=query, val=base_layer_ids))
    
    if type(rows) is list:
        for row in rows:
            index = base_layer_ids.index(row[f'{prefix}_name'])
            for col in cols:
                def_return[col][index] = row[col] if type(row[col]) is str else str(round(row[col],3)) if type(row[col]) is float else str((row[col]))
    
    return [cols] + [[def_return[col][i] for col in cols] for i in range(len(base_layer_ids))]


###################################################################################
################################# UPLOAD TO DATABASE ###############################
#################################################################################

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

async def read_val_from_db(conn_info=[], query = '', val = []):
    try:
        pool = await init_pool(conn_info)  
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, list(val))
            print(f'Query executed successfully: {query}')
        await pool.close() ## outside the loop
        return rows
    except Exception as e:
        print(f"Error during query execution: {str(e)}")
        return None

async def post_assembly_update(conn_info=[], post_ass_update_query='', db_upload_val = ()):
    try:
        pool = await init_pool(conn_info)  
        async with pool.acquire() as conn:
            await conn.execute(post_ass_update_query, *db_upload_val)
            print(f'Query executed successfully: {post_ass_update_query}')
        await pool.close() ## outside the loop
        return 'Update successful'
    except Exception as e:
        print(f"Error during query execution: {str(e)}")
        return f"Update failed: {str(e)}"


async def proto_assembly_seq(conn_info, db_table_name, db_upload):
    pool = await init_pool(conn_info)
    proto_no = await upload_PostgreSQL(pool, db_table_name, db_upload, req_return='proto_no')
    if proto_no is not False:
        read_query = f"""SELECT 
        EXISTS( SELECT 1 FROM baseplate  WHERE REPLACE(bp_name, '-', '') = '{db_upload['bp_name']}')   AS bp_exists,
        EXISTS( SELECT 1 FROM sensor     WHERE REPLACE(sen_name, '-', '') = '{db_upload['sen_name']}') AS sen_exists; """
        records = await fetch_PostgreSQL(pool, read_query)
        check = [dict(record) for record in records][0]

        if not check['bp_exists']:
            db_upload_bp = {'bp_name': db_upload['bp_name'], 'proto_no': proto_no}
            # await upload_PostgreSQL(pool, 'baseplate', db_upload_bp)
        else:
            await update_PostgreSQL(pool, 'baseplate', {'proto_no': proto_no}, name_col = 'bp_name', part_name = db_upload['bp_name'] )

        if not check['sen_exists']:
            db_upload_sen = {'sen_name': db_upload['sen_name'], 'proto_no': proto_no}
            if db_upload['comment']:
                db_upload_sen.update({'comment': db_upload['comment']})
            # await upload_PostgreSQL(pool, 'sensor', db_upload_sen)
        else:
            db_update_sen = {'proto_no': proto_no}
            if db_upload['comment']:
                db_update_sen.update({'comment': db_upload['comment']})
            await update_PostgreSQL(pool, 'sensor', db_update_sen, name_col = 'sen_name', part_name = db_upload['sen_name'] )

    await pool.close()
    return f"Success! for {db_upload['proto_name']}"
    

async def module_assembly_seq(conn_info, db_upload_dict):
    pool = await init_pool(conn_info)
    module_no = await upload_PostgreSQL(pool, 'module_info', db_upload_dict['module_info'], 'module_no')  
    if module_no is not None:
        module_assembly_dict = db_upload_dict['module_assembly']
        module_assembly_dict.update({'module_no': module_no})
        await upload_PostgreSQL(pool, 'module_assembly', module_assembly_dict)
        proto_name, hxb_name = db_upload_dict['module_info']['proto_name'], db_upload_dict['module_info']['hxb_name']
        await update_PostgreSQL(pool, 'proto_assembly', {'module_no': module_no}, name_col = 'proto_name', part_name = proto_name )
        temp_query = f"""UPDATE module_info SET bp_name = proto_assembly.bp_name, sen_name = proto_assembly.sen_name FROM proto_assembly WHERE proto_assembly.proto_name = module_info.proto_name;"""
        async with pool.acquire() as conn: 
            await conn.execute(temp_query)

        read_query = f"""SELECT EXISTS(SELECT REPLACE(hxb_name, '-','') FROM hexaboard WHERE REPLACE(hxb_name, '-','') ='{hxb_name}');"""
        records = await fetch_PostgreSQL(pool, read_query)
        check = [dict(record) for record in records][0]
        if not check['exists']:
            db_upload_bp = {'hxb_name': hxb_name, 'module_no': module_no}
            # await upload_PostgreSQL(pool, 'hexaboard', db_upload_bp)
        else:
            await update_PostgreSQL(pool, 'hexaboard', {'module_no': module_no}, name_col = 'hxb_name', part_name = hxb_name )
    else:
        await upload_PostgreSQL(pool, 'module_assembly', db_upload_dict['module_assembly'])
    await pool.close()
    return f"Success! for {db_upload_dict['module_info']['proto_name']}"


def get_query_write(table_name, column_names, req_return = None):
    pre_query = f""" INSERT INTO {table_name} ({', '.join(column_names)}) VALUES """
    data_placeholder = ', '.join(['${}'.format(i) for i in range(1, len(column_names)+1)])
    query = f"""{pre_query} {'({})'.format(data_placeholder)}"""
    if req_return is not None:
        query = f"""{query} RETURNING {req_return}"""
    return query

async def upload_PostgreSQL(pool, table_name, db_upload_data, req_return = None):
    async with pool.acquire() as conn: 
        pk = None
        try:
            query = get_query_write(table_name, list(db_upload_data.keys()), req_return)
            print(f'Executing query: {query}')
            if req_return:
                pk = await conn.fetchval(query, *db_upload_data.values())
                print(f'Data successfully uploaded to the {table_name}!')
                return pk
            else: 
                await conn.execute(query, *db_upload_data.values())
                print(f'Data successfully uploaded to the {table_name}!')
                return None
        except Exception as e:
            traceback.print_exc()
            return None
        
def get_query_update(table_name, column_names, name_col):
    data_placeholder = ', '.join([f"{col} = ${i+1}" for i, col in enumerate(column_names)])
    pre_query = f""" UPDATE {table_name} SET {data_placeholder} WHERE """
    query = f""" {pre_query} {name_col} = ${1+len(column_names)}; """
    return query

async def update_PostgreSQL(pool, table_name, db_upload_data, name_col, part_name):
    async with pool.acquire() as conn: 
        query = get_query_update(table_name, list(db_upload_data.keys()), name_col)
        params = list(db_upload_data.values()) + [part_name]
        try:
            await conn.execute(query, *params)
            print(f'Data for {part_name} updated into {table_name} table.')
        except Exception as e:
            print(e, f"for query {query}.")


######################################################################################
######################### READ FROM DATABASE ########################################
#######################################################################################
comptable = {'baseplate':{'prefix': 'bp'},'hexaboard':{'prefix': 'hxb'},'protomodule':{'prefix': 'proto'},'module':{'prefix': 'module'}}
def get_query_read(component_type, part_name = None, comptable=comptable):
    if part_name is None:
        query = f"""SELECT {comptable[component_type]['prefix']}_name FROM {comptable[component_type]['prefix']}_inspect ORDER BY {comptable[component_type]['prefix']}_row_no DESC LIMIT 10;"""
    else:
        query = f"""SELECT hexplot FROM {comptable[component_type]['prefix']}_inspect WHERE {comptable[component_type]['prefix']}_name = '{part_name}'"""
    return query

async def fetch_PostgreSQL(pool, query):
    try:
        async with pool.acquire() as conn:  # Acquire a connection from the pool
            value = await conn.fetch(query)
        return value
    except Exception as e:
        print(e, f"for query {query}.")


async def find_largest_suffix(conn_info, prefix, table_name = 'proto_assembly', col_name = 'proto_name'):  ####### For getting protomodule count suffix based on type
    conn = await asyncpg.connect(host=conn_info[0], database=conn_info[1], user=conn_info[2], password=conn_info[3])
    query = f"""
        SELECT MAX(CAST(RIGHT({col_name}, 4) AS INTEGER))
        FROM {table_name} 
        WHERE REPLACE({col_name},'-','') LIKE '{prefix.replace("-","")}%'"""
    largest_suffix = await conn.fetchval(query) ##, f'{prefix}%')
    await conn.close()
    if largest_suffix == None: largest_suffix = '0';
    print('New suffix:', str(int(largest_suffix)+1).zfill(4))
    return str(int(largest_suffix)+1).zfill(4)
   
def get_number_for_type(conn_info, prefix):
    try:
        try:
            return asyncio.run(find_largest_suffix(conn_info, prefix.replace("-","")))
        except:
            return (asyncio.get_event_loop()).run_until_complete(find_largest_suffix(conn_info, prefix.replace("-","")))
    except:
        return '9009'
    
def get_col_row(i):
    col, row = 1+(i-1)//2, 1+(i-1)%2
    return col, row


#############################################################################
############################ OLDER FUNCTION #################################
#############################################################################
def assembly_data(conn_info=[], 
                  ass_type = '', 
                  geometry= '', 
                  resolution= '', 
                  base_layer_id = '', 
                  top_layer_id = '', 
                  bl_position=None, 
                  tl_position=None, 
                  put_position=None, 
                  region = None, 
                  ass_tray_id= '', 
                  comp_tray_id= '', 
                  put_id= '', 
                  ass_run_date= '', 
                  ass_time_begin= '', 
                  ass_time_end= '', 
                  operator= '', 
                  tape_batch = None, 
                  glue_batch = None, 
                  stack_name = 'test', 
                  adhesive = None, 
                  comment = None, 
                  temp_c = None, 
                  rel_hum = None):  #### This is an alternate way to 'assembly_data_as_list' to writing to the database.
    if (len(str(base_layer_id)) != 0) and (len(str(top_layer_id)) != 0):  ### dummy runs don't get saved
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
        
        inst_code_dict = {'CM':'CMU', 'SB':'UCSB','IH':'IHEP', 'NT':'NTU', 'TI':'TIFR', 'TT':'TTU'}
        sensor_thickness_dict = {'1': 120, '2': 200, '3': 300}
        bp_material_dict = {'W': 'CuW', 'P': 'PCB', 'T': 'Titanium', 'C': 'Carbon fiber'}
        roc_version_dict = {'X': 'Preseries', '2': 'HGCROCV3b-2', '4': 'HGCROCV3b-4','C': 'HGCROCV3c',}
        
        pos_col, pos_row = get_col_row(int(bl_position))
        comment = f"{comment}; " if comment else None

        db_upload = {'geometry' : geometry, 
                    'resolution': resolution, 
                    'ass_run_date': ass_run_date, 
                    'ass_time_begin': ass_time_begin, 
                    'ass_time_end': ass_time_end, 
                    'pos_col': pos_col,
                    'pos_row': pos_row,
                    'adhesive': adhesive,
                    'operator': operator,
                    'comment': comment,
                    'temp_c': temp_c,
                    'rel_hum':rel_hum,}
        if ass_type == 'proto':
            db_table_name = 'proto_assembly'
            db_upload.update({
                    'proto_name': stack_name, 
                    'bp_name': base_layer_id, 
                    'sen_name': top_layer_id, 
                    'bp_position': str(bl_position), 
                    'sen_position': str(tl_position), 
                    'put_position': str(put_position), 
                    'region': str(region), 
                    'ass_tray_id': str(ass_tray_id), 
                    'sen_tray_id': str(comp_tray_id), 
                    'sen_put_id': str(put_id), 
                    'tape_batch': tape_batch, 
                    'glue_batch': glue_batch})

            try:
                return asyncio.run(proto_assembly_seq(conn_info, db_table_name, db_upload))
            except:
                return (asyncio.get_event_loop()).run_until_complete(proto_assembly_seq(conn_info, db_table_name, db_upload))
        
        elif ass_type == 'module':
            db_table_name = 'module_assembly'
            db_upload.update({
                    'module_name': stack_name, 
                    'proto_name': base_layer_id, 
                    'hxb_name': top_layer_id, 
                    'pml_position': str(bl_position), 
                    'hxb_position': str(tl_position), 
                    'put_position': str(put_position), 
                    'region': str(region), 
                    'ass_tray_id': str(ass_tray_id), 
                    'hxb_tray_id': str(comp_tray_id), 
                    'hxb_put_id': str(put_id), 
                    'tape_batch': tape_batch, 
                    'glue_batch': glue_batch})
            db_upload_info = {'module_name': stack_name, 
                              'proto_name': base_layer_id, 
                             'hxb_name': top_layer_id, 
                            'geometry' : geometry, 
                            'resolution': resolution,
                            'assembled': ass_run_date}
            try:
                db_upload_info.update({'bp_material': bp_material_dict[(stack_name.replace("-",""))[7]],
                                    'sen_thickness': sensor_thickness_dict[(stack_name.replace("-",""))[6]],
                                    'institution': inst_code_dict[(stack_name.replace("-",""))[9:11]],   
                                    'roc_version': roc_version_dict[(stack_name.replace("-",""))[8]]})
            except: print('Check module name again. Code incomplete.')
            db_upload_dict = {db_table_name: db_upload, 'module_info': db_upload_info}
        try:
            return asyncio.run(module_assembly_seq(conn_info, db_upload_dict))
        except:
            return (asyncio.get_event_loop()).run_until_complete(module_assembly_seq(conn_info, db_upload_dict))
        
    return "Dummy run. Data not saved."
   


##########################################################################
############################# DEBUGGING TOOLS ################################
#########################################################################

############ OTHER STUFF #######

def debugprint(test=[], news=''):
    return test[2]
#print((cmd_debugger()))

def cmd_debugger(conn_info=[]):
    ass_type, base_layer_id, top_layer_id = 'proto', 'BA_123_test', 'SL_123_test'
    ass_type, base_layer_id, top_layer_id = 'module', 'PL_123_test', 'HB_123_test'
    geometry, resolution = 'Full', 'LD'
    bl_position, tl_position, put_position, region = 1, 1, 1, 1
    ass_tray_id, comp_tray_id, put_id = '1', 2, 1
    ass_run_date = '2012-07-04'
    ass_time_begin = '12:01:00.123'
    ass_time_end = '12:03:59.456'
    tape_batch, glue_batch = None, None
    t = assembly_data(conn_info, ass_type, geometry, resolution, base_layer_id, top_layer_id, str(bl_position), str(tl_position))
    print(t)
    
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
