# Light curve attitude estimation using particle swarm optimizers

DOI: 10.1016/j.asr.2024.09.008
URL: https://www.sciencedirect.com/science/article/pii/S0273117724009281
Authors: Alexander Burton; Liam Robinson; Carolin Frueh


## Advances in Space Research


## Published by: Elsevier


### Published by


## Highlights

鈥?The attitude of space objects is estimated using only light curves with no initial state guess.


## Abstract


## Keywords

Previous article in this issue

Next article in this issue


## 1. Introduction


## 2. Analytic torque-free motion


### 2.1. Motivation and attitude representation


### 2.2. Short-Axis Mode (SAM) Expressions


### 2.3. Long-Axis Mode (LAM) Expressions


### 2.4. Initial Euler angles


## 3. Attitude inversion method

Download: Download high-res image (148KB)

Download: Download full-size image

Fig. 1. A flowchart giving an overview of the attitude inversion process (Burton et al., 2023).


### 3.1. Possible attitude non-social particle swarm optimizer


#### 3.1.1. Cost Function


#### 3.1.2. Initialization

Download: Download high-res image (325KB)

Download: Download full-size image

Fig. 2. A flowchart of the structure of the two PSOs used in the attitude inversion method.


#### 3.1.3. Iterations


#### 3.1.4. Motion in angle space


### 3.2. Full state particle swarm optimizer


#### 3.2.1. State and cost function


#### 3.2.2. Full State PSO particle creation


#### 3.2.3. Motion in the solution spaces


## 4. The flip problem


## 5. Results

Table 1. A summary of the setup for each test case.


Case Object Observers Light Curves Offset Measurements 1 Cylinder 1 1 鈥?25 2 Tetrahedron 1 1 鈥?25 3 Landsat 8 2 2 2.2 s 50


### 5.1. Particle swarm optimizer parameters

Table 2. The parameters used to run the possible attitude nsPSO for each test case.


Empty Cell Case 1 Case 2 Case 3 饾惤 thresh 10 - 3 10 - 3 10 - 3 Particles 17,576 17,576 314,432 Iterations 10 10 10 饾懀 max [rad] 0.05 0.05 0.05 饾憪 饾懀 [rad] 0.2 0.2 0.2

Table 3. The parameters used to run the full state PSO for each test case.


Empty Cell Case 1 Case 2 Case 3 Neighbors 12 12 12 Iterations 50 50 100 饾懁 饾憴 0.5 0.5 0.5 饾懁 饾憯 0 0 0 饾懀 max , 饾懃 [rad] 0.05 0.05 0.05 饾憪 饾懀 , 饾懃 [rad] 0.1 0.1 0.1 饾懀 max , 饾湐 [rad/s] 0.2 0.2 0.1 饾憪 饾懀 , 饾湐 [rad/s] 0.4 0.4 0.2 饾湐 space [rad/s] 0.35 0.45 0.45


### 5.2. Case 1: Spinning GEO cylinder with one observer

Download: Download high-res image (127KB)

Download: Download full-size image

Fig. 3. The cylinder model and measurements for the Case 1 object.

Download: Download high-res image (256KB)

Download: Download full-size image

Fig. 4. The cylinder鈥檚 true attitude and angular velocity time history.

Table 4. Errors in the Case 1 cylinder axis pointing direction and inertial frame angular momentum vector estimates.


Empty Cell Empty Cell Axis Estimate Error [deg] Empty Cell Angular Momentum Error Rank 饾惛 frac Initial Average Empty Cell Magnitude [%] Direction [deg] 1 2 . 426 路 10 - 5 129 . 291 91 . 272 - 4 . 861 路 10 - 3 180 - 0 . 5936 2 9.961 路 10 - 5 50.711 88.736 - 4.689 路 10 - 3 180 - 0.5819 3 1.126 路 10 - 4 13.381 9.823 1.296 路 10 - 4 13.191 4 1.870 路 10 - 4 131.333 94.000 - 5.154 路 10 - 3 166.568 5 2.455 路 10 - 4 166.618 170.236 1.420 路 10 - 4 13.058


### 5.3. Case 2: GEO uniformly-reflecting regular tetrahedron

Download: Download high-res image (104KB)

Download: Download full-size image

Fig. 5. The Case 2 observed object and measured light curve (Burton et al., 2024).

Download: Download high-res image (303KB)

Download: Download full-size image

Fig. 6. The tetrahedron鈥檚 true attitude and angular velocity time history.

Table 5. Errors in the Case 2 tetrahedron attitude and angular velocity estimates.


Empty Cell Empty Cell Initial Estimate Error Empty Cell Average Estimate Error Rank 饾惛 frac Attitude [deg] Ang. Vel. [rad/s] Empty Cell Attitude [deg] Ang. Vel. [rad/s] 1 1 . 225 路 10 - 6 1 . 005 路 10 - 4 2 . 071 路 10 - 6 7 . 841 路 10 - 5 1 . 340 路 10 - 6 鈰?8 1.665 路 10 - 5 157.250 2.831 116.388 2.803 鈰?24 8.233 路 10 - 4 180 - 0.02302 7.463 路 10 - 4 180 - 0.06394 3.839 路 10 - 4

Download: Download high-res image (176KB)

Download: Download full-size image

Fig. 7. The best estimated light curve and its normalized error at each measurement time for Case 2.


### 5.4. Case 3: Full satellite model

Download: Download high-res image (122KB)

Download: Download full-size image

Fig. 8. The Landsat 8 object model and two-observer light curve for Case 3 (Meaney, 2016, Burton et al., 2024).

Table 6. Errors in the Case 3 Landsat 8 attitude and angular velocity estimates.


Empty Cell Empty Cell Initial Estimate Error Empty Cell Average Estimate Error Rank 饾惛 frac Attitude [deg] Ang. Vel. [rad/s] Empty Cell Attitude [deg] Ang. Vel. [rad/s] 1 7 . 617 路 10 - 3 0 . 7852 0 . 01386 0 . 5905 7 . 139 路 10 - 3 2 0.01222 4.389 6.782 路 10 - 3 4.616 3.677 路 10 - 3 3 0.01558 4.449 5.125 路 10 - 3 4.486 3.075 路 10 - 3 4 0.02230 1.979 0.07731 2.322 0.03856 5 0.02676 9.178 4.774 路 10 - 3 9.565 7.117 路 10 - 3

Download: Download high-res image (201KB)

Download: Download full-size image

Fig. 9. The best estimated light curves and their normalized errors at each measurement time for Case 3.


## 6. Discussion of potential application to real data


## 7. Conclusions


## Declaration of Competing Interest


## Acknowledgments


## Appendix A. Attitude representation derivation


### A.1. 313 Sequence quaternion


### A.2. 131 Sequence quaternion


### A.3. Short-axis mode attitude representation


### A.4. Long-axis mode attitude representation


### A.5. Short-axis mode initial euler angles


### A.6. Long-axis mode initial angles


## References

Abramowitz and Stegun, 1948 Abramowitz, M., Stegun, I.A., 1948. Handbook of mathematical functions with formulas, graphs, and mathematical tables volume 55. US Government printing office. Google Scholar

Balster et al., 2023 Balster, P., Jones, G., Hofer, G. et al., 2023. Object characteristic determination using brightness measurements. In: Proceedings of the Advanced Maui Optical and Space Surveillance (AMOS) Technologies Conference (p. 72). Google Scholar

Benson et al., 2020 C.J. Benson, D.J. Scheeres, N.A. Moskovitz Spin state evolution of asteroid (367943) duende during its 2013 earth flyby Icarus, 340 (2020), p. 113518 View PDF View articleView in ScopusGoogle Scholar

Benson et al., 2018 Benson, C.J., Scheeres, D.J., Ryan, W.H. et al., 2018. Cyclic complex spin state evolution of defunct geo satellites. In: Proceedings of the Advanced Maui Optical and Space Surveillance Technologies Conference, Maui, HI. Google Scholar

Burton and Frueh, 2020 Burton, A., Frueh, C., 2020. Light curve attitude estimation using the viewing sphere. In: Astrodynamics Specialist Conference 2020. Google Scholar

Burton and Frueh, 2021 Burton, A., Frueh, C., 2021. Two methods for light curve inversion for space object attitude determination. In: 8th European Conference on Space Debris. Google Scholar

Burton and Frueh, 2023 Burton, A., Frueh, C., 2023. Fast light curve inversion for all - regular and tumbling - attitudes. In: Advanced Maui Optical and Space Surveillance Technologies Conference 2023. Google Scholar

Burton et al., 2023 Burton, A., Robinson, L., Frueh, C., 2023. Simultaneous attitude and shape estimation from scratch using light curves for human-made space objects. In: The Second International Orbital Debris Conference. Google Scholar

Burton et al., 2024 Burton, A., Robinson, L., Frueh, C., 2024. Attitude estimation using light curves: A particle swarm approach. In: AIAA SciTech 2024 Forum. Google Scholar

Burton, 2024 Burton, A., 2024. Attitude Estimation using Light Curves. Ph.D. thesis Purdue University. Google Scholar

Cabrera et al., 2023 D.V. Cabrera, J. Utzmann, R. F枚rstner The adaptive gaussian mixtures unscented kalman filter for attitude determination using light curves Adv. Space Res., 71 (6) (2023), pp. 2609-2628 Google Scholar

Carlson, 1963 Carlson, B.C. (1963). Normal elliptic integrals of the first and second kinds. University of North Texas Libraries, UNT Digital Library. URL: https://digital.library.unt.edu/ark:/67531/metadc1201580/ last accessed June 8, 2023. Google Scholar

Clark et al., 2020 Clark, R., Dave, S., Wawrow, J. et al., 2020. Performance of parameterization algorithms for resident space object (rso) attitude estimates. In: Proceedings of the Advanced Maui Optical and Space Surveillance Technologies, Maui, HI, USA, pp. 15鈥?8. Google Scholar

Clark et al., 2022 R. Clark, Y. Fu, S. Dave, et al. Resident space object (rso) attitude and optical property estimation from space-based light curves Adv. Space Res., 70 (11) (2022), pp. 3271-3280, 10.1016/j.asr.2022.08.068 URL: https://www.sciencedirect.com/science/article/pii/S0273117722008043 View PDF View articleView in ScopusGoogle Scholar

Dianetti, 2020 A.D. Dianetti Resident Space Object Characterization Using Polarized and Multispectral Light Curves State University of New York at Buffalo (2020) Ph.D. thesis Google Scholar

Dianetti and Crassidis, 2023 A.D. Dianetti, J.L. Crassidis Resident space object characterization using polarized light curves J. Guid., Control, Dynam., 46 (2) (2023), pp. 246-263 CrossrefView in ScopusGoogle Scholar

膸urech and Kaasalainen, 2003 J. 膸urech, M. Kaasalainen Photometric signatures of highly nonconvex and binary asteroids Astron. Astrophys., 404 (2) (2003), pp. 709-714, 10.1051/0004-6361:20030505 View in ScopusGoogle Scholar

Duvenhage et al., 2013 Duvenhage, B., Bouatouch, K., Kourie, D., 2013. Numerical verification of bidirectional reflectance distribution functions for physical plausibility. In: SAICSIT 鈥?3: Proceedings of the South African Institute for Computer Scientists and Information Technologists Conference (pp. 200鈥?08). doi:10.1145/2513456.2513499. Google Scholar

Eberhart and Kennedy, 1995 Eberhart, R., Kennedy, J., 1995. A new optimizer using particle swarm theory. In: MHS鈥?5. Proceedings of the sixth international symposium on micro machine and human science, pp. 39鈥?3. Ieee. Google Scholar

Falduto et al., 2015 Falduto, V., Lippman, D., Norwood, R. et al., 2015. Algebra and trigonometry. Google Scholar

Fan and Frueh, 2019 S. Fan, C. Frueh A direct light curve inversion scheme in the presence of measurement noise J. Astronaut. Sci., 67 (2019), 10.1007/s40295-019-00190-3 Google Scholar

Fr眉h and Jah, 2014 C. Fr眉h, M.K. Jah Coupled orbit attitude motion of high area-to-mass ratio (hamr) objects including efficient self-shadowing Acta Astronaut., 95 (2014), pp. 227-241, 10.1016/j.actaastro.2013.11.017 View PDF View articleView in ScopusGoogle Scholar

Fukushima, 2008 T. Fukushima Simple, regular, and efficient numerical integration of rotational motion Astron. J., 135 (6) (2008), p. 2298 CrossrefView in ScopusGoogle Scholar

Gagnon and Crassidis, 2022 Gagnon, S.R., Crassidis, J.L., 2022. Augmenting light curve based attitude estimation with geometric information. In: AIAA SCITECH 2022 Forum (p. 1767). Google Scholar

Hall et al., 2006 Hall, D., Africano, J., Archambeault, D. et al., 2006. Amos observations of nasa鈥檚 image satellite. In: The 2006 AMOS Technical Conference Proceedings (pp. 10鈥?4). Google Scholar

Hall et al., 2007 Hall, D., Calef, B., Knox, K. et al., 2007. Separating attitude and shape effects for non-resolved objects. In: The 2007 AMOS Technical Conference Proceedings (pp. 464鈥?75). Maui Economic Development Board, Inc. Kihei, Maui, HI. Google Scholar

Hapke, 2012 B. Hapke Theory of reflectance and emittance spectroscopy. chapter 10.3 Reciprocity Cambridge University Press (2012), pp. 264-265 Google Scholar

Kaasalainen et al., 1992 M. Kaasalainen, L. Lamberg, K. Lumme, et al. Interpretation of lightcurves of atmosphereless bodies. i-general theory and new inversion schemes Astron. Astrophys., 259 (1992), pp. 318-332 Google Scholar

Kaasalainen and Torppa, 2001a M. Kaasalainen, J. Torppa Optimization methods for asteroid lightcurve inversion: I. shape determination Icarus, 153 (1) (2001), pp. 24-36, 10.1006/icar.2001.6673 URL: https://www.sciencedirect.com/science/article/pii/S0019103501966734 View PDF View articleView in ScopusGoogle Scholar

Kaasalainen and Torppa, 2001b M. Kaasalainen, J. Torppa Optimization methods for asteroid lightcurve inversion: I. shape determination Icarus, 153 (1) (2001), pp. 24-36, 10.1006/icar.2001.6673 URL: https://www.sciencedirect.com/science/article/pii/S0019103501966734 View PDF View articleView in ScopusGoogle Scholar

Kaasalainen et al., 2001 M. Kaasalainen, J. Torppa, K. Muinonen Optimization methods for asteroid lightcurve inversion: Ii. the complete inverse problem Icarus, 153 (1) (2001), pp. 37-51, 10.1006/icar.2001.6674 URL: https://www.sciencedirect.com/science/article/pii/S0019103501966746 View PDF View articleView in ScopusGoogle Scholar

Kingma and Ba, 2017 Kingma, D., Ba, J., 2017. Adam: A method for stochastic optimization. arXiv preprint arXiv:1412.6980. URL: https://arxiv.org/abs/1412.6980 doi:https://doi.org/10.48550/arXiv.1412.6980. Google Scholar

Linares et al., 2014 R. Linares, J. Crassidis, M. Jah Particle filtering light curve based attitude estimation for non-resolved space objects Adv. Astronaut. Sci., 152 (2014), pp. 119-130 View in ScopusGoogle Scholar

Longuski and Frueh, 2019 J. Longuski, C. Frueh Aae 340 dynamics and vibrations Purdue University Lecture Notes (2019) Google Scholar

Markley and Crassidis, 2014 F.L. Markley, J.L. Crassidis Fundamentals of spacecraft attitude determination and control, volume 1286, Springer (2014) Google Scholar

Meaney, 2016 Meaney, C. (2016). Landsat 8 (ldcm). NASA 3D Resources. URL: https://nasa3d.arc.nasa.gov/detail/landsat-8 last accessed on 10/25/23. Google Scholar

Merlet, 2004 Merlet, J.-P., 2004. A note on the history of trigonometric functions and substitutions. Proceedings of HMM. Google Scholar

Minnaert, 1941 Minnaert, M., 1941. The reciprocity principle in lunar photometry. Astrophysical Journal, vol. 93, p. 403鈥?10 (1941)., 93, 403鈥?10. Google Scholar

Murakami, 2021 C. Murakami Analytical solution of the euler-poinsot problem J. Geometry Symmet. Phys., 60 (2021), pp. 25-46 CrossrefView in ScopusGoogle Scholar

Nijhawan and Dhar Choudhury, 1999 N. Nijhawan, S. Dhar Choudhury Training neural networks with multi-activations Int. J. Eng. Res. Technol. (IJERT), 10 (1999), pp. 434-438 Google Scholar

Pedregosa et al., 2011 F. Pedregosa, G. Varoquaux, A. Gramfort, et al. Scikit-learn: Machine learning in Python J. Mach. Learn. Res., 12 (2011), pp. 2825-2830 Google Scholar

Robinson and Frueh, 2022 Robinson, L., Frueh, C., 2022. Light curve inversion for reliable shape reconstruction of human-made space objects. In: Proceedings of the 32nd AIAA/AAS Astrodynamics Specialist Conference, pp. 1鈥?9. Google Scholar

Russell, 1906 H.N. Russell On the light-variations of asteroids and satellites Astrophys. J., 24 (1) (1906), pp. 1-18 Google Scholar

Samarasinha and A鈥橦earn, 1991 N.H. Samarasinha, M.F. A鈥橦earn Observational and dynamical constraints on the rotation of comet p/halley Icarus, 93 (2) (1991), pp. 194-225 View PDF View articleView in ScopusGoogle Scholar

Schildknecht et al., 2015 Schildknecht, T., Linder, E., Silha, J. et al., 2015. Photometric monitoring of non-resolved space debris and databases of optical light curves. In: Advanced Maui Optical and Space Surveillance Technologies Conference 25. Google Scholar

Thomson, 1986 W. Thomson Introduction to space dynamics Dover Publications Inc (1986) Google Scholar

Vince, 2021 Vince, J., 2021. Quaternion algebra. In Quaternions for Computer Graphics (pp. 77鈥?03). London: Springer, London. doi:10.1007/978-1-4471-7509-4_6. Google Scholar

Wetterer and Jah, 2009 C.J. Wetterer, M. Jah Attitude determination from light curves J. Guid., Control, Dynam., 32 (5) (2009), pp. 1648-1651 CrossrefView in ScopusGoogle Scholar

Williams, 1967 Williams, J., 1967. The determination of the orientation of a tumbling cylinder from the shape of the light curve. Office of Aerospace Research, (p. 31). Google Scholar

Wright, 2006 Wright, S.J., 2006. Numerical optimization. chapter Quasi-Newton Methods. (pp. 136鈥?43). Google Scholar

Zill and Carlson, 1970 D. Zill, B. Carlson Symmetric elliptic integrals of the third kind Math. Comput., 24 (109) (1970), pp. 199-214 View in ScopusGoogle Scholar


## Cited by (6)

Research article APSIS: Automated Photometric Survey of Inactive Satellites for rotational dynamics and lightcurve characterization Trelia M.M., 鈥? Birlan M. Acta Astronautica 鈥?Volume 242 鈥?2026 Show abstract

Research article Open access Attitude estimation of uncontrolled space objects: A Bayesian-informed swarm intelligence approach Rubio J., 鈥? Escobar D. Advances in Space Research 鈥?Volume 77 鈥?2026 Show abstract

Global Light Curve Attitude Estimation with Noisy Measurements and Inertia Uncertainty Robinson L., Fr眉h C.E. Journal of the Astronautical Sciences 鈥?Volume 73 鈥?2026 鈥?Article 7

Joint Estimation of Attitude and Optical Properties of Uncontrolled Space Objects from Light Curves Considering Atmospheric Effects Rubio J., 鈥? Escobar D. Aerospace 鈥?Volume 12 鈥?2025 鈥?Article 942

The locus of the angular velocity vector of a moving rigid body is a cylindrical surface Cervantes J.J., 鈥? Garc铆a-Garc铆a R. Mechanics Based Design of Structures and Machines 鈥?Volume 53 鈥?2025

Periodicity Detection in TESS Light Curves using Clustering and the Footprint Aquila Optimizer Perez-Ramirez C.E., 鈥? Hernitschek N. Proceedings International Conference of the Chilean Computer Science Society Sccc 鈥?2025


## Metrics


### Citations

Citation Indexes 6


### Captures

Mendeley Readers 11

