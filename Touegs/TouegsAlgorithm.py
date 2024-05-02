from adhoccomputing.GenericModel import GenericModel, GenericMessagePayload
from adhoccomputing.Experimentation.Topology import Topology
import time
import queue
from threading import Thread
from multiprocessing import Queue
from timeit import default_timer as timer
from adhoccomputing.Generics import *
from threading import Lock

class GenericMessagePayload:

  def __init__(self, messagepayload):
    self.messagepayload = messagepayload

class GenericMessage:

  def __init__(self, header, payload):
    self.header = header
    self.payload = payload
    self.uniqueid = str(header.messagefrom) + "-" + str(header.sequencenumber)
  def __str__(self) -> str:
    return f"GENERIC MESSAGE: HEADER: {str(self.header)} PAYLOAD: {str(self.payload)}"
class GenericMessageHeader:

  def __init__(self, messagetype, messagefrom, messageto, nexthop=float('inf'), interfaceid=float('inf'), sequencenumber=-1):
    self.messagetype = messagetype
    self.messagefrom = messagefrom
    self.messageto = messageto
    self.nexthop = nexthop
    self.interfaceid = interfaceid
    self.sequencenumber = sequencenumber
  def __str__(self) -> str:
    return f"GenericMessageHeader: TYPE: {self.messagetype} FROM: {self.messagefrom} TO: {self.messageto} NEXTHOP: {self.nexthop} INTERFACEID: {self.interfaceid} SEQUENCE#: {self.sequencenumber}"


class ComponentModel:
    """
    ComponentModel defines the base for a component in a networked or distributed system,
    facilitating event-driven interactions with other components via defined connectors.
    It manages the sending and receiving of events, and controls threading and event handling.
    """
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None, child_conn=None, node_queues=None, channel_queues=None):
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
        # Add default handlers to all instantiated components.
        # If a component overwrites the __init__ method it has to call the super().__init__ method
        self.inputqueue = queue.Queue()
        self.componentname = componentname
        self.componentinstancenumber = componentinstancenumber
        self.num_worker_threads = num_worker_threads
        #self.connectors = {}
        self.terminatestarted = False
        self.terminated = False
        self.initeventgenerated = False

        self.t = [None]*self.num_worker_threads
        for i in range(self.num_worker_threads):
            self.t[i] = Thread(target=self.queue_handler, args=[self.inputqueue])
            self.t[i].daemon = True
            self.t[i].start()

        # self.mpqueuethread = Thread(target=self.mp_queue_handler, args=[self.node_queues])
        # self.mpqueuethread.daemon = True
        # self.mpqueuethread.start()

        # self.mp_conn_thread = Thread(target=self.mp_pipe_handler, args=[])
        # self.mp_conn_thread.daemon = True
        # self.mp_conn_thread.start()
        logger.info(f"Generated NAME:{self.componentname} COMPID: {self.componentinstancenumber}")

        try:
            if self.connectors is not None:
                pass
        except AttributeError:
            self.connectors = ConnectorList()
            logger.debug(f"NAME:{self.componentname} COMPID: {self.componentinstancenumber} created connector list")
            # self.connectors = ConnectorList()

        #TODO: Handle This Part
        # for i in range(self.num_worker_threads):
        #     t = Thread(target=self.queue_handler, args=[self.inputqueue])
        #     t.daemon = True
        #     t.start()

        # self.registry = ComponentRegistry()
        # self.registry.add_component(self)


    def initiate_process(self):
        self.trigger_event(Event(self, EventTypes.INIT, None))
        self.initeventgenerated = True
        for c in self.components:
            #c.inputqueue.put_nowait(Event(self, EventTypes.INIT, None))
            #c.trigger_event(Event(self, EventTypes.INIT, None))
            c.initiate_process()
        #self.inputqueue.put_nowait(Event(self, EventTypes.INIT, None))
        


    def exit_process(self):
        for c in self.components:
            #c.inputqueue.put_nowait(Event(self, EventTypes.EXIT, None))
            c.trigger_event(Event(self, EventTypes.EXIT, None))
        #self.inputqueue.put_nowait(Event(self, EventTypes.EXIT, None))
        self.trigger_event(Event(self, EventTypes.EXIT, None))
        

    
    def send_down(self, event: Event):
        try:
            for p in self.connectors[ConnectorTypes.DOWN]:
                p.trigger_event(event)
        except Exception as e:
            raise(f"Cannot send message to Down Connector {self.componentname } -- {self.componentinstancenumber}")
            #logger.error(f"Cannot send message to DOWN Connector {self.componentname}-{self.componentinstancenumber} {str(event)} {e}")
            pass
        try:
            src = int(self.componentinstancenumber)
            event.eventsource = None # for avoiding thread.lock problem
            if self.channel_queues is not None:
                n = len(self.channel_queues[0])
                for i in range(n):
                    dest = i
                    if self.channel_queues[src][dest] is not None:
                        self.channel_queues[src][dest].put(event)
        except Exception as e:
            logger.error(f"Cannot send message to DOWN Connector over queues {self.componentname}-{self.componentinstancenumber} {str(event)} {e}")


    def send_up_from_channel(self, event: Event, loopback = False):
        try:
            #self.connectors[ConnectorTypes.UP].eventhandlers[EventTypes.MFRB](event)
            if loopback: # loopback is only valid in symmetric channel constructors of the topology class
                for p in self.connectors[ConnectorTypes.UP]:
                        p.trigger_event(event)
            else:
                for p in self.connectors[ConnectorTypes.UP]:
                    if p.componentinstancenumber != event.eventsource_componentinstancenumber: #TO AVOID LOOPBACK provide the loopback optional parameter
                        p.trigger_event(event)

        except Exception as e:
            #logger.error(f"Cannot send message to UP Connector from channel {self.componentname}-{self.componentinstancenumber} {str(event)} {e}")
            pass

        try:
            src = int(event.fromchannel.split("-")[0]) 
            dest = int(event.fromchannel.split("-")[1])
            event.eventsource = None # for avoiding thread.lock problem
            if self.node_queues is not None:
                if self.node_queues[src][dest] is not None:
                    try:
                        self.node_queues[src][dest].put(event) 
                        pass
                    except Exception as ex:
                        logger.error(f"Cannot put to queue {self.componentname}-{self.componentinstancenumber} {str(event)} {e}")
        except Exception as ex:
            logger.error(f"Cannot send message to UP Connector from channel {self.componentname}-{self.componentinstancenumber} {str(event)} {e}")

    def send_up(self, event: Event):
        try:
            #self.connectors[ConnectorTypes.UP].eventhandlers[EventTypes.MFRB](event)
            for p in self.connectors[ConnectorTypes.UP]:
                p.trigger_event(event)

        except Exception as e:
            logger.error(f"Cannot send message to UP Connector {self.componentname}-{self.componentinstancenumber} {str(event)} {e}")

    def send_peer(self, event: Event):
        try:
            for p in self.connectors[ConnectorTypes.PEER]:
                p.trigger_event(event)
        except Exception as e:
            logger.error(f"Cannot send message to PEER Connector {self.componentname}-{self.componentinstancenumber} {str(event)} {e}")

    def U(self, component):
        self.connect_me_to_component(ConnectorTypes.UP, component)
  
    def D(self, component):
        self.connect_me_to_component(ConnectorTypes.DOWN, component)
  
    def P(self, component):
        self.connect_me_to_component(ConnectorTypes.PEER, component)
    
    def connect_me_to_component(self, name, component):
        logger.debug(f"Connecting {self.componentname}-{self.componentinstancenumber} {name} to {component.componentname}-{component.componentinstancenumber}")
        #self.connectors[name] = component
        try:
            self.connectors[name] = component
        except AttributeError:
            self.connectors = ConnectorList()
            self.connectors[name] = component

    def on_message_from_bottom(self, eventobj: Event):
        logger.debug(f"{EventTypes.MFRB} is not handled  {self.componentname}.{self.componentinstancenumber}")
        pass

    def on_message_from_top(self, eventobj: Event):
        logger.debug(f"{EventTypes.MFRT} is not handled  {self.componentname}.{self.componentinstancenumber}")
        pass
        #if self.child_conn is not None:
        #    self.child_conn.send("Channel Deneme")

    def on_message_from_peer(self, eventobj: Event):
        logger.debug(f"{EventTypes.MFRP} is not handled  {self.componentname}.{self.componentinstancenumber}")
        pass

    def on_exit(self, eventobj: Event):
        logger.debug(f"{EventTypes.EXIT} is not handled  {self.componentname}.{self.componentinstancenumber} exiting")
        self.terminated = True
    

    def on_init(self, eventobj: Event):
        logger.debug(f"{EventTypes.INIT} is not handled {self.componentname}.{self.componentinstancenumber} exiting")
        

         
    def queue_handler(self, myqueue):
        while not self.terminated:
            workitem = myqueue.get()
            if workitem.event in self.eventhandlers:
                self.on_pre_event(workitem)
                #logger.debug(f"{self.componentname}-{self.componentinstancenumber} will handle {workitem.event}")
                self.eventhandlers[workitem.event](eventobj=workitem)  # call the handler
            else:
                logger.error(f"{self.componentname}.{self.componentinstancenumber} Event Handler: {workitem.event} is not implemented")
            myqueue.task_done()

    def on_connected_to_component(self, name, channel):
        logger.debug(f"Connected channel-{name} by component-{self.componentinstancenumber}:{channel.componentinstancenumber}")
        
        pass

    def trigger_event(self, eventobj: Event):
        #logger.debug(f"{self.componentname}.{self.componentinstancenumber} invoked with {str(eventobj)}")
        self.inputqueue.put_nowait(eventobj)

    def on_pre_event(self, event):
        #logger.debug(f"{self.componentname}.{self.componentinstancenumber} invoked with {str(event)} will run on_pre_event here")
        pass
        
    def send_self(self, event: Event):
        #logger.debug(f"{self.componentname}.{self.componentinstancenumber} invoking itself with {str(event)}")
        self.trigger_event(event)
        
class TouegRoutingComponent(ComponentModel):
    """
    Implements a distributed routing algorithm similar to Floyd-Warshall.
    This class manages routing information across a network of nodes and computes shortest paths.
    
    Attributes:
        TOPO (object): The network topology object holding the graph information.
        DistanceInformation (dict): Stores the shortest path distance values.
        ParentInformation (dict): Stores the predecessor node for path tracing.
        all_process_ids (list): List of all node IDs in the network.
        Su (list): List of processed nodes; the algorithm terminates when all nodes are processed.
        neighbors (list): List of direct neighbors to this node.
        message_queue (list): Queue to hold messages for further processing.
        queue_lock (Lock): Lock to synchronize access to the message queue.
    """
    def __init__(self, componentname, componentid ,topology):
        """
        Initializes a new instance of TouegRoutingComponent.

        Parameters:
            componentname (str): Name of the component.
            componentid (int): Unique identifier for the component.
            topology (object): The network topology used for routing.
        """
        super(TouegRoutingComponent, self).__init__(componentname, componentid, topology=topology, num_worker_threads=3)
        # two dictionaries are indexed with the component id, hence, while broadcasting, the other nodes can easily understant whose distance information they are currently working
        self.TOPO = topology
        self.DistanceInformation = {self.componentinstancenumber: {}} # stores the shortest path distance values
        self.ParentInformation = {self.componentinstancenumber: {}}
        self.all_process_ids = []
        self.Su = [] # processed node list, algorithm terminates when all nodes are processed...
        self.neighbors = [] # the list of neighbors (ids) connected to main node...
        self.message_queue = [] # for the next invication clear it...
        self.queue_lock = Lock()

    def on_init(self, eventobj: Event):
        """
        Handles the initialization event for the component. Starts the routing algorithm in a separate thread.

        Parameters:
            eventobj (Event): The event object containing initialization details.
        """
        super(TouegRoutingComponent, self).on_init(eventobj)
        # the first process does not start immediate, it stars with a peer message
        
        thread = Thread(target=self.job, args=[45, 54, 123])
        thread.start()

    def on_message_from_bottom(self, eventobj: Event):
        """
        Processes messages received from lower layers or subsystems, filtering them by target ID.

        Parameters:
            eventobj (Event): The event object containing message details.
        """    
        message_destination = eventobj.eventcontent.header.messageto.split("-")[1]
        if int(message_destination) == int(self.componentinstancenumber): # process only the messages targeted to this component...
            message_source_id = eventobj.eventcontent.header.messagefrom.split("-")[1]
            message_type = eventobj.eventcontent.header.messagetype
            content = eventobj.eventcontent.payload
            if message_type == "INFO" or message_type == "DISTANCE":
                self.queue_lock.acquire() # protect message_queue, both component thread and Toueg thread are trying to access data
                self.message_queue.append((int(message_source_id), message_type, content))
                self.queue_lock.release()

        message_header = eventobj.eventcontent.header
        message_target = eventobj.eventcontent.header.messageto.split("-")[1]
        if message_target == int(0):
            if self.componentinstancenumber == 0:
                if message_header.messagetype == "INITIATEROUTE":
                    thread = Thread(target=self.job, args=[45, 54, 123])
                    thread.start()

    def on_message_from_peer(self, eventobj: Event):
        message_header = eventobj.eventcontent.header
        message_target = eventobj.eventcontent.header.messageto.split("-")[0]
        if message_target == "TouegRoutingComponent":
            if self.componentinstancenumber == 0:
                if message_header.messagetype == "INITIATEROUTE":
                    thread = Thread(target=self.job, args=[45, 54, 123])
                    thread.start()

    def job(self, *arg):
        """
        The main job function for the routing component which computes the shortest paths using the TOUEG algorithm.

        Parameters:
            args (tuple): Contains parameters passed to the job, usually configuration or context.
        """
        self.all_process_ids = []
        self.neighbors = self.TOPO.get_neighbors(self.componentinstancenumber) # retrieve all neighbor ids...

        self.neighbor_weights = {a: 1 for a in self.neighbors} # for the time being each edge weight is 1...
        for i in range (len(self.TOPO.G.nodes)) :
            self.all_process_ids.append(i)

        neighbor_ids = [a for a in self.neighbors]
        # found shortest path information will be sent to Coordinator component
        message_payload = self.TOUEG(self.all_process_ids, neighbor_ids, self.neighbor_weights)
        message_header = GenericMessageHeader("ROUTINGCOMPLETED", self.componentname+"-"+str(self.componentinstancenumber),
                                              "Coordinator-"+str(self.componentinstancenumber))
        message = GenericMessage(message_header, message_payload)
        #print(message)
        #broadcast it !
        #event = Event(self, EventTypes.MFRP, message)
        #self.send_peer(event)


    def TOUEG(self, vertices, neigbors, neighbor_weights):
        """
        Implements the TOUEG algorithm for distributed routing, calculating shortest paths in a network.

        Parameters:
            vertices (list): List of all vertex IDs in the network.
            neighbors (list): List of neighbor vertex IDs for the current node.
            neighbor_weights (dict): Dictionary mapping neighbor vertex IDs to their respective edge weights.
        """    
        self.process_id = self.componentinstancenumber
        self.Su = set([])
        self.ParentInformation = {self.process_id: {}}
        for v in vertices:
            if v == self.process_id:
                self.DistanceInformation[self.process_id][v] = 0
                self.ParentInformation[self.process_id][v] = v
            elif v in neigbors:
                self.DistanceInformation[self.process_id][v] = neighbor_weights[v]
                self.ParentInformation[self.process_id][v] = v;
            else:
                self.DistanceInformation[self.process_id][v] = float("inf")
                self.ParentInformation[self.process_id][v] = None

        # For pivot selection, nodes are labeled with their process id
        unordered_vertices = [a for a in vertices]
        unordered_vertices.sort()
        sorted_ids = unordered_vertices
        current_pivot_index = 0
        vertices = set(vertices)
        while len(vertices.difference(self.Su)) != 0 : # Su != Vertices should be...
            pivot = sorted_ids[current_pivot_index]
            # print(f"Process {self.process_id} picks pivot={pivot}")
            for neighbor in neigbors:
                if self.ParentInformation[self.process_id][pivot] == neighbor:
                    self.sendMessageToNeighbor(neighbor, "INFO", "Child("+str(pivot)+")")
                else:
                    self.sendMessageToNeighbor(neighbor, "INFO", "NotChild("+str(pivot)+")")
            # wait for a specific number of messages
            while True:
                t = self.getPendingChildMessageCount(pivot)
                if t != len(neigbors):
                    time.sleep(0.4)
                else:
                    break

            if self.DistanceInformation[self.process_id][pivot] < float("inf"):
                if self.process_id != pivot:

                    D_pivot = self.waitPivotDistanceFrom(self.ParentInformation[self.process_id][pivot], pivot)
                    while D_pivot is None:
                        D_pivot = self.waitPivotDistanceFrom(self.ParentInformation[self.process_id][pivot], pivot)

                    for neighbor in neigbors:
                        if self.getParticularChildMessage(neighbor, pivot):
                            self.sendMessageToNeighbor(neighbor, "DISTANCE", (pivot, D_pivot))
                    for vertex in vertices:
                        if self.DistanceInformation[self.process_id][vertex] > self.DistanceInformation[self.process_id][pivot] + D_pivot[pivot][vertex]:
                            self.DistanceInformation[self.process_id][vertex] = self.DistanceInformation[self.process_id][pivot]+D_pivot[pivot][vertex]
                            self.ParentInformation[self.process_id][vertex] = self.ParentInformation[self.process_id][pivot]
                elif self.process_id == pivot:
                    received_child_messages = []
                    for neighbor in neigbors:
                        if self.getParticularChildMessage(neighbor, pivot):
                            received_child_messages.append(neighbor)
                    for neighbor in received_child_messages:
                        self.sendMessageToNeighbor(neighbor, "DISTANCE", (pivot, self.DistanceInformation))

            self.Su.add(pivot)
            current_pivot_index += 1
        print(f"\n\nPath Finding has been completed {self.process_id} - {self.DistanceInformation} - {self.ParentInformation}")
        return (self.DistanceInformation, self.ParentInformation)


    def sendMessageToNeighbor(self, neighbor_id, message_type, message):
        message_header = GenericMessageHeader(message_type, TouegRoutingComponent.__name__+"-"+str(self.componentinstancenumber),
        TouegRoutingComponent.__name__+"-"+str(neighbor_id), interfaceid=str(self.componentinstancenumber)+"-"+str(neighbor_id))
        mess_ = GenericMessage(message_header, message)
        event = Event(self, EventTypes.MFRT, mess_)
        self.send_down(event)

    def getPendingChildMessageCount(self, pivot):
        child_message_count = 0
        for i in self.message_queue:
            if i[1] == "INFO" and (("Child(" + str(pivot) + ")" == i[2]) or ("NotChild(" + str(pivot) + ")" == i[2])):
                child_message_count += 1
        return child_message_count

    def waitPivotDistanceFrom(self, source, pivot):
        self.queue_lock.acquire()
        for index, i in enumerate(self.message_queue):
            if i[0] == source and i[1] == "DISTANCE" and i[2][0] == pivot:
                data = self.message_queue.pop(index)
                self.queue_lock.release()
                return data[2][1]
        self.queue_lock.release()
        return None

    def getParticularChildMessage(self, neigh, pivot):
        self.queue_lock.acquire()
        for index, i in enumerate(self.message_queue):
            if i[0] == neigh and i[1] == "INFO" and "Child("+str(pivot)+")" == i[2]:
                data = self.message_queue.pop(index)
                self.queue_lock.release()
                return True
        self.queue_lock.release()
        return False

