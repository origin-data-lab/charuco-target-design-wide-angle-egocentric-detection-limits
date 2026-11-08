import cv2, numpy as np, sys, json
vid,step,out,kind=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4]
if kind=='a4':
    d=cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100); board=cv2.aruco.CharucoBoard((9,6),0.030,0.022,d)
else:
    d=cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50); board=cv2.aruco.CharucoBoard((5,3),0.055,0.042,d)
det=cv2.aruco.CharucoDetector(board); adet=cv2.aruco.ArucoDetector(d,cv2.aruco.DetectorParameters())
def clusters(mc):
    c=np.array([m.reshape(4,2).mean(0) for m in mc]); s=np.array([np.linalg.norm(m.reshape(4,2)[0]-m.reshape(4,2)[2]) for m in mc])
    lab=-np.ones(len(c),int); k=0
    for i in range(len(c)):
        if lab[i]>=0: continue
        st=[i]; lab[i]=k
        while st:
            j=st.pop(); dd=np.linalg.norm(c-c[j],axis=1)
            for q in np.where((dd<3.0*max(s[j],1))&(lab<0))[0]: lab[q]=k; st.append(q)
        k+=1
    return lab
cap=cv2.VideoCapture(vid); res=[]; i=0
while True:
    if not cap.grab(): break
    if i%step==0:
        ok,f=cap.retrieve(); g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
        mc,mi,_=adet.detectMarkers(g); rec={'f':i,'mean':float(g.mean()),'boards':[]}
        if mi is not None and len(mi):
            mi=mi.ravel(); lab=clusters(mc)
            for k in np.unique(lab):
                sel=np.where(lab==k)[0]; ids=mi[sel]
                if len(sel)<2 or len(set(ids))<len(ids): continue
                cc,ci,_,_=det.detectBoard(g,markerCorners=[mc[j] for j in sel],markerIds=ids.reshape(-1,1))
                b={'nm':int(len(sel)),'mcen':[mc[j].reshape(4,2).mean(0).round(1).tolist() for j in sel],
                   'msize':float(np.mean([np.linalg.norm(mc[j].reshape(4,2)[0]-mc[j].reshape(4,2)[1]) for j in sel]))}
                if ci is not None and len(ci): b['ids']=ci.ravel().tolist(); b['pts']=cc.reshape(-1,2).round(3).tolist()
                rec['boards'].append(b)
        res.append(rec)
    i+=1
json.dump(res,open(out,'w')); print(vid,i,len(res))
