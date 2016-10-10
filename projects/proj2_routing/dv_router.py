"""Your awesome Distance Vector router for CS 168."""

import sim.api as api
import sim.basics as basics

# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter(basics.DVRouterBase):
    # NO_LOG = True # Set to True on an instance to disable its logging
    # POISON_MODE = True # Can override POISON_MODE here
    # DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

    def __init__(self):
        """
        Called when the instance is initialized.

        You probably want to do some additional initialization here.

        """
        self.start_timer()  # Starts calling handle_timer() at correct rate
        self.dst_latency_lookup = {}
        self.dst_port_lookup = {}
        self.port_dst_lookup = {}
        self.entry_time  = {}

    def delete_entry(self, entity):
        self.port_dst_lookup[self.dst_port_lookup[entity]].remove(entity)
        self.dst_port_lookup.pop(entity)
        self.dst_latency_lookup.pop(entity)
        self.entry_time.pop(entity)


    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.

        The port attached to the link and the link latency are passed
        in.

        """
        pack = basics.RoutePacket(self, latency)
        self.send(pack, port)

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this Entity does down.

        The port number used by the link is passed in.

        """
        if self.POISON_MODE:
            for neighbor in self.port_dst_lookup:
                if neighbor != port:
                    for dst in self.port_dst_lookup[port]:
                        pack = basics.RoutePacket(dst, INFINITY)
                        self.send(pack, neighbor)
        for dst in self.port_dst_lookup[port]:
            self.dst_latency_lookup.pop(dst)
            self.dst_port_lookup.pop(dst)
        self.port_dst_lookup.pop(port)


    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.

        """
        self.log("RX %s on %s (%s)", packet, port, api.current_time())
        changed = False
        if isinstance(packet, basics.RoutePacket):
            root = packet.destination
            r_latency = packet.latency
            p_from = packet.src

            if root == p_from:
                self.port_dst_lookup[port] = [root]
                self.dst_port_lookup[root] = port
                self.dst_latency_lookup[root] = r_latency
                self.entry_time[root] = api.current_time()
            elif root not in dst_port_lookup:
                d_from_src = self.dst_latency_lookup[p_from]
                self.port_dst_lookup[port] += [root]
                self.dst_port_lookup[root] = port
                self.dst_port_lookup[root] = r_latency + d_from_src
            else:
                old_latency = self.dst_latency_lookup[root]
                new_latency = self.dst_latency_lookup[p_from] + r_latency
                if new_latency >= old_latency:
                    self.port_dst_lookup[self.dst_port_lookup[root]].remove(root)
                    self.port_dst_lookup[port] += [root]
                    self.dst_port_lookup[root] = port_dst_lookup
                    self.dst_port_lookup[root] = new_latency
                    self.entry_time[root] = api.current_time()

            if changed:
                for neighbor in self.port_dst_lookup:
                    if neighbor != port:
                        pack = basics.RoutePacket(root, n_latency)
                        self.send(pack, neighbor)

        elif isinstance(packet, basics.HostDiscoveryPacket):
            self.dst_port_lookup[packet.src] = port
            print(packet.src)
            print(packet.src.name)
            print(port)
        else:
            # Totally wrong behavior for the sake of demonstration only: send
            # the packet back to where it came from!
            print(packet.dst)
            print(self.dst_port_lookup[packet.dst])
            self.send(packet, self.dst_port_lookup[packet.dst])

    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """
        for entry in self.entry_time:
            if api.current_time() - self.entry_time[entry]:
                delete_entry(entry)
        for port in self.port_dst_lookup:
            for dst in self.dst_latency_lookup:
                pack = basics.RoutePacket(dst, latency)
                self.send(pack, port)
