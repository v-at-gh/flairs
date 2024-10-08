// PcapFilter.js
const purposes = ['capture', 'display'];
const directions = ['src', 'dst'];
const filterGoals = ['exclude', 'include'];

class PcapFilter {
    static constructEndpointFilter({purpose, proto, addr, port, filterGoal = 'exclude'}) {
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
            packetEnvelope = directions.map(direction => {
                const hostOrNet = addr ? (addr.split('/').length === 1 ? 'host' : 'net') : 'any';
                const addrPart = addr ? `${hostOrNet} ${addr}` : 'any';
                const portPart = port ? `and ${proto} ${direction} port ${port}` : '';
                return `(${direction} ${addrPart} ${portPart})`;
            });
        } else if (purpose === 'display') {
            packetEnvelope = directions.map(direction => {
                const addrPart = addr ? `ip.${direction} == ${addr}` : 'ip.any == any';
                const portPart = port ? `and ${proto}.${direction}port == ${port}` : '';
                return `(${addrPart} ${portPart})`;
            });
        }

        const expression = `${inclusionPrefix}(${packetEnvelope.join(' or ')})`;
        return expression;
    }

    static tcpdumpEndpointFilter(kwargs) {
        return PcapFilter.constructEndpointFilter({purpose: 'capture', ...kwargs});
    }

    static wiresharkEndpointFilter(kwargs) {
        return PcapFilter.constructEndpointFilter({purpose: 'display', ...kwargs});
    }
}

// // Example usage:
// const tcpdumpFilterForAddr = PcapFilter.tcpdumpEndpointFilter({
//     proto: 'tcp',
//     addr: '192.168.1.1',
//     port: 80,
//     filterGoal: 'exclude'
// });
// console.log(tcpdumpFilterForAddr);

// const tcpdumpFilterForNet = PcapFilter.tcpdumpEndpointFilter({
//     proto: 'tcp',
//     addr: '192.168.1.0/24',
//     port: 80,
//     filterGoal: 'exclude'
// });
// console.log(tcpdumpFilterForNet);

// const wiresharkFilter = PcapFilter.wiresharkEndpointFilter({
//     proto: 'udp',
//     addr: '10.0.0.1',
//     port: 8080,
//     filterGoal: 'include'
// });
// console.log(wiresharkFilter);

// const commonTestFilter = PcapFilter.constructEndpointFilter({
//     purpose: 'display',
//     proto: 'udp',
//     addr: '10.255.255.0/24',
//     port: 8080,
//     filterGoal: 'exclude'
// });
// console.log(commonTestFilter);
