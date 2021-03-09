import csv
import os.path
import math
import sys
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import mannwhitneyu

def test(fixed, jittered, name1):
    # compare samples
    stat, p = mannwhitneyu(fixed, jittered)
    print(name1)
    print('Statistics=%.3f, p=%.3f' % (stat, p))
    # interpret
    alpha = 0.05
    if p > alpha:
	       print('Same distribution (fail to reject H0)')
    else:
	       print('Different distribution (reject H0)')

foleder1 = 'experiments/fixed/'
foleder2 = 'experiments/jittered/'
foleder3 = 'experiments/offset/'

for e in [1,2,3,5]:
    if e == 1: #simple market
        for m in range(4):
            name = str(e)+'_'+str(m+1)
            name1 = name+'_mmProfits.pkl'
            with open(os.path.join(foleder1, name1), 'rb') as pickle_file:
                fixed = pickle.load(pickle_file)
            name = str(e)+'_'+str(m+1)
            name2 = name+'_mmProfits.pkl'
            with open(os.path.join(foleder2, name2), 'rb') as pickle_file:
                jittered = pickle.load(pickle_file)
            test(fixed, jittered, name1)
    elif e == 2: #one shock (x->y)
        for m1 in range(4):
            for m2 in range(4):
                if not m1 == m2:
                    name = str(e)+'_'+str(m1+1)+'_'+str(m2+1)
                    name1 = name+'_mmProfits.pkl'
                    with open(os.path.join(foleder1, name1), 'rb') as pickle_file:
                        fixed = pickle.load(pickle_file)
                    name = str(e)+'_'+str(m1+1)+'_'+str(m2+1)
                    name2 = name+'_mmProfits.pkl'
                    with open(os.path.join(foleder2, name2), 'rb') as pickle_file:
                        jittered = pickle.load(pickle_file)
                    test(fixed, jittered, name1)
    elif e == 3: #two shock (x->y->x)
        for m1 in range(4):
            for m2 in range(4):
                if not m1 == m2:
                    name = str(e)+'_'+str(m1+1)+'_'+str(m2+1)+'_'+str(m1+1)
                    name1 = name+'_mmProfits.pkl'
                    with open(os.path.join(foleder1, name1), 'rb') as pickle_file:
                        fixed = pickle.load(pickle_file)
                    name = str(e)+'_'+str(m1+1)+'_'+str(m2+1)+'_'+str(m1+1)
                    name2 = name+'_mmProfits.pkl'
                    with open(os.path.join(foleder2, name2), 'rb') as pickle_file:
                        jittered = pickle.load(pickle_file)
                    test(fixed, jittered, name1)
    elif e == 5: #simple market w offset
        for m in range(4):
            name = str(e)+'_fixed_'+str(m+1)
            name1 = name+'_mmProfits.pkl'
            with open(os.path.join(foleder3, name1), 'rb') as pickle_file:
                fixed = pickle.load(pickle_file)
            name = str(e)+'_jittered_'+str(m+1)
            name2 = name+'_mmProfits.pkl'
            with open(os.path.join(foleder3, name2), 'rb') as pickle_file:
                jittered = pickle.load(pickle_file)
            test(fixed, jittered, name1)
