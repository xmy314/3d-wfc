# symmetries
# label, req. for (a,b) being equal, annotation
#    0 : 0==(a^b)&111                 i (no symmetry)
#    1 : 0==(a^b)&100                 r1|r3=> r1+r2+r3 (90 symmetry)
#    2 : 0==(a^b)&101                 r2 (180 symmetry)

#    3 : a==b or (min(a,b),max(a,b)) in [(2,4),(1,5),(0,6),(3,7)]          ref by y axis
#    4 : a==b or (min(a,b),max(a,b)) in [(0,4),(3,5),(2,6),(1,7)]          ref by x axis
#    5 : 0==(a^b^111)&111             ref by minor diagnoal axis
#    6 : 0==(a^b^101)&111             ref by major diagonal axis

#    7 : 0==(a^b)&001                 (refx|refy)&(refx|r2)&(refy|r2) => refx+refy+r2 (orthagonal symmetry)
#    8 : 0==(a^b^((a^b)>>2))&1        (refm1|refm2)&(refm1|r2)&(refm2|r2) => refm1+refm2+r2 (diagonal symmetry)
#    9 : 0==(a^b)&000                 (efx|refy|refm1|refm2)&(refx|refy|r1|r3)&(refm1|refm2|r1|r3) => all (all eight are fine)

# for a and b to match:
# inf(180(a))==b with equal being defined as a.label == b.label and the symmetry defined from above

# 10 types, 4 bits, but that doesn't matter as the decomposition is messier than worthy
import numpy as np
from enum import IntEnum 

class SymmetryGroup(IntEnum):
    no_symmetry=0
    rot_by_four_fold=1
    rot_by_two_fold=2
    ref_by_y=3
    ref_by_x=4
    ref_by_minor=5
    ref_by_major=6
    ref_orth=7
    ref_diag=8
    all_symmetry=9
 
class Face:
    def __init__(self,label:int,symmetry:SymmetryGroup,initial_state:int=0):
        # state is relative to the default at the position.
        # the default position for + faces are starting from +++ and rotate cw
        # the default position for - faces are starting from ++- and rotate cw
        # this way, 
        #   the two asymmetric faces match if they are inf*180   (a^b^5=0)
        #   the two horizontally faces match if they are inf*180 or 90 ( ((a^5)&(((a)&4+(a+1)&3)))^b==0 )
        #   the two vertically faces match if they are inf*180 or 270 ( ((a^5)&(((a)&4+(a-1)&3)))^b==0 )
        #   the two rotational faces match if they are inf or inf*90 or inf*180 or inf*270 (a^b^5)&4==0
        #   the ones where all eight state are the same, all state match 
        # relative states are:
        #   0 : identity
        #   1 : cw
        #   2 : 180
        #   3 : ccw
        #   4 : reflected along the axis that (the midpoint of origin and cw origin sits on)
        #   5 : reflected along the axis that (origin sits on)
        #   6 : reflected along the axis that (the midpoint of origin and ccw origin sits on)
        #   7 : reflected along the axis that (would make origin move to the opposite corner)
        self.label=label
        self.symmetry=symmetry
        self.state=initial_state
    
    def ind(self):
        return Face(self.label,self.symmetry,self.state)
    
    def inf(self):
        return Face(self.label,self.symmetry,7-self.state)
    
    def cw(self):
        return Face(self.label,self.symmetry,(self.state&4)+((self.state+1)&3))

    def ccw(self):
        return Face(self.label,self.symmetry,(self.state&4)+((self.state-1)&3))

    @staticmethod
    def match(a,b):
        return a.inf().cw().cw()==b

    def __repr__(self):
        if   self.symmetry==0:pass
        elif self.symmetry==1:self.state&=0b100
        elif self.symmetry==2:self.state&=0b101
        elif self.symmetry==3:
            la=[0,1,2,3,2,3,0,1]
            self.state=la[self.state]
        elif self.symmetry==4:
            la=[0,1,2,3,0,1,2,3]
            self.state=la[self.state]
        elif self.symmetry==5:
            la=[0,1,2,3,1,2,3,0]
            self.state=la[self.state]
        elif self.symmetry==6:
            la=[0,1,2,3,3,0,1,2]
            self.state=la[self.state]
        elif self.symmetry==7:self.state&=0b001
        elif self.symmetry==8:
            la=[0,1,0,1,1,0,1,0]
            self.state=la[self.state]
        elif self.symmetry==9:self.state=0
        return f" {self.label} {bin(8+self.state)[-3:]} "

    def __eq__(self, other) -> bool:
        if (not isinstance(other,Face)):
            return False
        if (self.label!=other.label):
            return False
        a=self.state
        b=other.state
        if   self.symmetry==0:return 0==(a^b)&0b111
        elif self.symmetry==1:return 0==(a^b)&0b100
        elif self.symmetry==2:return 0==(a^b)&0b101
        elif self.symmetry==3:return 0==(a^b)&0b111 or (min(a,b),max(a,b)) in [(2,4),(3,5),(0,6),(1,7)]
        elif self.symmetry==4:return 0==(a^b)&0b111 or (min(a,b),max(a,b)) in [(0,4),(1,5),(2,6),(3,7)]
        elif self.symmetry==5:return 0==(a^b)&0b111 or (min(a,b),max(a,b)) in [(1,4),(2,5),(3,6),(0,7)]
        elif self.symmetry==6:return 0==(a^b)&0b111 or (min(a,b),max(a,b)) in [(3,4),(0,5),(1,6),(2,7)]
        elif self.symmetry==7:return 0==(a^b)&0b001
        elif self.symmetry==8:return 0==(a^b^((a^b)>>2))&0b001
        elif self.symmetry==9:return 0==(a^b)&0b000
    
class Cube:
    def __init__(self,face_labels,face_symmetries,face_states,mesh_id,transformation=None,reflected=False):
        self.faces = [Face(face_labels[i],face_symmetries[i],face_states[i]) for i in range(6)]
        self.mesh_id=mesh_id
        if transformation is None:
            self.transformation = np.identity(4)
        else:
            self.transformation = transformation
        self.reflected=reflected

    def rot_x_cw(self):
        n_faces = [
            self.faces[0].cw(),
            self.faces[2].ccw(),
            self.faces[4].ind(),
            self.faces[3].ccw(),
            self.faces[5].cw(),
            self.faces[1].ind(),
        ]
        n_transformation = np.asarray([
            [1,0,0,0],
            [0,0,1,0],
            [0,-1,0,0],
            [0,0,0,1],
        ])
        return Cube(*zip(*((face.label,face.symmetry,face.state) for face in n_faces)),self.mesh_id,np.matmul(n_transformation,self.transformation),self.reflected)

    def rot_y_cw(self):
        n_faces =  [
            self.faces[5].ind(),
            self.faces[1].cw(),
            self.faces[0].ccw(),
            self.faces[2].ind(),
            self.faces[4].ccw(),
            self.faces[3].cw(),
        ]
        n_transformation = np.asarray([
            [0,0,-1,0],
            [0,1,0,0],
            [1,0,0,0],
            [0,0,0,1],
        ])
        return Cube(*zip(*((face.label,face.symmetry,face.state) for face in n_faces)),self.mesh_id,np.matmul(n_transformation,self.transformation),self.reflected)

    def rot_z_cw(self):
        n_faces =  [
            self.faces[1].ccw(),
            self.faces[3].ind(),
            self.faces[2].cw(),
            self.faces[4].cw(),
            self.faces[0].ind(),
            self.faces[5].ccw(),
        ]
        n_transformation = np.asarray([
            [0,1,0,0],
            [-1,0,0,0],
            [0,0,1,0],
            [0,0,0,1],
        ])
        return Cube(*zip(*((face.label,face.symmetry,face.state) for face in n_faces)),self.mesh_id,np.matmul(n_transformation,self.transformation),self.reflected)

    def rot_x_ccw(self):
        n_faces =  [
            self.faces[0].ccw(),
            self.faces[5].ind(),
            self.faces[1].cw(),
            self.faces[3].cw(),
            self.faces[2].ind(),
            self.faces[4].ccw(),
        ]
        n_transformation = np.asarray([
            [1,0,0,0],
            [0,0,-1,0],
            [0,1,0,0],
            [0,0,0,1],
        ])
        return Cube(*zip(*((face.label,face.symmetry,face.state) for face in n_faces)),self.mesh_id,np.matmul(n_transformation,self.transformation),self.reflected)

    def rot_y_ccw(self):
        n_faces =  [
            self.faces[2].cw(),
            self.faces[1].ccw(),
            self.faces[3].ind(),
            self.faces[5].ccw(),
            self.faces[4].cw(),
            self.faces[0].ind(),
        ]
        n_transformation = np.asarray([
            [0,0,1,0],
            [0,1,0,0],
            [-1,0,0,0],
            [0,0,0,1],
        ])
        return Cube(*zip(*((face.label,face.symmetry,face.state) for face in n_faces)),self.mesh_id,np.matmul(n_transformation,self.transformation),self.reflected)

    def rot_z_ccw(self):
        n_faces =  [
            self.faces[4].ind(),
            self.faces[0].cw(),
            self.faces[2].ccw(),
            self.faces[1].ind(),
            self.faces[3].ccw(),
            self.faces[5].cw(),
        ]
        n_transformation = np.asarray([
            [0,-1,0,0],
            [1,0,0,0],
            [0,0,1,0],
            [0,0,0,1],
        ])
        return Cube(*zip(*((face.label,face.symmetry,face.state) for face in n_faces)),self.mesh_id,np.matmul(n_transformation,self.transformation),self.reflected)

    def inf(self):
        n_faces=[self.faces[x].inf() for x in [3,4,5,0,1,2]]
        n_transformation = np.asarray([
            [-1,0,0,0],
            [0,-1,0,0],
            [0,0,-1,0],
            [0,0,0,1],
        ])
        return Cube(*zip(*((face.label,face.symmetry,face.state) for face in n_faces)),self.mesh_id,np.matmul(n_transformation,self.transformation),not self.reflected)

    def ind(self):
        n_faces= [self.faces[x].ind() for x in range(6)]
        return Cube(*zip(*((face.label,face.symmetry,face.state) for face in n_faces)),self.mesh_id,self.transformation,self.reflected)
    
    def generateVariations(self):
        ret=[self.ind()]
        tba = self.rot_z_cw()
        if not tba in ret: ret.append(tba)
        tba = self.rot_z_cw().rot_z_cw()
        if not tba in ret: ret.append(tba)
        tba = self.rot_z_ccw()
        if not tba in ret: ret.append(tba)
        tba = self.rot_y_cw()
        if not tba in ret: ret.append(tba)
        tba = self.rot_y_ccw()
        if not tba in ret: ret.append(tba)

        ite=len(ret)
        for i in range(ite):
            tba = ret[i].rot_x_cw()
            if not tba in ret: ret.append(tba)
            tba = ret[i].rot_x_cw().rot_x_cw()
            if not tba in ret: ret.append(tba)
            tba = ret[i].rot_x_ccw()
            if not tba in ret: ret.append(tba)
        ite=len(ret)
        for i in range(ite):
            tba = ret[i].inf()
            if not tba in ret: ret.append(tba)
        return ret

    def __repr__(self):
        return str(self.faces)

    def __eq__(self, other) -> bool:
        # this comparison compares orientation as well.
        # same mesh, different orientation are different cubes.
        if (not isinstance(other,Cube)):
            return False
        for i in range(6):
            if self.faces[i]!=other.faces[i]:
                return False
        return True

if __name__=="__main__":
    cube_sample=Cube(
                    face_labels=[0,0,0,1,1,1],
                    face_symmetries=[SymmetryGroup.all_symmetry]*6,
                    face_states=[0,0,0,0,0,0],
                    mesh_id=0)

    cube_samples=cube_sample.generateVariations()
    print("\n".join([str(x) for x in cube_samples]))