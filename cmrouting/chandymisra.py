import time
from adhoccomputing.GenericModel import Topology, GenericModel, Event, EventTypes, ConnectorTypes, GenericMessage, GenericMessagePayload, GenericMessageHeader, MessageDestinationIdentifiers
# from adhoccomputing.DistributedAlgorithms.Broadcasting import BroadcastingMessageHeader
# from adhoccomputing.Networking.LogicalChannels import GenericChannel
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer, LinkLayerMessageTypes
from adhoccomputing.Networking.ApplicationLayer.GenericApplicationLayer import GenericApplicationLayer, ApplicationLayerMessageTypes, ApplicationLayerMessageHeader, ApplicationLayerMessagePayload
from enum import Enum
import logging
from threading import Lock

# For common stuff
import os
import sys

import networkx
sys.path.insert(0, os.path.abspath('..'))
from common import *

logger = logging.getLogger("AHC-CM")
logger.setLevel(logging.DEBUG)
# logging.basicConfig(level=logging.INFO)
logging.basicConfig()

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
    OVER_QM = "OVER_QM"
    """
    An "over?" message for positive algorithm termination inquiry.
    """
    OVER_NEG = "OVER_NEG"
    """
    An "over-" message for negative algorithm termination inquiry.
    """


class DistanceMessage(GenericMessage):
    """
    Carries distance of a node to the destination.
    """
    def __init__(self, header: GenericMessageHeader, distance: float):
        super().__init__(header, GenericMessagePayload(distance))


class AcknowledgementMessage(GenericMessage):
    """
    Reports the end of processing of a distance report. 
    """
    def __init__(self, header: GenericMessageHeader):
        super().__init__(header, GenericMessagePayload(None))


class OverQMMessage(GenericMessage):
    """
    Initially sent by the sink for positive termination inquiry. 
    """
    def __init__(self, header: GenericMessageHeader):
        super().__init__(header, GenericMessagePayload(None))


class OverNegMessage(GenericMessage):
    """
    Termination message sent upon detection of a negative cycle. 
    """
    def __init__(self, header: GenericMessageHeader):
        super().__init__(header, GenericMessagePayload(None))


class CMLayer(GenericModel):
    """
    Implements Chandy-Misra layer of the routing.
    """
    LAYERS = []

    def __init__(self, destination_node_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        CMLayer.LAYERS.append(self)

        # NOTE The following is added for measurements
        self.destination_node_id = destination_node_id

        self.distance: float = float('inf')
        self.predecessor_instance_number: int = -1
        self.num: int = 0
        self.num_lock = Lock()
        # NOTE Paper is unclear on termination, so I added this
        # See the note on "initiate_phase_two"
        self.overqm_msgs_sent: bool = False

        self.eventhandlers[CMMessageType.DISTANCE] = self.on_distance
        self.eventhandlers[CMMessageType.ACKNOWLEDGEMENT] = self.on_acknowledgement
        self.eventhandlers[CMMessageType.OVER_QM] = self.on_overqm
        self.eventhandlers[CMMessageType.OVER_NEG] = self.on_overneg
        self.eventhandlers[EventTypes.INIT] = self.on_init

    def on_init(self, eventobj: Event):
        logger.info(f"Initializing {self.componentname} - {self.componentinstancenumber}")

    def on_message_from_top(self, eventobj: Event):
        """
        Forward application layer message over chandy-misra layer
        """
        logger.debug(f"Message from app layer: {eventobj.eventcontent}")
        # TODO Route it
        self.send_down(eventobj)

    def on_message_from_bottom(self, eventobj: Event):
        """
        Deliver the message from link layer to the application if
        - This node has registered to the even type, and
        - This node is the target.
        """
        try:
            hdr = eventobj.eventcontent.header
            if hdr.messagetype == CMMessageType.DISTANCE:
                self.send_self(Event(self, CMMessageType.DISTANCE, eventobj.eventcontent))
            elif hdr.messagetype == CMMessageType.ACKNOWLEDGEMENT:
                self.send_self(Event(self, CMMessageType.ACKNOWLEDGEMENT, eventobj.eventcontent))
            elif hdr.messagetype == CMMessageType.OVER_NEG:
                self.send_self(Event(self, CMMessageType.OVER_NEG, eventobj.eventcontent))
            elif hdr.messagetype == CMMessageType.OVER_QM:
                self.send_self(Event(self, CMMessageType.OVER_QM, eventobj.eventcontent))
            else:
                # TODO
                self.send_up(eventobj)
        except AttributeError:
            logger.critical("Attribute Error")

    def on_distance(self, eventobj: Event):
        """
        Upon a distance report, if it indicates a shorter path, the receiver
        updates its shortest distance and reports this update to its neighbors.
        If there is no neighbor, immediately sends an acknowledgement to the sender, otherwise
        acknowledgement is sent from "on_acknowledgement" handler.
        If it is not a shorter path, the receiver sends an acknowledgement to the sender.
        """
        dist_msg: DistanceMessage = eventobj.eventcontent
        distance_in_msg = dist_msg.payload.messagepayload
        if distance_in_msg < self.distance:
            if self.num > 0:
                # Send ack
                self.send_acknowledgement_msg(self.predecessor_instance_number)
            logger.info(f"{self.componentname}-{self.componentinstancenumber} has set their predecessor from {self.predecessor_instance_number} to {dist_msg.header.messagefrom} because new distance is {distance_in_msg}, shorter than {self.distance}")
            self.predecessor_instance_number = dist_msg.header.messagefrom
            self.distance = distance_in_msg
            # Send distance msgs to all neighbors
            neighbors = self.topology.get_neighbors(self.componentinstancenumber)
            for n in neighbors:
                # None
                estimated_distance = self.distance + self.topology.G.get_edge_data(self.componentinstancenumber, n)['weight']
                self.send_distance_msg(n, estimated_distance)
            with self.num_lock:
                self.num += len(neighbors)
                # Send ack if we are done
                if self.num == 0:
                    self.send_acknowledgement_msg(self.predecessor_instance_number)
        else:
            # Useless, just finish it
            self.send_acknowledgement_msg(dist_msg.header.messagefrom)

    def on_acknowledgement(self, eventobj: Event):
        """
        Indicates that a neighbor has completed processing of a distance report.

        If no other acknowledgement message is expected, sends an
        acknowledgement to the predecessor.
        """
        with self.num_lock:
            self.num -= 1
            if self.num == 0:
                self.send_acknowledgement_msg(self.predecessor_instance_number)
    
    def on_overqm(self, eventobj: Event):
        self.initiate_phase_two(True)

    def on_overneg(self, eventobj: Event):
        self.initiate_phase_two(False)

    def make_msg_header(self, destination_instance_number):
        """
        Calculates next hop and prepares message header accordingly.
        Message type needs to be set by the caller.
        """
        # TODO
        nexthop = destination_instance_number # TODO
        interface_id = float("inf")  # self.uniquebroadcastidentifier
        hdr = GenericMessageHeader(
            None,
            self.componentinstancenumber,
            MessageDestinationIdentifiers.LINKLAYERBROADCAST,
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
        hdr.messagetype = CMMessageType.DISTANCE
        msg = DistanceMessage(hdr, distance)
        self.send_down(Event(self, EventTypes.MFRT, msg))

    def send_acknowledgement_msg(self, destination_instance_number):
        """
        Sends acknowledgement message to the neighbor with id 
        `destination_instance_number`
        """
        hdr = self.make_msg_header(destination_instance_number)
        msg = AcknowledgementMessage(hdr)
        hdr.messagetype = CMMessageType.ACKNOWLEDGEMENT
        self.send_down(Event(self, EventTypes.MFRT, msg))
    
    def send_overqm_msg(self, destination_instance_number):
        """
        Send an "over?" message to the given node.
        """
        hdr = self.make_msg_header(destination_instance_number)
        msg = OverQMMessage(hdr)
        hdr.messagetype = CMMessageType.OVER_QM
        self.send_down(Event(self, EventTypes.MFRT, msg))
    
    def send_overneg_msg(self, destination_instance_number):
        """
        Send an "over-" message to the given node.
        """
        hdr = self.make_msg_header(destination_instance_number)
        msg = OverNegMessage(hdr)
        hdr.messagetype = CMMessageType.OVER_NEG
        self.send_down(Event(self, EventTypes.MFRT, msg))

    def initiate_phase_two(self, success: bool):
        """
        Called when over- or over? is received
        success: True if over? is recevied, 
                 False if over- is received
        """
        logger.debug(f"{self.componentname}-{self.componentinstancenumber} is in phase two with {success}")
        with self.num_lock:
            num = self.num
        if num > 0:
            if self.distance != float("-inf"):
                self.distance = float("-inf")
                # Send over- to all neighbors
                neighbors = self.topology.get_neighbors(self.componentinstancenumber)
                for n in neighbors:
                    self.send_overneg_msg(n)
                self.report_finished()
        elif num == 0:
            if not success:
                # num == 0 and over- is recv
                if self.distance != float("-inf"):
                    self.distance = float("-inf")
                    # Send over- to all neighbors
                    neighbors = self.topology.get_neighbors(self.componentinstancenumber)
                    for n in neighbors:
                        self.send_overneg_msg(n)
                    self.report_finished()
            else:
                # num == 0 and over? is recv
                if self.distance != float("-inf"):
                    # Send over? to all neighbors who have not received such a msg

                    # NOTE It is unclear how the authors expect to know "who have
                    # not received such a msg" at this point so I just send it to
                    # everyone once here.
                    if self.overqm_msgs_sent:
                       return
                    
                    neighbors = self.topology.get_neighbors(self.componentinstancenumber)
                    for n in neighbors:
                        self.send_overqm_msg(n)
                    self.report_finished()
                    self.overqm_msgs_sent = True

    def report_finished(self):
        """
        NOTE This is not a part of the paper. I am using this to measure
        when the algorithm terminates.
        According to the theorem 3 in the paper, in phase 2,
        at most 2 messages are sent: first over? then over-.
        Hence, the this method will increment FINISHED only once per node.
        """
        dest_node: CMNode = self.topology.nodes[self.destination_node_id]
        dest_svc: CMLayerDestination = dest_node.cmservice
        if self.overqm_msgs_sent:
            # Already reported, do not decrement
            return
        with dest_svc.finished_node_count_lock:
            dest_svc.finished_node_count += 1
            logger.debug(f"Finished: {dest_svc.finished_node_count} and Node Count: {dest_svc.node_count}")
        if dest_svc.finished_node_count == dest_svc.node_count:
            finish_time = time.time()
            duration = finish_time - dest_svc.start_time
            logger.info(f"Calculations are finished at {finish_time}")
            logger.info(f"Algorithm took {duration} seconds")
            dest_node.on_finish(duration)
        elif dest_svc.finished_node_count > dest_svc.node_count:
            logger.error(f"Some nodes finished twice!")


class CMLayerDestination(CMLayer):
    """
    Implements Chandy-Misra layer functionality for the destination component.
    """
    def __init__(self, destination_node_id, *args, **kwargs):
        super().__init__(destination_node_id, *args, **kwargs)
        # NOTE The following are added for measurements
        G: networkx.Graph = self.topology.G 
        self.node_count = len(G.nodes)
        self.finished_node_count = 0
        self.finished_node_count_lock = Lock()
        self.start_time = -1

    def on_init(self, eventobj: Event):
        logger.info(f"Initializing {self.componentname} Destination Node - {self.componentinstancenumber}")
        self.start_time = time.time()
        logger.info(f"Algorithm start time is {self.start_time}")
        self.initiate_phase_one()

    def initiate_phase_one(self):
        self.distance = 0
        self.predecessor_instance_number = -1
        neighbors = self.topology.get_neighbors(self.componentinstancenumber)
        self.num = len(neighbors)
        for n in neighbors:
            estimated_distance = self.topology.G.get_edge_data(self.componentinstancenumber, n)['weight']
            self.send_distance_msg(n, estimated_distance)

    def on_distance(self, eventobj: Event):
        dist_msg: DistanceMessage = eventobj.eventcontent
        distance_in_msg = dist_msg.payload.messagepayload
        if distance_in_msg < 0:
            # Negative cycle
            self.initiate_phase_two(False)
        else:
            self.send_acknowledgement_msg(dist_msg.header.messagefrom)

    def on_acknowledgement(self, eventobj: Event):
        msg: AcknowledgementMessage = eventobj.eventcontent
        with self.num_lock:
            self.num -= 1
            if self.num == 0:
                # Terminate phase 1, start phase 2
                self.initiate_phase_two(True)

    def on_overqm(self, eventobj: Event):
        # NOTE Not in paper. Perhaps this means do nothing.
        # OverQM message is first sent by the destination node so
        # we should do nothing here.
        pass

    def on_overneg(self, eventobj: Event):
        # NOTE Not in paper. Perhaps this means do nothing.
        # This means that a negative cycle is detected.
        # If we do not send an overneg message here,
        # some nodes may never get this message. However,
        # they would still terminate with "over?" msgs. 
        # So I chose to do nothing.
        pass

    def initiate_phase_two(self, success: bool):
        logger.info(f"Destination node {self.componentname}-{self.componentinstancenumber} has initiated phase two with {success}")
        if success:
            # Send over? msgs to all neighbors
            neighbors = self.topology.get_neighbors(self.componentinstancenumber)
            for n in neighbors:
                self.send_overqm_msg(n)
        else:
            # Send over- msgs to all neighbors
            neighbors = self.topology.get_neighbors(self.componentinstancenumber)
            for n in neighbors:
                self.send_overneg_msg(n)
        self.report_finished()


class CMNode(GenericModel):
    """
    Initializes a Chandy-Misra node with application, Chandy-Misra, and link layers.
    """
    def initialize_subcomponents(self, is_destination_node: bool, destination_node_id: int, on_finish=lambda x: x):
        """
        Initializes subcomponents.

        is_destination_node: When true, cmservice is a CMLayerDestination instance.
        Otherwise, CMLayer instance.
        """
        self.on_finish = lambda x: logger.error("On finish called on non-destination node.")
        # SUBCOMPONENTS
        self.applicationlayer = CommonApplicationLayer(
            "ApplicationLayer", self.componentinstancenumber, topology=self.topology)
        if is_destination_node:
            # NOTE The following is added for measurements 
            self.on_finish = on_finish
            self.cmservice = CMLayerDestination(destination_node_id, "CMLayer", self.componentinstancenumber, topology=self.topology)
        else:
            self.cmservice = CMLayer(destination_node_id, "CMLayer", self.componentinstancenumber, topology=self.topology)
        self.linklayer = CommonLinkLayer("LinkLayer", self.componentinstancenumber, topology=self.topology)
        self.components.append(self.applicationlayer)
        self.components.append(self.cmservice)
        self.components.append(self.linklayer)

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

    def on_init(self, eventobj: Event):
        logger.info(f"Initializing {self.componentname} - {self.componentinstancenumber}")

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
