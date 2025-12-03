from math import atan2, radians, cos, sin, pi

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
    

def fiducial_prediction(assembly_type, pos, new_fds, old_fds):
    ### Define fiducial distances based on whether module or protomodule
    distances = []
    xy1 = [0,0,0]
    #xy2 = [0,0,0]
    xy3 = [0,0,0]
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
        y_sign = -1
    elif pos == 1:
        x_sign = -1
        y_sign = 1
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
        x_distance = x_sign*distances[0]
        y_distance = y_sign*distances[1]
        if new_fds[6] == 0:
            rotation = 0
            Z_avg = new_fds[2]
        else:
            rotation = adjust_rotation(atan2((new_fds[1]-new_fds[7]),(new_fds[0]-new_fds[6])))
            Z_avg = Average([new_fds[2],new_fds[8]])
        predicted[1] = [new_fds[0] + x_distance*cos(rotation), new_fds[1] + y_distance*sin(rotation),Z_avg]
        predicted[2] = [new_fds[0] + x_distance*sin(rotation), new_fds[1] + y_distance*cos(rotation),Z_avg]
        predicted[3] = [predicted[1][0] + x_distance*sin(rotation), predicted[1][1] + y_distance*cos(rotation),Z_avg]
        rows = [0,3,6,9]
        index = 0
        for ind in rows:
            if ind in res:
                predicted[index] = [new_fds[ind],new_fds[ind+1],new_fds[ind+2]]
            index += 1
    return predicted

#res = fiducial_prediction('Protomodule LD Full', 0, [42.113607, 850.579980, 79.511506, 0, 0, 0, 0, 0, 0, 0, 0, 0], [42.113607, 850.579980, 79.511506, 208.097094, 851.087029, 79.446726, 42.351756, 774.582687, 79.529125, 208.334551, 775.089152, 79.479104])
res = fiducial_prediction('Protomodule LD Full', 0, [42.113607, 850.579980, 79.511506, 0, 0, 0, 42.351756, 774.582687, 79.529125, 0, 0, 0], [42.113607, 850.579980, 79.511506, 208.097094, 851.087029, 79.446726, 42.351756, 774.582687, 79.529125, 208.334551, 775.089152, 79.479104])
print(res)