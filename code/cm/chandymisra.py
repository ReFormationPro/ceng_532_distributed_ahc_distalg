from adhoccomputing.GenericModel import Topology, GenericModel, Event, EventTypes, ConnectorTypes, GenericMessage, GenericMessagePayload, GenericMessageHeader, MessageDestinationIdentifiers
# from adhoccomputing.DistributedAlgorithms.Broadcasting import BroadcastingMessageHeader
# from adhoccomputing.Networking.LogicalChannels import GenericChannel
from adhoccomputing.Networking.LinkLayer import GenericLinkLayer
from adhoccomputing.Networking.ApplicationLayer import GenericApplicationLayer
from enum import Enum

class CMMessageType(Enum):
    DISTANCE = "DISTANCE"
    ACKNOWLEDGEMENT = "ACKNOWLEDGEMENT"

class DistanceMessage(GenericMessage):
    def __init__(self, header: GenericMessageHeader, distance: float):
        super(header, GenericMessagePayload(distance))

class AcknowledgementMessage(GenericMessage):
    def __init__(self, header: GenericMessageHeader):
        super(header, GenericMessagePayload(None))

class CMLayer(GenericModel):
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
        # TODO Use locks
        self.num -= 1
        if self.num == 0:
            self.send_acknowledgement_msg(self.predecessor_instance_number)

    def make_msg_header(self, destination_instance_number):
        # TODO
        nexthop = MessageDestinationIdentifiers.LINKLAYERBROADCAST
        interface_id = float("inf") #self.uniquebroadcastidentifier
        hdr = GenericMessageHeader(
            CMMessageType.DISTANCE,
            self.componentinstancenumber,
            destination_instance_number,
            nexthop,
            interface_id,
            #sequence_number
        )
        return hdr
    
    def send_distance_msg(self, destination_instance_number, distance):
        hdr = self.make_msg_header(destination_instance_number)
        msg = DistanceMessage(hdr, distance)
        self.send_down(Event(self, EventTypes.MFRT, msg))
    
    def send_acknowledgement_msg(self, destination_instance_number):
        hdr = self.make_msg_header(destination_instance_number)
        msg = AcknowledgementMessage(hdr)
        self.send_down(Event(self, EventTypes.MFRT, msg))


class CMNode(GenericModel):
    def __init__(self, componentname, componentid):
        # SUBCOMPONENTS
        self.applicationlayer = GenericApplicationLayer(
            "ApplicationLayer", componentid)
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
        self.send_down(Event(self, EventTypes.MFRT, eventobj.eventcontent))

    def on_message_from_bottom(self, eventobj: Event):
        self.send_up(Event(self, EventTypes.MFRB, eventobj.eventcontent))
