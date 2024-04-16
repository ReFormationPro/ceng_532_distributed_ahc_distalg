from adhoccomputing.GenericModel import Topology, GenericModel, Event, EventTypes, ConnectorTypes, GenericMessage, GenericMessagePayload, GenericMessageHeader, MessageDestinationIdentifiers
# from adhoccomputing.DistributedAlgorithms.Broadcasting import BroadcastingMessageHeader
# from adhoccomputing.Networking.LogicalChannels import GenericChannel
from adhoccomputing.Networking.LinkLayer import GenericLinkLayer
from adhoccomputing.Networking.ApplicationLayer import GenericApplicationLayer
from enum import Enum

class MSMessageType(Enum):
    """
    Merlin-Segall message types
    """
    DISTANCE = "MS_DISTANCE"
    """
    Distance reports from neighbors
    """
    FAIL = "MS_FAIL"
    """
    Indicates that a link has failed
    """
    REQ = "MS_REQ"
    """
    Request for a new update cycle
    """
    WAKE = "MS_WAKE"
    """
    Indicated that a new link is available
    """

class MSLinkStatus(Enum):
    DOWN = "MS_DOWN"
    READY = "MS_READY"
    UP = "MS_UP"

class FailureMessage(GenericMessage):
    def __init__(self, header: GenericMessageHeader, sender_id: int):
        super(header, GenericMessagePayload(sender_id))

class DistanceMessage(GenericMessage):
    """
    Carries cycle number, distance and id of the sender.
    Receiver updates their distance table with the sender distance.
    """
    def __init__(self, header: GenericMessageHeader, 
                 sender_cycle_number: int, 
                 sender_distance: float, 
                 sender_id: int):
        super(header, GenericMessagePayload({sender_cycle_number, sender_distance, sender_id}))

class WakeMessage(GenericMessage):
    """
    Indicates that a new link is available
    """
    def __init__(self, header: GenericMessageHeader, sender_id: int):
        super(header, GenericMessagePayload(sender_id))

class RequestMessage(GenericMessage):
    """
    Request for a new update cycle
    """
    def __init__(self, header: GenericMessageHeader, sender_cycle_number: int):
        super(header, GenericMessagePayload(sender_cycle_number))

class MSLayer(GenericModel):
    """
    Implements the Merlin-Segall layer functionality for non-destination component.
    """
    def __init__(self, componentname, componentinstancenumber):
        super().__init__(componentname, componentinstancenumber)

        self.predecessor_instance_number: int = -1  # p_i
        self.distance: float = float('inf')         # d_i
        # Maps neighbor id to its link weight
        self.link_weights = {}                      # d_il
        self.curr_cycle_number = -1                 # n_i
        self.maximum_received_cycle_number = -1     # mx_i
        self.context                                # CT
        self.last_recevied_cycle_number = {}        # N_i(l)
        self.distance_table = {}                    # D_i(l)
        self.link_status = {}                       # F_i(l)
        self.synchronization_number = {}            # z_i(l)

        self.eventhandlers[MSMessageType.DISTANCE] = self.on_distance
        self.eventhandlers[MSMessageType.FAIL] = self.on_fail
        self.eventhandlers[MSMessageType.REQ] = self.on_req
        self.eventhandlers[MSMessageType.WAKE] = self.on_wake
        self.eventhandlers[EventTypes.INIT] = self.on_init
    
    def on_init(self, init_event: Event):
        """
        Non-destination nodes do not use this event.
        """
        pass

    def on_distance(self, distance_event: Event):
        """
        Updates distance table
        """
        distance_msg = distance_event.eventcontent
        sender_cycle_number, sender_distance, sender_id = distance_msg.payload.messagepayload
        if self.link_status[sender_id].get() == MSLinkStatus.READY:
            self.link_status[sender_id] = MSLinkStatus.UP
        # NOTE m > z_i(l)
        self.last_recevied_cycle_number[sender_id] = sender_cycle_number
        link_weigth = 0 # TODO Estiamte link weight
        self.distance_table[sender_id] = sender_distance + link_weigth
        self.maximum_received_cycle_number = max(self.maximum_received_cycle_number, sender_cycle_number)
        # TODO Run FSM
        
    def on_fail(self, fail_event: Event):
        """
        Handles link failure by sending a new update cycle request.
        """
        fail_msg = fail_event.eventcontent
        sender_id = fail_msg.payload.messagepayload
        self.link_status[sender_id] = MSLinkStatus.DOWN
        # TODO Execute FSM
        if self.predecessor_instance_number != None:
            self.send_req(self.predecessor_instance_number, self.curr_cycle_number)
        
    def on_req(self, req_event: Event):
        """
        Forwards update cycle requests.
        """
        req_msg = req_event.eventcontent
        sender_cycle_number = req_msg.payload.messagepayload
        if self.predecessor_instance_number != None:
            self.send_req(self.predecessor_instance_number, sender_cycle_number)
        
    def on_wake(self, wake_event: Event):
        """
        TODO Pseudo-code has unclear comments. Needs to determine how it
        will be implemented.
        """
        # NOTE Assuming F_i(l) is DOWN
        # TODO
        pass

    def send_req(self, destination_instance_number):
        """
        Sends a new update cycle request
        """
        pass

class MSLayerDestination(MSLayer):
    """
    Merlin-Segall layer implementation for the destination node.

    TODO: Heavily depends on FSM. Implement FSM.
    """
    
    def on_init(self, init_event: Event):
        """
        Executes FSM.
        """
        self.CT = 0
        # TODO Execute FSM

    def on_distance(self, distance_event: Event):
        """
        Updates last received cycle number and runs FSM
        """
        distance_msg = distance_event.eventcontent
        sender_cycle_number, sender_distance, sender_id = distance_msg.payload.messagepayload
        self.last_recevied_cycle_number[sender_id] = sender_cycle_number
        self.CT = 0
        # TODO Execute FSM
        
    def on_fail(self, fail_event: Event):
        """
        Handles link failure by updating link status and running FSM.
        """
        fail_msg = fail_event.eventcontent
        sender_id = fail_msg.payload.messagepayload
        self.link_status[sender_id] = MSLinkStatus.DOWN
        self.CT = 0
        # TODO Execute FSM
        
    def on_req(self, req_event: Event):
        """
        Handles new cycle requests by running FSM.
        """
        self.CT = 0
        # TODO Execute FSM
        
    def on_wake(self, wake_event: Event):
        """
        TODO Pseudo-code has unclear comments. Needs to determine how it
        will be implemented. 
        """
        # NOTE F_i(l) = DOWN
        # TODO
        pass

class MSNode(GenericModel):
    """
    Initializes a node with application, Merlin-Segall, and link layers.
    """
    def __init__(self, componentname, componentid, is_destination_node = False):
        # SUBCOMPONENTS
        self.applicationlayer = GenericApplicationLayer(
            "ApplicationLayer", componentid)
        if is_destination_node:
            self.msservice = MSLayerDestination("MSLayer", componentid)
        else:
            self.msservice = MSLayer("MSLayer", componentid)
        self.linklayer = GenericLinkLayer("LinkLayer", componentid)

        # CONNECTIONS AMONG SUBCOMPONENTS
        self.applicationlayer.connect_me_to_component(
            ConnectorTypes.DOWN, self.msservice)
        self.msservice.connect_me_to_component(
            ConnectorTypes.UP, self.applicationlayer)

        self.msservice.connect_me_to_component(
            ConnectorTypes.DOWN, self.linklayer)
        self.linklayer.connect_me_to_component(
            ConnectorTypes.UP, self.msservice)

        # Connect the bottom component to the composite component....
        self.linklayer.connect_me_to_component(ConnectorTypes.DOWN, self)
        self.connect_me_to_component(ConnectorTypes.UP, self.linklayer)

        super().__init__(componentname, componentid)

    def on_message_from_top(self, eventobj: Event):
        self.send_down(Event(self, EventTypes.MFRT, eventobj.eventcontent))

    def on_message_from_bottom(self, eventobj: Event):
        self.send_up(Event(self, EventTypes.MFRB, eventobj.eventcontent))
