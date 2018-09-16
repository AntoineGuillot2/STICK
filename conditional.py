###Exemple of conditional structures with the STICK paradigm


from neurons_and_synapses import *
from memory import *




def generate_modulator_synapse(G,mod = 5,idx_start=0,name=''):
    """
    Synapse to create a network which only returns spike which are emitted at a time which is a multiple of mod
    :param G:
    :param neurons_index:
    :param mod:
    :return:
    """
    synapses_list = []
    neurons_index = {'input': 0, 'modulator': 1, 'synchronize': 2, 'output': 3}
    for _key in neurons_index:
        neurons_index[_key] +=idx_start


    synapses_list += [v_synapse(G,G,neurons_index['input'],neurons_index['synchronize'],w_e/2)]
    synapses_list += [v_synapse(G, G, neurons_index['input'], neurons_index['synchronize'], - w_e / 2,delay=2*T_syn)]

    synapses_list += [v_synapse(G, G, neurons_index['modulator'], neurons_index['synchronize'], w_e/2)]
    synapses_list += [v_synapse(G, G, neurons_index['modulator'], neurons_index['synchronize'], - w_e / 2, delay=2 * T_syn)]
    synapses_list += [v_synapse(G, G, neurons_index['synchronize'], neurons_index['synchronize'], w_e)]

    synapses_list += [v_synapse(G, G, neurons_index['modulator'], neurons_index['modulator'], w_e, delay= mod*T_syn - 0.1*ms)]

    synapses_list += [v_synapse(G, G, neurons_index['synchronize'], neurons_index['output'], w_e)]

    nodes_names = {}
    for _key in neurons_index:
        nodes_names[_key+name] = neurons_index[_key]

    return synapses_list,nodes_names



def generate_maximum_synapse(G,idx_start=0,name=''):
    synapses_list = []
    neurons_index = {'input_1': 0, 'input_2': 1, "larger_1": 2, "larger_2": 3, "output": 4}
    for _key in neurons_index:
        neurons_index[_key] +=idx_start

    synapses_list += [v_synapse(G,G,neurons_index['input_1'],neurons_index['output'],w_e/2)]
    synapses_list += [v_synapse(G, G, neurons_index['input_2'], neurons_index['output'], w_e / 2)]

    synapses_list += [v_synapse(G, G, neurons_index['input_1'], neurons_index['larger_2'], w_e / 2)]
    synapses_list += [v_synapse(G, G, neurons_index['input_2'], neurons_index['larger_1'], w_e / 2)]

    synapses_list += [v_synapse(G, G, neurons_index['larger_1'], neurons_index['larger_2'], - w_e )]
    synapses_list += [v_synapse(G, G, neurons_index['larger_2'], neurons_index['larger_1'], - w_e )]
    nodes_names = {}
    for _key in neurons_index:
        nodes_names[_key+name] = neurons_index[_key]


    return synapses_list,nodes_names


def generate_programable_maximum_synapse(G,idx_start=0,name=''):
    synapses_list = []
    synapses_list_memory, memory_nodes = generate_persistant_memory_synapses(G,idx_start,name='_memory')
    synapses_list_maximum, maximum_nodes = generate_maximum_synapse(G,idx_start+len(memory_nodes),name='_maximum')
    neurons_index = {'input':len(memory_nodes)+len(maximum_nodes) + idx_start}
    neurons_index.update(memory_nodes)
    neurons_index.update(maximum_nodes)


    synapses_list += synapses_list_memory
    synapses_list += synapses_list_maximum
    synapses_list += [v_synapse(G,G,neurons_index['input'],neurons_index['input_2_maximum'],weight=w_e,delay=3*T_syn)]
    synapses_list += [v_synapse(G, G, neurons_index['input'], neurons_index['recall_memory'],weight=w_e)]
    synapses_list += [v_synapse(G, G, neurons_index['recall_memory'], neurons_index['recall_memory'], weight=- w_e)]
    synapses_list += [v_synapse(G, G, neurons_index['output_memory'], neurons_index['input_1_maximum'],weight=w_e)]
    nodes_names = {}
    for _key in neurons_index:
        nodes_names[_key+name] = neurons_index[_key]

    return synapses_list,nodes_names


def generate_list_maximum_synapse(G,idx_start=0,name=''):
    synapses_list = []
    synapses_list_maximum, nodes_maximum = generate_programable_maximum_synapse(G,idx_start)
    synapses_list += synapses_list_maximum
    synapses_list += [v_synapse(G,G,nodes_maximum['output_maximum'],nodes_maximum['input_memory'],weight=w_e)]

    nodes_names = {}
    for _key in nodes_maximum:
        nodes_names[_key+name] = nodes_maximum[_key]

    return synapses_list,nodes_names



if __name__ =='__main__':

    ###Check if modulator is working
    G = neurons(4)
    synapses_list,_ = generate_modulator_synapse(G)

    init = SpikeGeneratorGroup(1, [0],[0*ms])
    s_init = v_synapse(init,G,0,1,w_e)

    spikes = SpikeGeneratorGroup(1,[0]*10, [5,10,25,36,49,60,80,101,110,500]*ms)
    s_spikes = v_synapse(spikes,G,0,0,w_e)
    M = StateMonitor(G, 'v', record=True)
    crossings = SpikeMonitor(G, variables='v', name='crossings')
    net = Network(G,init,s_init,spikes,s_spikes,M ,crossings,*synapses_list)
    net.run(1000*ms)
    print(crossings)
    all_values = crossings.all_values()
    print(all_values['t'][2] -2.2 * ms)
    plot(M.t/ms, M.v[2], 'C0', label='Brian')

    # Check if maximum is working
    G = neurons(5)
    spikes = SpikeGeneratorGroup(2, [0, 0, 1, 1], [0, 30, 0, 50] * ms)
    s_input_1 = v_synapse(spikes, G, 0, 0, w_e)
    s_input_2 = v_synapse(spikes, G, 1, 1, w_e)
    synapses_list,_ = generate_maximum_synapse(G)
    crossings = SpikeMonitor(G, variables='v', name='crossings')
    net = Network(G, spikes, s_input_1, s_input_2, crossings, *synapses_list)
    net.run(100 * ms)

    ## Check if programmable maximum is working
    G = neurons(14)
    synapses_list, nodes = generate_programable_maximum_synapse(G)

    write_memory_spike = SpikeGeneratorGroup(1, [0] * 4, [0, 30, 1000, 1050] * ms)
    write_memory_synapse = v_synapse(write_memory_spike, G, 0, 0, w_e)

    input_spikes = SpikeGeneratorGroup(1, [0] * 8, [250, 275, 600, 700, 1300, 1375, 1500, 1510] * ms)
    s_spikes = v_synapse(input_spikes, G, 0, 13, w_e)
    M = StateMonitor(G, 'v', record=True)
    crossings = SpikeMonitor(G, variables='v', name='crossings')
    net = Network(G, write_memory_spike, write_memory_synapse, input_spikes, s_spikes, M, crossings, *synapses_list)
    net.run(2000 * ms)
    print(crossings)
    all_values = crossings.all_values()
    np.diff(np.sort(all_values['t'][12]))

    ##List maximum test, Not working ....
    G = neurons(14)
    synapses_list, nodes = generate_list_maximum_synapse(G)

    spikes = [500, 520, 1100, 1105, 1550, 1601, 1800, 1880, 2200, 2250] * ms

    write_memory_spike = SpikeGeneratorGroup(1, [0] * 2, [0, 10] * ms)
    write_memory_synapse = v_synapse(write_memory_spike, G, 0, 0, w_e)

    input_spikes = SpikeGeneratorGroup(1, [0] * len(spikes), spikes)
    s_spikes = v_synapse(input_spikes, G, 0, 13, w_e)
    M = StateMonitor(G, 'v', record=True)
    crossings = SpikeMonitor(G, variables='v', name='crossings')
    net = Network(G, input_spikes, s_spikes, M, crossings, *synapses_list, write_memory_spike, write_memory_synapse)
    net.run(3000 * ms)
    print(crossings)
    all_values = crossings.all_values()
    np.diff(np.sort(all_values['t'][7]))
    plot(M.t / ms, M.v[4])