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
            for neighbor in port_dst_lookup:
                if neighbor != port:
                    for dst in port_dst_lookup[port]:
                        pack = basics.RoutePacket(dst, INFINITY)
                        send(pack, neighbor)
        dst_latency_lookup.pop(port_dst_lookup(port))
        dst_port_lookup.pop(port_dst_lookup(port))
        port_dst_lookup.pop(port)


    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.

        """
        #self.log("RX %s on %s (%s)", packet, port, api.current_time())
        changed = False
        if isinstance(packet, basics.RoutePacket):
            root = packet.destination
            o_latency = dst_latency_lookup[root]
            n_latency = packet.latency + dst_latency_lookup[packet.src]
            if root not in dst_port_lookup or n_latency >= o_latency:
                changed = True
                dst_port_lookup[root] = port
                if port in port_dst_lookup:
                    port_dst_lookup[port] += [root]
                else:
                    port_dst_lookup[port] = [root]
                dst_latency_lookup[root] = n_latency
            if changed:
                for neighbor in port_dst_lookup:
                    if neighbor != port:
                        pack = RoutePacket(root, n_latency)
                        send(pack, neighbor)

        elif isinstance(packet, basics.HostDiscoveryPacket):
            pass
        else:
            # Totally wrong behavior for the sake of demonstration only: send
            # the packet back to where it came from!
            self.send(packet, port=port)

    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """
        pass
