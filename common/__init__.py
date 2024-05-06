from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer, LinkLayerMessageTypes
from adhoccomputing.Networking.ApplicationLayer.GenericApplicationLayer import GenericApplicationLayer, ApplicationLayerMessageTypes, ApplicationLayerMessageHeader, ApplicationLayerMessagePayload
from adhoccomputing.GenericModel import Topology, GenericModel, Event, EventTypes, ConnectorTypes, GenericMessage, GenericMessagePayload, GenericMessageHeader, MessageDestinationIdentifiers
import logging

logger = logging.getLogger("AHC-COMMON")
logger.setLevel(logging.DEBUG)
# logging.basicConfig(level=logging.INFO)
logging.basicConfig()


class CommonLinkLayer(GenericLinkLayer):
    def on_message_from_top(self, eventobj: Event):
        #logger.info(f"{self.componentname}-{self.componentinstancenumber} RECEIVED FROM TOP {str(eventobj)}")
        abovehdr = eventobj.eventcontent.header
        if abovehdr.messageto == MessageDestinationIdentifiers.NETWORKLAYERBROADCAST:
            hdr = GenericMessageHeader(LinkLayerMessageTypes.LINKMSG, self.componentinstancenumber, abovehdr.nexthop,
                                        MessageDestinationIdentifiers.LINKLAYERBROADCAST,nexthop=MessageDestinationIdentifiers.LINKLAYERBROADCAST)
        else:
            #if we do not broadcast, use nexthop to determine interfaceid and set hdr.interfaceid
            myinterfaceid = str(self.componentinstancenumber) + "-" + str(abovehdr.nexthop)
            hdr = GenericMessageHeader(LinkLayerMessageTypes.LINKMSG, self.componentinstancenumber,
                                        abovehdr.nexthop, nexthop=abovehdr.nexthop, interfaceid=myinterfaceid)

        payload = eventobj.eventcontent
        msg = GenericMessage(hdr, payload)
        self.send_down(Event(self, EventTypes.MFRT, msg))


class CommonApplicationLayer(GenericApplicationLayer):
    """
    Implements necessary functionality for a minimal application layer
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.eventhandlers[ApplicationLayerMessageTypes.PROPOSE] = self.on_propose
        self.eventhandlers[ApplicationLayerMessageTypes.ACCEPT] = self.on_accept
        
    def on_init(self, eventobj: Event):
        logger.debug(f"Initializing {self.componentname}.{self.componentinstancenumber}")

        if self.componentinstancenumber == 0:
            # destination = random.randint(len(Topology.G.nodes))
            destination = 1
            hdr = ApplicationLayerMessageHeader(ApplicationLayerMessageTypes.PROPOSE, self.componentinstancenumber,
                                                destination)
            payload = ApplicationLayerMessagePayload("23")
            proposalmessage = GenericMessage(hdr, payload)
            # randdelay = random.randint(0, 5)
            # time.sleep(randdelay)
            self.send_self(Event(self, ApplicationLayerMessageTypes.PROPOSE, proposalmessage))
        else:
            pass

    def on_propose(self, eventobj: Event):
        logger.debug(f"CommonAppL on propose {eventobj}")

    def on_accept(self, eventobj: Event):
        logger.debug(f"CommonAppL on accept {eventobj}")
