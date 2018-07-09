from numpy.random import randn
from filterpy.kalman import UnscentedKalmanFilter
from filterpy.common import Q_discrete_white_noise
from filterpy.kalman import JulierSigmaPoints
from filterpy.kalman import MerweScaledSigmaPoints
import pymap3d as pm
import numpy as np
import matplotlib.pyplot as plt
import math

def fx(x, dt):
    """
    state x = [E N pi v dpi a]
    E - East
    N - North
    pi - heading
    v  - body velocity
    dpi - heading rate
    a   - body acceleration
    """
    xout = np.empty_like(x)
    xout[0] = x[0] + x[3] * dt * math.cos(x[2])
    xout[1] = x[1] + x[3] * dt * math.sin(x[2])
    xout[2] = x[2] + x[4] * dt
    xout[3] = x[3] + x[5] * dt
    xout[4] = x[4]
    xout[5] = x[5]

    return np.array(xout)


def hx(x):
    """
    measurement - X, Y, Z
    """
    hx = []
    hx[0] = x[0]
    hx[1] = x[1]
    hx[2] = x[5]

    return np.array(hx)


sigmas = JulierSigmaPoints(n=6, kappa=1)

ukf = UnscentedKalmanFilter(dim_x=6, dim_z=3, dt=0.01, hx=hx, fx=fx, points=sigmas)
ukf.x = np.array([0., 0., 0., 0., 0., 0.])
ukf.P = np.diag([0.0001, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001])
ukf.R = np.diag([0.009, 0.009, 0.009])
ukf.Q = Q_discrete_white_noise(6, dt=0.01, var=0.03)

zs, xs = [], []
for i in range(len(x)):
    z = np.array([x[i], y[i], AX[i]])
    ukf.predict()
    ukf.update(z)