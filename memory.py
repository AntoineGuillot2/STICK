
from neurons_and_synapses import *
import copy


def generate_memory_synapses(G,idx_start=0,name=''):
    synapses_list = []
    neurons_idx = {'input': 0, 'first': 1, 'last': 2, 'acc': 3, 'acc2': 4, 'ready': 5, 'recall': 6, 'output': 7}
    for _key in neurons_idx:
        neurons_idx[_key] +=idx_start
    #Transmission of the input spike
    synapses_list += [v_synapse(G,G,neurons_idx['input'],neurons_idx['first'],weight=w_e)]
    synapses_list += [v_synapse(G, G, neurons_idx['input'], neurons_idx['last'], weight=w_e*0.5)]

    #inhibition
    synapses_list += [ v_synapse(G,G,neurons_idx['first'],neurons_idx['first'],weight=-w_e)]

    #accumulation
    synapses_list += [ g_e_synapse(G,G,neurons_idx['first'],neurons_idx['acc'],w_acc)]

    #accumulation_2
    synapses_list += [ g_e_synapse(G, G, neurons_idx['last'], neurons_idx['acc2'], w_acc)]

    #stop accumulation
    synapses_list += [g_e_synapse(G, G, neurons_idx['acc'], neurons_idx['acc2'], -w_acc)]
    # value is ready
    synapses_list += [v_synapse(G, G, neurons_idx['acc'], neurons_idx['ready'], w_e)]

    #empty accumulator
    synapses_list += [ g_e_synapse(G, G, neurons_idx['recall'], neurons_idx['acc2'], w_acc)]

    #1st output spike
    synapses_list += [ v_synapse(G, G, neurons_idx['recall'], neurons_idx['output'], w_e)]

    #2nd output spike
    synapses_list += [ v_synapse(G, G, neurons_idx['acc2'], neurons_idx['output'], w_e)]


    nodes_names = {}
    for _key in neurons_idx:
        nodes_names[_key+name] = neurons_idx[_key]


    return synapses_list,nodes_names


def generate_persistant_memory_synapses(G,idx_start=0,name=''):
    synapses_list = []
    synapses_list_tp, neurons_idx = generate_memory_synapses(G,idx_start=idx_start)
    synapses_list += synapses_list_tp

    synapses_list += [v_synapse(G,G,neurons_idx['output'],neurons_idx['first'],w_e)]
    synapses_list += [v_synapse(G, G, neurons_idx['output'], neurons_idx['last'], w_e/2)]
    synapses_list += [v_synapse(G, G, neurons_idx['input'], neurons_idx['acc2'], w_e)]
    synapses_list += [v_synapse(G, G, neurons_idx['input'], neurons_idx['output'], -w_e)]

    nodes_names = {}
    for _key in neurons_idx:
        nodes_names[_key+name] = neurons_idx[_key]

    return synapses_list,nodes_names


if __name__ == '__main__':
    G = neurons(8)
    synapses_list, _ = generate_persistant_memory_synapses(G)
    indices = array([0, 0, 0,0])
    times = array([0,15,500,510]) * ms
    inp = SpikeGeneratorGroup(1, indices, times)
    s = v_synapse(inp, G, i=0, j=0, weight=w_e, delay=0)

    recall = SpikeGeneratorGroup(1, [0,0], [250*ms,900*ms])
    s_recall = v_synapse(recall, G, i=0, j=6, weight=w_e, delay=0)

    M = StateMonitor(G, 'v', record=True)
    S_monitor = SpikeMonitor(G,'v',record=True)
    print('building model')
    net_1 = Network(G,inp,s,*synapses_list,M,recall,s_recall,S_monitor)
    print('starting computation')
    net_1.run(1000*ms)
    print('computation end')

    plot(M.t / ms, M.v[7], 'C0', label='Brian_2')
    S_monitor.all_values()['t'][7]/ms
