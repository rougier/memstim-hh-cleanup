#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Memory Stimulation and Phase-Amplitude Coupling
# Copyright 2021 Nikolaos Vardlakis & Nicolas P. Rougier
# Released under the BSD 3-clauses license
# -----------------------------------------------------------------------------
import os
import json
import time
import subprocess
from numpy import pi

# Constants
noise_exc = 10e-06
noise_inh = 1e-06

# Default parameters
_data = {
    "seed_val"              : 42,       # Reproducibility

    # areas, tables 3.1-3.3, pages 45-48, Aussel
    "areas": {
        "EC"    : {
            "E" : {
                "N"     : int(10e3),
                "type"  : "PyCAN",
                "noise" : noise_exc     # Volts
            },
            "I" : {
                "N"     : int(1e3),
                "type"  : "Inh",
                "noise" : noise_inh
            }
        },
        "DG"    : {
            "E" : {
                "N"     : int(10e3),
                "type"  : "Py",
                "noise" : noise_exc
            },
            "I" : {
                "N"     : int(0.1e3),
                "type"  : "Inh",
                "noise" : noise_inh
            }
        },
        "CA3"   : {
            "E" : {
                "N"     : int(1e3),
                "type"  : "PyCAN",
                "noise" : noise_exc
            },
            "I" : {
                "N"     : int(0.1e3),
                "type"  : "Inh",
                "noise" : noise_inh
            }
        },
        "CA1"   : {
            "E" : {
                "N"     : int(10e3),
                "type"  : "PyCAN",
                "noise" : noise_exc
            },
            "I" : {
                "N"     : int(1e3),
                "type"  : "Inh",
                "noise" : noise_inh
            }
        }
    },

    # Kuramoto oscillator parameters
    "Kuramoto" : {
        "N"             : 250,
        "f0"            : 6.,
        "sigma"         : 0.5,  # normal std
        "kN"            : 15,
        "gain_reset"    : 4.0,
        "gain_rhythm"   : 1.0,  # nA
        "offset"        : -0*pi/2
    },

    # connectivity parameters
    "connectivity" : {
        "intra" : { # intra-area conn. probabilities per area |
            "EC"        : [[0., 0.37], [0.54, 0.]], # [[E-E, E-I], [I-E, I-I]]
            "DG"        : [[0., 0.06], [0.14, 0.]],
            "CA3"       : [[0.56, 0.75], [0.75, 0.]],
            "CA1"       : [[0., 0.28], [0.3, 0.7]]
        },
        "inter" : { # inter-area conn. probabilities
            "p_tri"     : 0.45,     # tri: [DG->CA3, CA3->CA1, CA1->EC] Aussel, pages 49,59
            "p_mono"    : 0.2       # mono: [EC->CA3, EC->CA1]
        }
    },

    # synapses
    # "synapses" : {
    #     "gmax_e"    : 60.,    # pSiemens
    #     "gmax_i"    : 600.
    # },

    # stimulation parameters
    "stimulation" : {
        "target"        : "CA1",            # target area [EC | DG | CA3 | CA1]
        "coordinates"   : (5.0, -8., 7.5),  # point electrode coordinates (x,y,z) [mm]
        "sigma"         : 0.33,             # conductivity of homogeneous conductive medium [S/m]
        "duration"      : 3.,               # [sec]
        "dt"            : .1e-3,            # [sec]
        "onset"         : 1.615,            # [sec]
        "I"             : [10.],            # stimulation amplitude [nA]
        "pulse_width"   : [1.e-3],          # width (in time) of pulse ON phase [sec]
        "stim_freq"     : 5,                # stimulation frequency [Hz]
        "pulse_freq"    : 100,              # pulse frequency, determines ON duration [Hz]
        "nr_of_trains"  : 1,                # number of pulse trains
        "nr_of_pulses"  : 1,                # number of pulses per train
        "ipi"           : .1e-3             # inter-pulse interval [sec]
        },

    # simulation parameters
    "simulation" : {
        "duration"      : 3.0,              # second
        "dt"            : .1e-3,            # second
        "debugging"     : False
    },

    # git stuff
    "timestamp"         : None,
    "git_branch"        : None,
    "git_hash"          : None,
    "git_short_hash"    : None
}

def is_git_repo():
    """ Return whether current directory is a git directory """
    if subprocess.call(["git", "branch"],
            stderr=subprocess.STDOUT, stdout=open(os.devnull, 'w')) != 0:
        return False
    return True

def get_git_revision_hash():
    """ Get current git hash """
    if is_git_repo():
        answer = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'])
        return answer.decode("utf8").strip("\n")
    return "None"

def get_git_revision_short_hash():
    """ Get current git short hash """
    if is_git_repo():
        answer = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'])
        return answer.decode("utf8").strip("\n")
    return "None"

def get_git_revision_branch():
    """ Get current git branch """
    if is_git_repo():
        answer = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        return answer.decode("utf8").strip("\n")
    return "None"

def default():
    """ Get default parameters """
    _data["timestamp"] = time.ctime()
    _data["git_branch"] = get_git_revision_branch()
    _data["git_hash"] = get_git_revision_hash()
    _data["git_short_hash"] = get_git_revision_short_hash()
    return _data

def save(filename, data=None):
    """ Save parameters into a json file """
    if data is None:
       data = { name : eval(name) for name in _data.keys()
                if name not in ["timestamp", "git_branch", "git_hash"] }
    data["timestamp"] = time.ctime()
    data["git_branch"] = get_git_revision_branch()
    data["git_hash"] = get_git_revision_hash()
    data["git_short_hash"] = get_git_revision_short_hash()
    with open(filename, "w") as outfile:
        json.dump(data, outfile, indent=4, sort_keys=False)

def load(filename):
    """ Load parameters from a json file """
    with open(filename) as infile:
        data = json.load(infile)
    return data

def dump(data):
    if not _data["timestamp"]:
        _data["timestamp"] = time.ctime()
    if not _data["git_branch"]:
        _data["git_branch"] = get_git_revision_branch()
    if not _data["git_hash"]:
        _data["git_hash"] = get_git_revision_hash()
        _data["git_short_hash"] = get_git_revision_short_hash()
    for key, value in data.items():
        print(f"{key:15s} : {value}")

# -----------------------------------------------------------------------------
if __name__  == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate parameters file using JSON format')
    parser.add_argument('parameters_file',
                        default='default',
                        type=str, nargs='?',
                        help='Parameters file (json format)')
    args = parser.parse_args()

    filename = "./configs/{0}.json".format(args.parameters_file)

    print('Saving file "{0}"'.format(filename))
    save(filename, _data)

    print('..:: Unit Testing ::..')
    print('----------------------------------')
    data = load(filename)
    dump(data)
    print('----------------------------------')

    locals().update(data)
    print('Saving file "{0}"'.format(filename))
    save(filename)
