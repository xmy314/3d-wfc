plane_sample=[1,2,3,4]

def identity(plane):
    return list(plane)

def cw(plane):
    ret=list(plane)
    ret=ret[1:]+ret[:1]
    ret[::2]=[-x for x in ret[::2]]
    return ret

def ccw(plane):
    ret=list(plane)
    ret=ret[-1:]+ret[:-1]
    ret[1::2]=[-x for x in ret[1::2]]
    return ret

def ref(plane,axis=0):
    ret=list(plane)
    td=len(ret)//2
    for d in range(td):
        if d==axis:
            ret[d::2]=[x for x in ret[td+d::-td]]
        else:
            ret[d::2]=[-x for x in ret[d::2]]
    return ret

def generatePlaneVariation(plane):
    variations = [
        identity(plane),
        cw(plane),
        cw(cw(plane)),
        ccw(plane),
        ref(plane),
        cw(ref(plane)),
        cw(cw(ref(plane))),
        ccw(ref(plane)),
    ]
    return variations

print(generatePlaneVariation(plane_sample))

