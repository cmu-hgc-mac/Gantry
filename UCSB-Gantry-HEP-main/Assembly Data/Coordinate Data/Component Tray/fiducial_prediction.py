from math import atan2, radians, cos, sin, pi

def Average(lst):
    return sum(lst) / len(lst)

def fiducial_prediction(assembly_type, pos, new_fds, old_fds):
    ### Define fiducial distances based on whether module or protomodule
    distances = []
    xy1 = [0,0,0]
    xy2 = [0,0,0]
    predicted = []
    if assembly_type == 'Protomodule LD Full':
        distances = [165.98, 75.999]
    elif assembly_type == 'Module LD Full':
        distances = [160, 70]
    else:
        return old_fds
    ### Negate X or Y, depending on pos 1 or 2
    if pos == 1:
        x_sign = 1
        y_sign = -1
    elif pos == 2:
        x_sign = -1
        y_sign = 1
    else:
        return old_fds
    ### The main program
    if new_fds[0] == 0:			### if no valid measurements, return nothing
        return old_fds
    else:
        xy1 = [new_fds[0], new_fds[1], new_fds[2]]
        xy2 = [new_fds[3], new_fds[4], new_fds[5]]
        predicted.append(xy1)
        x_distance = x_sign*distances[0]
        y_distance = y_sign*distances[1]
        if new_fds[3] == 0:		### if only one measurement, assume no rotation
            rotation = 0
            predicted.append([xy1[0] + x_distance, xy1[1], xy1[2]])
            predicted.append([xy1[0], xy1[1] + y_distance, xy1[2]])
            predicted.append([xy1[0] + x_distance, xy1[1] + y_distance, xy1[2]])
        else:
            angle = atan2((new_fds[1]-new_fds[4]),(new_fds[0]-new_fds[3]))
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
            predicted.append(xy2)
            Z_avg = Average([new_fds[2], new_fds[5]])
            deg90 = pi/2
            predicted.append([xy1[0] + y_distance*cos(rotation+deg90), xy1[1] + y_distance*sin(rotation+deg90),Z_avg])
            predicted.append([xy2[0] + y_distance*cos(rotation+deg90), xy2[1] + y_distance*sin(rotation+deg90),Z_avg])

    return predicted

