from math import atan2, sqrt, cos, sin, degrees, radians ###https://docs.python.org/3/library/math.html


### Common procedures ###

def Average(lst):
    return sum(lst) / len(lst)

### define function to get angle between two points with atan2(y,x)
def get_angle(XYi, XYf):
    return atan2((XYf[1]-XYi[1]),(XYf[0]-XYi[0]))

### define function to account for assembly tray rotation
### Assumes the actual rotation angle is less than +/- 15 degrees. 
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


#### Symmetric Hexaboard (HD Full, LD Full)
#### Symmetric Sensor (HD Full, LD Full, LD Five)

### define function to build pos 1, 2, 3, and 4 center coordinates
def build_XYZU(reshape_input):
    X = []                      ### get separate each axis value to get overall average
    Y = []
    Z = []
    for item in reshape_input:
        X.append(item[0])  ### Full: no offset; Bottom: 41.7355
        Y.append(item[1])
        Z.append(item[2])
    XYZ = [X,Y,Z]
    XYZU = []
    for item in XYZ:            ### get average of each axis value
        XYZU.append(Average(item))
    XYZU.append(get_angle(reshape_input[2],reshape_input[0]))     ### get angle between CH 81 and 95 for sensor or FD3 and FD6 for hexaboard
    distance = sqrt(((X[0]-X[1])**2)+((Y[0]-Y[1])**2))
    return XYZU, distance

### Main LV function    
def calculate_center(input, position, adjustment, left_handed):
    reshape_input = []          ### reshape input to XYZ
    XYZ = []
    i = 1
    for item in input:
        XYZ.append(item)
        if not (i % 3):
            reshape_input.append(XYZ)
            XYZ = []
        i += 1
    center, distance = build_XYZU(reshape_input)  ### get center coordinates
    CH1 = get_CH_1(center,distance)
    CH1.append(0)
    ID = get_ID(center)
    ID.append(0)
    print(center[3])
    center[3] = setup_rotation(center[3])
    return([center,CH1,ID])



##### For Hexaboard LD Right, LD Left and LD Five
## LD Right is Left_handed, while LD Left and LD Five are Right_handed.

### define function to build pos 1, 2, 3, and 4 center coordinates
def build_XYZU_adjY_axisX(reshape_input, position, adjustment, left_handed):
#def build_XYZU_adjY_axisX(reshape_input, position, adjustment):
    X = []                      ### get separate each axis value to get overall average
    Y = []
    Z = []
    #left_handed = 1
    if (position == 1) or (position == 3):
        adj = adjustment
    if (position == 2) or (position == 4):
        adj = -adjustment
    for item in reshape_input:
        X.append(item[0])
        Y.append(item[1] + adj) # PCB 28 ; kapton 44.945
        Z.append(item[2])
    XYZ = [X,Y,Z]
    #print(XYZ)
    XYZU = []
    for item in XYZ:            ### get average of each axis value
        XYZU.append(Average(item))
    # XYZU.append(get_angle(reshape_input[3],reshape_input[2])) 

    alpha = get_angle(reshape_input[1],reshape_input[2])  ### get angle between CH 81 and 95 for sensor or FD3 and FD6 for hexaboard

    ### adjust for off-hexaboard-center fiducial-center
    delta_x = adj*sin(alpha)
    delta_y = adj*(1-cos(alpha))
    
    # Pos1 vs pos2 is taken care of with the sign of adj-variable. 
    #print("delta_x: ", delta_x, " delta_y :", delta_y)
    if left_handed == 1:
        XYZU[0] -= delta_x
    else:
       XYZU[0] += delta_x
    XYZU[1] += delta_y
    # end angular correction

    XYZU.append(alpha)    
    return XYZU

### Main LV function for Hexaboard LD Right, LD Left and LD Five   
def calculate_center_adjY_axisX(input, position, adjustment, left_handed):
#def calculate_center_adjY_axisX(input, position, adjustment):
    reshape_input = []          ### reshape input to XYZ
    XYZ = []
    i = 1
    for item in input:
        XYZ.append(item)
        if not (i % 3):
            reshape_input.append(XYZ)
            XYZ = []
        i += 1
    #print("before build", input, reshape_input)
    center = build_XYZU_adjY_axisX(reshape_input, position, adjustment, left_handed)
    #center = build_XYZU_adjY_axisX(reshape_input, position, adjustment)  ### get center coordinates
    CH1 = get_CH_1(center)
    CH1.append(0)
    ID = get_ID(center)
    ID.append(0)
    #print("before center", center[3])
    center[3] = setup_rotation(center[3])
    return([center,CH1,ID])



#### For Sensor LD Right, LD Left

def build_XYZU_adjY_axisY(reshape_input, position, adjustment, left_handed):
    #print("This is reshape input", reshape_input)
    X = []                      ### get separate each axis value to get overall average
    Y = []
    Z = []
    if (position == 1) or (position == 3):
        adj = adjustment
    if (position == 2) or (position == 4):
        adj = -adjustment
    for item in reshape_input:
        X.append(item[0])
        Y.append(item[1] + adj)  ## sensor 45.14; kapton 44.945; Alum 45.9
        Z.append(item[2])
    XYZ = [X,Y,Z]
    XYZU = []
    for item in XYZ:            ### get average of each axis value
        XYZU.append(Average(item))
    reshape_input_top_average_center_x = (reshape_input[0][0] + reshape_input[1][0])/2
    reshape_input_top_average_center_y = (reshape_input[0][1] + reshape_input[1][1])/2
    reshape_input_bottom_average_center_x = (reshape_input[2][0] + reshape_input[3][0])/2
    reshape_input_bottom_average_center_y = (reshape_input[2][1] + reshape_input[3][1])/2
    reshape_input_top_center = [reshape_input_top_average_center_x,reshape_input_top_average_center_y]
    reshape_input_bottom_center = [reshape_input_bottom_average_center_x,reshape_input_bottom_average_center_y]
    XYZU.append(get_angle(reshape_input_bottom_center,reshape_input_top_center))     ### get angle between CH 81 and 95 for sensor or FD3 and FD6 for hexaboard
    #print("This is XYZU", XYZU)
    XYZU[0] = reshape_input_bottom_average_center_x
    return XYZU



### Main LV function for Sensor LD Right, LD Left    
def calculate_center_adjY_axisY(input, position, adjustment, left_handed):
    reshape_input = []          ### reshape input to XYZ
    XYZ = []
    i = 1
    for item in input:
        XYZ.append(item)
        if not (i % 3):
            reshape_input.append(XYZ)
            XYZ = []
        i += 1
    center = build_XYZU_adjY_axisY(reshape_input, position, adjustment, left_handed)  ### get center coordinates
    CH1 = get_CH_1(center)
    #print("This is Center", center)
    #print("This is CH1", CH1)
    CH1.append(0)
    ID = get_ID(center)
    #print("This is ID", ID)
    ID.append(0)
    #print("This is center[3]", center[3])
    #center[3] = setup_rotation_Right_Partial_Sensor(center[3])
    center[3] = setup_rotation(center[3])
    return([center,CH1,ID])


## For Sensors HD Top, LD Top, LD Bottom and Hexaboards HD Top, LD Top, LD Bottom

def build_XYZU_adjX_axisY(reshape_input, position, adjustment, left_handed):
    X = []                      ### get separate each axis value to get overall average
    Y = []
    Z = []
    if (position == 1) or (position == 3):
        adj = adjustment
    if (position == 2) or (position == 4):
        adj = -adjustment
    for item in reshape_input:
        X.append(item[0] + adj)
        Y.append(item[1])  
        Z.append(item[2])
    XYZ = [X,Y,Z]
    XYZU = []
    for item in XYZ:            ### get average of each axis value
        XYZU.append(Average(item))
    reshape_input_top_average_center_x = (reshape_input[0][0] + reshape_input[1][0])/2
    reshape_input_top_average_center_y = (reshape_input[0][1] + reshape_input[1][1])/2
    reshape_input_bottom_average_center_x = (reshape_input[2][0] + reshape_input[3][0])/2
    reshape_input_bottom_average_center_y = (reshape_input[2][1] + reshape_input[3][1])/2
    reshape_input_top_center = [reshape_input_top_average_center_x,reshape_input_top_average_center_y]
    reshape_input_bottom_center = [reshape_input_bottom_average_center_x,reshape_input_bottom_average_center_y]
    XYZU.append(get_angle(reshape_input_bottom_center,reshape_input_top_center))     ### get angle between CH 81 and 95 for sensor or FD3 and FD6 for hexaboard
    #XYZU[0] = reshape_input_bottom_average_center_x
    return XYZU



### Main LV function for Sensors HD Top, LD Top, LD Bottom and Hexaboards HD Top, LD Top, LD Bottom    
def calculate_center_adjX_axisY(input, position, adjustment, left_handed):
    reshape_input = []          ### reshape input to XYZ
    XYZ = []
    i = 1
    for item in input:
        XYZ.append(item)
        if not (i % 3):
            reshape_input.append(XYZ)
            XYZ = []
        i += 1
    center = build_XYZU_adjX_axisY(reshape_input, position, adjustment, left_handed)  ### get center coordinates
    CH1 = get_CH_1(center)
    CH1.append(0)
    ID = get_ID(center)
    ID.append(0)
    center[3] = setup_rotation(center[3])
    return([center,CH1,ID])




### Additional common procedures ###


def polar_to_XY(r,theta):
    return ([r * cos(theta), r * sin(theta)])

def get_CH_1(center, distance):
    if distance <165:      ### check for sensor vs HB fiducials, default to sensor
        XY = polar_to_XY(87.938,radians(62.903) + center[3])      ### CH1 is radius 87.938 mm at (62.903 degrees + rotation) relative to the center for the HB
    else:
        XY = polar_to_XY(87.16,radians(61.215) + center[3])      ### CH1 is radius 87.16 mm at (61.215 degrees + rotation) relative to the center for the sensor
    CH1_XYZ = [XY[0]+center[0],XY[1]+center[1]]        ### add center XY to get absolute value on gantry
    CH1_XYZ.append(center[2])
    return CH1_XYZ

def get_ID(center):
    XY = polar_to_XY(83.104,radians(270-1.134) + center[3])      ### ID is radius 82mm at (270 degrees + rotation) relative to the center
    ID_XYZ = [XY[0]+center[0],XY[1]+center[1]]        ### add center XY to get absolute value on gantry
    ID_XYZ.append(center[2])
    return ID_XYZ







#input = [42.792827, 795.474849, 51.0,
#         42.792827, 795.474849, 51.0,
#         206.831202, 794.569494, 51.1,
#         206.831202, 794.569494, 51.1]

#input = [42.973427, 794.203312, 51.0,
#         42.973427, 794.203312, 51.0,
#         207.013262, 794.732292, 51.1,
#         207.013262, 794.732292, 51.1]

#input = [42.647238, 796.176853, 51.0,
#         42.647238, 796.176853, 51.0,
#         206.658514, 792.836328, 51.1,
#         206.658514, 792.836328, 51.1]

#print("Input FD1: [", input[0], " ", input[1], "] FD2: [", input[6], ' ', input[7], "]")
#print("This is calculate Component Center:", calculate_center_adjY_axisX(input, 1, 28, 1))

#print("This is calculate Component Center:", calculate_center_adjY_axisX(input, 2, 28, 1))





