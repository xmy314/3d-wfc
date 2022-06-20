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
In case when a face is like the folloing where "o" is the origin.<br>
`o═══╗    `<br>`    ║    `<br>`    ║    `<br>`         `<br>`         `

The orientation and state number can be seen from the following table.

orientation|state number
---|---
`o═══╗    `<br>`    ║    `<br>`    ║    `<br>`         `<br>`         `|0(optional)
`o       ║`<br>`        ║`<br>`    ════╝`<br>`         `<br>`         `|1
`o        `<br>`         `<br>`    ║    `<br>`    ║    `<br>`    ╚════`|2
`o        `<br>`         `<br>`╔════    `<br>`║        `<br>`║        `|3
`o        `<br>`         `<br>`    ║    `<br>`    ║    `<br>`════╝    `|4
`o        `<br>`║        `<br>`╚════    `<br>`         `<br>`         `|5
`o   ╔════`<br>`    ║    `<br>`    ║    `<br>`         `<br>`         `|6
`o        `<br>`         `<br>`    ════╗`<br>`        ║`<br>`        ║`|7

Each face may also be symmetric in some way, below is a look up table. This need to be configured for each face name in mainv3.

shape|symmetry type
---|---
`o═══╗    `<br>`    ║    `<br>`    ║    `<br>`         `<br>`         `|no_symmetry
`════╗   ║`<br>`    ║   ║`<br>`╔═══╬═══╝`<br>`║   ║    `<br>`║   ╚════`|rot_by_four_fold<br>(please don't cancel me)<br>(this is not the symbol)
`════╗    `<br>`    ║    `<br>`    ║    `<br>`    ║    `<br>`    ╚════`|rot_by_two_fold
`o═══╦════`<br>`    ║    `<br>`    ║    `<br>`         `<br>`         `|ref_by_y
`o═══╗    `<br>`    ║    `<br>`    ║    `<br>`    ║    `<br>`════╝    `|ref_by_x
`o═══╗    `<br>`    ║    `<br>`    ╚═══╗`<br>`        ║`<br>`        ║`|ref_by_minor
`o═══╗    `<br>`║   ║    `<br>`╚═══╝    `<br>`         `<br>`         `|ref_by_major
`o═══╦════`<br>`    ║    `<br>`    ║    `<br>`    ║    `<br>`════╩════`|ref_orth
`o═══╗    `<br>`║   ║    `<br>`╚═══╬═══╗`<br>`    ║   ║`<br>`    ╚═══╝`|ref_diag
`o═══╦═══╗`<br>`║   ║   ║`<br>`╠═══╬═══╣`<br>`║   ║   ║`<br>`╚═══╩═══╝`|all_symmetry
 
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

this currently have a three step look ahead baked in.

updating constraints whenever something changes is a step look ahead.
checkvalidity is one step look ahead when that is present.
propagate uses check validity is another step look ahead.

this reduces the number of back propagation to extremely low, but it also couldn't really be sped fast or to apply alpha beta trimming.

maybe another way that focuses on using back propagation would be more valuable?
