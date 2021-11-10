from brian2 import *

from model import settings
from model.globals import *

def plot_raster_all(spike_mon_E_all, spike_mon_I_all):
    """ Plots the activity of all the excitatory and inhibitory populations in the network in a raster plot.
    Returns a figure handler """

    # raster plot of all regions
    fig, axs = subplots(len(areas),2) # from globals.py
    fig.set_figheight(16)
    fig.set_figwidth(12)

    for ii in range(4):
        axs[ii][0].plot(spike_mon_E_all[ii][0].t/msecond, spike_mon_E_all[ii][0].i, '.g', markersize=.5,alpha=0.5)
        axs[ii][0].set_title('raster '+areas[ii]+' exc')
        axs[ii][0].set_xlim(0, settings.duration/msecond)
        axs[ii][0].set_ylim(0, settings.N_all[ii][0])
        axs[ii][0].set_xlabel('Time (ms)')
        axs[ii][0].set_ylabel('Neuron index')

        axs[ii][1].set_title('raster '+areas[ii]+' inh')
        axs[ii][1].plot(spike_mon_I_all[ii][0].t/msecond, spike_mon_I_all[ii][0].i, '.r',
                    markersize=.5,alpha=0.5)
        axs[ii][1].set_xlim(0, settings.duration/msecond)
        axs[ii][1].set_ylim(0, settings.N_all[ii][1])
        axs[ii][1].set_xlabel('Time (ms)')
        axs[ii][1].set_ylabel('Neuron index')

    #print('Raster all duration: ', settings.duration)

    return fig, axs



def plot_kuramoto(order_param_mon):
    """ Plots the average phase and the phase coherence of the ensemble of Kuramoto oscillators. Also plots the generated theta rhythm from the MS. """

    # Kuramoto oscillators plots
    fig, axs = subplots(3,1) # [0] output rhythm, [1] avg. phase, [2] phase coherence
    fig.set_figheight(12)
    fig.set_figwidth(16)
    fig.suptitle("Kuramoto Oscillators")

    #axs[0].plot(kuramoto_mon.t/second, mean(sin(kuramoto_mon.Theta), axis=0), label='Mean theta')
    #axs[0].plot(kuramoto_mon.t/second, imag(r), '--', label='sin(Im(r))')
    axs[0].plot(order_param_mon.t/second, order_param_mon.rhythm_rect[0], '-', label='Generated theta rhythm')
    axs[1].plot(order_param_mon.t/second, order_param_mon.phase[0], '-', label='Avg. phase')
    axs[2].plot(order_param_mon.t/second, order_param_mon.coherence[0], '-', label='Coherence (|r|)')

    axs[0].set_ylabel("Ensemble Theta Rhythm")
    axs[1].set_ylabel("Average Phase")
    axs[2].set_ylabel("Phase Coherence")
    axs[2].set_xlabel("Time [s]")
    #axs[0].set_ylim([-1,1])
    axs[1].set_ylim([-pi,pi])
    axs[2].set_ylim([0,1])

    if settings.I_stim:
        axs[0].axvline(x=settings.t_stim/second, ymin=-1, ymax=1, c="red", linewidth=2, zorder=0, clip_on=False)
        axs[1].axvline(x=settings.t_stim/second, ymin=-1, ymax=1, c="red", linewidth=2, zorder=0, clip_on=False)
        axs[2].axvline(x=settings.t_stim/second, ymin=-1, ymax=1, c="red", linewidth=2, zorder=0, clip_on=True)

    # make things pretty
    axs[0].legend()
    axs[0].grid()
    axs[1].legend()
    axs[1].grid()
    axs[2].legend()
    axs[2].grid()

    #print('Kuramoto duration: ', settings.duration)

    return fig, axs



def plot_network_output(spike_mon_E, spike_mon_I, rate_mon, order_param_mon, tv, stim_inp):
    """ Plots the network output (population CA1 E/I) activity along with the Kuramoto oscillators and the stimulation input. """

    fig, axs = subplots(nrows=5, ncols=1)
    fig.set_figheight(12)
    fig.set_figwidth(16)

    axs[0].plot(spike_mon_E.t/msecond, spike_mon_E.i, '.g', markersize=.5,alpha=0.5)
    axs[0].set_title('CA1 Excitatory Neurons')
    axs[0].set_xlim(0, settings.duration/msecond)
    axs[0].set_ylim(0, settings.N_CA1[0])
    axs[0].set_ylabel('Neuron index')

    axs[1].plot(spike_mon_I.t/msecond, spike_mon_I.i, '.r', markersize=.5,alpha=0.5)
    axs[1].set_title('CA1 Inhibitory Neurons')
    axs[1].set_xlim(0, settings.duration/msecond)
    axs[1].set_ylim(0, settings.N_CA1[1])
    axs[1].set_ylabel('Neuron index')

    axs[1].plot(tv*1000, stim_inp)
    axs[1].set_title('Stimulation Input')
    axs[1].set_xlim(0, settings.duration/msecond)
    axs[1].set_ylabel('Current [nA]')
    axs[1].grid()

    axs[2].plot(rate_mon.t/msecond, rate_mon.drive[0], label='LPF Output')
    axs[2].set_title('CA1 Population Firing Rates')
    axs[2].set_ylabel('Rate [Hz]')
    axs[2].set_xlim(0, settings.duration/msecond)
    axs[2].legend()
    axs[2].grid()

    axs[3].plot(order_param_mon.t/msecond, order_param_mon.coherence[0], '-', label='Order Param')
    axs[3].set_title('Kuramoto Oscillators Order Parameter')
    axs[3].set_xlim(0, settings.duration/msecond)
    axs[3].set_ylabel('r')
    axs[3].legend()
    axs[3].grid()

    axs[4].plot(order_param_mon.t/msecond, order_param_mon.rhythm_rect[0]/nA, '-', label='Theta Rhythm (Ensemble)')
    #axs[4].plot(tv, inp_theta_sin, '--', label='Constant Theta')
    axs[4].set_title('Generated Theta Rhythm')
    axs[4].set_xlim(0, settings.duration/msecond)
    axs[4].set_ylabel('MS output (corr)')
    axs[4].set_xlabel('Time (ms)')
    axs[4].legend()
    axs[4].grid()

    if settings.I_stim > 0:
        axs[0].axvline(x=settings.t_stim/msecond, ymin=-1, ymax=1, c="red", linewidth=2, zorder=0, clip_on=False)
        axs[1].axvline(x=settings.t_stim/msecond, ymin=-1, ymax=1, c="red", linewidth=2, zorder=0, clip_on=False)
        axs[2].axvline(x=settings.t_stim/msecond, ymin=-1, ymax=1, c="red", linewidth=2, zorder=0, clip_on=False)
        axs[3].axvline(x=settings.t_stim/msecond, ymin=-1, ymax=1, c="red", linewidth=2, zorder=0, clip_on=False)
        axs[4].axvline(x=settings.t_stim/msecond, ymin=-1, ymax=1, c="red", linewidth=2, zorder=0, clip_on=True)

    return fig, axs