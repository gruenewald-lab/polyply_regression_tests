import numpy as np
import itertools
from polyply.src.linalg_functions import angle, dih
from polyply.src.virtual_site_builder import construct_vs

def matches_geometry(block, coords, tolerances):
    """
    Given the interactions of a block and some coordinates,
    verify that the coordinates match the geometry as defined
    in the block interactions within accpatable deviations.
    """
    for bond in itertools.chain(block.interactions["bonds"], block.interactions["constraints"]):
        ref = float(bond.parameters[1])
        dist = np.linalg.norm(coords[bond.atoms[0]] - coords[bond.atoms[1]])
        assert np.isclose(dist, ref, atol=tolerances['bond'])

    for inter in block.interactions["angles"]:
        ref = float(inter.parameters[1])
        ang = angle(coords[inter.atoms[0]], coords[inter.atoms[1]], coords[inter.atoms[2]])
        assert np.isclose(ang, ref, atol=tolerances['angles'])

    # only improper dihedrals
    for inter in block.interactions["dihedrals"]:
        if inter.parameters[0] == "2":
            ref = float(inter.parameters[1])
            ang = dih(coords[inter.atoms[0]],
                      coords[inter.atoms[1]],
                      coords[inter.atoms[2]],
                      coords[inter.atoms[3]])
            assert np.isclose(ang, ref, atol=tolerances["dihedrals"])

    for virtual_site in block.interactions["virtual_sitesn"]:
        ref_coord = construct_vs("virtual_sitesn", virtual_site, coords)
        vs_coords = coords[virtual_site.atoms[0]]
        assert np.allclose(ref_coord, vs_coords)


