from math import atan2, radians, cos, sin, pi   ### atan2 takes (y,x)

def Average(lst):
    return sum(lst) / len(lst)

def adjust_rotation(angle):
    deg30 = radians(30)     ### work in radians
    deg15 = radians(15)     ### This could be anything less than 30, as long as it accounts for rotations that round up to 30
    if (angle > deg30) or (angle < -deg30):     ### check if angle is more than 30
        res = angle % deg30                     ### if so, find number of times angle can be divided by 30
    else:
        res = angle                             ### consider the angle input as is if less than 30
    if (res > deg15):       ### account for just a little under 30 deg
        rotation = res - deg30  ### for instance, return -1 degrees if the angle is 29 degrees
    elif (res < -deg15):    ### account for just a little over -30 deg
        rotation = res + deg30  ### for instance, return 1 degree if the angle is -29 degrees
    else:
        rotation = res
    return rotation
    

def fiducial_prediction(assembly_type, pos, new_fds, old_fds, init_rotation):
    ### Define fiducial distances based on whether module or protomodule
    distances = []
    predicted = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
    if assembly_type == 'Protomodule LD Full':
        distances = [165.98, 75.999]
    elif assembly_type == 'Module LD Full':
        distances = [160, 70]
    else:
        return old_fds
    ### Negate X or Y, depending on pos 1 or 2
    if pos == 0:
        x_sign = 1
        y_sign = 1
    elif pos == 1:
        x_sign = -1
        y_sign = -1
    else:
        return old_fds
    ### The main program
    index = 0
    res = []
    for xyz in new_fds:
        if xyz != 0:
            res.append(index)
        index += 1
    if len(res) == 0:
        return old_fds
    else:
        rows = [0,3,6,9]
        CHs = [[],[],[],[]]
        index = 0
        for ind in rows:
            if ind in res:
                CHs[index] = [new_fds[ind],-new_fds[ind+1],new_fds[ind+2]]
            index += 1
        CH1 = CHs[0]
        CH191 = CHs[1]
        CH8 = CHs[2]
        CH197 = CHs[3]
        x_distance = x_sign*distances[0]
        y_distance = y_sign*distances[1]
        rotation = adjust_rotation(init_rotation)
        if not CH1:
            return old_fds
        else:
            predicted[0] = CH1
            Z_diff = round(CH1[2]-old_fds[0][2],1) ### check Z compared to previously fiducials to check for 200/300 um sensor
        if not CH8:
            CH8 = [CH1[0]+y_distance*sin(rotation),CH1[1]+y_distance*cos(rotation), old_fds[2][2]+Z_diff]
        else:
            rotation = adjust_rotation(atan2((CH8[1]-CH1[1]),(CH8[0]-CH1[0])))
        predicted[2] = CH8
        if not CH191:
            CH191 = [CH1[0]+x_distance*cos(rotation),CH1[1]+x_distance*sin(rotation),old_fds[1][2]+Z_diff]
        predicted[1] = CH191
        if not CH197:
            CH197 = [CH191[0]-y_distance*sin(rotation),CH8[1]+x_distance*sin(rotation),old_fds[3][2]+Z_diff]
        predicted[3] = CH197
        for CH in predicted:
            CH[1] = -CH[1] 
    return predicted

#res = fiducial_prediction('Protomodule LD Full', 0, [42.113607, 850.579980, 79.511506, 0, 0, 0, 0, 0, 0, 0, 0, 0], [42.113607, 850.579980, 79.511506, 208.097094, 851.087029, 79.446726, 42.351756, 774.582687, 79.529125, 208.334551, 775.089152, 79.479104])
#res = fiducial_prediction('Protomodule LD Full', 0, [42.113607, 850.579980, 79.511506, 0, 0, 0, 42.351756, 774.582687, 79.529125, 0, 0, 0], [42.113607, 850.579980, 79.511506, 208.097094, 851.087029, 79.446726, 42.351756, 774.582687, 79.529125, 208.334551, 775.089152, 79.479104])
#res = fiducial_prediction('Protomodule LD Full', 0, [41.438762, 851.012194, 79.526488, 0, 0, 0, 0, 0, 0, 0, 0, 0], [[41.438762, 851.012194, 79.526488], [207.417864, 852.334928, 79.456480], [42.050709, 775.016558, 79.526465], [208.029164, 776.339373, 79.454066]],-1.04968)
#res = fiducial_prediction('Protomodule LD Full', 0, [41.438762, 851.012194, 79.526488, 0, 0, 0, 42.050709, 775.016558, 79.526465, 0, 0, 0], [41.438762, 851.012194, 79.526488, 207.417864, 852.334928, 79.456480, 42.050709, 775.016558, 79.526465, 208.029164, 776.339373, 79.454066],-1.04968)
#res = fiducial_prediction('Protomodule LD Full', 0, [41.438762, 851.012194, 79.526488, 207.417864, 852.334928, 79.456480, 42.050709, 775.016558, 79.526465, 0, 0, 0], [41.438762, 851.012194, 79.526488, 207.417864, 852.334928, 79.456480, 42.050709, 775.016558, 79.526465, 208.029164, 776.339373, 79.454066],-1.04968)

res = fiducial_prediction('Protomodule LD Full', 0, [43.5748, 852.603, 79.5095, 0, 0, 0, 0, 0, 0, 0, 0, 0], [[41.590141, 849.715210, 79.519510], [207.553262, 852.426136, 79.469729], [42.837366, 773.726273, 79.494661], [208.800131, 776.437027, 79.469751]],-1.57537)


print(res)