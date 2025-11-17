#!/usr/bin/env python3

"""
Mininet Experiment 1: IP Routing with Multiple Subnets

This script creates a network topology with:
- 3 hosts (h1, h2, h3)
- 2 routers (r1, r2)
- 4 subnets (10.0.0.0/24, 10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24)
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class LinuxRouter(Node):
    """A Node with IP forwarding enabled."""
    
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Enable IP forwarding on the router
        self.cmd('sysctl net.ipv4.ip_forward=1')
    
    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    """Network topology with routers and multiple subnets."""
    
    def build(self, **_opts):
        # Add routers
        r1 = self.addNode('r1', cls=LinuxRouter, ip='10.0.0.3/24')
        r2 = self.addNode('r2', cls=LinuxRouter, ip='10.0.1.2/24')
        
        # Add hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24', defaultRoute='via 10.0.0.3')
        h2 = self.addHost('h2', ip='10.0.3.2/24', defaultRoute='via 10.0.3.4')
        h3 = self.addHost('h3', ip='10.0.2.2/24', defaultRoute='via 10.0.2.1')
        
        # Add links
        # h1 <-> r1 (subnet 10.0.0.0/24)
        self.addLink(h1, r1, intfName2='r1-eth0', 
                     params2={'ip': '10.0.0.3/24'})
        
        # r1 <-> r2 (subnet 10.0.1.0/24)
        self.addLink(r1, r2, intfName1='r1-eth1', intfName2='r2-eth0',
                     params1={'ip': '10.0.1.1/24'}, 
                     params2={'ip': '10.0.1.2/24'})
        
        # r2 <-> h3 (subnet 10.0.2.0/24)
        self.addLink(r2, h3, intfName1='r2-eth1',
                     params1={'ip': '10.0.2.1/24'})
        
        # r1 <-> h2 (subnet 10.0.3.0/24)
        self.addLink(r1, h2, intfName1='r1-eth2',
                     params1={'ip': '10.0.3.4/24'})


def run():
    """Create network, configure routes, and run ping tests."""
    
    topo = NetworkTopo()
    net = Mininet(topo=topo, waitConnected=True)
    net.start()
    
    info('*** Network started\n')
    
    # Get node references
    r1 = net['r1']
    r2 = net['r2']
    h1 = net['h1']
    h2 = net['h2']
    h3 = net['h3']
    
    info('*** Configuring routes\n')
    
    # Configure routes on r1
    # Route to 10.0.2.0/24 (h3's network) via r2
    r1.cmd('ip route add 10.0.2.0/24 via 10.0.1.2 dev r1-eth1')
    
    # Configure routes on r2
    # Route to 10.0.0.0/24 (h1's network) via r1
    r2.cmd('ip route add 10.0.0.0/24 via 10.0.1.1 dev r2-eth0')
    # Route to 10.0.3.0/24 (h2's network) via r1
    r2.cmd('ip route add 10.0.3.0/24 via 10.0.1.1 dev r2-eth0')
    
    info('*** Routes configured\n')
    
    # Open output file
    with open('result1.txt', 'w') as f:
        f.write('Mininet Experiment 1: IP Routing Results\n')
        f.write('=' * 50 + '\n\n')
        
        # Test 1: h1 to h3
        info('*** Testing: h1 -> h3 (10.0.2.2)\n')
        f.write('Test 1: Ping from h1 (10.0.0.1) to h3 (10.0.2.2)\n')
        f.write('-' * 50 + '\n')
        result = h1.cmd('ping -c 1 10.0.2.2')
        f.write(result + '\n\n')
        
        # Test 2: h2 to h3
        info('*** Testing: h2 -> h3 (10.0.2.2)\n')
        f.write('Test 2: Ping from h2 (10.0.3.2) to h3 (10.0.2.2)\n')
        f.write('-' * 50 + '\n')
        result = h2.cmd('ping -c 1 10.0.2.2')
        f.write(result + '\n\n')
        
        # Test 3: h3 to h1
        info('*** Testing: h3 -> h1 (10.0.0.1)\n')
        f.write('Test 3: Ping from h3 (10.0.2.2) to h1 (10.0.0.1)\n')
        f.write('-' * 50 + '\n')
        result = h3.cmd('ping -c 1 10.0.0.1')
        f.write(result + '\n\n')
        
        # Test 4: h3 to h2
        info('*** Testing: h3 -> h2 (10.0.3.2)\n')
        f.write('Test 4: Ping from h3 (10.0.2.2) to h2 (10.0.3.2)\n')
        f.write('-' * 50 + '\n')
        result = h3.cmd('ping -c 1 10.0.3.2')
        f.write(result + '\n\n')
        
        f.write('=' * 50 + '\n')
        f.write('All tests completed!\n')
    
    info('*** Results written to result1.txt\n')
    info('*** All ping tests completed\n')
    
    
    info('*** Starting CLI (type "exit" to quit)\n')
    CLI(net)
    
    # Stop network
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
