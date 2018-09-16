from brian2 import *



start_scope()

### Global neuron variables

##Transmision time
T_syn = 1*ms
T_neu = 1*us
T_min = 10*ms
T_cod = 100*ms
T_max = T_min + T_cod

## Voltage to spike
v_t = 10.

## Neurone time constants
tau_m = 100 * second
tau_f = 20 * ms

## Reset values
gate = 0
g_e_reset = 0.
v_reset = 0.
g_f_reset = 0.
gate_reset = 0.

##common synapse weights:
w_acc = v_t*tau_m/(T_min+T_cod)
w_acc_bar = v_t*tau_m/(T_cod)
w_e = v_t
w_i = - v_t


def neurons(N=1):
    eqs = '''
        dg_e/dt = 0 * hertz :1 (unless refractory)
        dg_f/dt = - (g_f/tau_f) :1 (unless refractory)
        dv/dt = ( g_e + gate*g_f)/tau_m :1 (unless refractory)
        '''

    reset = '''
        v = v_reset
        g_e = g_e_reset
        g_f = g_f_reset
        gate = gate_reset
        '''

    return NeuronGroup(N, eqs, threshold='v>=v_t', reset=reset, refractory=T_neu,method='euler')

def g_e_synapse(G_in,G_out,i,j,weight,delay=T_syn):
    S = Synapses(G_in,G_out, 'w : 1', on_pre='g_e_post += w')
    S.connect(i=i, j=j)
    S.w = weight
    S.delay = delay
    return S

def v_synapse(G_in,G_out,i,j,weight,delay=T_syn):
    S = Synapses(G_in,G_out, 'w : 1', on_pre='v_post += w')
    S.connect(i=i, j=j)
    S.w = weight
    S.delay = delay
    return S

def g_f_synapse(G_in,G_out,i,j,weight,delay=T_syn):
    S = Synapses(G_in,G_out, 'w : 1', on_pre='g_f_post += w')
    S.connect(i=i, j=j)
    S.w = weight
    S.delay = delay
    return S

def gate_synapse(G_in,G_out,i,j,weight,delay=T_syn):
    if weight == 1 :
        S = Synapses(G_in,G_out, 'w : 1', on_pre='gate_post = 1.')
    elif weight == -1:
        S = Synapses(G_in,G_out, 'w : 1', on_pre='gate_post = 0.')
    else:
        raise ValueError
    S.connect(i=i, j=j)
    S.delay = delay
    return S


### Some basic test

if __name__ == '__main__':
    indices = array([0, 0])
    times = array([1, 8])*ms
    inp = SpikeGeneratorGroup(1, indices, times)
    G = neurons(1)
    synapse_1 = v_synapse(inp,G,i = 0, j = 0,weight=v_t,delay=T_syn)
    synapse_2 = v_synapse(inp,G,i=0,j=0,weight=v_t,delay=5*T_syn)
    M = StateMonitor(G, 'v', record=True)
    run(50*ms)
    plot(M.t/ms, M.v[0], 'C0', label='Brian')