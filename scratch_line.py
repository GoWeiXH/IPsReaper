# -*- coding: utf-8 -*-

from reaper import IPReaper

if __name__ == '__main__':
    # proxy = "https://115.200.37.94:80"
    # rp = IPReaper(proxy=proxy)
    rp = IPReaper(proxy=None)
    rp.run_reaper()
    rp.test_ips()