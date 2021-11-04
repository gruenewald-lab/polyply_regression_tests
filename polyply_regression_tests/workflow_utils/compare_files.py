# Copyright 2021 University of Groningen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Compare two files and check if they're content is conceptually
the same.
"""
from collections import defaultdict
from pathlib import Path
import shlex
import subprocess
import sys
import numpy as np

import pytest
import vermouth
from vermouth.forcefield import ForceField

from polyply import TEST_DATA
from vermouth.tests.helper_functions import find_in_path

INTEGRATION_DATA = Path(TEST_DATA + '/library_tests')

PATTERN = '{path}/{library}/{polymer}/polyply'

POLYPLY = find_in_path(names=("polyply", ))

def _interaction_equal(interaction1, interaction2, inter_type):
    """
    Returns True if interaction1 == interaction2, ignoring rounding errors in
    interaction parameters.
    """
    p1 = list(map(str, interaction1.parameters))
    p2 = list(map(str, interaction2.parameters))
    a1 = list(interaction1.atoms)
    a2 = list(interaction2.atoms)


    if p1 != p2:
        return False

    if interaction1.meta != interaction2.meta:
        return False

    if inter_type in ["constraints", "bonds", "exclusions", "pairs"]:
        a1.sort()
        a2.sort()
        return a1 == a2

    elif inter_type in ["impropers", "dihedrals"]:
        if a1 == a2:
            return True
        a1.reverse()
        if a1 == a2:
            return True
        else:
            print(a1, a2)

    elif inter_type in ["angles"]:
        return a1[1] == a2[1] and frozenset([a1[0], a1[2]]) == frozenset([a2[0], a2[2]])

    return False


def assert_equal_blocks(block1, block2):
    """
    Asserts that two blocks are equal to gain the pytest rich comparisons,
    which is lost when doing `assert block1 == block2`
    """
    assert block1.name == block2.name
    assert block1.nrexcl == block2.nrexcl
    assert block1.force_field == block2.force_field  # Set to be equal

    for node in block1.nodes:
        # for the simulation only these two attributes matter
        # as we have 3rd party reference files we don't do more
        # checks
        for attr in ["atype", "charge"]:
            # if the reference itp has the attribute check it
            if attr in block1.nodes[node]:
                assert block1.nodes[node][attr] == block2.nodes[node][attr]

    edges1 = {frozenset(e[:2]): e[2] for e in block1.edges(data=True)}
    edges2 = {frozenset(e[:2]): e[2] for e in block2.edges(data=True)}

    for e, attrs in edges2.items():
        for k, v in attrs.items():
            if isinstance(v, float):
                attrs[k] = pytest.approx(v, abs=1e-3) # PDB precision is 1e-3

    assert edges1 == edges2

    for inter_type in ["bonds", "angles", "constraints", "exclusions", "pairs", "impropers", "dihedrals"]:
        ref_interactions = block1.interactions.get(inter_type, [])
        new_interactions = block2.interactions.get(inter_type, [])
        print(inter_type)
        assert len(ref_interactions) == len(new_interactions)

        ref_terms = defaultdict(list)
        for inter in ref_interactions:
            atoms = inter.atoms
            ref_terms[frozenset(atoms)].append(inter)

        new_terms = defaultdict(list)
        for inter_new in new_interactions:
            atoms = inter_new.atoms
            new_terms[frozenset(atoms)].append(inter_new)

        for atoms, ref_interactions in ref_terms.items():
            new_interactions = new_terms[atoms]
            for ref_inter in ref_interactions:
                print(ref_inter)
                for new_inter in new_interactions:
                    if _interaction_equal(ref_inter, new_inter, inter_type):
                        break
                else:
                    assert False

def compare_itp(filename1, filename2):
    """
    Asserts that two itps are functionally identical
    """
    dummy_ff = ForceField(name='dummy')
    with open(filename1) as fn1:
        vermouth.gmx.read_itp(fn1, dummy_ff)
    dummy_ff2 = ForceField(name='dummy')
    with open(filename2) as fn2:
        vermouth.gmx.read_itp(fn2, dummy_ff2)
    for block in dummy_ff2.blocks.values():
        block._force_field = dummy_ff
    assert set(dummy_ff.blocks.keys()) == set(dummy_ff2.blocks.keys())
    for name in dummy_ff.blocks:
        block1 = dummy_ff.blocks[name]
        block2 = dummy_ff2.blocks[name]
        assert_equal_blocks(block1, block2)


def compare_pdb(filename1, filename2):
    """
    Asserts that two pdbs are functionally identical
    """
    pdb1 = vermouth.pdb.read_pdb(filename1)
    pdb2 = vermouth.pdb.read_pdb(filename2)
    assert len(pdb1) == len(pdb2)
    for mol1, mol2 in zip(pdb1, pdb2):
        for mol in (mol1, mol2):
            for n_idx in mol:
                node = mol.nodes[n_idx]
                if 'position' in node and node['atomname'] in ('SCN', 'SCP'):
                    # Charge dummies get placed randomly, which complicated
                    # comparisons to no end.
                    # These will be caught by the distances in the edges instead.
                    del node['position']

        assert_equal_blocks(mol1, mol2)
