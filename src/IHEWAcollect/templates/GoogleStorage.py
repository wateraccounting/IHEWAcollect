# -*- coding: utf-8 -*-
try:
    from ..base.gis import GIS
    from ..base.dtime import Dtime
except ImportError:
    from src.IHEWAcollect.base.gis import GIS
    from src.IHEWAcollect.base.dtime import Dtime


class Template(GIS, Dtime):
    status = 'Global status.'

    __status = {}
    __conf = {}

    def __init__(self, status, config, **kwargs):
        print('Template.__init__()')
        # Class self.__status < Download.__status
        self.__status = status
        # Class self.__conf <- Download.__conf
        self.__conf = config

        # super(IHE, self).__init__(status, config, **kwargs)
        GIS.__init__(self, config['path'], status['is_print'], **kwargs)
        Dtime.__init__(self, config['path'], status['is_print'], **kwargs)

        # Class GIS
        # self.latlim = self.var['lat']
        # self.lonlim = self.var['lon']
        # self.timlim = self.var['time']

        # Class Dtime

    def check(self):
        print('Template.check()')

    def download(self):
        print('Template.download()')

        from pprint import pprint
        print('\n=> Template.__status')
        pprint(self.__status)
        print('\n=> Template.__conf')
        pprint(self.__conf)

    def convert(self):
        print('Template.convert()')

    def saveas(self):
        print('Template.saveas()')
