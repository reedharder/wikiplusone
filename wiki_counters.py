# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 10:43:56 2014

@author: Reed
"""

from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pylab as plb
from scipy.stats import linregress

labels, values = zip(*aggCount.most_common(50))

indexes = np.arange(len(labels))
width = 1

plt.bar(indexes, values, width)

plt.xticks(indexes + width * 0.5, labels)
plt.show()

X=indexes +1
Y=values
plt.plot(X,Y, 'bo')
plt.savefig('rawplot.png')

plt.loglog(X,Y,'bo')
plt.savefig('loglogplot.png')

m,b=plb.polyfit(plb.log10(X),plb.log10(Y),1)
slope, intercept, r_value, p_value, std_err=linregress(plb.log10(X),plb.log10(Y))
rsquared=r_value**2
plt.plot(plb.log10(X),plb.log10(Y),'bo',plb.log10(X), plb.log10(X)*slope +intercept, '--k')
plt.savefig('loglogplot_fitted.png')
