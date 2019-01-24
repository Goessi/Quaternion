# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 22:42:44 2019

@author: JingQIN
"""

import math
import random
import numpy as np
from Quaternion import Quaternion
import timeit
import decimal as d

def computeDCM(theta, vectors):
    '''
    compute standard DCM, a list of lists, 3*3 matrix
    
    arguments:
        theta: rotation angle, radians
        vectors: coordinates of f, [f1, f2 ,f3]        
    '''
    DCM = [[0] * 3 for i in range(3)]
    f1 = vectors[0]
    f2 = vectors[1]
    f3 = vectors[2]
    cosTheta = d.Decimal(math.cos(theta))
    sinTheta = d.Decimal(math.sin(theta))
    oneCosT = 1 - cosTheta
    DCM[0][0] = cosTheta + pow(f1, 2) * oneCosT
    DCM[0][1] = f1 * f2 * oneCosT + f3 * sinTheta
    DCM[0][2] = f1 * f3 * oneCosT - f2 * sinTheta
    DCM[1][0] = f1 * f2 * oneCosT - f3 * sinTheta
    DCM[1][1] = cosTheta + pow(f2, 2) * oneCosT
    DCM[1][2] = f2 * f3 * oneCosT + f1 * sinTheta
    DCM[2][0] = f1 * f3 * oneCosT + f2 * sinTheta
    DCM[2][1] = f2 * f3 * oneCosT - f1 * sinTheta
    DCM[2][2] = cosTheta + pow(f3, 2) * oneCosT

    return np.array(DCM)

def DCMtoQuaternion(aListOfLists):
    '''
    transfer from DCM to Quaternion, DCM is a list of lists
    
    argument:
        aListOfLists: a DCM    
    '''
    q0s = d.Decimal(0.5 * math.sqrt(aListOfLists[0][0] + aListOfLists[1][1] + aListOfLists[2][2] + 1))
    q0x = d.Decimal(0.5 * math.sqrt(aListOfLists[0][0] - aListOfLists[1][1] - aListOfLists[2][2] + 1))
    q0y = d.Decimal(0.5 * math.sqrt(-aListOfLists[0][0] + aListOfLists[1][1] - aListOfLists[2][2] + 1))
    q0z = d.Decimal(0.5 * math.sqrt(-aListOfLists[0][0] - aListOfLists[1][1] + aListOfLists[2][2] + 1))
    max_q = max([q0s, q0x, q0y, q0z])
    
    if max_q == q0s:
        qx = d.Decimal(aListOfLists[1][2] - aListOfLists[2][1]) / (4 * q0s) 
        qy = d.Decimal(aListOfLists[2][0] - aListOfLists[0][2]) / (4 * q0s)
        qz = d.Decimal(aListOfLists[0][1] - aListOfLists[1][0]) / (4 * q0s)
        return Quaternion(q0s, qx, qy, qz)
    elif max_q == q0x:
        qs = d.Decimal(aListOfLists[1][2] - aListOfLists[2][1]) / (4 * q0x)
        qy = d.Decimal(aListOfLists[0][1] + aListOfLists[1][0]) / (4 * q0x)
        qz = d.Decimal(aListOfLists[2][0] + aListOfLists[0][2]) / (4 * q0x)
        return Quaternion(qs, q0x, qy, qz)
    elif max_q == q0y:
        qs = d.Decimal(aListOfLists[2][0] - aListOfLists[0][2]) / (4 * q0y)
        qx = d.Decimal(aListOfLists[0][1] + aListOfLists[1][0]) / (4 * q0y)
        qz = d.Decimal(aListOfLists[1][2] + aListOfLists[2][1]) / (4 * q0y)
        return Quaternion(qs, qx, q0y, qz)
    elif max_q == q0z:
        qs = d.Decimal(aListOfLists[0][1] - aListOfLists[1][0]) / (4 * q0z)
        qx = d.Decimal(aListOfLists[2][0] + aListOfLists[0][2]) / (4 * q0z)
        qy = d.Decimal(aListOfLists[1][2] + aListOfLists[2][1]) / (4 * q0z)
        return Quaternion(qs, qx, qy, q0z)

def Quaternion_rotation_precision(N, R, x_theta, y_theta, z_theta):
    '''
    calculate precision for Quaternion rotation
    
    arguments:
        N: how many steps for each round, steps is N in loop
        R: how many rounds you want to compute
        x_theta: total rotation angle around x-axis, radian
        y_theta: total rotation angle around y-axis, radian
        z_theta: total rotation angle around z-axis, radian
    
    '''
    X1 = []
    X2 = []
    MEANDIFF = []
    MINDIFF = []
    MAXDIFF = []
    TIME = []
    
    for n in range (1,N):
        meandiff = 0.0
        maxdiff = 0.0
        mindiff = 1e9
        time = 0
        for r in range(0,R):
            x = d.Decimal(random.random())
            y = d.Decimal(random.random())
            z = d.Decimal(random.random())
            p = Quaternion(d.Decimal(0.0), x, y, z)
            p_zero = Quaternion(d.Decimal(0.0), x, y, z)
            steps = n
            aTime = timeit.default_timer()
            for i in range(0, steps):
                p = p.rotator(x_theta / steps, [1.0, 0.0, 0.0])
            for j in range(0, steps):
                p = p.rotator(y_theta / steps, [0.0, 1.0, 0.0])
            for k in range(0, steps):
                p = p.rotator(z_theta / steps, [0.0, 0.0, 1.0])  
            bTime = timeit.default_timer()
            time += (bTime - aTime) / (3 * n)
            diff = (p_zero - p).norm()
            meandiff += diff
            mindiff = min(mindiff, diff)
            maxdiff = max(maxdiff, diff)        
        TIME.append(time / R)
        X1.append(1.0 / n)
        X2.append(n)
        MEANDIFF.append(meandiff / R)
        MINDIFF.append(mindiff)
        MAXDIFF.append(maxdiff)
    return X1, X2, MEANDIFF, MINDIFF, MAXDIFF, TIME


def DCM_rotation_precision(N, R, x_theta, y_theta, z_theta):
    '''
    calculate precision for DCM rotation
    
    arguments:
        N: how many steps for each round, steps is N in loop
        R: how many rounds you want to compute
        x_theta: total rotation angle around x-axis, radian
        y_theta: total rotation angle around y-axis, radian
        z_theta: total rotation angle around z-axis, radian
    
    '''
    X1 = []
    X2 = []
    MEANDIFF = []
    MINDIFF = []
    MAXDIFF = []
    TIME = []
    
    for n in range (1,N):
        meandiff = 0.0
        maxdiff = 0.0
        mindiff = 1e9
        time = 0
        for r in range(0, R):
            x = d.Decimal(random.random())
            y = d.Decimal(random.random())
            z = d.Decimal(random.random())
            v = [x, y, z]
            v_zero = [x, y, z]
            steps = n
            m1 = computeDCM(d.Decimal(x_theta / steps), [d.Decimal(1), d.Decimal(0), d.Decimal(0)])
            m2 = computeDCM(d.Decimal(y_theta / steps), [d.Decimal(0), d.Decimal(1), d.Decimal(0)])
            m3 = computeDCM(d.Decimal(z_theta / steps), [d.Decimal(0), d.Decimal(0), d.Decimal(1)])
            aTime = timeit.default_timer()
            for i in range(0, steps):
                v = np.dot(m1, v)
            for j in range(0, steps):
                v = np.dot(m2, v)
            for k in range(0, steps):
                v = np.dot(m3, v)   
            bTime = timeit.default_timer()
            time += (bTime - aTime) / (3 * n)
            diff = math.sqrt(pow(v[0] - v_zero[0], 2) + pow(v[1] - v_zero[1], 2) + pow(v[2] - v_zero[2], 2))
            meandiff += diff
            mindiff = min(mindiff, diff)
            maxdiff = max(maxdiff, diff)        
        TIME.append(time / R)
        X1.append(1.0 / n)
        X2.append(n)
        MEANDIFF.append(meandiff / R)
        MINDIFF.append(mindiff)
        MAXDIFF.append(maxdiff)
    return X1, X2, MEANDIFF, MINDIFF, MAXDIFF, TIME

def Quaternion_DCM_rotation_precision(N, R, x_theta, y_theta, z_theta):
    '''
    calculate precision for Quaternion and DCM rotation, using same initial vector
    
    arguments:
        N: how many steps for each round, steps is N in loop
        R: how many rounds you want to compute
        x_theta: double total rotation angle around x-axis, radian
        y_theta: double total rotation angle around y-axis, radian
        z_theta: double total rotation angle around z-axis, radian
    
    '''
    X1 = []
    X2 = []
    MEANDIFF_Q = []
    MINDIFF_Q = []
    MAXDIFF_Q = []
    MEANDIFF_DCM = []
    MINDIFF_DCM = []
    MAXDIFF_DCM = []
    
    for n in range (1,N):
        meandiff_Q = 0.0
        maxdiff_Q = 0.0
        mindiff_Q = 1e9
        meandiff_DCM = 0.0
        maxdiff_DCM = 0.0
        mindiff_DCM = 1e9
        for r in range(0,R):
            x = d.Decimal(random.random())
            y = d.Decimal(random.random())
            z = d.Decimal(random.random())
            p = Quaternion(d.Decimal(0.0), x, y, z)
            p_zero = Quaternion(d.Decimal(0.0), x, y, z)
            v = [x, y, z]
            v_zero = [x, y, z]
            steps = n
            m1 = computeDCM(d.Decimal(x_theta / steps), [d.Decimal(1), d.Decimal(0), d.Decimal(0)])
            m2 = computeDCM(d.Decimal(y_theta / steps), [d.Decimal(0), d.Decimal(1), d.Decimal(0)])
            m3 = computeDCM(d.Decimal(z_theta / steps), [d.Decimal(0), d.Decimal(0), d.Decimal(1)])       
            for i in range(0, steps):
                p = p.rotator(x_theta / steps, [1.0, 0.0, 0.0])
                v = np.dot(m1, v)
            for i in range(0, steps):
                p = p.rotator(y_theta / steps, [0.0, 1.0, 0.0])
                v = np.dot(m2, v)
            for i in range(0, steps):
                p = p.rotator(z_theta / steps, [0.0, 0.0, 1.0])
                v = np.dot(m3, v)               
            x_Q = (p_zero - p).norm()
            meandiff_Q += x_Q
            mindiff_Q = min(mindiff_Q, x_Q)
            maxdiff_Q = max(maxdiff_Q, x_Q)
            x_DCM = math.sqrt(pow(v[0] - v_zero[0], 2) + pow(v[1] - v_zero[1], 2) + pow(v[2] - v_zero[2], 2))
            meandiff_DCM += x_DCM
            mindiff_DCM = min(mindiff_DCM, x_DCM)
            maxdiff_DCM = max(maxdiff_DCM, x_DCM)
        X1.append(1.0 / n)
        X2.append(n)
        MEANDIFF_Q.append(meandiff_Q / R)
        MINDIFF_Q.append(mindiff_Q)
        MAXDIFF_Q.append(maxdiff_Q)
        MEANDIFF_DCM.append(meandiff_DCM / R)
        MINDIFF_DCM.append(mindiff_DCM)
        MAXDIFF_DCM.append(maxdiff_DCM)
    return X1, X2, MEANDIFF_Q, MINDIFF_Q, MAXDIFF_Q, MEANDIFF_DCM, MINDIFF_Q, MAXDIFF_Q

def DCM_diagonal_check(aDCM):
    '''
    calculate differences  between aDCM disgonal and ones, mean of euclidean distance 
    '''
    diff = (math.sqrt(pow(aDCM[0][0] - 1, 2) + pow(aDCM[1][1] - 1, 2) + pow(aDCM[2][2] - 1, 2))) / 3
    return diff

def DCM_off_diagonal_check(aDCM):
    '''
    calculate differences between aDCM off-diagonal and zeros
    '''
    diff = math.sqrt(pow(aDCM[0][1], 2) + pow(aDCM[0][2], 2) + pow(aDCM[1][0], 2) + pow(aDCM[1][2], 2) + pow(aDCM[2][0], 2) + pow(aDCM[2][1], 2)) / 6
    return diff

def DCM_orthonormality_check(aDCM, direction):
    '''
    calculate differences between columns dot products or rows dot products
    
    arguments:
        aDCM: a 3*3 rotation matrix
        direction: define if columns or rows in calculation, 0 is columns product, 1 is rows product'
    '''
    if direction == 0:
        dot_product01 = [aDCM[0][0] * aDCM[0][1], aDCM[1][0] * aDCM[1][1], aDCM[2][0] * aDCM[2][1]]
        dot_product12 = [aDCM[0][1] * aDCM[0][2], aDCM[1][1] * aDCM[1][2], aDCM[2][1] * aDCM[2][2]]
        dot_product02 = [aDCM[0][0] * aDCM[0][2], aDCM[1][0] * aDCM[1][2], aDCM[2][0] * aDCM[2][2]]
    if direction == 1:
        dot_product01 = [aDCM[0][0] * aDCM[1][0], aDCM[0][1] * aDCM[1][1], aDCM[0][2] * aDCM[1][2]]
        dot_product12 = [aDCM[1][0] * aDCM[2][0], aDCM[1][1] * aDCM[2][1], aDCM[1][2] * aDCM[2][2]]
        dot_product02 = [aDCM[0][0] * aDCM[2][0], aDCM[0][1] * aDCM[2][1], aDCM[0][2] * aDCM[2][2]]
    
    L = math.sqrt(pow(dot_product01[0], 2) + pow(dot_product01[1], 2) + pow(dot_product01[2], 2)) + math.sqrt(pow(dot_product12[0], 2) + pow(dot_product12[1], 2) + pow(dot_product12[2], 2)) + math.sqrt(pow(dot_product02[0], 2) + pow(dot_product02[1], 2) + pow(dot_product02[2], 2))
    return L

def DCM_Quaternion_rotator_check(N, R, x_theta, y_theta, z_theta):
    '''
    calculate how many differences from rotation operator after rotation
    
    arguments:
        N: how many steps for each round, steps is N in loop
        R: how many rounds you want to compute
        x_theta: total rotation angle around x-axis, radian
        y_theta: total rotation angle around y-axis, radian
        z_theta: total rotation angle around z-axis, radian    
    '''
    X1 = []
    X2 = []
    DIAGONAL_CHECK_Q = []
    OFF_DIAGONAL_CHECK_Q = []
    ORTHONORMALITY_COL_Q = []
    ORTHONORMALITY_ROW_Q = []
    DIAGONAL_CHECK_DCM = []
    OFF_DIAGONAL_CHECK_DCM = []
    ORTHONORMALITY_COL_DCM = []
    ORTHONORMALITY_ROW_DCM = []
    
    for n in range (1,N):
        diagonal_check_q = 0
        off_diagonal_check_q = 0
        orthonormality_col_q = 0
        orthonormality_row_q = 0
        diagonal_check_dcm = 0
        off_diagonal_check_dcm = 0
        orthonormality_col_dcm = 0
        orthonormality_row_dcm = 0
        for r in range(0,R):
            x = random.random()
            y = random.random()
            z = random.random()
            
            m1 = computeDCM(d.Decimal(x), [d.Decimal(1), d.Decimal(0), d.Decimal(0)])
            m2 = computeDCM(d.Decimal(y), [d.Decimal(0), d.Decimal(1), d.Decimal(0)])
            m3 = computeDCM(d.Decimal(z), [d.Decimal(0), d.Decimal(0), d.Decimal(1)])
            
            DCM = m3 @ m2 @ m1
            Q = DCMtoQuaternion(DCM)
            steps = n
            m1 = computeDCM(d.Decimal(x_theta / steps), [d.Decimal(1), d.Decimal(0), d.Decimal(0)])
            m2 = computeDCM(d.Decimal(y_theta / steps), [d.Decimal(0), d.Decimal(1), d.Decimal(0)])
            m3 = computeDCM(d.Decimal(z_theta / steps), [d.Decimal(0), d.Decimal(0), d.Decimal(1)])
            q1 = Quaternion(d.Decimal(math.cos(x_theta / (2 * steps))), d.Decimal(math.sin(x_theta / (2 * steps))), d.Decimal(0), d.Decimal(0)).norm_q()
            q2 = Quaternion(d.Decimal(math.cos(x_theta / (2 * steps))), d.Decimal(0), d.Decimal(math.sin(x_theta / (2 * steps))), d.Decimal(0)).norm_q()
            q3 = Quaternion(d.Decimal(math.cos(x_theta / (2 * steps))), d.Decimal(0), d.Decimal(0), d.Decimal(math.sin(x_theta / (2 * steps)))).norm_q()
            for i in range(0, steps):
                DCM = m1 @ DCM
                Q = (q1 * Q).norm_q()
            for j in range(0, steps):
                DCM = m2 @ DCM
                Q = (q2 * Q).norm_q()
            for k in range(0, steps):
                DCM = m3 @ DCM
                Q = (q3 * Q).norm_q()
            Q = Q.toDCM()
            diagonal_check_q += DCM_diagonal_check(Q)
            off_diagonal_check_q += DCM_off_diagonal_check(Q)
            orthonormality_col_q += DCM_orthonormality_check(Q, 0)
            orthonormality_row_q += DCM_orthonormality_check(Q, 1)
            diagonal_check_dcm += DCM_diagonal_check(DCM)
            off_diagonal_check_dcm += DCM_off_diagonal_check(DCM)
            orthonormality_col_dcm += DCM_orthonormality_check(DCM, 0)
            orthonormality_row_dcm += DCM_orthonormality_check(DCM, 1)
        X1.append(1.0 / n)
        X2.append(n)
        DIAGONAL_CHECK_Q.append(diagonal_check_q / R)
        OFF_DIAGONAL_CHECK_Q.append(off_diagonal_check_q / R)
        ORTHONORMALITY_COL_Q.append(orthonormality_col_q / R)
        ORTHONORMALITY_ROW_Q.append(orthonormality_row_q / R)
        DIAGONAL_CHECK_DCM.append(diagonal_check_dcm / R)
        OFF_DIAGONAL_CHECK_DCM.append(off_diagonal_check_dcm / R)
        ORTHONORMALITY_COL_DCM.append(orthonormality_col_dcm / R)
        ORTHONORMALITY_ROW_DCM.append(orthonormality_row_dcm / R)
    return X1, X2, DIAGONAL_CHECK_Q, OFF_DIAGONAL_CHECK_Q, ORTHONORMALITY_COL_Q, ORTHONORMALITY_ROW_Q, \
           DIAGONAL_CHECK_DCM, OFF_DIAGONAL_CHECK_DCM, ORTHONORMALITY_COL_DCM, ORTHONORMALITY_ROW_DCM

def DCM_check (aDCM,bDCM): 
    '''
    calculate differences between each elements in 2 DCMs, mean of Manhattan Distance
    '''
    diff = abs(aDCM[0][0] - bDCM[0][0]) + abs(aDCM[0][1] - bDCM[0][1]) + abs(aDCM[0][2] - bDCM[0][2]) + \
    abs(aDCM[1][0] - bDCM[1][0]) + abs(aDCM[1][1] - bDCM[1][1]) + abs(aDCM[1][2] - bDCM[1][2]) + \
    abs(aDCM[2][0] - bDCM[2][0]) + abs(aDCM[2][1] - bDCM[2][1]) + abs(aDCM[2][2] - bDCM[2][2])
    return diff / 9.0

def DCM_Quaternion_rotator_check2(N, R, x_theta, y_theta, z_theta):
    '''
    calculate how many differences from rotation operator after rotation
    
    arguments:
        N: how many steps for each round, steps is N in loop
        R: how many rounds you want to compute
        x_theta: total rotation angle around x-axis, radian
        y_theta: total rotation angle around y-axis, radian
        z_theta: total rotation angle around z-axis, radian    
    '''
    X1 = []
    X2 = []
    DIFF_CHECK_Q = []
    DIFF_CHECK_DCM = []

    
    for n in range (1, N):
        diff_chk_q = 0
        diff_chk_dcm = 0

        for r in range(0, R):
            x = random.random()
            y = random.random()
            z = random.random()

            m1 = computeDCM(d.Decimal(x), [d.Decimal(1), d.Decimal(0), d.Decimal(0)])
            m2 = computeDCM(d.Decimal(y), [d.Decimal(0), d.Decimal(1), d.Decimal(0)])
            m3 = computeDCM(d.Decimal(z), [d.Decimal(0), d.Decimal(0), d.Decimal(1)])
            
            DCM = m3 @ m2 @ m1
            DCM_zero = DCM
            Q = DCMtoQuaternion(DCM)
            steps = n
            m1 = computeDCM(d.Decimal(x_theta / steps), [d.Decimal(1), d.Decimal(0), d.Decimal(0)])
            m2 = computeDCM(d.Decimal(y_theta / steps), [d.Decimal(0), d.Decimal(1), d.Decimal(0)])
            m3 = computeDCM(d.Decimal(z_theta / steps), [d.Decimal(0), d.Decimal(0), d.Decimal(1)])
            m4 = computeDCM(d.Decimal(-y_theta / steps), [d.Decimal(0), d.Decimal(1), d.Decimal(0)])
            q1 = Quaternion(d.Decimal(math.cos(x_theta / (2 * steps))), d.Decimal(math.sin(x_theta / (2 * steps))), d.Decimal(0), d.Decimal(0)).norm_q()
            q2 = Quaternion(d.Decimal(math.cos(y_theta / (2 * steps))), d.Decimal(0), d.Decimal(math.sin(y_theta / (2 * steps))), d.Decimal(0)).norm_q()
            q3 = Quaternion(d.Decimal(math.cos(z_theta / (2 * steps))), d.Decimal(0), d.Decimal(0), d.Decimal(math.sin(z_theta / (2 * steps)))).norm_q()
            q4 = Quaternion(d.Decimal(math.cos(-y_theta / (2 * steps))), d.Decimal(0), d.Decimal(math.sin(-y_theta / (2 * steps))), d.Decimal(0)).norm_q()
            for i in range(0, steps):
                DCM = DCM @ m1
                Q = (q1 * Q).norm_q()
            for j in range(0, steps):
                DCM = DCM @ m2
                Q = (q2 * Q).norm_q()
            for k in range(0, steps):
                DCM = DCM @ m3
                Q = (q3 * Q).norm_q()
            for k in range(0, steps):
                DCM = DCM @ m4
                Q = (q4 * Q).norm_q()
            Q = Q.toDCM();
            diff_chk_q += DCM_check(Q, DCM_zero)
            diff_chk_dcm += DCM_check(DCM, DCM_zero)
        X1.append(1.0 / n)
        X2.append(n)
        DIFF_CHECK_Q.append(diff_chk_q / R)
        DIFF_CHECK_DCM.append(diff_chk_dcm / R)
        
    return X1, X2, DIFF_CHECK_Q, DIFF_CHECK_DCM

def extracAngleQuaternion(aQuaternion, x, y, z):
    '''
    extract angles from a Quaternion and calculate angle differences 
    
    arguments:
        aQuaternion: a Quaternion
        x: original theta
        y: original beta
        z: original phi
    '''
    q0 = aQuaternion.a
    q1 = aQuaternion.b
    q2 = aQuaternion.c
    q3 = aQuaternion.d
    
    alpha = math.atan2(2 * (q0 * q1 + q2 * q3), 1 - 2 * (pow(q1, 2) + pow(q2, 2)))
    theta = math.asin(2 * (q0 * q2 - q3 * q1))
    phi = math.atan2(2 * (q0 * q3 + q2 * q1), 1 - 2 * (pow(q2, 2) + pow(q3, 2)))
    diff = abs((alpha - x) + (theta - y) + (phi - z)) / 3
    return diff

def extracAngleDCM(aDCM, x, y, z):
    '''
    extract angles from a DCM and calculate angle differences 
    
    arguments:
        aQuaternion: a Quaternion
        x: original theta
        y: original beta
        z: original phi
    '''
    alpha = math.atan2(aDCM[1][2], aDCM[2][2])
    beta = math.asin(-aDCM[0][2])
    phi = math.atan2(aDCM[0][1], aDCM[0][0])
    diff = abs((x - alpha) + (y - beta) + (z - phi)) / 3
    return diff

def DCM_Quaternion_rotator_check3(N, R, x_theta, y_theta, z_theta):
    '''
    calculate how many differences in angles from rotation operator after rotation, radians
    
    arguments:
        N: how many steps for each round, steps is N in loop
        R: how many rounds you want to compute
        x_theta: total rotation angle around x-axis, radian
        y_theta: total rotation angle around y-axis, radian
        z_theta: total rotation angle around z-axis, radian    
    '''
    X1 = []
    X2 = []
    DIFF_CHECK_Q = []
    DIFF_CHECK_DCM = []

    
    for n in range (1, N):
        diff_chk_q = 0
        diff_chk_dcm = 0

        for r in range(0, R):
            x = random.random()
            y = random.random()
            z = random.random()

            m1 = computeDCM(d.Decimal(x), [d.Decimal(1), d.Decimal(0), d.Decimal(0)])
            m2 = computeDCM(d.Decimal(y), [d.Decimal(0), d.Decimal(1), d.Decimal(0)])
            m3 = computeDCM(d.Decimal(z), [d.Decimal(0), d.Decimal(0), d.Decimal(1)])
            
            DCM = m3 @ m2 @ m1
            Q = DCMtoQuaternion(DCM)
            steps = n
            m1 = computeDCM(d.Decimal(x_theta / steps), [d.Decimal(1), d.Decimal(0), d.Decimal(0)])
            m2 = computeDCM(d.Decimal(y_theta / steps), [d.Decimal(0), d.Decimal(1), d.Decimal(0)])
            m3 = computeDCM(d.Decimal(z_theta / steps), [d.Decimal(0), d.Decimal(0), d.Decimal(1)])
            m4 = computeDCM(d.Decimal(-y_theta / steps), [d.Decimal(0), d.Decimal(1), d.Decimal(0)])
            q1 = Quaternion(d.Decimal(math.cos(x_theta / (2 * steps))), d.Decimal(math.sin(x_theta / (2 * steps))), d.Decimal(0), d.Decimal(0)).norm_q()
            q2 = Quaternion(d.Decimal(math.cos(y_theta / (2 * steps))), d.Decimal(0), d.Decimal(math.sin(y_theta / (2 * steps))), d.Decimal(0)).norm_q()
            q3 = Quaternion(d.Decimal(math.cos(z_theta / (2 * steps))), d.Decimal(0), d.Decimal(0), d.Decimal(math.sin(z_theta / (2 * steps)))).norm_q()
            q4 = Quaternion(d.Decimal(math.cos(-y_theta / (2 * steps))), d.Decimal(0), d.Decimal(math.sin(-y_theta / (2 * steps))), d.Decimal(0)).norm_q()
            for i in range(0, steps):
                DCM = DCM @ m1
                Q = (q1 * Q).norm_q()
            for j in range(0, steps):
                DCM = DCM @ m2
                Q = (q2 * Q).norm_q()
            for k in range(0, steps):
                DCM = DCM @ m3
                Q = (q3 * Q).norm_q()
            for q in range(0, steps):
                DCM = DCM @ m4
                Q = (q4 * Q).norm_q()
            diff_chk_q += extracAngleQuaternion(Q, x, y, z)
            diff_chk_dcm += extracAngleDCM(DCM, x, y, z)
        X1.append(1.0 / n)
        X2.append(n)
        DIFF_CHECK_Q.append(diff_chk_q / R)
        DIFF_CHECK_DCM.append(diff_chk_dcm / R)
        
    return X1, X2, DIFF_CHECK_Q, DIFF_CHECK_DCM