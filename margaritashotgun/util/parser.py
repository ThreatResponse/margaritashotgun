import re


class ProcNetTcpParser():

    def parse(self, proc_data):
        """
        """
        tcp_connections = []
        lines = proc_data.split('\n')
        header = re.sub('\s+', ' ', lines[0]).strip().split(' ')
        for line in lines[1:-1]:
            fields = re.sub('\s+', ' ', line).strip().split(' ')
            res = dict([ (v, fields[i]) for i, v in enumerate(header) ])
            tcp_connections.append(self.__decode_connection(res))

        return tcp_connections

    def __decode_connection(self, conn):
        """
        """
        local_addr = self.__decode_address(conn['local_address'])
        remote_addr = self.__decode_address(conn['rem_address'])
        return (local_addr, remote_addr)


    def __decode_address(self, address):
        """
        """
        hex_addr, hex_port = address.split(':')
        addr_list = self.__split_every_n(2, hex_addr)
        addr_list.reverse()
        addr = ".".join(map(lambda x: str(int(x, 16)), addr_list))
        port = str(int(hex_port, 16))
        return "{}:{}".format(addr, port)

    def __split_every_n(self, n, data):
        """
        """
        return [data[i:i+n] for i in range(0, len(data), n)]
