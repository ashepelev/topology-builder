__author__ = 'ash'

#import socket
import threading
import time
import SocketServer
import YamlDoc
import BandwidthHistory
import Node
import os




class TrafficServer:

    def __init__(self):
        self.start_time = 0
        self.refresh_time = 2
        self.bw_id = 0
        self.traffic_stat = dict()

        self.get_topology()
        self.bw_hist = BandwidthHistory.BandwidthHistory(self.node_list,self.edge_list)

        self.router_id = self.get_router_id()
        self.node_dict = self.get_node_dict()

        self.previous_packet_data = dict()


    def launch(self,port):
        HOST, PORT ='0.0.0.0', port
        server = MyThreadedTCPServer((HOST, PORT),MyTCPHandler)
        server.traffic = self
        server_thread = threading.Thread(target=server.serve_forever)
        #server_thread.daemon = True
        server_thread.start()
        start_time = time.clock()
        print("Server started!")

    def get_topology(self):
        yd = YamlDoc.YamlDoc('current-topology/nodes.yaml','current-topology/edges.yaml')
        self.node_list = yd.node_list
        self.edge_list = yd.edge_list

    def get_node_dict(self):
        node_dict = dict()
        for x in self.node_list:
            if not isinstance(x,Node.Switch):
                node_dict[x.ip_addr] = x.id
        return node_dict

    def get_router_id(self):
        for x in self.node_list:
            if isinstance(x,Node.Router):
                return x.id
        print "No router found"


class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.hostname = self.request.getsockname()[0]
        traffic_server = self.server.traffic
        print 'Connected: ' + str(self.request.getsockname())
        while True:
            capt_time = time.clock()
            """
            if capt_time - traffic_server.start_time > traffic_server.refresh_time:
                self.process_bandwidth(capt_time)
                traffic_server.bw_id += 1
                traffic_server.start_time = capt_time
                traffic_server.traffic_stat.clear()
            """
            data = self.get_data()
            if len(data) < 5:
                continue
            self.handle_data(data)

    def handle_data(self,data):
        for data_chunk in data:
            traffic_records = data_chunk.split(',')
            traffic_server = self.server.traffic
            for i in range(0,len(traffic_records)):
                traf = traffic_records[i]
                split_data = traf.split('|')
                (src_id,dst_id,leng) = self.get_packet_info(split_data)
                #   pk = Packet(src,dst,leng)
                #	print "Packet handled: Src: " + src + " Dst: " + dst + " Length: " + leng
                if (src_id,dst_id) not in traffic_server.traffic_stat:
                    traffic_server.traffic_stat[(src_id,dst_id)] = 0
                traffic_server.traffic_stat[(src_id,dst_id)] += int(leng)
                """
                if len(split_data) < 3:
                    remains_data = True
                    traffic_server[self.hostname] = remains_data
                else:

                """
    def get_packet_info(self,split_data):
        traffic_server = self.server.traffic
        src = split_data[0]
        if src not in traffic_server.node_dict:
            src_id = traffic_server.router_id
        else:
            src_id = traffic_server.node_dict[src]

        dst = split_data[1]
        if dst not in traffic_server.node_dict:
            dst_id = traffic_server.router_id
        else:
            dst_id = traffic_server.node_dict[dst]

        leng = split_data[2]

        return (src_id,dst_id,leng)

    def process_bandwidth(self,capt_time):
        traffic_server = self.server.traffic
        print "Bandwidth Refresh"
        os.system("clear")
        for k in traffic_server.traffic_stat.keys():
            bandwidth = traffic_server.traffic_stat[k] / (capt_time - traffic_server.start_time)
            (src,dst) = k
            traffic_server.bw_hist.append((src,dst),bandwidth,capt_time,traffic_server.bw_id)
            print "Src: " + src + " Dst: " + dst + " Bandwidth: " + bandwidth
		 	

    def get_data(self):
        data = ""
        while self.request.recv != 0:

            data.append(self.request.recv(2048))
        print("{}: data accepted: {}".format(self.hostname, data))
        return data


class MyThreadedTCPServer(SocketServer.ThreadingMixIn,
        SocketServer.TCPServer):
    pass

#if __name__ =="__main__":
ts = TrafficServer()
ts.get_topology()
ts.launch(12345)
