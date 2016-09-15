import fiber, utils

def lossy_propagation(thisFiber, i, theta):

    test_fiber = fiber.GHModes(thisFiber.w, XX, YY, theta =0.0)
    test_fiber1 = fiber.GHModes(thisFiber.w, XX, YY, theta = theta_vals[i],offset_x = offset_x[i], offset_y = offset_y[i])
    #print "M1"
    #print M1
    E = []
    for i in range(M):
        p, q = thisFiber.admissible_modes[i][0], thisFiber.admissible_modes[i][1]
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
            
         
