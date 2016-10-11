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
        self.routes = {}
        self.port_routes = {}
        self.link = {}

    def delete_entry(self, entity):
        self.port_dst_lookup[self.dst_port_lookup[entity[0]]].remove(entity[0])
        self.dst_port_lookup.pop(entity[0])
        self.dst_latency_lookup.pop(entity[0])
        self.entry_time.pop(entity)
        self.routes[entity[0]].remove(entity)
        self.port_routes[entity[1]].remove(entity)


        best_port = None
        shortest_latency = INFINITY
        for route in self.routes[entity[0]]:
            if route[2] <= shortest_latency:
                best_port = route[1]
        if entity[0] not in self.port_dst_lookup[best_port]:
            self.port_dst_lookup[best_port] += [entity[0]]
        self.dst_port_lookup[entity[0]] = best_port
        self.dst_latency_lookup[entity[0]] = shortest_latency

    def update_neighbors(self, entity, port, latency):
        for neighbor_port in self.port_dst_lookup:
            if neighbor_port != port:
                pack = basics.RoutePacket(entity, latency)
                self.send(pack, neighbor_port)

    def update_local(self, root, port, latency):
        if root in self.routes:
            self.routes[root] += [(root, port, latency)]
        else:
            self.routes[root] = [(root, port, latency)]
        self.entry_time[(root, port, latency)] = api.current_time()
        if port in self.port_routes:
            self.port_routes[port] += [(root, port, latency)]
        else:
            self.port_routes[port] = [(root, port, latency)]

        best_port = None
        shortest_latency = INFINITY
        for route in self.routes[root]:
            if route[2] <= shortest_latency:
                best_port = route[1]
        if best_port not in self.port_dst_lookup:
            self.port_dst_lookup[best_port] = []
        if root not in self.port_dst_lookup[best_port]:
            self.port_dst_lookup[best_port] += [root]
        self.dst_port_lookup[root] = best_port
        self.dst_latency_lookup[root] = shortest_latency

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.

        The port attached to the link and the link latency are passed
        in.

        """
        self.link[port] = latency
        self.port_dst_lookup[port] = []
        for dst in self.dst_latency_lookup:
            pack = basics.RoutePacket(dst, self.dst_latency_lookup[dst])
            self.send(pack, port)
        pack = basics.RoutePacket(self, 0)
        self.send(pack, port)

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this Entity does down.

        The port number used by the link is passed in.

        """
        if self.POISON_MODE:
            self.link.pop(port)

            for dst in self.port_dst_lookup[port]:
                self.update_neighbors(dst, None, INFINITY)
                self.dst_port_lookup.pop(dst)
                self.dst_latency_lookup.pop(dst)
                self.entry_time.pop(dst)
            self.port_dst_lookup.pop(port)
        else:
            self.link.pop(port)

            for dst in self.port_dst_lookup[port]:
                self.dst_port_lookup.pop(dst)
                self.dst_latency_lookup.pop(dst)
            for route in self.port_routes[port]:
                self.routes[route[0]].pop(routes)
            self.port_routes.pop(port)
            self.port_dst_lookup.pop(port)
        


    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.

        """
        # self.log("RX %s on %s %s (%s)", packet, port, self.name, api.current_time())
        if isinstance(packet, basics.RoutePacket):
            root = packet.destination
            r_latency = packet.latency
            p_from = packet.src
            if root == p_from:
                self.update_local(root, port, r_latency + self.link[port])
                self.update_neighbors(root, port, r_latency + self.link[port])
            elif root not in self.dst_port_lookup:
                self.update_local(root, port, r_latency + self.link[port])
                self.update_neighbors(root, port, r_latency + self.link[port])
            else:
                # old_latency = self.dst_latency_lookup[root]
                new_latency = self.dst_latency_lookup[p_from] + r_latency
                # if self.dst_port_lookup[root] == port:
                #     self.update_local(root, port, new_latency)
                #     self.update_neighbors(root, port, new_latency)
                # elif new_latency <= old_latency:
                #     self.port_dst_lookup[self.dst_port_lookup[root]].remove(root)
                #     self.update_local(root, port, new_latency)
                #     self.update_neighbors(root, port, new_latency)
                self.port_dst_lookup[self.dst_port_lookup[root]].remove(root)
                self.update_local(root, port, new_latency)
                self.update_neighbors(root, port, new_latency)
        elif isinstance(packet, basics.HostDiscoveryPacket):
            self.dst_port_lookup[packet.src] = port
            self.dst_latency_lookup[packet.src] = self.link[port]
            self.port_dst_lookup[port]+=[packet.src]
            self.update_neighbors(packet.src, port, self.link[port])
        else:
            if packet.dst in self.dst_port_lookup and self.dst_port_lookup[packet.dst] != port:
                if self.dst_latency_lookup[packet.dst] >= INFINITY:
                    return
                else:
                    self.send(packet, self.dst_port_lookup[packet.dst])
                # self.send(packet, self.dst_port_lookup[packet.dst])

    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """
        list_to_delete = []
        for entry in self.entry_time:
            if (api.current_time() - self.entry_time[entry]) > self.ROUTE_TIMEOUT:
                list_to_delete.append(entry)
        for item in list_to_delete:
            if self.POISON_MODE:
                for neighbor in self.link:
                    self.update_neighbors(item, neighbor, INFINITY)
            self.delete_entry(item)
        for port in self.link:
            for dst in self.dst_latency_lookup:
                pack = basics.RoutePacket(dst, self.dst_latency_lookup[dst])
                self.send(pack, port)
            pack = basics.RoutePacket(self, 0)
            self.send(pack, port)
