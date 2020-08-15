import math
import numpy as np

# Our axis is: 
# [0, 0, 0] = origin = center of mirror_G
# [1, 0, 0] = x-direction = mirror_G to mirror_M2
# [0, 1, 0] = y-direction = mirror_G to mirror_M1
# [0, 0, 1] = z-direction, obeying verter product rule

class MichelsonSimulation:
    # We have a list of point-source, each with its position and wavelength information.
    # We give central mirror(G), position-changing mirror(M1), direction-changing mirror(M2)
    # information respectively, including its central point and direction.
    # All of the above information should be 'np.array' type.
    # We give a term to control interference type, and the initialize of screen is related to it.
    def __init__(self):
        self.source_list = []
        self.mirror_G = []
        self.mirror_M1 = []
        self.mirror_M2 = []
        self.islocalInterference = False
        self.screen = []
    
    # insert a list of source information, including its position and wavelength
    def insertSource(self, source_position, wavelength):
        position = np.array(source_position)
        self.source_list.append([position, wavelength])
    
    # delete a point source, using its position information
    def deleteSource(self, position):
        positionVector = np.array(position)
        source_list = self.source_list
        self.source_list = [x for x in source_list if not (x[0]==positionVector).all()]
    
    # clear all the point sources
    def clearSource(self):
        self.source_list.clear()
    
    def get_SourceList(self):
        return self.source_list
    
    # initialize information of central mirror —— G, input '[...], [...]'
    def initialmirror_G(self, mirror_G_position, mirror_G_direction):
        position = np.array(mirror_G_position)
        direction = np.array(mirror_G_direction)
        self.mirror_G.append(position)
        self.mirror_G.append(direction)
    
    # initialize information of mirror M1 (the type is [np.array, np.array])
    def initialmirror_M1(self, mirror_M1_position, mirror_M1_direction):
        position = np.array(mirror_M1_position)
        direction = np.array(mirror_M1_direction)
        self.mirror_M1.append(position)
        self.mirror_M1.append(direction)
    
    # initialize information of mirror M2 (the type is [np.array, np.array])
    def initialmirror_M2(self, mirror_M2_position, mirror_M2_direction):
        position = np.array(mirror_M2_position)
        direction = np.array(mirror_M2_direction)
        self.mirror_M2.append(position)
        self.mirror_M2.append(direction)
    
    # move M1 mirror(i.e. move its central point)
    def movemirror_M1(self, movement):
        movementVector = np.array(movement)
        self.mirror_M1[0] += movementVector
    
    # move M2 mirror(i.e. change its direction)
    def movemirror_M2(self, directionChange):
        directionVector = np.array(directionChange)
        self.mirror_M2[1] += directionVector
    
    def get_mirror(self):
        G, M1, M2 = self.mirror_G, self.mirror_M1, self.mirror_M2
        return 'G', G, 'M1', M1, 'M2', M2
    
    # change to non-local interference mode, together with finite-distance-screen
    # we set distance from mirror_G to screen is 30cm
    def changeTo_nonlocal(self):
        self.islocalInterference = False
        screen = []                         # here initialize screen, 100*100 points, 5cm*5cm
        center = np.array([0, -30, 0])
        for i in range(-50, 50):
            for j in range(-50, 50):
                point = center + np.array([5 * i / 100, 0, 5 * j /100])
                screen.append(point)
        self.screen = screen
    
    # change to local interference mode, together with infinite-distance-screen
    # we only consider the relative position between screen and lens(i.e. our eyes)
    # thus we set lens as [0, 0, 0], the relative distance is 0.5cm
    def changeTo_local(self):
        self.islocalInterference = True
        screen = []                         # here initialize screen, 100*100 points, 5cm*5cm
        center = np.array([0, -0.5, 0])
        for i in range(-50, 50):
            for j in range(-50, 50):
                point = center + np.array([2 * i / 100, 0, 2 * j /100])
                screen.append(point)
        self.screen = screen
        
    def get_InterferenceMode(self):
        mode = self.islocalInterference
        if mode:
            return 'local interference'
        else:
            return 'non-local interference'
    
    def get_screen(self):
        return self.screen
    
    # This is the mirror symmetry operation acting on a point source.
    # mirror = [np.array(central position), np.array(direction)]
    # source = [np.array(position), wavelength], here we just use the former
    def mirror_operation(self, source_position, mirror):
        const = np.inner(mirror[1], -1 * mirror[0])                 # change a(x-x0)+b(y-y0)+c(z-z0) to ax+by+cz+d
        coe = -2 * (np.inner(mirror[1], source_position) + const) \
                / np.inner(mirror[1], mirror[1])                    # compute the coeffient for image_coordinate calculation
        image_coordinate = source_position + coe * mirror[1]
        return image_coordinate
    
    # This is the projection from a vector to a given axis, both input and output are np.array
    def projection(self, vector, axis):
        coe = np.inner(vector, axis) / np.inner(axis, axis)
        projectVector = coe * axis
        return projectVector
    
    # Output an image source list, corresponding to source S, 
    # the term is like '[np.array(position of S1), np.array(position of S2), wavelength]'
    # Detailly speaking, S-mirrorG-mirrorM1-S1, S-mirrorM2-mirrorG-S2
    def get_imageSourceList(self):
        source_list = self.source_list
        image_list = []
        for source in source_list:
            wavelength = source[1]           # get information of wavelength
            position_S = source[0]
            
            # get position of S1
            position_S1 = self.mirror_operation(self.mirror_operation(position_S, self.mirror_G), self.mirror_M1)
            
            # get position of S2
            position_S2 = self.mirror_operation(self.mirror_operation(position_S, self.mirror_M2), self.mirror_G)
            
            image_list.append([position_S1, position_S2, wavelength])  # generate coherent light source unit
        return image_list
    
    # get interval between two vector, supporting both type(list) and type(np.ndarray)
    def get_interval(self, vec1, vec2):
        if type(vec1) is not np.ndarray:
            vec1 = np.array(vec1)
        if type(vec2) is not np.ndarray:
            vec2 = np.array(vec2)
        return np.linalg.norm(vec1 - vec2)
    
    # This is the interference pattern calculation for non-local interference.
    # The output is a list, and the term is like '[position on screen, wavelength, intensity]'
    # Since no interference between different source, we give an output for
    # each source-screenPoint combination, we can get final pattern by simply adding their intensity.
    def nonlocalInterference(self):
        if not self.islocalInterference:
            image_list = self.get_imageSourceList()       # get imformation of image-source-pair
            screen = self.screen                          # get point list of screen
            pattern = []
            for point in screen:
                for coherentSource in image_list:         # calculate for each source-screenPoint combination
                    point1, point2, wavelength = coherentSource

                    # calculate interval between source and screen straightly, using them to derive phase difference
                    interval1 = self.get_interval(point1, point)
                    interval2 = self.get_interval(point2, point)
                    delta = 2 * math.pi * (interval1 - interval2) / wavelength  # derive phase differnce

                    intensity1 = 1/(interval1 ** 2)
                    intensity2 = 1/(interval2 ** 2)
                    intensity = intensity1 + intensity2 + \
                                2 * math.sqrt(intensity1 * intensity2) * math.cos(delta)
                    pattern.append([point, wavelength, intensity])              # forming one term, not interfere with others
            return pattern
        else:
            raise Exception('Mode is local interference now, please change mode')
    
    # This is the interference pattern calculation for local interference.
    # The output is a list, and the term is like '[position on screen, wavelength, intensity]'
    def localInterference(self):
        if self.islocalInterference:
            image_list = self.get_imageSourceList()       # get imformation of image-source-pair
            screen = self.screen                          # get point list of screen
            pattern = []
            for point in screen:
                for coherentSource in image_list:         # calculate for each source-screenPoint combination
                    point1, point2, wavelength = coherentSource
                    intervalVector = point1 - point2      # derive vector from one coherent image source to the other

                    # since specified screenPoint gives a pair of parallel light, 
                    # we follow screenPoint-lightDirection-phaseDifference calculation, 
                    # type(point) == np.ndarray, and the term denotes relative distance.
                    direction = np.array(point)
                    delta = 2 * math.pi * np.inner(intervalVector, direction) / np.linalg.norm(direction)

                    intensity = 2 + 2 * math.cos(delta)
                    pattern.append([point, wavelength, intensity])              # forming one term, not interfere with others
            return pattern
        else:
            raise Exception('Mode is nonlocal interference now, please change mode')