import numpy as np
import cv2
import pyvista as pv
import vtk
import shapely as sh
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

vrtx_qty = 343

scale = 491/192.1 # to px

""" image_path = 'C:\\Users\\gener\\OneDrive\\Documents\\Python\\images-to-stl\\images\\pa0st0st1-tragets\\'
cnt_array = []
approx_array = []
range_x1 = 0
range_x2 = 10
start_img = 21
slising_offset = 5.07*scale """
image_path = 'C:/Users/gener/OneDrive/Documents/Python/images-to-stl/images/pa0st0se2-targets/'
cnt_array = []
approx_array = []
range_x1 = 0
range_x2 = 37
start_img = 88
slising_offset = 1.259*scale
image_ids = range(range_x1 + start_img, range_x2 + start_img)

def plotPolygon(polygon, style):
    x = []
    y = []
    for v in polygon:
        x.append(v[0])
        y.append(v[1])
    plt.plot(x, y, style)

for im in image_ids:
    image = cv2.imread(image_path + 'IM' + str(im) + '.png')
    """ cv2.imshow('shapes', image)
    cv2.waitKey(0)  """
    b,g,r = cv2.split(image)
    #cv2.imshow("winname1", image)

    lower_green = np.array([0,100,0])
    upper_green = np.array([50,255,50])

    mask = cv2.inRange(image,lower_green,upper_green)
    mask_rgb = cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR)
    image = image & mask_rgb
    
    imgGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #cv2.imshow("winname", imgGray)
    _, thresh = cv2.threshold(imgGray, 100, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cnt = contours[0]
    approx = cv2.approxPolyDP(cnt, 0.000001*cv2.arcLength(cnt, True), True)
    cnt_array.append(cnt)
    #print(approx)
    approx_array.append(approx)
    #plotPolygon([a[0] for a in approx], 'r.')
    #plotPolygon([a[0] for a in approx], 'b-')
    #plt.axis([150, 400,150, 400])
    #plt.grid()
    #plt.show()


#cv2.waitKey(0)
#exit()
""" cv2.destroyAllWindows()
exit() """
def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def toStructoredArray(polygon):
    retval = []
    for v in polygon:
        retval.append([v[0][0], v[0][1]])
    return retval



def smoothPolygon(poly):
    length = len(poly)
    smoothed_raw = []
    for i in range(length-1):
        dx = poly[i][0] - poly[i+1][0]
        dy = poly[i][1] - poly[i+1][1]
        newx = poly[i][0] - dx/2
        newy = poly[i][1] - dy/2
        smoothed_raw.append([newx, newy])
    dx = poly[length-1][0] - poly[0][0]
    dy = poly[length-1][1] - poly[0][1]
    newx = poly[length-1][0] - dx/2
    newy = poly[length-1][1] - dy/2
    smoothed_raw.append([newx, newy])
    return smoothed_raw

def averageEdgeLength(poly):
    length = len(poly)
    total = 0
    for i in range(length-1):
        dx = poly[i][0] - poly[i+1][0]
        dy = poly[i][1] - poly[i+1][1]
        total += np.sqrt(dx*dx + dy*dy)
    dx = poly[length-1][0] - poly[0][0]
    dy = poly[length-1][1] - poly[0][1]
    total += np.sqrt(dx*dx + dy*dy)
    return total / length

def minimalEdgeLength(poly):
    length = len(poly)
    min_length = float('inf')
    for i in range(length-1):
        dx = poly[i][0] - poly[i+1][0]
        dy = poly[i][1] - poly[i+1][1]
        length = np.sqrt(dx*dx + dy*dy)
        if length < min_length:
            min_length = length
    """ dx = poly[length-1][0] - poly[0][0]
    dy = poly[length-1][1] - poly[0][1]
    length = np.sqrt(dx*dx + dy*dy)
    if length < min_length:
        min_length = length """
    return min_length

def maximumEdgeLength(poly):
    length = len(poly)
    max_length = 0
    ret_index = 0
    for i in range(length-1):
        dx = poly[i][0] - poly[i+1][0]
        dy = poly[i][1] - poly[i+1][1]
        length = np.sqrt(dx*dx + dy*dy)
        if length > max_length:
            max_length = length
            ret_index = i
    return (max_length, ret_index)



# add vertices to polygon while maximum edge length is less than average edge length
def addVerticesUntilAvg(poly):
    length = len(poly)
    avg = averageEdgeLength(poly)
    max_length, ret_index = maximumEdgeLength(poly)
    while max_length > avg:
        dx = poly[ret_index][0] - poly[ret_index+1][0]
        dy = poly[ret_index][1] - poly[ret_index+1][1]
        newx = poly[ret_index][0] - dx/2
        newy = poly[ret_index][1] - dy/2
        poly.insert(ret_index+1, [newx, newy])
        max_length, ret_index = maximumEdgeLength(poly)
    return poly

def addVerticesUntilNumber(poly, number):
    length = len(poly)
    while length < number:
        _, ret_index = maximumEdgeLength(poly)
        dx = poly[ret_index][0] - poly[ret_index+1][0]
        dy = poly[ret_index][1] - poly[ret_index+1][1]
        newx = poly[ret_index][0] - dx/2
        newy = poly[ret_index][1] - dy/2
        poly.insert(ret_index+1, [newx, newy])
        length += 1
    return poly

def listToArray(poly):
    length = len(poly)
    retval = []
    for i in range(length):
        retval.append([poly[i][0], poly[i][1]])
    return retval

def gaussFunction(x):
    sigma = np.sqrt(2)
    mu = 1
    return 1/(sigma*np.sqrt(2*np.pi))*np.exp(-(x-mu)**2/(2*sigma**2))

#for a in range(len(approx_array)):
bufferd_poly_array = []
raw_mlop = 0 # maximum length of polygon
mlop = 0
idx_of_mlop = 0
image_qnt = len(image_ids)
for a in range(image_qnt):
    raw = cnt_array[a]
    #exit()

    length = len(raw)
    structured_raw = toStructoredArray(raw)
    structured_approx = toStructoredArray(approx_array[a])

    smoothed_raw = []
    dx=0
    dy=0
    newx=0
    new=0


    smoothed_raw = smoothPolygon(structured_raw)
    smoothed_approx = smoothPolygon(structured_approx)
    structured_approx.append(structured_approx[0])
    polygon_obj = Polygon(smoothed_approx).buffer(30, resolution=13, join_style=1).buffer(-30, resolution=13, join_style=1)
    buffered_approx_list = list(polygon_obj.exterior.coords)
    buffered_approx_array = listToArray(buffered_approx_list)
    buffered_array_length = len(buffered_approx_array)
    
    if(buffered_array_length > raw_mlop):
        raw_mlop = buffered_array_length
        idx_of_mlop = a
    bufferd_poly_array.append(buffered_approx_array)

filled_approx_array = addVerticesUntilAvg(bufferd_poly_array[idx_of_mlop])  
mlop = len(filled_approx_array)
#print(mlop)
#print(idx_of_mlop)


filled_poly_array = []
for a in range(image_qnt):
    if(a == idx_of_mlop):
        filled_poly_array.append(filled_approx_array)
    else:
        filled_poly_array.append(addVerticesUntilNumber(bufferd_poly_array[a], mlop))
    #print(maximumEdgeLength(buffered_approx_array))
    #filled_approx_array = addVertices(buffered_approx_array)
    #print(buffered_approx[0], buffered_approx[-2])
    #exit()
    #plotPolygon(structured_raw, 'r')
    #print(len(filled_approx_array))
    #plotPolygon(filled_approx_array, 'r')
    #plotPolygon(filled_approx_array, 'ro')
    #plt.plot()
    #plotPolygon(smoothed_raw, 'g')
    #plotPolygon(structured_approx, 'b')
    #plotPolygon(structured_approx, 'bo')
    #plotPolygon(smoothed_approx, 'bo')
    #print(buffered_approx_array[a])
    #plotPolygon([bufferd_poly_array[a][0]], 'ro')

""" for a in range(image_qnt):
    plotPolygon(filled_poly_array[a], 'bo')
    plotPolygon(filled_poly_array[a], 'b')
    print(len(filled_poly_array[a]))


plt.axis([-160, 110,-160, 110])
plt.show()  """
#print(mlop)
#exit()


for a in range(image_qnt):
    del filled_poly_array[a][-1]
mlop-=1

offsets = np.zeros(image_qnt, dtype=int)






#surf = pv.PolyData(vertices, faces)
#print([[1, 2],[3, 4],[5, 6]])
#print(filled_poly_array[0])
#exit()

def centeroidnp(arr):
    length = len(arr)
    sum_x = np.sum([p[0] for p in arr])
    sum_y = np.sum([p[1] for p in arr])
    return [sum_x/length, sum_y/length]

def centeroidnp3d(arr):
    length = len(arr)
    sum_x = np.sum([p[0] for p in arr])
    sum_y = np.sum([p[1] for p in arr])
    sum_z = np.sum([p[2] for p in arr])
    return [sum_x/length, sum_y/length, sum_z/length]


def map(i, offset):
    ret_val = i + offset
    if(ret_val >= mlop):
        ret_val = ret_val - mlop
    if(ret_val < 0):
        ret_val = ret_val + mlop
    return ret_val
#print(mlop)

def lineFuinctionByTwo3dPoints(p1, p2):
    a = p1[1] - p2[1]
    b = p2[0] - p1[0]
    c = p1[0]*p2[1] - p2[0]*p1[1]
    return [a, b, c]

""" def getLinePointByLineAndZcoord(line, z):
    x = (z - line[2])/line[1]
    y = line[0]*x + line[2]
    return [x, y] """

def getLinePointByPointsAndZcoord(p1, p2, z):
    t = (z - p1[2])/(p2[2] - p1[2])
    x = p1[0] + t*(p2[0] - p1[0])
    y = p1[1] + t*(p2[1] - p1[1])
    return [x, y]

def angelBetweenTwoVectors(v1, v2):
    return np.arccos(np.dot(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)))

def angelOfLineByTwoPoints(p1, p2):
    v1 = [0, 0, 1]
    v2 = [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]]
    return angelBetweenTwoVectors(v1, v2)

focused_vertex = []
p = pv.Plotter()

#exit()


def create_mesh(offsets, test_val):  
    global mlop  
    global p

    vertices2d = structured_raw
    vertices = np.zeros((mlop*image_qnt+2, 3), np.double)
    faces_hstack = np.zeros((((mlop))*(image_qnt-1), 5), np.int32)

    for j in range(image_qnt):
        for i in range(mlop):
            vertices[i+(j*mlop)] = [filled_poly_array[j][i][0], filled_poly_array[j][i][1], j*slising_offset]

    
    main_line_p1 = centeroidnp3d(vertices[0:int(mlop*image_qnt/2)])
    main_line_p2 = centeroidnp3d(vertices[int(mlop*image_qnt/2):mlop*image_qnt])
    
    for j in range(image_qnt-1):
        errors = []
        local_main_line_p1 = centeroidnp3d(vertices[j*mlop:(j+1)*mlop])
        local_main_line_p2 = centeroidnp3d(vertices[(j+1)*mlop:(j+2)*mlop])
        for offset in range(-50,50):
            error = 0
            for i in range(0,mlop-1, 10):
                m_i_h = map(i, offset)
                m_i_l = i
                if i != mlop-1-offset and i != abs(offset)-1:
                    error += np.sqrt(angelOfLineByTwoPoints(main_line_p1, main_line_p2)**2+(angelOfLineByTwoPoints(main_line_p1, main_line_p2)*gaussFunction(j/(image_qnt-2)))**2) - angelOfLineByTwoPoints(vertices[m_i_h+j*mlop], vertices[m_i_l+(j+1)*mlop])
            errors.append(error)
        min_i = 0
        for i in range(len(errors)):
            if np.abs(errors[i]) < np.abs(errors[min_i]):
                min_i = i
        offsets[j] = min_i-50

    


    for j in range(image_qnt-1):
        for i in range(mlop-1):
        #print(offsets[0])
            m_i_h = map(i, offsets[j])
            m_i_l = i
            if i==mlop-1-offsets[j] and offsets[j] > 0:
                faces_hstack[i+(j*((mlop)))] = [4, 0+j*mlop, m_i_h+j*mlop, m_i_l+(j+1)*mlop, m_i_l+1+(j+1)*mlop]
            elif(i==abs(offsets[j])-1) and offsets[j] < 0:
                #faces_hstack[i+(j*((mlop)))] = [4, 1+j*mlop, m_i_h+j*mlop, m_i_l+(j+1)*mlop, m_i_l+1+(j+1)*mlop]
                faces_hstack[i+(j*((mlop)))] = [4, j*mlop, m_i_h+j*mlop, m_i_l+(j+1)*mlop, m_i_l+1+(j+1)*mlop]
            else:
                faces_hstack[i+(j*((mlop)))] = [4, m_i_h+1+j*mlop, m_i_h+j*mlop, m_i_l+(j+1)*mlop, m_i_l+1+(j+1)*mlop]
                #print(vertices[m_i_h+j*mlop])
                
                
        m_i_h = map(mlop-1, offsets[j])+test_val
        if offsets[j] == 0:
            faces_hstack[mlop-1+(j*((mlop)))] = [4, 0+j*mlop, mlop-1+j*mlop, mlop-1+(j+1)*mlop, 0+(j+1)*mlop]
        else:
            faces_hstack[mlop-1+(j*((mlop)))] = [4, m_i_h+1+j*mlop, m_i_h+j*mlop, mlop-1+(j+1)*mlop, 0+(j+1)*mlop]

    
    
    point1_idx = mlop*image_qnt
    point2_idx = mlop*image_qnt+1
    mid_2d_1 = centeroidnp(filled_poly_array[0])
    mid_2d_2 = centeroidnp(filled_poly_array[image_qnt-1])
    vertices[point1_idx] = [mid_2d_1[0], mid_2d_1[1], -slising_offset/2]
    vertices[point2_idx] = [mid_2d_2[0], mid_2d_2[1], (image_qnt-1)*slising_offset+slising_offset/2]
    
    
    j=0
    """ triangle_faces_hstack = np.zeros((((mlop+1))*2-1, 4), np.int32)
    for i in range(mlop-1):
        triangle_faces_hstack[i] = [3, i+1, i, point1_idx]
    triangle_faces_hstack[mlop-1] = [3, 0, mlop-1, point1_idx]
    
    for i in range(mlop, mlop*2-1):
        triangle_faces_hstack[i] = [3, i+1+(image_qnt-2)*mlop, i+(image_qnt-2)*mlop, point2_idx]
    triangle_faces_hstack[mlop*2-1] = [3, (image_qnt-2)*mlop, mlop*2-1+(image_qnt-2)*mlop, point2_idx] """


    bottom_cap = np.zeros((((mlop+1))-1, 4), np.int32)
    for i in range(mlop-1):
        bottom_cap[i] = [3, i+1, i, point1_idx]
    bottom_cap[mlop-1] = [3, 0, mlop-1, point1_idx]

    top_cap = np.zeros((((mlop+1))-1, 4), np.int32)
    for i in range(mlop-1):
        top_cap[i] = [3, i+1+(image_qnt-1)*mlop, i+(image_qnt-1)*mlop, point2_idx]
    top_cap[mlop-1] = [3, (image_qnt-1)*mlop, mlop-1+(image_qnt-1)*mlop, point2_idx]

    
    

    z1 = -slising_offset/2-20
    z2 = (image_qnt-1)*slising_offset+slising_offset/2+20
    main_line_point_1 = getLinePointByPointsAndZcoord(main_line_p1, main_line_p2, z1)
    main_line_point_2 = getLinePointByPointsAndZcoord(main_line_p1, main_line_p2, z2)

    #print(angelOfLineByTwoPoints(main_line_p1, main_line_p2))
    width = 5
    triangular_prism_vertices = [
        [main_line_point_1[0], main_line_point_1[1], z1],
        [main_line_point_1[0]+width, main_line_point_1[1]-width, z1],
        [main_line_point_1[0]+width, main_line_point_1[1]+width, z1],
        [main_line_point_2[0], main_line_point_2[1], z2],
        [main_line_point_2[0]+width, main_line_point_2[1]-width, z2],
        [main_line_point_2[0]+width, main_line_point_2[1]+width, z2],
    ]
    v_length = len(vertices)
    triangular_prism_faces = [
        [3, 0+v_length, 1+v_length, 2+v_length],
        [4, 0+v_length, 2+v_length, 5+v_length, 3+v_length],
        [4, 2+v_length, 1+v_length, 4+v_length, 5+v_length],
        [4, 1+v_length, 0+v_length, 3+v_length, 4+v_length],
        [3, 5+v_length, 4+v_length, 3+v_length],
    ]


    #print("error!!!!!!!!!")
    #print(faces_hstack[-2])

    """ for i in range(len(faces_hstack)):
    #print(v, [0,0,0])
        if not faces_hstack[i].any():
            print(i, faces_hstack[i])
    print(len(faces_hstack))
    for j in range(image_qnt):
        print(j, j*mlop)
    #exit() """
    
    faces = np.hstack(faces_hstack)
    faces = np.hstack([faces, np.hstack(bottom_cap), np.hstack(top_cap)])
    mesh = pv.PolyData(np.concatenate((vertices)), faces)

    """ faces = np.hstack([faces, np.hstack(bottom_cap), np.hstack(top_cap), np.hstack(triangular_prism_faces)])
    mesh = pv.PolyData(np.concatenate((vertices, triangular_prism_vertices)), faces) """

    """ faces = np.hstack([faces, np.hstack(triangular_prism_faces)])
    mesh = pv.PolyData(np.concatenate((vertices, triangular_prism_vertices)), faces) """



    """ faces = np.hstack([faces])
    mesh = pv.PolyData(vertices, faces) """

  


    return mesh

class MyCustomRoutine():
    def __init__(self, mesh):
        self.output = mesh # Expected PyVista mesh type
        # default parameters
        self.offsets = np.zeros(image_qnt, dtype=int)
        self.firest_time_call = np.zeros(image_qnt, dtype=int)
        self.test_val=0

    def __call__(self, param, value):
        if(self.firest_time_call[param] == 0):
            self.firest_time_call[param] = 1
            return
        self.offsets[param] = value
        self.update()
    
    def test(self, test_val):
        self.test_val = test_val
        self.update()

    def update(self):
        # This is where you call your simulation
        result = create_mesh(self.offsets, self.test_val)
        self.output.overwrite(result)
        return

#print(offsets)
starting_mesh = create_mesh(offsets, 0)
engine = MyCustomRoutine(starting_mesh)






""" p.add_slider_widget(
    callback=lambda value: engine(2, int(value)),
    rng=[-100, 100],
    value=0,
    title="2",
    pointa=(.35, .1), pointb=(.64, .1),
    style='modern',
) """



""" for j in range(range_x2-range_x1-1):
    k = int(j)
    h = j/(image_qnt-1)+0.05
    p.add_slider_widget(
        callback=lambda value, k=k: engine(k, int(value)),
        rng=[-100, 100],
        value=0,
        title=str(j),
        pointa=(.8, h), pointb=(1.005, h),
        style='modern',
    ) """

""" p.add_slider_widget(
    callback=lambda value: engine.test(int(value)),
    rng=[-10, 10],
    value=0,
    title="test",
    pointa=(.025, .1), pointb=(.31, .1),
    style='modern',
) """


    
# plot each face with a different color
#surf.save("C:\\Users\gener\OneDrive\Documents\Python\images-to-stl\OMG.vtp", True)
#surf.save("C:\\Users\gener\OneDrive\Documents\Python\images-to-stl\OMG.ply", True)
starting_mesh.save("C:\\Users\\gener\\OneDrive\\Documents\\Python\\images-to-stl\\models\\final.vtk", True)
mesh = pv.read("C:\\Users\\gener\\OneDrive\\Documents\\Python\\images-to-stl\\models\\final.vtk")
surf = mesh#.smooth(n_iter=250)
surf = mesh.smooth(n_iter=150)
surf.save("C:\\Users\\gener\\OneDrive\\Documents\\Python\\images-to-stl\\models\\pa0st0se2_raw.ply")
p.add_mesh(surf)
#cpos = mesh.plot()




surf.plot(show_edges=True)
#surf.plot()

#actor = 0
#
#def smooothRoutine(value):
#    global mesh
#    global actor
#    surf = mesh.smooth(n_iter=value)
#    if actor:
#        p.remove_actor(actor)
#    actor = p.add_mesh(surf, show_edges=True)
#
#p.add_slider_widget(
#    callback=lambda value: smooothRoutine(int(value)),
#    rng=[0, 1000],
#    value=200,
#    title="test",
#    pointa=(.025, .1), pointb=(.31, .1),
#    style='modern',
#) 


p.show()
