import fiber
import propagationmatrix
import numpy
length=1000.0
step_length=1.0
n_sections=int(length / step_length)
#print n_section
sigma_kappa = 3.0 
sigma_theta = .36
diameter= 10e-6
test_fiber=fiber.LargeCoreMMF(length=length,step_length=step_length,a=diameter, sigma_kappa = sigma_kappa, sigma_theta = sigma_theta)
Kappa_list = numpy.random.randn(n_sections)
kappa_vals = numpy.abs(test_fiber.sigma_kappa*Kappa_list)
theta_list = numpy.random.randn(n_sections)
theta_vals = test_fiber.sigma_theta*theta_list
L=1.55e-6
U01 = test_fiber.calculate_matrix(L, kappa_vals, theta_vals)
print U01
