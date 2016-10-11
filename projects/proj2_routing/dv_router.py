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
        self.port_list_dst_lookup = {}
        self.route_ports = {}
        self.route_destination = {}
        self.route_time = {}
        self.routes = []
        self.link = {}

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.

        The port attached to the link and the link latency are passed
        in.

        """
        self.link[port] = latency
        self.port_list_dst_lookup[port] = []
        self.route_ports[port] = []
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
        for route in self.route_ports[port]:
            self.log("I am %s deleting route %s (%s)", self.name, route, api.current_time())
            self.delete_route(route)

    def update_neighbors(self, root, uport, latency):
        for neighbor_port in self.link:
            if neighbor_port != uport:
                pack = basics.RoutePacket(root, latency)
                self.send(pack, neighbor_port)

    def add_route(self, packet, port):
        route = (packet.destination, port, packet.latency + self.link[port])
        self.route_time[route] = api.current_time()
        if route not in self.route_ports[port]:
            self.route_ports[port].append(route)
        if route not in self.routes:
            self.routes.append(route)
        if packet.destination in self.route_destination:
            if route not in self.route_destination[packet.destination]:
                self.route_destination[packet.destination].append(route)
        else:
            self.route_destination[packet.destination] = [route]

    def delete_route(self, route):
        if route in self.routes:
            self.routes.remove(route)
            self.route_destination[route[0]].remove(route)
            self.route_ports[route[1]].remove(route)
            self.route_time.pop(route)
            self.update_state(route[0])

    def update_state(self, root):
        changed = False

        best_port = None
        shortest_latency = INFINITY
        for route in self.route_destination[root]:
            if route[2] < shortest_latency:
                shortest_latency = route[2]
                best_port = route[1]

        if best_port == None:
            self.dst_port_lookup.pop(root)
            self.dst_latency_lookup.pop(root)
            return

        if root not in self.dst_port_lookup or self.dst_port_lookup[root] != best_port or self.dst_latency_lookup[root] != shortest_latency:
            changed = True

        if changed:
            if root in self.dst_port_lookup:
                self.port_list_dst_lookup[self.dst_port_lookup[root]].remove(root)

            self.port_list_dst_lookup[best_port].append(root)
            self.dst_port_lookup[root] = best_port
            self.dst_latency_lookup[root] = shortest_latency

        if changed:
            self.log("I am %s and i think the shorest path to %s is on port %s with latency %s (%s)", self.name, root, best_port, shortest_latency, api.current_time())
            self.update_neighbors(root, best_port, shortest_latency)

    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.

        """
        # self.log("RX %s on %s %s (%s)", packet, port, self.name, api.current_time())
        if isinstance(packet, basics.RoutePacket):
            self.add_route(packet, port)
            self.update_state(packet.destination)
        elif isinstance(packet, basics.HostDiscoveryPacket):
            self.dst_port_lookup[packet.src] = port
            self.dst_latency_lookup[packet.src] = self.link[port]
            self.port_list_dst_lookup[port] += [packet.src]
            self.update_neighbors(packet.src, port, self.link[port])
        else:
            if packet.dst in self.dst_port_lookup and self.dst_port_lookup[packet.dst] != port and packet.dst != self:
                if self.dst_latency_lookup[packet.dst] >= INFINITY:
                    return
                else:
                    self.send(packet, self.dst_port_lookup[packet.dst])

    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """
        for route in self.routes:
            if (api.current_time() - self.route_time[route]) > self.ROUTE_TIMEOUT:
                self.log("%s (%s)", api.current_time() - self.route_time[route], api.current_time())
                self.delete_route(route)

        for destination in self.dst_port_lookup:
            self.update_neighbors(destination, self.dst_port_lookup[destination], self.dst_latency_lookup[destination])
        for port in self.link:
            pack = basics.RoutePacket(self, 0)
            self.send(pack, port)
        
