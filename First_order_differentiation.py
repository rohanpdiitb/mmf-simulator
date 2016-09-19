import fiber
import numpy
W=1.55e-6
c=3e8
f= c/W
def first_difference (omega,length,step_length,kappa1,theta1,diameter,n_section):
    test_fiber=fiber.LargeCoreMMF(length=length,step_length=step_length,a=diameter)
    M= len(test_fiber.get_admissible_modes())
    U_first_difference = numpy.zeros(shape=(2*M,2*M))
    for section in range(n_section):
        test_fiber=fiber.LargeCoreMMF(length=length,step_length=step_length,a= diameter)
        U, uiprop = test_fiber.calculate_matrix(L= c/(omega+f), kappa_vals = kappa1, theta_vals= theta1)
        U1, uiprop1 = test_fiber.calculate_matrix(L=c/(omega+f+1), kappa_vals= kappa1,theta_vals = theta1)
        uiprop_first = (uiprop-uiprop1 / 2 * numpy.pi)
        theta = theta1[section]
        Mi = test_fiber.generate_projection_matrix(theta)
        Ri = test_fiber.generate_rotation_matrix(theta)
        U_section = numpy.mat(Mi)*numpy.mat(Ri)*numpy.mat(uiprop)
        U_section_first= numpy.mat(Mi)*numpy.mat(Ri)*numpy.mat(uiprop_first)
        U_first_difference=numpy.mat(U_section)*numpy.mat(U_first_difference) + numpy.mat(U_section_first)*numpy.mat(U)
    #U = numpy.dot(U_section, U)
    return U,U_first_difference







