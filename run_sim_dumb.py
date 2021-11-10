#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from brian2 import *
from tqdm import tqdm

import time

import argparse
import parameters
import re # regular expressions

from model.globals import *
from model.HH_equations import *
from model.kuramoto_equations import *
from model.filter_equations import *
from model import settings
from model import setup

from src.annex_funcs import make_flat
from src.myplot import *

# C++ standalone mode :: NOT WORKING
#set_device('cpp_standalone')



# Configuration
# -------------------------------------------------------------#
# Use C++ standalone code generation TODO: Experimental!
#set_device('cpp_standalone')
parser = argparse.ArgumentParser(description='MemStim using HH neurons')
parser.add_argument('parameters_file',
                    nargs='?',
                    metavar='m',
                    type=str,
                    default='configs/default.json',
                    help='Parameters file (json format)')
args = parser.parse_args()
filename = args.parameters_file
print('Using "{0}"'.format(filename))

try:
    data = parameters.load(filename)
except:
    data = parameters._data
parameters.dump(data)
print()
#locals().update(data)

# settings initialization
settings.init(data)



# Make the neuron groups
# -------------------------------------------------------------#
print('\n >  Making the neuron groups...')

#fig, axs = subplots(nrows=1, ncols=1)
fig_anat = figure()
ax_anat = fig_anat.add_subplot(111, projection='3d')

G_all = [[[] for pops in range(2)] for areas in range(4)]

def parse_coords(fname, NG):
    """ Opens file and parses coordinates """
    pattern = r'[\[\],\n]' # to remove from read lines

    with open(fname, 'r') as fin:
        idx = 0
        for line in fin:
            tok = re.sub(pattern, '', line).split()
            NG.x_soma[idx] = float(tok[0])*scale
            NG.y_soma[idx] = float(tok[1])*scale
            NG.z_soma[idx] = float(tok[2])*scale
            idx += 1

# EC -> theta input from MS
G_E = NeuronGroup(N=settings.N_EC[0],
    model=py_CAN_inp_eqs,
    threshold='v>V_th',
    reset=reset_eqs,
    refractory=refractory_time,
    method=integ_method,
    name='EC_pyCAN')
G_E.size = cell_size_py
G_E.glu = 1
'''
pos = np.load('./neuron_positions/full/EC_E-stipple-10000.npy')
G_E.x_soma = pos[:,0]*scale
G_E.y_soma = pos[:,1]*scale
axs.plot(G_E.x_soma, G_E.y_soma, 'b.', markersize=.5, alpha=0.5, label='EC-PyCAN')
'''
parse_coords(fname='positions/EC_exc.txt', NG=G_E)

# Plot X,Y,Z
#ax_anat.plot_trisurf(G_E.x_soma, G_E.y_soma, G_E.z_soma, color='white', edgecolors='grey', alpha=0.5)
ax_anat.scatter(G_E.x_soma, G_E.y_soma, G_E.z_soma, c='blue')

G_I = NeuronGroup(N=settings.N_EC[1],
    model=inh_inp_eqs,
    threshold='v>V_th',
    refractory=refractory_time,
    method=integ_method,
    name='EC_inh')
G_I.size = cell_size_inh
'''
pos = np.load('./neuron_positions/full/EC_I-stipple-1000.npy')
G_I.x_soma = pos[:,0]*scale
G_I.y_soma = pos[:,1]*scale
axs.plot(G_I.x_soma, G_I.y_soma, 'r.', markersize=.5, alpha=0.5, label='EC-Inh')
'''
parse_coords(fname='positions/EC_inh.txt', NG=G_I)

# Plot X,Y,Z
#ax_anat.plot_trisurf(G_E.x_soma, G_E.y_soma, G_E.z_soma, color='white', edgecolors='grey', alpha=0.5)
ax_anat.scatter(G_I.x_soma, G_I.y_soma, G_I.z_soma, c='red')

G_all[0][0].append(G_E)
G_all[0][1].append(G_I)
print('EC: done')


# DG
G_E = NeuronGroup(N=settings.N_DG[0],
    model=py_eqs,
    threshold='v>V_th',
    reset=reset_eqs,
    refractory=refractory_time,
    method=integ_method,
    name='DG_py')
G_E.size = cell_size_py
G_E.glu = 1
'''
pos = np.load('./neuron_positions/full/DG_E-stipple-10000.npy')
G_E.x_soma = pos[:,0]*scale
G_E.y_soma = pos[:,1]*scale
axs.plot(G_E.x_soma, G_E.y_soma, 'g.', markersize=.5, alpha=0.5, label='DG-Py')
'''
parse_coords(fname='positions/DG_exc.txt', NG=G_E)

# Plot X,Y,Z
#ax_anat.plot_trisurf(G_E.x_soma, G_E.y_soma, G_E.z_soma, color='white', edgecolors='grey', alpha=0.5)
ax_anat.scatter(G_E.x_soma, G_E.y_soma, G_E.z_soma, c='green')

G_I = NeuronGroup(N=settings.N_DG[1],
    model=inh_eqs,
    threshold='v>V_th',
    refractory=refractory_time,
    method=integ_method,
    name='DG_inh')
G_I.size = cell_size_inh
'''
pos = np.load('./neuron_positions/full/DG_I-stipple-100.npy')
G_I.x_soma = pos[:,0]*scale
G_I.y_soma = pos[:,1]*scale
axs.plot(G_I.x_soma, G_I.y_soma, 'r.', markersize=.5, alpha=0.5, label='DG-Inh')
'''
parse_coords(fname='positions/DG_inh.txt', NG=G_I)

# Plot X,Y,Z
#ax_anat.plot_trisurf(G_E.x_soma, G_E.y_soma, G_E.z_soma, color='white', edgecolors='grey', alpha=0.5)
ax_anat.scatter(G_I.x_soma, G_I.y_soma, G_I.z_soma, c='red')

G_all[1][0].append(G_E)
G_all[1][1].append(G_I)
print('DG: done')


# CA3
G_E = NeuronGroup(N=settings.N_CA3[0],
    model=py_CAN_eqs,
    threshold='v>V_th',
    reset=reset_eqs,
    refractory=refractory_time,
    method=integ_method,
    name='CA3_pyCAN')
G_E.size = cell_size_py
G_E.glu = 1
'''
pos = np.load('./neuron_positions/full/CA3_E-stipple-1000.npy')
G_E.x_soma = pos[:,0]*scale
G_E.y_soma = pos[:,1]*scale
axs.plot(G_E.x_soma, G_E.y_soma, 'b.', markersize=.5, alpha=0.5, label='CA3-PyCAN')
'''
parse_coords(fname='positions/CA3_exc.txt', NG=G_E)

# Plot X,Y,Z
#ax_anat.plot_trisurf(G_E.x_soma, G_E.y_soma, G_E.z_soma, color='white', edgecolors='grey', alpha=0.5)
ax_anat.scatter(G_E.x_soma, G_E.y_soma, G_E.z_soma, c='blue')

G_I = NeuronGroup(N=settings.N_CA3[1],
    model=inh_eqs,
    threshold='v>V_th',
    refractory=refractory_time,
    method=integ_method,
    name='CA3_inh')
G_I.size = cell_size_inh
'''
pos = np.load('./neuron_positions/full/CA3_I-stipple-100.npy')
G_I.x_soma = pos[:,0]*scale
G_I.y_soma = pos[:,1]*scale
axs.plot(G_I.x_soma, G_I.y_soma, 'r.', markersize=.5, alpha=0.5, label='CA3-Inh')
'''
parse_coords(fname='positions/CA3_inh.txt', NG=G_I)

# Plot X,Y,Z
#ax_anat.plot_trisurf(G_E.x_soma, G_E.y_soma, G_E.z_soma, color='white', edgecolors='grey', alpha=0.5)
ax_anat.scatter(G_I.x_soma, G_I.y_soma, G_I.z_soma, c='red')

G_all[2][0].append(G_E)
G_all[2][1].append(G_I)
print('CA3: done')


# CA1
G_E = NeuronGroup(N=settings.N_CA1[0],
    model=py_CAN_eqs,
    threshold='v>V_th',
    reset=reset_eqs,
    refractory=refractory_time,
    method=integ_method,
    name='CA1_pyCAN')
G_E.size = cell_size_py
G_E.glu = 1
'''
pos = np.load('./neuron_positions/full/CA1_E-stipple-10000.npy')
G_E.x_soma = pos[:,0]*scale
G_E.y_soma = pos[:,1]*scale
axs.plot(G_E.x_soma, G_E.y_soma, 'b.', markersize=.5, alpha=0.5, label='CA1-PyCAN')
'''
parse_coords(fname='positions/CA1_exc.txt', NG=G_E)

# Plot X,Y,Z
#ax_anat.plot_trisurf(G_E.x_soma, G_E.y_soma, G_E.z_soma, color='white', edgecolors='grey', alpha=0.5)
ax_anat.scatter(G_E.x_soma, G_E.y_soma, G_E.z_soma, c='blue')

G_I = NeuronGroup(N=settings.N_CA1[1],
    model=inh_eqs,
    threshold='v>V_th',
    refractory=refractory_time,
    method=integ_method,
    name='CA1_inh')
G_I.size = cell_size_inh
'''
pos = np.load('./neuron_positions/full/CA1_I-stipple-1000.npy')
G_I.x_soma = pos[:,0]*scale
G_I.y_soma = pos[:,1]*scale
axs.plot(G_I.x_soma, G_I.y_soma, 'r.', markersize=.5, alpha=0.5, label='CA1-Inh')
'''
parse_coords(fname='positions/CA1_inh.txt', NG=G_I)

# Plot X,Y,Z
#ax_anat.plot_trisurf(G_E.x_soma, G_E.y_soma, G_E.z_soma, color='white', edgecolors='grey', alpha=0.5)
ax_anat.scatter(G_I.x_soma, G_I.y_soma, G_I.z_soma, c='red')

G_all[3][0].append(G_E)
G_all[3][1].append(G_I)
print('CA1: done')

G_flat = make_flat(G_all)

# initialize the groups, set initial conditions
for ngroup in G_flat:
    ngroup.v = '-60.*mvolt-rand()*10*mvolt' # str -> individual init. val. per neuron
    #ngroup.v = -60.*mV

    # EC populations get stimulated
    if ngroup.name=='EC_pyCAN' or ngroup.name=='EC_inh':
        ngroup.r = 1 # 1 means on
    else:
        ngroup.r = 0 # int -> same init. val. for all neurons



# Make the synapses
# -------------------------------------------------------------#
print('\n >  Making the synapses...')

# gains
gains_all =  [[1./G, 1.], [G, G], [1./G, 1.], [1., G]]

# intra
print('     * intra-region')

syn_EC_all = setup.connect_intra(G_all[0][0], G_all[0][1], settings.p_EC_all, gains_all[0])
print('EC-to-EC: done')
syn_DG_all = setup.connect_intra(G_all[1][0], G_all[1][1], settings.p_DG_all, gains_all[1])
print('DG-to-DG: done')
syn_CA3_all = setup.connect_intra(G_all[2][0], G_all[2][1], settings.p_CA3_all, gains_all[2])
print('CA3-to-CA3: done')
syn_CA1_all = setup.connect_intra(G_all[3][0], G_all[3][1], settings.p_CA1_all, gains_all[3])
print('CA1-to-CA1: done')
syn_intra_all = [syn_EC_all, syn_DG_all, syn_CA3_all, syn_CA1_all]

# inter
print('     * inter-region')

# p_inter_all = [[[[],[]],[[],[]]],[[[],[]],[[],[]]],[[[],[]],[[],[]]],[[[],[]],[[],[]]]]
p_inter_all = [[[[0,0] for ii in range(2)] for jj in range(4)] for kk in range(4)]
p_inter_all[0][1][0] = [settings.p_tri for ii in range(2)] # EC_E to DG_E | DG_I
p_inter_all[0][2][0] = [settings.p_mono for ii in range(2)] # EC_E to CA3_E | CA3_I
p_inter_all[0][3][0] = [settings.p_mono for ii in range(2)] # EC_E to CA1_E | CA1_I
p_inter_all[1][2][0] = [settings.p_tri for ii in range(2)] # DG_E to CA3_E | CA3_I
p_inter_all[2][3][0] = [settings.p_tri for ii in range(2)] # CA3_E to CA1_E | CA1_I
p_inter_all[3][0][0] = [settings.p_tri for ii in range(2)] # CA1_E to EC_E | EC_I

syn_EC_DG_all = setup.connect_inter(G_all[0][0], G_all[1][0], G_all[1][1], p_inter_all[0][1], gains_all[0])
syn_EC_CA3_all = setup.connect_inter(G_all[0][0], G_all[2][0], G_all[2][1], p_inter_all[0][2], gains_all[0])
syn_EC_CA1_all = setup.connect_inter(G_all[0][0], G_all[3][0], G_all[3][1], p_inter_all[0][3], gains_all[0])
print('EC-to-all: done')

syn_DG_CA3_all = setup.connect_inter(G_all[1][0], G_all[2][0], G_all[2][1], p_inter_all[1][2], gains_all[1])
print('DG-to-CA3: done')

syn_CA3_CA1_all = setup.connect_inter(G_all[2][0], G_all[3][0], G_all[3][1], p_inter_all[2][3], gains_all[2])
print('CA3-to-CA1: done')

syn_CA1_EC_all = setup.connect_inter(G_all[3][0], G_all[0][0], G_all[0][1], p_inter_all[3][0], gains_all[3])
print('CA1-to-EC: done')
syn_inter_all = [syn_EC_DG_all, syn_EC_CA3_all, syn_EC_CA1_all, syn_DG_CA3_all, syn_CA3_CA1_all, syn_CA1_EC_all]



# Add the monitors (spikes/rates)
# -------------------------------------------------------------#
print('\n >  Monitors...')
state_mon_all = []
spike_mon_all = []
rate_mon_all = []

state_mon_E_all = [[StateMonitor(G_py, ['v', 'm', 'n', 'h'], record=True) for G_py in G_all[i][0] if G_py] for i in range(4)]
state_mon_I_all = [[StateMonitor(G_inh, ['v', 'm', 'n', 'h'], record=True) for G_inh in G_all[i][1] if G_inh] for i in range(4)]
print('State monitors [v]: done')

spike_mon_E_all = [[SpikeMonitor(G_py) for G_py in G_all[i][0] if G_py] for i in range(4)]
spike_mon_I_all = [[SpikeMonitor(G_inh) for G_inh in G_all[i][1] if G_inh] for i in range(4)]
print('Spike monitors: done')

rate_mon_E_all = [[PopulationRateMonitor(G_py) for G_py in G_all[i][0] if G_py] for i in range(4)]
rate_mon_I_all = [[PopulationRateMonitor(G_inh) for G_inh in G_all[i][1] if G_inh] for i in range(4)]
print('Rate monitors: done')



# Stimulation and other inputs
# -------------------------------------------------------------#
print('\n >  Inputs and Stimulation...')
tv = linspace(0, settings.duration/second, int(settings.duration/(settings.dt_stim))+1)
xstim = settings.I_stim * logical_and(tv>settings.t_stim/second, tv<settings.t_stim/second+0.01)
inputs_stim = TimedArray(xstim, dt=settings.dt_stim)

inp_theta_sin = 1*sin(2*pi*4*tv)
inp_theta = TimedArray(inp_theta_sin*nA, dt=settings.dt_stim) # external theta (TESTING)



# Kuramoto Oscillators (MS)
# -------------------------------------------------------------#
print('\n >  Kuramoto Oscillators...')

# Make the necessary groups
f0 = settings.f0 # settings.f0 does not work inside equations
sigma = settings.sigma
G_K = NeuronGroup(settings.N_Kur,
    model=kuramoto_eqs_stim,
    threshold='True',
    method='euler',
    name='Kuramoto_oscillators_N_%d' % settings.N_Kur)
G_K.Theta = '2*pi*rand()' # uniform U~[0,2π]
G_K.omega = '2*pi*(f0+sigma*randn())' # normal N~(f0,σ)
G_K.kN = settings.kN_frac
G_K.kG = settings.k_gain
G_flat.append(G_K) # append to the group list!
print('Group: done')

syn_kuramoto =  Synapses(G_K, G_K, on_pre=syn_kuramoto_eqs, method='euler', name='Kuramoto_intra')
syn_kuramoto.connect(condition='i!=j')
print('Synapses: done')

# Kuramoto order parameter group
G_pop_avg = NeuronGroup(1, pop_avg_eqs)
r0 = 1/settings.N_Kur * sum(exp(1j*G_K.Theta))
G_pop_avg.x = real(r0)  # avoid division by zero
G_pop_avg.y = imag(r0)
G_flat.append(G_pop_avg) # append to the group list!
syn_avg = Synapses(G_K, G_pop_avg, syn_avg_eqs, name='Kuramoto_avg')
syn_avg.connect()
print('Order parameter group: done')



# Firing Rate Filter Population
# -------------------------------------------------------------#
# Make the spikes-to-rates group
print('\n >  Spikes-to-Rates Filter...')

G_S2R = NeuronGroup(1,
    model=firing_rate_filter_eqs,
    method='exact',
    namespace=filter_params)
G_S2R.Y = 0 # initial conditions
G_flat.append(G_S2R) # append to the group list!
print('Group: done')



# Connections
# -------------------------------------------------------------#
print('\n >  Connections...')

# CA1 spikes-to-rates synapses
# find the CA1-E group
G_CA1_E = None
for g in G_flat:
    if g.name=='CA1_pyCAN':
        G_CA1_E = g
        break

# connect the CA1-E group to the low-pass-filter spikes-2-rates (S2R) group
if G_CA1_E:
    syn_CA1_2_rates = Synapses(G_CA1_E, G_S2R, on_pre='Y_post += (1/tauFR)', namespace=filter_params)
    syn_CA1_2_rates.connect()
print('CA1-to-S2R: done')


# connect the S2R group to the Kuramoto by linking input X to firing rates (drive)
G_K.X = linked_var(G_S2R, 'drive')
print('Linking S2R to Kuramoto oscillators: done')

# connect the Kuramoto ensemble rhythm to the I_exc variable in EC_E and EC_I (Kuramoto output as input to EC_E/I pop.)
'''for g in G_flat:
    if g.name=='EC_pyCAN' or g.name=='EC_inh':
        print('>> Setting input rhythm for group ', g.name)
        g.I_exc = linked_var(G_pop_avg, 'rhythm_rect')
'''
# avoid linking when using a fixed theta input sin : TESTING
#G_flat[0].I_exc = linked_var(G_pop_avg, 'rhythm_zero')
#G_flat[1].I_exc = linked_var(G_pop_avg, 'rhythm_zero')
G_flat[0].I_exc = linked_var(G_pop_avg, 'rhythm_rect')
G_flat[1].I_exc = linked_var(G_pop_avg, 'rhythm_rect')



# Monitors
# -------------------------------------------------------------#
# Kuramoto monitors
print('\n >  Kuramoto and Filter Monitors...')

kuramoto_mon = StateMonitor(G_K, ['Theta'], record=True)
order_param_mon = StateMonitor(G_pop_avg, ['coherence', 'phase', 'rhythm', 'rhythm_rect'], record=True)
print('State monitor [Theta]: done')

# spikes2rates monitor (vout)
s2r_mon = StateMonitor(G_S2R, ['drive'], record=True)
print('State monitor [drive]: done')

'''
G_CA1_E, G_CA1_I = None, None
for g in G_flat:
    if g.name=='CA1_pyCAN':
        G_CA1_E = g
    if g.name=='CA1_inh':
        G_CA1_I = g
    if G_CA1_E and G_CA1_I:
        break

mon_tmp_E = StateMonitor(G_CA1_E, [], record=True)
mon_tmp_I = StateMonitor(G_CA1_I, [], record=True)
'''



# Create the Network
# -------------------------------------------------------------#
print('\n >  Connecting the network...')
net = Network()
net.add(G_all) # add groups
net.add(G_K)
net.add(G_pop_avg)
net.add(G_S2R)

for syn_intra_curr in make_flat(syn_intra_all): # add synapses (intra)
    if syn_intra_curr!=0:
        net.add(syn_intra_curr)

for syn_inter_curr in make_flat(syn_inter_all): # add synapses (inter)
    if syn_inter_curr!=0:
        net.add(syn_inter_curr)

net.add(syn_kuramoto) # kuramoto intra-synapses
net.add(syn_avg) # kuramoto population average (order parameter) synapses
net.add(syn_CA1_2_rates) # CA1 spikes2rates

net.add(state_mon_E_all) # monitors
net.add(state_mon_I_all)
net.add(spike_mon_E_all)
net.add(spike_mon_I_all)
net.add(rate_mon_E_all)
net.add(rate_mon_I_all)
net.add(kuramoto_mon)
net.add(order_param_mon)
net.add(s2r_mon)
print('Network connections: done')



# Run the simulation
# -------------------------------------------------------------#
#defaultclock.dt = 0.01*ms
tstep = defaultclock.dt

print('\n >  Starting simulation...')
start = time.time()
net.run(settings.duration, report='text', report_period=10*second, profile=True)
end = time.time()
print('Simulation ended')
print('Simulation ran for '+str((end-start)/60)+' minutes')

print(profiling_summary(net=net, show=4)) # show the top 10 objects that took the longest



# Plot the results
# -------------------------------------------------------------#
# raster plot of all regions
raster_fig, raster_axs = plot_raster_all(spike_mon_E_all, spike_mon_I_all)
print("Saving figure 'figures/Raster_stim_EC_I_stim_%d_nA_tstim_%d_ms.png'" % (settings.I_stim/namp, settings.t_stim/ms))
raster_fig.savefig('figures/Raster_stim_EC_I_stim_%d_nA_tstim_%d_ms.png' % (settings.I_stim/namp, settings.t_stim/ms))

'''
# calculate order parameter in the end
samples = len(kuramoto_mon.Theta[0])
r = np.zeros(samples, dtype='complex')
for s in range(samples):
    r[s] = 1/N_Kur * sum(exp(1j*kuramoto_mon.Theta[:,s])) # order parameter r(t)
'''

# kuramoto order parameter plots
kuramoto_fig, kuramoto_axs = plot_kuramoto(order_param_mon)
print("Saving figure 'figures/Kuramoto_rhythms_stim_EC_I_stim_%d_nA_tstim_%d_ms.png'" % (settings.I_stim/namp, settings.t_stim/ms))
kuramoto_fig.savefig('figures/Kuramoto_rhythms_stim_EC_I_stim_%d_nA_tstim_%d_ms.png' % (settings.I_stim/namp, settings.t_stim/ms))


# Plot more stuff
fig_extra, raster_extra = plot_network_output(spike_mon_E_all[-1][0], spike_mon_I_all[-1][0], s2r_mon, order_param_mon, tv, xstim)
print("Saving figure 'figures/Kuramoto_extra_stim_EC_I_stim_%d_nA_tstim_%d_ms.png'" % (settings.I_stim/namp, settings.t_stim/ms))
fig_extra.savefig('figures/Kuramoto_extra_stim_EC_I_stim_%d_nA_tstim_%d_ms.png' % (settings.I_stim/namp, settings.t_stim/ms))


tight_layout()
show()
