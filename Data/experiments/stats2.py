import csv
import os.path
import math
import sys
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import friedmanchisquare

def test(fixed, jittered, random, name1):
    # compare samples
    stat, p = friedmanchisquare(fixed, jittered, random)
    print(name1)
    print('Statistics=%.3f, p=%.3f' % (stat, p))
    # interpret
    alpha = 0.05
    if p > alpha:
	       print('Same distribution (fail to reject H0)')
    else:
	       print('Different distribution (reject H0)')

folder1 = 'data/fixed/'
folder2 = 'data/jittered/'
folder3 = 'data/random/'
folder4 = 'data/offset/'

for e in [1,2,3,5]:
    if e == 1: #simple market
        for m in range(4):
            name = str(e)+'_'+str(m+1)
            name1 = name+'_mmProfits.pkl'
            with open(os.path.join(folder1, name1), 'rb') as pickle_file:
                fixed = pickle.load(pickle_file)
            name2 = name+'_mmProfits.pkl'
            with open(os.path.join(folder2, name2), 'rb') as pickle_file:
                jittered = pickle.load(pickle_file)
            name3 = name+'_mmProfits.pkl'
            with open(os.path.join(folder3, name3), 'rb') as pickle_file:
                random = pickle.load(pickle_file)
            test(fixed, jittered, random, name1)
    elif e == 2: #one shock (x->y)
        for m1 in range(4):
            for m2 in range(4):
                if not m1 == m2:
                    name = str(e)+'_'+str(m1+1)+'_'+str(m2+1)
                    name1 = name+'_mmProfits.pkl'
                    with open(os.path.join(folder1, name1), 'rb') as pickle_file:
                        fixed = pickle.load(pickle_file)
                    name2 = name+'_mmProfits.pkl'
                    with open(os.path.join(folder2, name2), 'rb') as pickle_file:
                        jittered = pickle.load(pickle_file)
                    name3 = name+'_mmProfits.pkl'
                    with open(os.path.join(folder3, name3), 'rb') as pickle_file:
                        random = pickle.load(pickle_file)
                    test(fixed, jittered, random, name1)
    elif e == 3: #two shock (x->y->x)
        for m1 in range(4):
            for m2 in range(4):
                if not m1 == m2:
                    name = str(e)+'_'+str(m1+1)+'_'+str(m2+1)+'_'+str(m1+1)
                    name1 = name+'_mmProfits.pkl'
                    with open(os.path.join(folder1, name1), 'rb') as pickle_file:
                        fixed = pickle.load(pickle_file)
                    name2 = name+'_mmProfits.pkl'
                    with open(os.path.join(folder2, name2), 'rb') as pickle_file:
                        jittered = pickle.load(pickle_file)
                    name3 = name+'_mmProfits.pkl'
                    with open(os.path.join(folder3, name3), 'rb') as pickle_file:
                        random = pickle.load(pickle_file)
                    test(fixed, jittered, random, name1)
    elif e == 5: #simple market w offset
        for m in range(4):
            name = str(e)+'_fixed_'+str(m+1)
            name1 = name+'_mmProfits.pkl'
            with open(os.path.join(folder4, name1), 'rb') as pickle_file:
                fixed = pickle.load(pickle_file)
            name = str(e)+'_jittered_'+str(m+1)
            name2 = name+'_mmProfits.pkl'
            with open(os.path.join(folder4, name2), 'rb') as pickle_file:
                jittered = pickle.load(pickle_file)
            name = str(e)+'_random_'+str(m+1)
            name3 = name+'_mmProfits.pkl'
            with open(os.path.join(folder4, name3), 'rb') as pickle_file:
                random = pickle.load(pickle_file)
            test(fixed, jittered, random, name1)
