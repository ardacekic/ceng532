from adhoccomputing.Generics import *
import networkx as nx
from adhoccomputing.Generics import *
import numpy as np
from threading import Lock
import queue
import adhoccomputing.GenericModel as GenericModel1
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
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=5, topology=None, child_conn=None, node_queues=None, channel_queues=None):
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

class FredericksonAlgorithmSimpleComponent(ComponentModel):
    def __init__(self, componentname, componentid, topology):
        super(FredericksonAlgorithmSimpleComponent, self).__init__(componentname, componentid, topology=topology)
        self.TOPO = topology
        self.queue_lock = Lock()
        self.message_queue = []

        if self.componentinstancenumber == 0:
            self.is_initiator = True
        else:
            self.is_initiator = False   

    def on_init(self, eventobj: Event):
        super(FredericksonAlgorithmSimpleComponent, self).on_init(eventobj)
        self.job([45, 54, 123])

    def on_message_from_bottom(self, eventobj: Event):
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


    def on_message_from_peer(self, eventobj: Event):
        print("anything?")
        message_header = eventobj.eventcontent.header
        message_target = eventobj.eventcontent.header.messageto.split("-")[0]
        if message_target == FredericksonAlgorithmSimpleComponent.__name__:
            if self.is_initiator:
                if message_header.messagetype == "INITIATEBFSCONSTRUCTION":
                    self.job([45, 54, 123])

    def job(self, *arg):
        self.neighbors = self.TOPO.get_neighbors(self.componentinstancenumber)  # retrieve all neighbor ids...
        self.neighbor_weights = {a: 1 for a in self.neighbors}  # for the time being each edge weight is 1...

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