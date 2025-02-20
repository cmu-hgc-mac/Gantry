from math import atan2, sqrt, cos, sin, degrees, radians ###https://docs.python.org/3/library/math.html

def Average(lst):
    return sum(lst) / len(lst)

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

### define function to build pos 1 and 2 center coordinates
def build_XYZU(reshape_input):
    X = []                      ### get separate each axis value to get overall average
    Y = []
    Z = []
    for item in reshape_input:
        X.append(item[0])
        Y.append(item[1])
        Z.append(item[2])
    XYZ = [X,Y,Z]
    XYZU = []
    for item in XYZ:            ### get average of each axis value
        XYZU.append(Average(item))
    XYZU.append(get_angle(reshape_input[2],reshape_input[0]))     ### get angle between CH 81 and 95 for sensor or FD3 and FD6 for hexaboard
    return XYZU

### define function to build pos 1 and 2 center coordinates
def build_XYZU_Right_Partial(reshape_input):
    X = []                      ### get separate each axis value to get overall average
    Y = []
    Z = []
    for item in reshape_input:
        X.append(item[0])
        Y.append(item[1] + 13)
        Z.append(item[2])
    XYZ = [X,Y,Z]
    XYZU = []
    for item in XYZ:            ### get average of each axis value
        XYZU.append(Average(item))
    XYZU.append(get_angle(reshape_input[2],reshape_input[0]))     ### get angle between CH 81 and 95 for sensor or FD3 and FD6 for hexaboard
    return XYZU

def build_XYZU_Right_Partial_Sensor(reshape_input):
    X = []                      ### get separate each axis value to get overall average
    Y = []
    Z = []
    for item in reshape_input:
        X.append(item[0])
        Y.append(item[1] + 45.14)
        Z.append(item[2])
    XYZ = [X,Y,Z]
    XYZU = []
    for item in XYZ:            ### get average of each axis value
        XYZU.append(Average(item))
    XYZU.append(get_angle(reshape_input[2],reshape_input[0]))     ### get angle between CH 81 and 95 for sensor or FD3 and FD6 for hexaboard
    return XYZU



def polar_to_XY(r,theta):
    return ([r * cos(theta), r * sin(theta)])

def get_CH_1(center):
    XY = polar_to_XY(88,radians(60) + center[3])      ### CH1 is radius 88mm at (60 degrees + rotation) relative to the center
    CH1_XYZ = [XY[0]+center[0],XY[1]+center[1]]        ### add center XY to get absolute value on gantry
    CH1_XYZ.append(center[2])
    return CH1_XYZ

def get_ID(center):
    XY = polar_to_XY(82,radians(270) + center[3])      ### ID is radius 82mm at (270 degrees + rotation) relative to the center
    ID_XYZ = [XY[0]+center[0],XY[1]+center[1]]        ### add center XY to get absolute value on gantry
    ID_XYZ.append(center[2])
    return ID_XYZ

### Main LV function    
def calculate_center(input):
    reshape_input = []          ### reshape input to XYZ
    XYZ = []
    i = 1
    for item in input:
        XYZ.append(item)
        if not (i % 3):
            reshape_input.append(XYZ)
            XYZ = []
        i += 1
    center = build_XYZU(reshape_input)  ### get center coordinates
    CH1 = get_CH_1(center)
    CH1.append(0)
    ID = get_ID(center)
    ID.append(0)
    print(center[3])
    center[3] = setup_rotation(center[3])
    return([center,CH1,ID])


### Main LV function for Right Partial    
def calculate_center_Right_Partial(input):
    reshape_input = []          ### reshape input to XYZ
    XYZ = []
    i = 1
    for item in input:
        XYZ.append(item)
        if not (i % 3):
            reshape_input.append(XYZ)
            XYZ = []
        i += 1
    center = build_XYZU_Right_Partial(reshape_input)  ### get center coordinates
    CH1 = get_CH_1(center)
    CH1.append(0)
    ID = get_ID(center)
    ID.append(0)
    print(center[3])
    center[3] = setup_rotation(center[3])
    return([center,CH1,ID])


### Main LV function for Right Partial    
def calculate_center_Right_Partial_Sensor(input):
    reshape_input = []          ### reshape input to XYZ
    XYZ = []
    i = 1
    for item in input:
        XYZ.append(item)
        if not (i % 3):
            reshape_input.append(XYZ)
            XYZ = []
        i += 1
    center = build_XYZU_Right_Partial_Sensor(reshape_input)  ### get center coordinates
    CH1 = get_CH_1(center)
    CH1.append(0)
    ID = get_ID(center)
    ID.append(0)
    print(center[3])
    center[3] = setup_rotation(center[3])
    return([center,CH1,ID])


### For test purposes only
#pos1_test = [570.987457,905.516075,78.957649,
#            578.986868,905.478159,78.979373,
#            570.126762,722.616272,78.711872,
#            578.127606,722.579092,78.719898]

#pos2_test = [578.127606,922.579092,78.719898,
#            570.126762,922.616272,78.711872,
#            578.986868,1105.478159,78.979373,
#            570.987457,1105.516075,78.957649]
      
# print(calculate_center(pos1_test))
# print(calculate_center(pos2_test))
# calculate_center(pos1_test)