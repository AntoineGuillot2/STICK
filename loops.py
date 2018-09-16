###Exemple of loops with the STICK paradigm

from neurons_and_synapses import *



def generate_synapse_sum(G,idx_start=0,name=''):
    """
    Function to generate the synapses to compute the sum of several spikes
    :param G: Neuron group
    :param neurons_index_sum: dict with the name and index of the different neurons
    :return: a list of synapses
    """
    synapse_list = []
    neurons_index_sum = {'input_1': 0, 'first_1': 1, 'last_1': 2, 'input_2': 3, 'first_2': 4, 'last_2': 5, 'sync': 6,
                         'acc': 7, 'acc2': 8, 'end': 9, 'out': 10}
    for _key in neurons_index_sum:
        neurons_index_sum[_key] +=idx_start

    ##First input first value
    synapse_list += [v_synapse(G,G,neurons_index_sum['input_1'],neurons_index_sum['first_1'],w_e)]
    synapse_list += [v_synapse(G, G, neurons_index_sum['first_1'], neurons_index_sum['first_1'], -w_e)]

    ##Second input first value
    synapse_list += [v_synapse(G, G, neurons_index_sum['input_2'], neurons_index_sum['first_2'], w_e)]
    synapse_list += [v_synapse(G, G, neurons_index_sum['first_2'], neurons_index_sum['first_2'], -w_e)]

    #Last value of the two inputs
    synapse_list += [v_synapse(G,G,neurons_index_sum['input_1'],neurons_index_sum['last_1'],w_e/2)]
    synapse_list += [v_synapse(G, G, neurons_index_sum['input_2'], neurons_index_sum['last_2'], w_e / 2)]

    # Syncronizer
    synapse_list += [v_synapse(G, G, neurons_index_sum['last_1'], neurons_index_sum['sync'], w_e / 2)]
    synapse_list += [v_synapse(G, G, neurons_index_sum['last_2'], neurons_index_sum['sync'], w_e / 2)]


    #accumulator synapse
    synapse_list += [g_e_synapse(G, G, neurons_index_sum['first_1'], neurons_index_sum['acc'], w_acc)]
    synapse_list += [g_e_synapse(G, G, neurons_index_sum['first_2'], neurons_index_sum['acc'], w_acc)]
    synapse_list += [g_e_synapse(G, G, neurons_index_sum['last_1'], neurons_index_sum['acc'], - w_acc)]
    synapse_list += [g_e_synapse(G, G, neurons_index_sum['last_2'], neurons_index_sum['acc'], - w_acc)]

    #compute value
    synapse_list += [g_e_synapse(G, G, neurons_index_sum['sync'], neurons_index_sum['acc'], w_acc)]
    synapse_list += [g_e_synapse(G, G, neurons_index_sum['sync'], neurons_index_sum['acc2'], w_acc)]

    synapse_list += [g_e_synapse(G, G, neurons_index_sum['end'], neurons_index_sum['acc'], w_acc)]
    synapse_list += [g_e_synapse(G, G, neurons_index_sum['end'], neurons_index_sum['acc2'], w_acc)]


    #trigger output
    synapse_list += [v_synapse(G, G, neurons_index_sum['acc2'], neurons_index_sum['out'], w_e)]
    synapse_list += [v_synapse(G, G, neurons_index_sum['acc'], neurons_index_sum['out'], w_e)]

    #summation
    synapse_list += [v_synapse(G,G,neurons_index_sum['out'],neurons_index_sum['input_2'],w_e)]

    nodes_names = {}
    for _key in neurons_index_sum:
        nodes_names[_key+name] = neurons_index_sum[_key]

    return synapse_list



def generate_synapse_count_spike(G,idx_start=0,name=''):
    """
    :param G: Neuron group
    :param index_count: dict with the name and index of the different neurons
    :return: a list of synapses to compute the number of input spikes
    """
    index_count = {'input': 0, 'count': 1, 'end': 2, 'diff': 3, 'out': 4}
    for _key in index_count:
        index_count[_key] +=idx_start


    synapses_list = []
    synapses_list += [v_synapse(G, G, index_count['input'], index_count['count'], w_e/1100)]
    synapses_list += [g_e_synapse(G, G, index_count['end'], index_count['count'], w_acc)]
    synapses_list += [g_e_synapse(G, G, index_count['end'], index_count['diff'], w_acc)]
    synapses_list += [v_synapse(G, G, index_count['count'], index_count['out'], w_e)]
    synapses_list += [v_synapse(G, G, index_count['diff'], index_count['out'], w_e)]

    nodes_names = {}
    for _key in index_count:
        nodes_names[_key+name] = index_count[_key]


    return synapses_list









###test
if __name__ =='__main__':
    ###Test cumulative sums
    G = neurons(11)
    synapses_list = generate_synapse_sum(G)

    synapse_numbers = array([0, 0, 0, 0, 0,0,0,0])
    numbers_to_add = array([10,15,200,207,600,612,500,503]) * ms
    inp = SpikeGeneratorGroup(1, synapse_numbers, numbers_to_add )
    s = v_synapse(inp, G, i=0, j=0, weight=w_e, delay=0)

    synapse_init = array([0])
    init = array([0]) * ms
    init_generator = SpikeGeneratorGroup(1, synapse_init , init)
    s_init = v_synapse(init_generator, G, i=0, j=6, weight=w_e/2, delay=0)

    synapse_init = array([0])
    end = array([800]) * ms
    result_generator = SpikeGeneratorGroup(1, synapse_init , end )
    s_result = v_synapse(result_generator, G, i=0, j=9, weight=w_e)

    M = StateMonitor(G, 'v', record=True)
    print('building model')
    net_1 = Network(G,inp,s,*synapses_list,M,init_generator,s_init,result_generator,s_result)
    print('starting computation')
    net_1.run(1000*ms)
    print('computation end')


    plot(M.t / ms, M.v[7], 'C0', label='Brian_2',c='green')
    plot(M.t / ms, M.v[0], 'C0', label='Brian_2',c='red')
    plot(M.t / ms, M.v[3], 'C0', label='Brian_2',c='blue')
    np.diff(np.where(M.v[10]>0))

    ###Test counter
    G = neurons(5)
    synapses_list = generate_synapse_count_spike(G)
    n = 300
    synapse_numbers = array([0] * n)
    spikes = array(np.random.choice(range(600), n, replace=False)) * ms
    inp = SpikeGeneratorGroup(1, synapse_numbers, spikes)
    s = v_synapse(inp, G, i=0, j=0, weight=w_e, delay=0)

    synapse_init = array([0])
    end = array([800]) * ms
    result_generator = SpikeGeneratorGroup(1, synapse_init, end)
    s_result = v_synapse(result_generator, G, i=0, j=2, weight=w_e)

    M = StateMonitor(G, 'v', record=True)
    print('building model')
    net_1 = Network(G, inp, s, *synapses_list, M, result_generator, s_result)
    print('starting computation')
    net_1.run(1000 * ms)
    print('computation end')

    plot(M.t / ms, M.v[3], 'C0', label='Brian_2', c='red')
    plot(M.t / ms, M.v[4], 'C0', label='Brian_2', c='blue')
    np.diff(np.where(M.v[4] > 0)[0])
