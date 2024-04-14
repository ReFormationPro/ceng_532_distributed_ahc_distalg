from adhoccomputing.GenericModel import Topology, GenericModel, Event, EventTypes, ConnectorTypes, GenericMessage, GenericMessagePayload, GenericMessageHeader, MessageDestinationIdentifiers
# from adhoccomputing.DistributedAlgorithms.Broadcasting import BroadcastingMessageHeader
# from adhoccomputing.Networking.LogicalChannels import GenericChannel
from adhoccomputing.Networking.LinkLayer import GenericLinkLayer
from adhoccomputing.Networking.ApplicationLayer import GenericApplicationLayer
from enum import Enum

class MSMessageType(Enum):
    DISTANCE = "MS_DISTANCE"
    FAIL = "MS_FAIL"
    REQ = "MS_REQ"
    WAKE = "MS_WAKE"

class MSLinkStatus(Enum):
    DOWN = "MS_DOWN"
    READY = "MS_READY"
    UP = "MS_UP"

class FailureMessage(GenericMessage):
    def __init__(self, header: GenericMessageHeader, sender_id: int):
        super(header, GenericMessagePayload(sender_id))

class DistanceMessage(GenericMessage):
    def __init__(self, header: GenericMessageHeader, 
                 sender_cycle_number: int, 
                 sender_distance: float, 
                 sender_id: int):
        super(header, GenericMessagePayload({sender_cycle_number, sender_distance, sender_id}))

class WakeMessage(GenericMessage):
    def __init__(self, header: GenericMessageHeader, sender_id: int):
        super(header, GenericMessagePayload(sender_id))

class RequestMessage(GenericMessage):
    def __init__(self, header: GenericMessageHeader, sender_cycle_number: int):
        super(header, GenericMessagePayload(sender_cycle_number))

class MSLayer(GenericModel):
    def __init__(self, componentname, componentinstancenumber):
        super().__init__(componentname, componentinstancenumber)

        self.distance: float = float('inf')
        self.predecessor_instance_number: int = -1
        # Maps neighbor id to its link weight
        self.link_weights = {}
        self.curr_cycle_number = -1
        self.last_recevied_cycle_number = {}
        self.maximum_received_cycle_number = -1
        self.distance_table = {}
        self.link_status = {}
        self.synchronization_number = {}

        self.eventhandlers[MSMessageType.DISTANCE] = self.on_distance
        self.eventhandlers[MSMessageType.FAIL] = self.on_fail
        self.eventhandlers[MSMessageType.REQ] = self.on_req
        self.eventhandlers[MSMessageType.WAKE] = self.on_wake
        self.eventhandlers[EventTypes.INIT] = self.on_init
    
    def on_distance(self, distance_event: Event):
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
        fail_msg = fail_event.eventcontent
        sender_id = fail_msg.payload.messagepayload
        self.link_status[sender_id] = MSLinkStatus.DOWN
        # TODO Execute FSM
        if self.predecessor_instance_number != None:
            self.send_req(self.predecessor_instance_number, self.curr_cycle_number)
        
    def on_req(self, req_event: Event):
        req_msg = req_event.eventcontent
        sender_cycle_number = req_msg.payload.messagepayload
        if self.predecessor_instance_number != None:
            self.send_req(self.predecessor_instance_number, sender_cycle_number)
        
    def on_wake(self, wake_event: Event):
        # NOTE Assuming F_i(l) is DOWN
        # TODO
        pass

    def send_req(self, destination_instance_number):
        pass

class MSNode(GenericModel):
    def __init__(self, componentname, componentid):
        # SUBCOMPONENTS
        self.applicationlayer = GenericApplicationLayer(
            "ApplicationLayer", componentid)
        self.cmservice = MSLayer("MSLayer", componentid)
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
