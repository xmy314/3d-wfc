# 3d wave function collapse implementation

## how to add new modules:
Each module is bounded by an axis aligned cube that range from ════0.5 to 0.5 on each axis.
Faces for modules in 3d modules need to be manually identified and labelled in the file name.
The entire file name is: `{face}-{face}-{face}-{face}-{face}-{face}.obj`.
Each face is represented with: `{name}{state}`.

The name of the face can be any combination of english alphabets and is case sensitive.

The state number is the orientation of the face relative to the default with values 0-7.
In order to determine the state, one needs to first figure out the origin of the face of the cube.
The origin is the point on the face that is the largest when components are added together.
egs: 
    face at x=.5, origin is (.5,.5,.5)
    face at y=.5, origin is (.5,.5,.5)
    face at y=-.5, origin is (.5,-.5,.5)

I'm total aware that it isn't natural, but I'm not aware of a more natural representation.
This is how i came up with this:
The two lower bits represents clockwise rotation and adding 1 is a clockwise rotation.
The third lowest bit is reflection and fliping all the bits is reflection along the diagonal that doesn't contain the origin.
eg:
If a face is like the folloing where "o" is the origin
o═══╗    
    ║    
    ║    
         
          
then:

orientation｜state number
---------｜---
o═══╗    ｜0(optional)
    ║    ｜
    ║    ｜
         ｜
         ｜
---------｜---
o       ║｜1
        ║｜
    ════╝｜
         ｜
         ｜
---------｜---
o        ｜2
         ｜
    ║    ｜
    ║    ｜
    ╚════｜
---------｜---
o        ｜3
         ｜
╔════    ｜
║        ｜
║        ｜
---------｜---
o        ｜4
         ｜
    ║    ｜
    ║    ｜
════╝    ｜
---------｜---
o        ｜5
║        ｜
╚════    ｜
         ｜
         ｜
---------｜---
o   ╔════｜6
    ║    ｜
    ║    ｜
         ｜
         ｜
---------｜---
o        ｜7
         ｜
    ════╗｜
        ║｜
        ║｜

Each face may also be symmetric in some way, below is an look up table. This need to be configured in mainv3.

orientation｜state number
---------｜---
o═══╗    ｜no_symmetry
    ║    ｜
    ║    ｜
         ｜
         ｜
---------｜---
════╗   ║｜rot_by_four_fold
    ║   ║｜please don't cancel me)(
╔═══╬═══╝｜(this is not the symbol)
║   ║    ｜
║   ╚════｜
---------｜---
════╗    ｜rot_by_two_fold
    ║    ｜
    ║    ｜
    ║    ｜
    ╚════｜
---------｜---
o═══╦════｜ref_by_y
    ║    ｜
    ║    ｜
         ｜
         ｜
---------｜---
o═══╗    ｜ref_by_x
    ║    ｜
    ║    ｜
    ║    ｜
════╝    ｜
---------｜---
o═══╗    ｜ref_by_minor
    ║    ｜
    ╚═══╗｜
        ║｜
        ║|
---------｜---
o═══╗    ｜6ref_by_major
║   ║    ｜
╚═══╝    ｜
         ｜
         ｜
---------｜---
o═══╦════｜ref_orth
    ║    ｜
    ║    ｜
    ║    ｜
════╩════｜
---------｜---
o═══╗    |ref_diag
║   ║    ｜
╚═══╬═══╗｜
    ║   ║｜
    ╚═══╝｜
---------｜---
o═══╦═══╗|all_symmetry
║   ║   ║｜
╠═══╬═══╣｜
║   ║   ║｜
╚═══╩═══╝｜
 
## how to run the code
run with
```
    python mainv3.py
```
profile with:
```
    python -m cProfile -o /tmp/tmp.prof mainv3.py
```
visualizing profiling result with:
```
    snakeviz /tmp/tmp.prof
```

## other stuff:
    symmetry_generation_2 doesn't work.

