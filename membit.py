#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
from bitmap import BitMap

class Show:
    def __init__(self):
        pass
    def show(self,mapfile):
        """Get echo pfn and fill the index bit

        Args:
            index: the pfn of the page

        Returns:
           0 is success.
        """
        print mapfile._bm.tostring()

        return 0

class Mapfile:
    """Mapfile define class.

    Attributes:
        _name: node name.
        _node: node index.
        _size: bitmap file size.
    """
    _name = ''
    _node = 0
    _start = 0
    _end = 0
    _size = 0
    _bm = None

class Process:
    """Main File Process Class.

    This class help for:
        1. read info from kernel dump file
        2. fill one bitmap file
        3. pass the result Class Show to display the bitmap picture.

    Attributes:

    """
    _file = None
    _debug = 0

    _curr_pfn = 0
    _curr_order = 0
    _curr_node = -1

    _pattern_n = None
    _pattern_l = None
    _pattern_h = None
    _zone_list = []

    def __init__(self, path, debug=0):
        self._debug = debug
        self._file = open(path)
        #TODO
        #self.pattern_n = re.compile(r'\s')
        self.pattern_h = re.compile(r'Node')
        self.pattern_d = re.compile(r'\d+')

    def read_lines(self):
        line = self._file.readline()
        while(line):
            info = self.parse(line)
            if (info[0] == -1):
                if(self._debug):
                    print 'pfn ' + str(info[1][0]) + \
                          '     order ' + str(info[1][1])
            else:
                if(self._debug):
                    print 'zone ' + str(info[0]) + \
                          '     start ' + str(info[1][0]) + \
                          '      end ' + str(info[1][1])

            line = self._file.readline()

    def parse(self, line):
        is_header = self.pattern_h.search(line)

        ret = self.pattern_d.findall(line)
        if(is_header):
            #self._name = self.pattern_n.search(line)
            self._curr_node = self._curr_node + 1
            mapfile = Mapfile()
            mapfile._start = int(ret[1])
            mapfile._end = int(ret[2])
            mapfile._size = int(ret[2]) - int(ret[1]) + 1
            mapfile._bm = BitMap(mapfile._size)
            self._zone_list.append(mapfile)
            return [int(ret[0]),[int(ret[1]),int(ret[2])]]  #return this node pfn start/end number
        else:
            self.fill_bitmap(self._curr_node, int(ret[0]), int(ret[1]))
            return [-1, [int(ret[0]), int(ret[1])]]   #return pfn and order

    def fill_bitmap(self,node, index, order):
        """Get echo pfn and fill the index bit

        Args:
            node: which node need to fill.
            index: the pfn of the page.
            order: fill how many bits.
        Returns:
           0 is success.
        """
        bm = self._zone_list[node]._bm

        if (self._zone_list[node]._start > 0 ):
            index = index - self._zone_list[node]._start

        limit = index + (1 << order)
        while ( index < limit ):
            bm.set(index)
            index = index + 1

        return 1 << order

    def get_zone_num(self):
        return self._curr_node + 1


if __name__ == "__main__":
    process = Process('membitmap',0)
    sh = Show()
    process.read_lines()
    for mapfile in process._zone_list:
        sh.show(mapfile)
