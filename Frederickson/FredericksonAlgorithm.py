from adhoccomputing.Generics import *
import networkx as nx
from adhoccomputing.Generics import *
import numpy as np
from threading import Lock
import queue

class GenericMessageHeader:
    """
    This class represents a generic message header for network messages.
    It encapsulates common header information used in messaging systems or network protocols.
    """

    def __init__(self, messagetype, messagefrom, messageto, nexthop=float('inf'), interfaceid=float('inf'), sequencenumber=-1):
        """
        Initializes a new instance of the GenericMessageHeader class.
        
        Parameters:
            messagetype (str): Specifies the type of the message.
            messagefrom (str): Identifier of the sender of the message.
            messageto (str): Identifier of the intended recipient of the message.
            nexthop (float): Designates the next system or interface to which the message should be sent (default is infinite).
            interfaceid (float): Specifies the network interface identifier (default is infinite).
            sequencenumber (int): An optional sequence number to keep track of message order (default is -1).
        """
        self.messagetype = messagetype
        self.messagefrom = messagefrom
        self.messageto = messageto
        self.nexthop = nexthop
        self.interfaceid = interfaceid
        self.sequencenumber = sequencenumber

    def __str__(self) -> str:
        """
        Returns a string representation of the message header, providing a human-readable form of its content.

        Returns:
            str: A formatted string detailing the message's type, source, destination, next hop, interface ID, and sequence number.
        """
        return f"GenericMessageHeader: TYPE: {self.messagetype} FROM: {self.messagefrom} TO: {self.messageto} NEXTHOP: {self.nexthop} INTERFACEID: {self.interfaceid} SEQUENCE#: {self.sequencenumber}"

class ComponentModel:
    """
    ComponentModel defines the base for a component in a networked or distributed system,
    facilitating event-driven interactions with other components via defined connectors.
    It manages the sending and receiving of events, and controls threading and event handling.
    """
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=2, topology=None, child_conn=None, node_queues=None, channel_queues=None):
        """
        Initializes a new instance of ComponentModel with various configurations.

        Parameters:
            componentname (str): The name identifier for the component.
            componentinstancenumber (int): Unique instance number for the component.
            context (any): Optional. A context wrapper for passing additional data.
            configurationparameters (dict): Optional. Parameters for configuring the component.
            num_worker_threads (int): Number of worker threads for handling events. Default is 2. More than 1 message should be handled. One node can be Triggered with other nodes in Graph. Use number of nodes.
            topology (any): Optional. The network topology associated with the component.
            child_conn, node_queues, channel_queues: Infrastructure for inter-component communication.
        """
        self.topology = topology
        self.child_conn = child_conn
        self.node_queues=node_queues
        self.channel_queues=channel_queues
        self.context = context
        self.components  = []
        self.configurationparameters = configurationparameters
        self.eventhandlers = {EventTypes.INIT: self.on_init, EventTypes.MFRB: self.on_message_from_bottom,
                            EventTypes.MFRT: self.on_message_from_top, EventTypes.MFRP: self.on_message_from_peer, EventTypes.EXIT: self.on_exit}

        self.inputqueue = queue.Queue()
        self.componentname = componentname
        self.componentinstancenumber = componentinstancenumber
        self.num_worker_threads = num_worker_threads
        self.terminatestarted = False
        self.terminated = False
        self.initeventgenerated = False

        self.t = [None]*self.num_worker_threads
        for i in range(self.num_worker_threads):
            self.t[i] = Thread(target=self.queue_handler, args=[self.inputqueue])
            self.t[i].daemon = True
            self.t[i].start()

        logger.info(f"Generated NAME:{self.componentname} COMPID: {self.componentinstancenumber}")

        try:
            if self.connectors is not None:
                pass
        except AttributeError:
            self.connectors = ConnectorList()
            logger.debug(f"NAME:{self.componentname} COMPID: {self.componentinstancenumber} created connector list")


    def initiate_process(self):
        """
        Initiates the component by triggering the INIT event and propagating it to subcomponents.
        """
        self.trigger_event(Event(self, EventTypes.INIT, None))
        self.initeventgenerated = True
        for c in self.components:
            c.initiate_process()
        
    def exit_process(self):
        """
        Safely exits the component by propagating the EXIT event through all subcomponents.
        """
        for c in self.components:
            c.trigger_event(Event(self, EventTypes.EXIT, None))
        self.trigger_event(Event(self, EventTypes.EXIT, None))
        
    def send_down(self, event: Event):
        """
        Send the event to lower level components.
        """
        try:
            for p in self.connectors[ConnectorTypes.DOWN]:
                p.trigger_event(event)
        except Exception as e:
            raise(f"Cannot send message to Down Connector {self.componentname } -- {self.componentinstancenumber}")
            pass
        try:
            src = int(self.componentinstancenumber)
            event.eventsource = None 
            if self.channel_queues is not None:
                n = len(self.channel_queues[0])
                for i in range(n):
                    dest = i
                    if self.channel_queues[src][dest] is not None:
                        self.channel_queues[src][dest].put(event)
        except Exception as e:
            logger.error(f"Cannot send message to DOWN Connector over queues {self.componentname}-{self.componentinstancenumber} {str(event)} {e}")

    def send_up(self, event: Event):
        try:
            #self.connectors[ConnectorTypes.UP].eventhandlers[EventTypes.MFRB](event)
            for p in self.connectors[ConnectorTypes.UP]:
                p.trigger_event(event)

        except Exception as e:
            logger.error(f"Cannot send message to UP Connector {self.componentname}-{self.componentinstancenumber} {str(event)} {e}")

    def connect_me_to_component(self, name, component):
        try:
            self.connectors[name] = component
        except AttributeError:
            self.connectors = ConnectorList()
            self.connectors[name] = component

    def connectMeToChannel(self, name, channel):
        try:
          self.connectors[name] = channel
        except AttributeError:
          self.connectors = ConnectorList()
          self.connectors[name] = channel
        connectornameforchannel = self.componentname + str(self.
        componentinstancenumber)
        channel.connectMeToComponent(connectornameforchannel, self)

    def on_message_from_bottom(self, eventobj: Event):
        logger.debug(f"{EventTypes.MFRB} is not handled  {self.componentname}.{self.componentinstancenumber}")
        pass

    def on_message_from_top(self, eventobj: Event):
        logger.debug(f"{EventTypes.MFRT} is not handled  {self.componentname}.{self.componentinstancenumber}")
        pass

    def on_message_from_peer(self, eventobj: Event):
        logger.debug(f"{EventTypes.MFRP} is not handled  {self.componentname}.{self.componentinstancenumber}")
        pass

    def on_exit(self, eventobj: Event):
        logger.debug(f"{EventTypes.EXIT} is not handled  {self.componentname}.{self.componentinstancenumber} exiting")
        self.terminated = True
    

    def on_init(self, eventobj: Event):
        logger.debug(f"{EventTypes.INIT} is not handled {self.componentname}.{self.componentinstancenumber} exiting")
                 
    def queue_handler(self, myqueue):
        """
        Handles queued events, processing each by invoking the appropriate event handler.
        """
        while not self.terminated:
            workitem = myqueue.get()
            if workitem.event in self.eventhandlers:
                self.on_pre_event(workitem)
                self.eventhandlers[workitem.event](eventobj=workitem)  # call the handler
            else:
                logger.error(f"{self.componentname}.{self.componentinstancenumber} Event Handler: {workitem.event} is not implemented")
            myqueue.task_done()

    def on_connected_to_component(self, name, channel):
        logger.debug(f"Connected channel-{name} by component-{self.componentinstancenumber}:{channel.componentinstancenumber}")
        pass

    def trigger_event(self, eventobj: Event):
        self.inputqueue.put_nowait(eventobj)


    def on_pre_event(self, event):
        pass
        
    def send_self(self, event: Event):
        self.trigger_event(event)

class FredericksonAlgorithmSimpleComponent(ComponentModel):
    """
    A specialized component that implements Frederickson's algorithm, a distributed algorithm for solving certain
    problems in a networked environment. This component extends ComponentModel, adding specific initializations and
    behaviors needed for the algorithm's operations.
    """
    def __init__(self, componentname, componentid, topology):
        """
        Initializes a new instance of FredericksonAlgorithmSimpleComponent with specified component name, ID, and topology.

        Parameters:
            componentname (str): The name identifier for the component.
            componentid (int): Unique identifier for this component instance.
            topology (any): The network topology associated with this component, necessary for algorithmic operations.
            num_worker_threads (int): Number of worker threads for handling events. Default is 2. More than 1 message should be handled. One node can be Triggered with other nodes in Graph. Use number of nodes.
        """
        super(FredericksonAlgorithmSimpleComponent, self).__init__(componentname, componentid, topology=topology, num_worker_threads=topology.G.number_of_nodes())
        self.TOPO = topology
        self.queue_lock = Lock()
        self.message_queue = []

        if self.componentinstancenumber == 0:
            self.is_initiator = True
        else:
            self.is_initiator = False   

    def on_init(self, eventobj: Event):
        """
        Handles the initialization event for the component. This method overrides the on_init method in ComponentModel
        to perform custom initialization steps specific to Frederickson's algorithm.

        Parameters:
            eventobj (Event): The event object associated with the INIT event, containing any relevant data.
        """
        super(FredericksonAlgorithmSimpleComponent, self).on_init(eventobj)
        self.job()

    def on_message_from_bottom(self, eventobj: Event):
        """
        Handles messages received from lower-level components or subsystems.
        Filters messages to process only those that are intended for this component,
        and depending on the message type, processes or queues them for further handling.

        Parameters:
            eventobj (Event): The event object containing the message and its metadata.
        """
        message_to = eventobj.eventcontent.header.messageto.split("-")[1]
        message_from = eventobj.eventcontent.header.messagefrom.split("-")[1]
        print(f"{self.componentinstancenumber} received {message_from}")
        if int(message_to) == int(self.componentinstancenumber): # process only the messages targeted to this component...
            print("message accepted")
            message_source_id = eventobj.eventcontent.header.messagefrom.split("-")[1]
            message_type = eventobj.eventcontent.header.messagetype
            content = eventobj.eventcontent.payload

            if message_type == "EXPLORE" or message_type == "FORWARD" or message_type=="REVERSE":
                self.queue_lock.acquire() # protect message_queue, both component thread and Toueg thread are trying to access data
                self.message_queue.append((int(message_source_id), message_type, content))
                self.queue_lock.release()

    def job(self):
        """
        Initiates the algorithm's task, such as exploring paths or processing data,
        based on the topology and neighbors of the component.
        """
        self.neighbors = self.TOPO.get_neighbors(self.componentinstancenumber)  # retrieve all neighbor ids...
        self.neighbor_weights = {a: 1 for a in self.neighbors}  

        def getPaths(data):
            if len(data) == 0:
                return [[]]
            if len(data) == 1:
                ret = getPaths(data[list(data.keys())[0]])
                for i in ret:
                    i.insert(0, list(data.keys())[0])
                return ret
            if len(data) > 1:
                ret = getPaths(data[list(data.keys())[0]])
                for kl in range(len(ret)):
                    ret[kl].insert(0, list(data.keys())[0])

                return ret + getPaths({a: data[a] for a in list(data.keys()) if a != list(data.keys())[0]})

        tree =  self.FredericksonAlgorithmSimple()
        paths = getPaths(tree)

    def FredericksonAlgorithmSimple(self):
        """
        Where the algorithm goes.
        Nodes may face with these messages:
        1. Node u receives ⟨forward,f⟩ from node v.
        2. Node u receives ⟨explore, f, m⟩ from node v. 
        3. Node u receives ⟨reverse, b⟩ from node v.
        See the algorithm detail:
        A Scrutiny of Frederickson’s Distributed Breadth-First Search Algorithm - Victor van der Veen
        """
        print(f"{self.componentinstancenumber} started FredericksonAlgorithm Thread")
        self.positively_responded_nodes = []
        self.level_u = np.inf
        self.neighbor_level_u = {}
        self.parent_u = None
        self.children_u = {}
        message_from_future = []
        self.subtree = []

        self.expectedreplies = expectedreplies = {}
        for neighbor in self.neighbors:
            self.neighbor_level_u[neighbor] = np.inf
            expectedreplies[neighbor] = 0

        bvalue_u = False

        if self.is_initiator:
            self.level_u = 0
            k = 0
            for n in self.neighbors:
                if not n in self.children_u:
                    self.children_u[n] = []
                self.sendMessageToNeighbor(n, "EXPLORE", k + 1)
                expectedreplies[n] = 1

        while True:
            new_message = self.waitNewMessage()
            sender, message_type, f = new_message
            search_depth = f

            if message_type == "FORWARD":
                bvalue_u = False
                minus = []
                for n in self.neighbors:
                    if expectedreplies[n] < 0:
                        minus.append(n)
                    expectedreplies[n] = 0

                if self.level_u < f:

                    for c in self.positively_responded_nodes:  # positively responded...
                        self.sendMessageToNeighbor(c, "FORWARD", f)
                        expectedreplies[c] += 1
                    self.positively_responded_nodes = []
                if self.level_u == f:
                    transmitted = 0
                    for n in self.neighbors:
                        if self.neighbor_level_u[n] != f - 1:
                            self.sendMessageToNeighbor(n, "EXPLORE", f + 1)
                            expectedreplies[n] = 1
                            transmitted += 1
                    for min_ in minus:
                        expectedreplies[min_] -= 1

                    if transmitted == 0:
                        self.sendMessageToNeighbor(sender, "REVERSE", (False, self.children_u))

            elif message_type == "EXPLORE":
                f = search_depth

                if self.level_u == np.inf:
                    self.parent_u = sender
                    self.level_u = f
                    self.sendMessageToNeighbor(sender, "REVERSE", (True, self.children_u))
                    self.neighbor_level_u[sender] = f - 1

                elif self.level_u == f:
                    self.neighbor_level_u[sender] = f - 1
                    self.sendMessageToNeighbor(sender, "REVERSE", (False, self.children_u))
                elif self.level_u == f - 1:
                    b = False
                    expectedreplies[sender] -= 1
                    all_responded = True
                    for i in expectedreplies:
                        if expectedreplies[i] != 0:
                            all_responded = False
                            break
                    if all_responded == True:
                        if self.parent_u is not None:
                            self.sendMessageToNeighbor(self.parent_u, "REVERSE", (bvalue_u, self.children_u))
                        elif bvalue_u == True:
                            k = k + 1
                            for c in self.positively_responded_nodes:  # list(set(self.children_u)):
                                self.sendMessageToNeighbor(c, "FORWARD", k)
                                expectedreplies[c] = 1
                            self.positively_responded_nodes = []
                        else:
                            print("BFS Completed Explore ....")
                            break
                else:
                    print(f"****************Wasted {new_message}****************")
                    message_from_future.append((sender, message_type, search_depth))

            elif message_type == "REVERSE":
                bvalue_u = False
                b = f[0]
                expectedreplies[sender] -= 1
                if b == True:
                    if sender not in self.positively_responded_nodes:
                        self.positively_responded_nodes.append(sender)
                    self.children_u[sender] = f[1]
                    bvalue_u = True

                all_responded = True
                for i in expectedreplies:
                    if expectedreplies[i] != 0:
                        all_responded = False
                        break
                if all_responded == True:

                    if self.parent_u is not None:
                        self.sendMessageToNeighbor(self.parent_u, "REVERSE", (bvalue_u, self.children_u))
                    elif bvalue_u == True:
                        bvalue_u = False
                        k = k + 1
                        for c in self.positively_responded_nodes: 
                            self.sendMessageToNeighbor(c, "FORWARD", k)
                            expectedreplies[c] = 1
                        self.positively_responded_nodes = []
                    else:
                        print("BFS Completed Reverse ....")
                        print("Tree : ", self.children_u)

                        break
        return {self.componentinstancenumber: self.children_u}


    def sendMessageToNeighbor(self, neighbor_id, message_type, message):
        print(f"{self.componentinstancenumber} sends {message_type} message to neighbor {neighbor_id}")
        message_header = GenericMessageHeader(message_type, FredericksonAlgorithmSimpleComponent.__name__+"-"+str(self.componentinstancenumber),
        FredericksonAlgorithmSimpleComponent.__name__+"-"+str(neighbor_id), interfaceid=str(self.componentinstancenumber)+"-"+str(neighbor_id))
        mess_ = GenericMessage(message_header, message)

        event = Event(self, EventTypes.MFRT, mess_ , fromchannel= self.TOPO.channels)
        self.send_down(event)

    def waitNewMessage(self):
        covertion = {0: "p", 1: "q", 2: "r", 3: "s", 4: "t", 5: "u"}
        self.queue_lock.acquire()
        if len(self.message_queue) > 0:
            print("Message:")
            message = self.message_queue.pop()
            print(message)
            sender = message[0]
            message_type = message[1]
            last_part = message[2]
            self.queue_lock.release()
            return (sender, message_type, last_part)
        else:
            self.queue_lock.release()
            return None, None, None