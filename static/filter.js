// Filter.js
const purposes = ['capture', 'preview'];
const directions = ['src', 'dst'];
const filterGoals = ['exclude', 'include'];

class Filter {
    static constructEndpointFilter(purpose, proto = null, addr = null, port = null, filterGoal = 'exclude') {
        // TODO: maybe we can come up with better naming?
        if (!purposes.includes(purpose)) {
            throw new Error(`Invalid purpose: ${purpose}\nChoose one of ${purposes.join(', ')}`);
        }

        if (!filterGoals.includes(filterGoal)) {
            throw new Error(`Invalid filterGoal: ${filterGoal}\nChoose one of ${filterGoals.join(', ')}`);
        }

        const inclusionPrefix = filterGoal === 'exclude' ? 'not ' : '';

        let packetEnvelope;

        if (purpose === 'capture') {
            packetEnvelope = directions.map(direction => `(${direction} ${
                addr && addr.split('/').length === 1 ? 'host' : 'net'
            } ${addr} and ${proto} ${direction} port ${port})`);
        } else if (purpose === 'preview') {
            packetEnvelope = directions.map(direction => `(ip.${direction} == ${addr} and ${proto}.${direction}port == ${port})`);
        }

        const expression = `${inclusionPrefix}(${packetEnvelope.join(' or ')})`;
        return expression;
    }

    static tcpdumpEndpointFilter(kwargs) {
        return Filter.constructEndpointFilter('capture', kwargs);
    }

    static wiresharkEndpointFilter(kwargs) {
        return Filter.constructEndpointFilter('preview', kwargs);
    }
}

// Example usage:
const tcpdumpFilterForAddr = Filter.tcpdumpEndpointFilter({
    proto: 'tcp',
    addr: '192.168.1.1',
    port: 80,
    filterGoal: 'exclude'
});
console.log(tcpdumpFilterForAddr);

const tcpdumpFilterForNet = Filter.tcpdumpEndpointFilter({
    proto: 'tcp',
    addr: '192.168.1.0/24',
    port: 80,
    filterGoal: 'exclude'
});
console.log(tcpdumpFilterForNet);

const wiresharkFilter = Filter.wiresharkEndpointFilter({
    proto: 'udp',
    addr: '10.0.0.1',
    port: 8080,
    filterGoal: 'include'
});
console.log(wiresharkFilter);
