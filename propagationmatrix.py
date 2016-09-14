import fiber
import utils
import numpy
import scipy
NA = 0.19
wavelength = 1.55e-6
k0 = 2*numpy.pi/wavelength
n0 = 1.443
Csk0 = 0.0878*pow(n0,3)
DELTA = 0.5*pow((NA/n0),2)
sqrt = numpy.sqrt
EXTENTS = 30e-6
STEP = .5e-6
length=1000.0
step_length=1.0
n_sections=int(length / step_length)
#print n_section
sigma_kappa = 3.0 
sigma_theta = .36
diameter= 10e-6
a= diameter/2
w = sqrt(sqrt(2)*a/(k0*n0*sqrt(DELTA)))
x=numpy.arange(-EXTENTS, EXTENTS, STEP)
y=numpy.arange(-EXTENTS, EXTENTS, STEP)
[XX, YY] = numpy.meshgrid(x,y)
offset_x = numpy.random.uniform(0,.4*w,5)
offset_y = numpy.random.uniform(0,.4*w,5)
#print mode_pattern_1
Max =int(numpy.floor((a/w)*(a/w)))
admissible_modes =[]
for p in range(Max+1):
    for q in range(Max+1):
        if (p+q)<=Max:
            admissible_modes.append([p,q])
admissible_modes= numpy.array(admissible_modes)
M= len(admissible_modes)
theta_list = numpy.random.randn(n_sections)
theta_vals = sigma_theta*theta_list
def lossy_propagation(i):
    test_fiber = fiber.GHModes(w, XX, YY, theta =0.0)
    test_fiber1 = fiber.GHModes(w,XX, YY, theta = theta_vals[i],offset_x = offset_x[i],offset_y = offset_y[i])
    #print "M1"
    #print M1
    E = []
    for i in range(M):
        p, q = admissible_modes[i][0], admissible_modes[i][1]
        for j in range(M):
            m,n = admissible_modes[j][0], admissible_modes[j][1]
            mode_pattern_1 = test_fiber.get_mode_pattern(p,q)
            mode_pattern_2 = test_fiber1.get_mode_pattern(m,n)
            overlap = utils.overlap(mode_pattern_1, mode_pattern_2)
            E.append(overlap)
    #print "E"
    #print E
    A = numpy.array(E)
    O=numpy.sqrt(len(A))
    A1=A.reshape(O,O)
    A1= numpy.mat(A1)
    psi_matrix = numpy.kron(numpy.eye(2), A1)
    #psi_matrix1 = numpy.dot(psi_matrix,psi_matrix.H)
    return psi_matrix
#print M
#print lossy_propagation(1)              
            
         
