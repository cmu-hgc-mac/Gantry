from math import atan2, sqrt, cos, sin, radians ###https://docs.python.org/3/library/math.html


### define function to get angle between two points with atan2(y,x)
def get_angle(XYi, XYf):        ### XYi is inital point (center pin), XYf is final point (offset pin)
    return atan2((XYf[1]-XYi[1]),(XYf[0]-XYi[0]))   ### OP Y - CP Y, OP X - CP X


### define function to account for assembly tray rotation
def setup_rotation(angle):
    deg30 = radians(30)     ### work in radians
    deg15 = radians(15)     ### This could be anything less than 30, as long as it accounts for rotations that round up to 30
    if (angle > deg30) or (angle < -deg30):     ### check if angle is more than 30
        res = angle % deg30                     ### if so, find number of times angle can be divided by 30
    else:
        res = angle                             ### consider the angle input as is if less than 30
    
    if (res > deg15):       ### account for just a little under 30 deg
        return res - deg30  ### for instance, return -1 degrees if the angle is 29 degrees
    elif (res < -deg15):    ### account for just a little over -30 deg
        return res + deg30  ### for instance, return 1 degree if the angle is -29 degrees
    else:
        return res          ### for instance, 0.1 degrees would be returned as-is


####LIAM NOTE - The better way to go about this would be to add a variable at the start
#That is checked - is this a partial? Right? Left? So on, and then that would add the correction
#Rather than need a seperate map to gantry function for each step. But this is the way I'm doing it for now

### define function to rotate and translate OGP relative measurements to gantry    
def map_to_gantry(gantry,OGP):
    XY_diff = [gantry [0][0] - OGP[0][0],gantry[0][1] - OGP[0][1]]    ### XY translational constant
    U_diff = get_angle(gantry[0],gantry[1]) - get_angle(OGP[0],OGP[1])    ### rotational constant
    mapped_OGP = []
    for XY in OGP:      ### OGP fiducials do not need to returned
 #       print("This is XY[0]", XY[0], "this is XY[1]", XY[1])
      #  print("This is Gantry[0][0]",gantry[0][0], "This is Gantry[0][1]", gantry[0][1])
        tXY = [XY[0] - gantry[0][0] + XY_diff[0], XY[1] - gantry[0][1] + XY_diff[1]]  ### subtract F1 and add translational XY
        theta_prime = atan2(tXY[1],tXY[0]) + U_diff       ### get angle of XY and add theta difference between F1 meas and rel
        tXYr = sqrt(tXY[0]**2+tXY[1]**2)                       ### get radius of translated points from F1
        #print("This is tXYr", tXYr)
        newXYZ = [tXYr * cos(theta_prime) + gantry[0][0],tXYr * sin(theta_prime) + gantry[0][1],OGP[6][2] + gantry[0][2] - OGP[0][2]]     ### get rotated and translated XY while also adding back 
       # print("This is newXYZ", newXYZ)
        mapped_OGP.append(newXYZ)      ### Append Z value, which is based on syringe. Find Workspace.vi adds baseplate pedestal height to pos1 and pos2.

    return(mapped_OGP)      ### return mapped XYZ for: pos1, pos2, syringe


##LIAM - Either Gantry[0][0] or newXYZ needs the 12 addition
### define function to rotate and translate OGP relative measurements to gantry    
def map_to_gantry_Right_Partial(gantry,OGP):
    XY_diff = [gantry [0][0] - OGP[0][0],gantry[0][1] - OGP[0][1]]    ### XY translational constant
    U_diff = get_angle(gantry[0],gantry[1]) - get_angle(OGP[0],OGP[1])    ### rotational constant
    mapped_OGP = []
    for XY in OGP:      ### OGP fiducials do not need to returned
        tXY = [XY[0] - gantry[0][0] + XY_diff[0], XY[1] - gantry[0][1] + XY_diff[1]]  ### subtract F1 and add translational XY
        #print("this is tXY", tXY)
        #print("This is XY", XY)
        theta_prime = atan2(tXY[1],tXY[0]) + U_diff       ### get angle of XY and add theta difference between F1 meas and rel
        #print("This is theta_prime right partial:", theta_prime)
        tXYr = sqrt(tXY[0]**2+tXY[1]**2)                       ### get radius of translated points from F1
        #print("this is tXYr", tXYr)
        print("this is tXYr", tXYr)
        print("this is theta_prime[2]", theta_prime)
        newXYZ = [tXYr * cos(theta_prime) + gantry[0][0],tXYr * sin(theta_prime) + gantry[0][1],OGP[6][2] + gantry[0][2] - OGP[0][2] - 10]     ### get rotated and translated XY while also adding back F1
        print("This is newXYZ right Partial: ", newXYZ)
        mapped_OGP.append(newXYZ)      ### Append Z value, which is based on syringe. Find Workspace.vi adds baseplate pedestal height to pos1 and pos2.
        #print("This is mapped_OGP", mapped_OGP)
    return(mapped_OGP)      ### return mapped XYZ for: pos1, pos2, syringe



### define function to get XYZU center based on center and offset pins
def build_XYZU(mapped_pos):
    XYZUcenter = mapped_pos[0]       ### use mapped center pin XYZ for baseplate center
   # print("This is XYZUcenter", XYZUcenter)
    rotation = get_angle(mapped_pos[0],mapped_pos[1])
    XYZUcenter.append(setup_rotation(rotation))    ### First, get the angle of the offset pin compared to the center pin. Then, pass this result to account for assembly tray rotation.
    return XYZUcenter

### define function to get XYZU center based on center and offset pins
def build_XYZU_Right_Partial(mapped_pos):
 #   print("This is mapped_pos:", mapped_pos)
    XYZUcenter = mapped_pos[0]       ### use mapped center pin XYZ for baseplate center
    rotation = get_angle(mapped_pos[0],mapped_pos[1])
    XYZUcenter.append(setup_rotation(rotation)) ### First, get the angle of the offset pin compared to the center pin. Then, pass this result to account for assembly tray rotation.
#    print("This is XYZUcenter Right Partial:", XYZUcenter)
    return XYZUcenter


### define main LV function
def Calculate_Centers(gantry,OGP):              ### gantry is fiducials measured on gantry. OGP is relative coordinates of: fiducials, pos1 center and offset pins, pos2 center and offset pins, and syringe
    mapped_OGP = map_to_gantry(gantry,OGP)      ### map OGP relative measurements onto gantry based on measured gantry fiducials
    #print("This is mapped_OGP", mapped_OGP)
    mapped_syringe = mapped_OGP[6]              ### mapped syringe XYZ
    mapped_pos1 = [mapped_OGP[2],mapped_OGP[3]] ### mapped pos1 XYZ of center and offset pins
    #print("This is mapped_pos1", mapped_pos1)
    mapped_pos2 = [mapped_OGP[4],mapped_OGP[5]] ### mapped pos2 XYZ of center and offset pins
    pos1 = build_XYZU(mapped_pos1)              ### pass center and offset pins to create center XYZU for pos1
    pos2 = build_XYZU(mapped_pos2)              ### pass center and offset pins to create center XYZU for pos2
    mapped_syringe.append(0)                    ### append 0 as U for syringe as an arbitrary place holder, otherwise LV throws an error
    Centers = [pos1,pos2,mapped_syringe]        ### return XYZU for pos1, pos2, and syringe
    return Centers


### define main LV function
def Calculate_Centers_Right_Partial(gantry,OGP):              ### gantry is fiducials measured on gantry. OGP is relative coordinates of: fiducials, pos1 center and offset pins, pos2 center and offset pins, and syringe
    mapped_OGP = map_to_gantry_Right_Partial(gantry,OGP)      ### map OGP relative measurements onto gantry based on measured gantry fiducials
    mapped_syringe = mapped_OGP[6]              ### mapped syringe XYZ
    mapped_pos1 = [mapped_OGP[2],mapped_OGP[3]] ### mapped pos1 XYZ of center and offset pins
    #print("This is mapped_pos1", mapped_pos1)
    mapped_pos2 = [mapped_OGP[4],mapped_OGP[5]] ### mapped pos2 XYZ of center and offset pins
    pos1 = build_XYZU_Right_Partial(mapped_pos1)              ### pass center and offset pins to create center XYZU for pos1
    #print("This is pos1", pos1)
    pos2 = build_XYZU_Right_Partial(mapped_pos2)              ### pass center and offset pins to create center XYZU for pos2
    mapped_syringe.append(0)                    ### append 0 as U for syringe as an arbitrary place holder, otherwise LV throws an error
    Centers = [pos1,pos2,mapped_syringe]  ### return XYZU for pos1, pos2, and syringe
    #print("This is Right Partial Centers: ", Centers)
    return Centers


# ### For testing only

# gantrytest = [[463.848342, 726.221313, 64.051654],
#                [462.521526, 1081.253003, 64.023415]]

# gantryRightPartial = [[457.573130, 712.877978, 64.051654],
#                [457.732729, 1119.256087, 64.023415]]

# OGPtest = [[0,-355.043,2.5828],
#             [0.0,0,2.49156],
#             [137.03, -260.73, 0],
#             [62.131, -260.471, 0],
#             [101.65204,324.00151,0],
#             [176.51029,323.94894,0],
#             [168.20555,416.07082,0.03927]]

# OGPPartialRight = [[0.003,-406.374,2.5828],
#             [0.0,0,2.49156],
#             [142.332, -298.176, 0], #[142.339, -308.182, 0],
#             [142.355, -373.200, 0],
#             [91.504,97.698,0],
#             [91.593,32.703,0],
#             [168.20555,416.07082,0.03927]]



# This is for the Partial Fiducials
# OGPtest = [[0,-355.043,2.5828],
#             [0.0,0,2.49156],
#             [137.03,-260.73,0],
#             [137.03,-180.471,0],
#             [101.65204,324.00151,0],
#             [176.51029,323.94894,0],
#             [168.20555,416.07082,0.03927]]

# OGPtest = [[31.20424,24.37047,2.5828],
#             [222.3899,435.14079,2.49156],
#             [152.41879,133.47891],
#             [77.4564,133.50847],
#             [101.65204,324.00151],
#             [176.51029,323.94894],
#             [168.20555,416.07082,0.03927]]

#print("This is Calculate Center:", Calculate_Centers(gantrytest,OGPtest))


