import pickle
import numpy as np

with open('0511.pkl', 'rb') as f:
    data1 = pickle.load(f)
    fitness1 = pickle.load(f)

with open('0512.pkl', 'rb') as f:
    data2 = pickle.load(f)
    fitness2 = pickle.load(f)

data=data1+data2
fit=np.concatenate((fitness1,fitness2),axis=0)
print(np.max(fit))
fitoverrounds=np.ones([3,5,5,5,5,5])
for i,v in enumerate(fit):
    fitoverrounds=fitoverrounds*v
meaningful= np.where(fitoverrounds!=0,1,0)
avefit=np.average(fit,axis=0)
fitoverrounds=avefit*meaningful
np.argmax(fitoverrounds)
np.where(fitoverrounds==np.max(fitoverrounds))
FIT=fitoverrounds[:,:,:,:,:,0:4]
np.where(FIT==np.max(FIT))


np.where(fitoverrounds[1]==np.max(fitoverrounds[1]))

np.where(fitoverrounds[2]==np.max(fitoverrounds[2]))


print(1)