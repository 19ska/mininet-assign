#!/usr/bin/env python3
import re, subprocess
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI


def sh(cmd): return subprocess.check_output(cmd, shell=True, text=True)

def ports_of(switch):
    out = sh(f"sudo ovs-ofctl show {switch}")
    m = {name:int(num) for num,name in re.findall(r'(\d+)\(([^)]+)\):', out)}
    return m, out

def main():
    setLogLevel('info')
    net = Mininet(controller=None, switch=OVSKernelSwitch, link=TCLink,
                  autoSetMacs=True, build=False)

    # Switches and hosts per spec
    s1 = net.addSwitch('s1', failMode='standalone')
    s2 = net.addSwitch('s2', failMode='standalone')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')

    # Links with explicit port names
    net.addLink(h1, s1, intfName1='h1-eth0', intfName2='s1-eth1')
    net.addLink(h2, s1, intfName1='h2-eth0', intfName2='s1-eth2')
    net.addLink(s1, s2, intfName1='s1-eth3', intfName2='s2-eth1')
    net.addLink(h3, s2, intfName1='h3-eth0', intfName2='s2-eth2')

    net.build(); net.start()
    CLI(net)

    def run(h, cmd):
        out = h.cmd(cmd)
        f.write(f"$ {h.name} {cmd}\n{out}\n")

    with open('result2.txt', 'w') as f:
        f.write("Experiment 2: L2/OVS with custom flows\n\n")

        # Before flows – both pings should work
        f.write("### Before adding flows\n")
        run(h1, 'ping -c 1 10.0.0.3')
        run(h2, 'ping -c 1 10.0.0.3')

        # Inspect s1 (port map + empty flows)
        ports, show_txt = ports_of('s1')
        f.write("### sudo ovs-ofctl show s1\n" + show_txt + "\n")
        f.write("### sudo ovs-ofctl dump-flows s1 (initial)\n" + sh("sudo ovs-ofctl dump-flows s1") + "\n")

        p1, p2, p3 = ports['s1-eth1'], ports['s1-eth2'], ports['s1-eth3']
        cmd_drop = f"sudo ovs-ofctl add-flow s1 'priority=100,in_port={p2},actions=drop'"
        cmd_fwd  = f"sudo ovs-ofctl add-flow s1 'priority=100,in_port={p1},actions=output:{p3}'"

        # Apply flows and record the exact commands used
        sh(cmd_drop); sh(cmd_fwd)
        f.write("### Flow commands used on s1\n" + cmd_drop + "\n" + cmd_fwd + "\n\n")

        # Show flows after
        f.write("### sudo ovs-ofctl dump-flows s1 (after)\n" + sh("sudo ovs-ofctl dump-flows s1") + "\n")

        # After flows – h1->h3 should pass, h2->h3 should fail
        f.write("### After adding flows\n")
        run(h1, 'ping -c 1 10.0.0.3')
        run(h2, 'ping -c 1 10.0.0.3')

    net.stop()

if __name__ == "__main__":
    main()
