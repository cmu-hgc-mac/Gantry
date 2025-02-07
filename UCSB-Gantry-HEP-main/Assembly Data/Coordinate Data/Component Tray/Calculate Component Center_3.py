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

### define function to build pos 1 and 2 center coordinates
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
    return XYZU

### Main LV function    
def calculate_center(input, position, adjustment):
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



##### For Hexaboard LD Right, LD Left and LD Five

### define function to build pos 1 and 2 center coordinates
def build_XYZU_adjY_axisX(reshape_input, position, adjustment):
    X = []                      ### get separate each axis value to get overall average
    Y = []
    Z = []
    if position == 1:
        adj = adjustment
    if position == 2:
        adj = -adjustment
    for item in reshape_input:
        X.append(item[0])
        Y.append(item[1] + adj) # PCB 13 ; kapton 44.945
        Z.append(item[2])
    XYZ = [X,Y,Z]
    XYZU = []
    for item in XYZ:            ### get average of each axis value
        XYZU.append(Average(item))
    # XYZU.append(get_angle(reshape_input[3],reshape_input[2])) 
    XYZU.append(get_angle(reshape_input[1],reshape_input[2]))    ### get angle between CH 81 and 95 for sensor or FD3 and FD6 for hexaboard
    return XYZU

### Main LV function for Hexaboard LD Right, LD Left and LD Five   
def calculate_center_adjY_axisX(input, position, adjustment):
    reshape_input = []          ### reshape input to XYZ
    XYZ = []
    i = 1
    for item in input:
        XYZ.append(item)
        if not (i % 3):
            reshape_input.append(XYZ)
            XYZ = []
        i += 1
    center = build_XYZU_adjY_axisX(reshape_input, position, adjustment)  ### get center coordinates
    CH1 = get_CH_1(center)
    CH1.append(0)
    ID = get_ID(center)
    ID.append(0)
    print(center[3])
    center[3] = setup_rotation(center[3])
    return([center,CH1,ID])



#### For Sensor LD Right, LD Left

def build_XYZU_adjY_axisY(reshape_input, position, adjustment):
    #print("This is reshape input", reshape_input)
    X = []                      ### get separate each axis value to get overall average
    Y = []
    Z = []
    if position == 1:
        adj = adjustment
    if position == 2:
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
def calculate_center_adjY_axisY(input, position, adjustment):
    reshape_input = []          ### reshape input to XYZ
    XYZ = []
    i = 1
    for item in input:
        XYZ.append(item)
        if not (i % 3):
            reshape_input.append(XYZ)
            XYZ = []
        i += 1
    center = build_XYZU_adjY_axisY(reshape_input, position, adjustment)  ### get center coordinates
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

def build_XYZU_adjX_axisY(reshape_input, position, adjustment):
    X = []                      ### get separate each axis value to get overall average
    Y = []
    Z = []
    if position == 1:
        adj = adjustment
    if position == 2:
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
def calculate_center_adjX_axisY(input, position, adjustment):
    reshape_input = []          ### reshape input to XYZ
    XYZ = []
    i = 1
    for item in input:
        XYZ.append(item)
        if not (i % 3):
            reshape_input.append(XYZ)
            XYZ = []
        i += 1
    center = build_XYZU_adjX_axisY(reshape_input, position, adjustment)  ### get center coordinates
    CH1 = get_CH_1(center)
    CH1.append(0)
    ID = get_ID(center)
    ID.append(0)
    center[3] = setup_rotation(center[3])
    return([center,CH1,ID])




### Additional common procedures ###


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



##### For Hexaboard LD Five

### define function to get angle between two points with atan2(y,x)
#def get_angle_five(XYi, XYf):
    #print("This is atan2", atan2((XYf[0]-XYi[0]),(XYf[1]-XYi[1])))
 #   if ((XYi[1]-XYf[1])>0):
  #      return atan2((XYi[1]-XYf[1]),(XYf[0]-XYi[0]))
   # else:
    #    return atan2((XYf[1]-XYi[1]),(XYf[0]-XYi[0]))


### define function to build pos 1 and 2 center coordinates
#def build_XYZU_five(reshape_input, position):
#    X = []                      ### get separate each axis value to get overall average
#    Y = []
#    Z = []
 #   if position == 1:
 #       adjustment = 0
 #   if position == 2:
 #       adjustment = 0
 #   for item in reshape_input:
#        X.append(item[0])
#        Y.append(item[1]) # + adjustment) 
#        Z.append(item[2])
#    XYZ = [X,Y,Z]
#    XYZU = []
#    for item in XYZ:            ### get average of each axis value
#        XYZU.append(Average(item))
#    XYZU.append(get_angle_five(reshape_input[0],reshape_input[1]))     ### get angle between CH 81 and 95 for sensor or FD3 and FD6 for hexaboard
#    return XYZU

### Main LV function for LD Five HB    
#def calculate_center_five(input, position, adjustment):
#    reshape_input = []          ### reshape input to XYZ
#    XYZ = []
#    i = 1
#    for item in input:
#        XYZ.append(item)
#        if not (i % 3):
#            reshape_input.append(XYZ)
#            XYZ = []
#        i += 1
#    center = build_XYZU_five(reshape_input, position)  ### get center coordinates
#    CH1 = get_CH_1(center)
#    CH1.append(0)
#    ID = get_ID(center)
#    ID.append(0)
    #print(center[3])
#    center[3] = setup_rotation(center[3])
#    return([center,CH1,ID])














