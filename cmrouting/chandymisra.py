from adhoccomputing.GenericModel import Topology, GenericModel, Event, EventTypes, ConnectorTypes, GenericMessage, GenericMessagePayload, GenericMessageHeader, MessageDestinationIdentifiers
# from adhoccomputing.DistributedAlgorithms.Broadcasting import BroadcastingMessageHeader
# from adhoccomputing.Networking.LogicalChannels import GenericChannel
from adhoccomputing.Networking.LinkLayer import GenericLinkLayer
from adhoccomputing.Networking.ApplicationLayer import GenericApplicationLayer
from enum import Enum


class CMMessageType(Enum):
    """
    Chandy-Misra message types
    """
    DISTANCE = "DISTANCE"
    """
    Reports distance to a neighbor.
    """
    ACKNOWLEDGEMENT = "ACKNOWLEDGEMENT"
    """
    Reports the end of processing of a distance report.
    """


class DistanceMessage(GenericMessage):
    """
    Carries distance of a node to the destination.
    """
    def __init__(self, header: GenericMessageHeader, distance: float):
        super(header, GenericMessagePayload(distance))


class AcknowledgementMessage(GenericMessage):
    """
    Reports the end of processing of a distance report. 
    """
    def __init__(self, header: GenericMessageHeader):
        super(header, GenericMessagePayload(None))


class CMLayer(GenericModel):
    """
    Implements Chandy-Misra layer of the routing.
    """
    def __init__(self, componentname, componentinstancenumber):
        super().__init__(componentname, componentinstancenumber)

        self.distance: float = float('inf')
        self.predecessor_instance_number: int = -1
        self.num: int = 0

        self.eventhandlers[CMMessageType.DISTANCE] = self.on_distance
        self.eventhandlers[CMMessageType.ACKNOWLEDGEMENT] = self.on_acknowledgement
        self.eventhandlers[EventTypes.INIT] = self.on_init

    def on_init(self, eventobj: Event):
        pass

    def on_message_from_top(self, eventobj: Event):
        """
        Forward application layer message over chandy-misra layer
        """
        pass

    def on_message_from_bottom(self, eventobj: Event):
        """
        Deliver the message from link layer to the application if
        - This node has registered to the even type, and
        - This node is the target.
        """
        pass

    def on_distance(self, dist_msg: DistanceMessage):
        """
        Upon a distance report, if it indicates a shorter path, the receiver
        updates its shortest distance and reports this update to its neighbors.
        If there is no neighbor, immediately sends an acknowledgement to the sender, otherwise
        acknowledgement is sent from "on_acknowledgement" handler.
        If it is not a shorter path, the receiver sends an acknowledgement to the sender.
        """
        # TODO Use locks
        distance_in_msg = dist_msg.payload.messagepayload
        if distance_in_msg < self.distance:
            if self.num > 0:
                # Send ack
                self.send_acknowledgement_msg(self.predecessor_instance_number)
            self.predecessor_instance_number = dist_msg.header.messagefrom
            self.distance = distance_in_msg
            # Send distance msgs to all neighbors
            neighbors = Topology().get_neighbors(self.componentinstancenumber)
            for n in neighbors:
                # None
                estimated_distance = None
                self.send_distance_msg(n, estimated_distance)
            self.num += len(neighbors)
            # Send ack if we are done
            if self.num == 0:
                self.send_acknowledgement_msg(self.predecessor_instance_number)
        else:
            # Useless, just finish it
            self.send_acknowledgement_msg(dist_msg.header.messagefrom)

    def on_acknowledgement(self, msg: AcknowledgementMessage):
        """
        Indicates that a neighbor has completed processing of a distance report.

        If no other acknowledgement message is expected, sends an
        acknowledgement to the predecessor.
        """
        # TODO Use locks
        self.num -= 1
        if self.num == 0:
            self.send_acknowledgement_msg(self.predecessor_instance_number)

    def make_msg_header(self, destination_instance_number):
        """
        Calculates next hop and prepares message header accordingly.
        """
        # TODO
        nexthop = MessageDestinationIdentifiers.LINKLAYERBROADCAST
        interface_id = float("inf")  # self.uniquebroadcastidentifier
        hdr = GenericMessageHeader(
            CMMessageType.DISTANCE,
            self.componentinstancenumber,
            destination_instance_number,
            nexthop,
            interface_id,
            # sequence_number
        )
        return hdr

    def send_distance_msg(self, destination_instance_number, distance):
        """
        Sends distance message to the neighbor with id 
        `destination_instance_number`
        """
        hdr = self.make_msg_header(destination_instance_number)
        msg = DistanceMessage(hdr, distance)
        self.send_down(Event(self, EventTypes.MFRT, msg))

    def send_acknowledgement_msg(self, destination_instance_number):
        """
        Sends acknowledgement message to the neighbor with id 
        `destination_instance_number`
        """
        hdr = self.make_msg_header(destination_instance_number)
        msg = AcknowledgementMessage(hdr)
        self.send_down(Event(self, EventTypes.MFRT, msg))

    def initiate_phase_two(self, success: bool):
        """
        Called when over- or over? is received
        success: True if over? is recevied, 
                 False if over- is received
        """
        if self.num > 0:
            if self.distance != float("-inf"):
                self.distance = float("-inf")
                # TODO Send over- to all neighbors
                pass
        elif self.num == 0:
            if not success:
                # num == 0 and over- is recv
                if self.distance != float("-inf"):
                    self.distance = float("-inf")
                    # TODO Send over- to all neighbors
                    pass
            else:
                # num == 0 and over? is recv
                if self.distance != float("-inf"):
                    # TODO Send over? to all neighbors who have not received such a msg
                    pass


class CMLayerDestination(CMLayer):
    """
    Implements Chandy-Misra layer functionality for the destination component.
    """
    # FIXME May need to override __init__ to override dist/ack message handlers

    def initiate_phase_one(self):
        self.distance = 0
        self.predecessor_instance_number = -1
        neighbors = Topology().get_neighbors(self.componentinstancenumber)
        self.num = len(neighbors)
        for n in neighbors:
            estimated_distance = None  # TODO
            self.send_distance_msg(n, estimated_distance)

    def on_distance(self, dist_msg: DistanceMessage):
        distance_in_msg = dist_msg.payload.messagepayload
        if distance_in_msg < 0:
            # Negative cycle
            self.initiate_phase_two(False)
            pass
        else:
            self.send_acknowledgement_msg(dist_msg.header.messagefrom)

    def on_acknowledgement(self, msg: AcknowledgementMessage):
        # TODO Use locks
        self.num -= 1
        if self.num == 0:
            # Terminate phase 1, start phase 2
            self.initiate_phase_two(True)

    def initiate_phase_two(self, success: bool):
        if success:
            # TODO Send over? msgs to all neigbors
            pass
        else:
            # TODO Send over- msgs to all neighbors
            pass


class CMNode(GenericModel):
    """
    Initializes a Chandy-Misra node with application, Chandy-Misra, and link layers.
    """
    def __init__(self, componentname, componentid, is_destination_node = False):
        # SUBCOMPONENTS
        self.applicationlayer = GenericApplicationLayer(
            "ApplicationLayer", componentid)
        if is_destination_node:
            self.cmservice = CMLayerDestination("CMLayer", componentid)
        else:
            self.cmservice = CMLayer("CMLayer", componentid)
        self.linklayer = GenericLinkLayer("LinkLayer", componentid)

        # CONNECTIONS AMONG SUBCOMPONENTS
        self.applicationlayer.connect_me_to_component(
            ConnectorTypes.DOWN, self.cmservice)
        self.cmservice.connect_me_to_component(
            ConnectorTypes.UP, self.applicationlayer)

        self.cmservice.connect_me_to_component(
            ConnectorTypes.DOWN, self.linklayer)
        self.linklayer.connect_me_to_component(
            ConnectorTypes.UP, self.cmservice)

        # Connect the bottom component to the composite component....
        self.linklayer.connect_me_to_component(ConnectorTypes.DOWN, self)
        self.connect_me_to_component(ConnectorTypes.UP, self.linklayer)

        super().__init__(componentname, componentid)

    def on_message_from_top(self, eventobj: Event):
        """
        Forwards messages from top to down.
        """
        self.send_down(Event(self, EventTypes.MFRT, eventobj.eventcontent))

    def on_message_from_bottom(self, eventobj: Event):
        """
        Forwards messages from bottom to up.
        """
        self.send_up(Event(self, EventTypes.MFRB, eventobj.eventcontent))
