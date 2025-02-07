from math import atan2, sqrt, cos, sin, degrees, radians ###https://docs.python.org/3/library/math.html

### define function to get angle between two points with atan2(y,x)
def get_angle(XYi, XYf):
    return atan2((XYf[1]-XYi[1]),(XYf[0]-XYi[0]))

### define function to account for assembly tray rotation
def setup_rotation(angle):
    deg30 = radians(30)
    deg15 = radians(15)
    if (angle > deg30) or (angle < -deg30):
        res = angle % deg30
    else:
        res = angle
    if (res > deg15):       ### account for just a little under 30 deg
        return res - deg30
    elif (res < -deg15):
        return res + deg30
    else:
        return res



### define function to rotate and translate OGP relative measurements to gantry    
def map_to_gantry(Fgantry,OGP):
    if (len(OGP) > 8):     ###  reshape inputs for XY or XYZ
        reshape = 3
    else:
        reshape = 2
    i = 1
    point = []
    points = []
    for item in OGP:
        point.append(item)
        if not (i % reshape):
            points.append(point)
            point = []
        i += 1
    OGP = points    ### end of reshaping inputs
    print(Fgantry,OGP)
    XY_diff = [Fgantry [0][0] - OGP[0][0],Fgantry[0][1] - OGP[0][1]]    ### XY translational const
    U_diff = get_angle(Fgantry[0],Fgantry[1]) - get_angle(OGP[0],OGP[1])    ### rotational const
    mapped_OGP = []
    for XY in OGP: ### XY = [CP1, OP1, CP2, OP2]
        tXY = [XY[0] - Fgantry[0][0] + XY_diff[0], XY[1] - Fgantry[0][1] + XY_diff[1]]  ### subtract F1 and add translational XY
        theta_prime = atan2(tXY[1],tXY[0]) + U_diff       ### get angle of XY and add theta difference between F1 meas and rel
        tXYr = sqrt(tXY[0]**2+tXY[1]**2)                       ### get radius of translated points from F1
        newXY = [tXYr * cos(theta_prime) + Fgantry[0][0],tXYr * sin(theta_prime) + Fgantry[0][1]]
        if len(XY) > 2:   #Originaly 2  ### if Z in input, get Z translational const
            newXY.append(XY[2] + Fgantry[0][2] - OGP[0][2])
        mapped_OGP.append(newXY)
        print("this is mapped_OGP", mapped_OGP)
    return(mapped_OGP)

### define function to build pos 1 and 2 center coordinates
def build_XYZU(mapped_pos, Z):
    XYZU = mapped_pos[2]
    XYZU.append(Z)
    XYZU.append(setup_rotation(get_angle(mapped_pos[2],mapped_pos[3])))
    return XYZU

### define main LV function
def Calculate_Centers(Camera_Fiducials, Relative_Coordinates, Syringe_Relative_Coordinates):
    ### Normally get inputs from files and LV measurements
    F_meas = Camera_Fiducials
    rel_OGP = Relative_Coordinates
    rel_syringe = Syringe_Relative_Coordinates
    
    mapped_syringe = map_to_gantry(F_meas, rel_syringe)
    mapped_pos1 = map_to_gantry(F_meas,rel_OGP[0])
    mapped_pos2 = map_to_gantry(F_meas,rel_OGP[1])
    pos1 = build_XYZU(mapped_pos1,mapped_syringe[2][2])
    pos2 = build_XYZU(mapped_pos2,mapped_syringe[2][2])
    mapped_syringe[2].append(0)  #### recently added
    Centers = [pos1,pos2,mapped_syringe[2]]
    return Centers
    #return(Centers,F_meas,rel_OGP,rel_syringe,mapped_syringe,mapped_pos1)

###### comparing gantry to OGP only
#actual_gantry = [
#        [778.751276,710.7112,83],
#        [970.100742,1121.40813,83],
#        [884.819147,818.844902,73],
#        [831.660747,815.894401,73],
#        [866.947108,1008.404829,73],
#        [916.756862,1004.114328,73]]
#    
#def gantry_OGP_compare(gantry,mapped_OGP):
#    diff = []
#    i = 0
#    for points in mapped_OGP:
#       XYZU = []
#       j = 0
#       for axis in points:
#           XYZU.append(gantry[i][j]-axis)
#           j += 1
#        diff.append(XYZU)
#        i += 1
#   return diff
#
#def gantry_vs_OGP(actual_gantry,mapped_OGP):
#    actual_gantry[2].append(setup_rotation(get_angle(actual_gantry[2],actual_gantry[3])))
#    actual_gantry[4].append(setup_rotation(get_angle(actual_gantry[4],actual_gantry[5])))
#   return(gantry_OGP_compare(actual_gantry,mapped_OGP))
#
#
#### Test cases
#TCrel_OGP = [[31.20583,24.36994,222.39108,435.14251,137.24732,132.51362,84.08351,129.54399],
#       [31.20583,24.36994,222.39108,435.14251,119.27682,322.06299,169.09574,317.7928]]
#
#TCrel_syringe = [31.20583,24.36994,10,222.39108,435.14251,10,137.24732,132.51362,0]

#TCF_meas = [[778.751276,710.7112,83],[970.100742,1121.40813,83]]

#print(Calculate_Centers(TCF_meas,TCrel_OGP,TCrel_syringe))

#diff = gantry_vs_OGP(actual_gantry, Calculate_Centers(TCF_meas,TCrel_OGP,TCrel_syringe)[1])

#print("F1: "+str(diff[0]))
#print("F2: "+str(diff[1]))
#print("Pos1 Center: "+str(diff[2]))
#print("Pos1 Offset: "+str(diff[3]))
#print("Pos2 Center: "+str(diff[4]))
#print("Pos2 Offset: "+str(diff[5]))