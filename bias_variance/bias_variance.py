#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 19:50:48 2018

@author: JSen
"""

import numpy as np
import matplotlib.pyplot as plt
from numpy import loadtxt, load
import os
from scipy import optimize
from scipy.optimize import minimize
from sklearn import linear_model
import scipy.io as spio
import random

os.chdir(os.path.realpath('.'))

#load training data
data = spio.loadmat('ex5data1.mat')

#X 5000x400   y 5000x1
X = data['X']
y = data['y']
Xval = data['Xval']
yval = data['yval']
Xtest = data['Xtest']
ytest = data['ytest']

plt.scatter(X, y, marker='x')
plt.xlabel('Change in water level (x)')
plt.ylabel('Water flowing out of the dam (y)')
plt.show()

def linearRegCostFunction(theta, X, y, lambda_coe):
    m = len(y)
    J = 0
    h = np.dot(X, theta)
    theta_1 = theta.copy()
    theta_1[0] = 0 #theta0 should not be regularized!
    J = 1/(2*m) * np.sum((h-y)**2) + lambda_coe/(2*m) * np.sum(theta_1**2)
    return J

def linearRegGradientFunction(theta, X, y, lambda_coe):
    m = len(y)
    theta = theta.reshape(-1, 1)
    h = np.dot(X, theta)
    theta_1 = theta.copy()
    theta_1[0] = 0

    grad = np.dot(X.T, h-y)/m + lambda_coe/m * theta_1
    return grad.ravel()

def test(X, y):
    theta = np.array([[1], [1]])
    X = np.hstack((np.ones((X.shape[0], 1)), X))

    cost = linearRegCostFunction(theta, X, y,  1)
    grad = linearRegGradientFunction(theta, X, y,  1)
    print(f'cost:{cost}, gradient:{grad}')
test(X, y)

def feature_normalization(X):
    X_norm = X

    column_mean = np.mean(X_norm, axis=0)
#    print('mean=', column_mean)
    column_std = np.std(X_norm, axis=0)
#    print('std=',column_std)

    X_norm = X_norm - column_mean
    X_norm = X_norm / column_std

    return column_mean.reshape(1, -1), column_std.reshape(1, -1), X_norm

#means, stds, X_norm = feature_normalization(X)

def feature_normalization_with_mu(X, mu, sigma):
    mu = mu.reshape(1, -1)
    sigma = sigma.reshape(1, -1)
    X_norm = X
    X_norm = X_norm - mu
    X_norm = X_norm / sigma

    return  X_norm



def trainLinearReg(X, y, lambda_coe):
#    X = np.hstack((np.ones((X.shape[0],1)), X))
    initial_theta = np.ones((X.shape[1], 1)).flatten()

    '''注意：此处使用Newton-CG方法，才可以得到和课程中一样的结果，只使用cg方法时，包含10个以上的样本不收敛'''
    result = optimize.minimize(linearRegCostFunction, initial_theta, method='Newton-CG' ,jac=linearRegGradientFunction, args=(X, y, lambda_coe), options={'maxiter':200, 'disp':True})
    return result['x']
    #和上面代码等价的
#    res = optimize.fmin_ncg(linearRegCostFunction, initial_theta, fprime=linearRegGradientFunction, args=(X, y, lambda_coe), maxiter=200)
#    return res

#res = trainLinearReg(X, y, 0)

def plotData(X, y, theta):
    plt.plot(X, y, 'ro')
    plt.xlabel('Change in water level (x)')
    plt.ylabel('Water flowing out of the dam (y)')
    plt.hold(True)

    X_t = np.hstack((np.ones((X.shape[0],1)), X))
    y_t = np.dot(X_t, theta.reshape(-1,1))
    plt.plot(X, y_t, 'g-')
    plt.hold(False)
    plt.show()

#plotData(X, y, res)

def learningCurve(X, y, Xval, yval, lambda_coe):
    m = len(y)
    error_train = np.zeros((m, 1))
    error_val = np.zeros((m, 1))

    for i in range(1, m+1):
#        i=2
        subX = X[:i, :]

        X_t = np.hstack((np.ones((subX.shape[0], 1)), subX))
        y_t = y[:i, :]
        theta = trainLinearReg(X_t, y_t, 0)
        theta = theta.reshape(-1, 1)

        train_loss = linearRegCostFunction(theta, X_t, y_t, 0) #最小二乘法

        X_val_t = np.hstack((np.ones((Xval.shape[0], 1)), Xval))
        val_loss = linearRegCostFunction(theta, X_val_t, yval, 0)
        error_train[i-1] = train_loss
        error_val[i-1] = val_loss

    return error_train, error_val

lambda_coe = 0
train_error, val_error = learningCurve(X, y, Xval, yval, lambda_coe)

def plotLearningCurve(train_error, val_error):

#    for i in range(len(train_error)):
#        print(f'{i}   {train_error[i]}     {val_error[i]}')

    m = len(y)
    plt.plot(list(range(1,m+1)), train_error, list(range(1,m+1)), val_error)
    plt.title('Learning curve for linear regression')
    plt.legend(['Train', 'Cross Validation'])
    plt.xlabel('Number of training examples')
    plt.ylabel('Error')
    plt.axis([0, 13, 0, 150])
    plt.show()

plotLearningCurve(train_error, val_error)

''' Part 6: Feature Mapping for Polynomial Regression'''
def polyFeatures(X: np.ndarray, p: int):
    X_t = X.copy()
    for i in range(2,p+1, 1):
        X_t = np.hstack((X_t, X**i))

    return X_t

p = 8
#Map X onto Polynomial Features and Normalize
X_poly = polyFeatures(X, p)
mu, sigma, X_poly = feature_normalization(X_poly)

#Map X_poly_test and normalize (using mu and sigma)
X_poly_test = polyFeatures(Xtest, p)
X_poly_test = feature_normalization_with_mu(X_poly_test, mu, sigma)

#Map X_poly_val and normalize (using mu and sigma)
X_poly_val = polyFeatures(Xval, p)
X_poly_val = feature_normalization_with_mu(X_poly_val, mu, sigma)


'''Part 7: Learning Curve for Polynomial Regression'''
lambda_coe = 10;
X_poly_train = np.hstack((np.ones((X_poly.shape[0], 1)), X_poly))
theta_02 = trainLinearReg(X_poly_train, y, lambda_coe)

plt.figure(1)
plt.plot(X, y, 'rx')
plt.hold(True)
min_x = np.min(X)
max_x = np.max(X)

x = np.arange(min_x - 15, max_x + 25, 0.05).reshape(-1, 1)
poly_x = polyFeatures(x, 8)
poly_x = feature_normalization_with_mu(poly_x, mu, sigma)

ones = np.ones((poly_x.shape[0], 1))
poly_x = np.hstack((ones, poly_x))
plt.plot(x, np.dot(poly_x, theta_02), '--')
plt.xlabel('Change in water level (x)')
plt.ylabel('Water flowing out of the dam (y)')
plt.hold(False)
plt.show()

lambda_coe = 10
train_error_p, val_error_p = learningCurve(X_poly, y, X_poly_val, yval, lambda_coe)
plotLearningCurve(train_error_p, val_error_p)


