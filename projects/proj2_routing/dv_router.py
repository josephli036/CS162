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
        self.log("sdfjklslkjghdskj (%s)", self.port_dst_lookup[self.dst_port_lookup[entity]])
        self.log("sdfjklslkjghdskj (%s)", entity)
        self.port_dst_lookup[self.dst_port_lookup[entity]].remove(entity)
        self.dst_port_lookup.pop(entity)
        self.dst_latency_lookup.pop(entity)
        self.entry_time.pop(entity)

    def update_neighbors(self, entity, port, latency):
        for neighbor_port in self.port_dst_lookup:
            if neighbor_port != port:
                pack = basics.RoutePacket(entity, latency)
                self.send(pack, neighbor_port)

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
        print("YOLOOOOOOOOO")
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
        self.log("RX %s on %s %s (%s)", packet, port, self.name, api.current_time())
        if isinstance(packet, basics.RoutePacket):
            root = packet.destination
            r_latency = packet.latency
            p_from = packet.src

            if root == p_from:
                self.port_dst_lookup[port] = [root]
                self.dst_port_lookup[root] = port
                self.dst_latency_lookup[root] = r_latency
                self.entry_time[root] = api.current_time()
                self.update_neighbors(root, port, r_latency)
            elif root not in self.dst_port_lookup:
                d_from_src = self.dst_latency_lookup[p_from]
                self.port_dst_lookup[port] += [root]
                self.dst_port_lookup[root] = port
                self.dst_latency_lookup[root] = r_latency + d_from_src
            else:
                old_latency = self.dst_latency_lookup[root]
                new_latency = self.dst_latency_lookup[p_from] + r_latency
                if new_latency <= old_latency:
                    self.log("sdfjklslkjghdskj (%s)", self.port_dst_lookup[self.dst_port_lookup[root]])
                    self.log("sdfjklslkjghdskj (%s)", root)
                    self.port_dst_lookup[self.dst_port_lookup[root]].remove(root)
                    self.entry_time.pop(root)
                    self.port_dst_lookup[port] += [root]
                    self.dst_port_lookup[root] = port
                    self.dst_latency_lookup[root] = new_latency
                    self.entry_time[root] = api.current_time()
                    self.update_neighbors(root, port, new_latency)
        elif isinstance(packet, basics.HostDiscoveryPacket):
            self.dst_port_lookup[packet.src] = port
            self.dst_latency_lookup[packet.src] = 0
            if port in self.port_dst_lookup:
                self.port_dst_lookup[port].append(packet.src)
            else:
                self.port_dst_lookup[port] = [packet.src]
            self.update_neighbors(packet.src, port, 0)
        else:
            # Totally wrong behavior for the sake of demonstration only: send
            # the packet back to where it came from!
            self.send(packet, self.dst_port_lookup[packet.dst])

    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """
        self.log("sdfjklslkjghdskj (%s)", api.current_time())
        list_to_delete = []
        for entry in self.entry_time:
            if (api.current_time() - self.entry_time[entry]) > self.ROUTE_TIMEOUT + 1:
                list_to_delete.append(entry)
        for item in list_to_delete:
            self.delete_entry(item)
        for port in self.port_dst_lookup:
            for dst in self.dst_latency_lookup:
                pack = basics.RoutePacket(dst, self.dst_latency_lookup[dst])
                self.send(pack, port)
            pack
