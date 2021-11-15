#!/bin/bash

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INPUT_DIR=${SCRIPT_DIR}"/input"
FF_DIR=$(find_path -p FF)

# the script will be run in its own directory
mkdir example_genome
cd example_genome

polyply gen_params -lib parmbsc1 -seqf ${INPUT_DIR}/DNA_seq.json -o csDNA.itp -name csDNA

cat >> system.top << END
; Include forcefield parameters
#include "${FF_DIR}/amber14sb_parmbsc1.ff/forcefield.itp"

; Include chain topologies
#include "${INPUT_DIR}/protein.itp"

; Include water topology
#include "${FF_DIR}/amber14sb_parmbsc1.ff/tip3p.itp"

; Include topology for ions
#include "${FF_DIR}/amber14sb_parmbsc1.ff/ions.itp"
#include "csDNA.itp"


[ system ]
; Name
Protein in #water

[ molecules ]
; Compound        #mols
Protein             60
csDNA                1
NA                1767
CL                 360
END

polyply gen_coords -p system.top -b ${INPUT_DIR}/build_file.bld -o start.gro -cycles csDNA -name csDNA\
                  -box 23.62 23.62 23.62 -nr 20 -cycle_tol 0.8 -res DA DG DT DC SOL NA -lig csDNA#60:NA -c ${INPUT_DIR}/conf2.gro -mf 1000

gmx grompp -f ${INPUT_DIR}/min.mdp -c start.gro -p system.top -o min.tpr -r start.gro
gmx mdrun -v -deffnm min -s min.tpr -nt 1

gmx solvate -cs spc216.gro -cp min.gro  -o solvated.gro -p system.top

gmx grompp -f ${INPUT_DIR}/min.mdp -c solvated.gro -p system.top -o min_sol.tpr -r solvated.gro
gmx mdrun -v -deffnm min_sol -s min_sol.tpr -nt 1

gmx grompp -f  ${INPUT_DIR}/eq1.mdp -c min_sol.gro -p system.top -o eq1.tpr -r solvated.gro
gmx mdrun -v -s eq1.tpr -deffnm eq1

gmx grompp -f  ${INPUT_DIR}/eq2.mdp -c eq1.gro -p system.top -o eq2.tpr -r solvated.gro
gmx mdrun -v -s eq2.tpr -deffnm eq2

gmx grompp -f  ${INPUT_DIR}/eq3.mdp -c eq2.gro -p system.top -o eq3.tpr -r solvated.gro
gmx mdrun -v -s eq3.tpr -deffnm eq3
