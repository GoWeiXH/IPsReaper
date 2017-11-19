# -*- coding: utf-8 -*-
from gevent import monkey;monkey.patch_all()
from bs4 import BeautifulSoup
from itertools import islice
import random,time,os
import urllib3
import certifi
import gevent

from reaperError import LackDataError,AnalysisError
from tools import Tools

class IPReaper():

    """
    IPReaper类，是主体核心类
    """

    #todo load ips
    #todo deduplication
    #todo email


    def __init__(self,proxy=None):
        """
        初始化IPReaper

        :param proxy: 要使用的代理ip，格式为：
            协议://IP地址:端口号
            举例： https://192.168.0.1:88
        """
        # 创建工具类
        self._tool = Tools()

        # 加载读取配置文件
        self.config = self.load_config()

        # IP缓存列表，通过get_**_ips()添加搜索到的IP，test_ips()读取此列表
        self.ip_catch_lib = []

        # 存放最终可用 IP 的列表
        self.ip_ok_lib = []

        # 设定超时时间
        timeout = urllib3.Timeout(connect=self.config["connect_timeout"],
                                  read=self.config["read_timeout"])

        # 若配置中 proxy 的值为 False，则不使用代理，创建普通 Manager
        # 若proxy 的值为 True，则使用代理，创建代理 Manager
        # cert_reqs="CERT_REQUIRED", ca_certs=certifi.where()是为了解决 urllib3 中对 https 的验证问题
        if not self.config["proxy"]:
            self.manager = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where(),
                                               timeout=timeout,)
        else:
            if proxy:
                self.manager = urllib3.ProxyManager(proxy,cert_reqs="CERT_REQUIRED", ca_certs=certifi.where(),
                                                timeout=timeout,)
            else:
                # 若参数 proxy 值为 None ，则抛出缺少 proxy 的异常
                msg = "proxy"
                raise LackDataError(msg)

        # 通过配置中的 判断是否存在此文件夹，若不存在则创建
        if not os.path.exists(self.config["abs_dir"]):
            os.makedirs(self.config["abs_dir"])

        # 调用测试连接的方法，决定要爬取的 IP 网站
        self.connect_test()


    def load_config(self):
        """
        读取加载文件：同级目录下的 config.txt
        并赋值给类属性 config，以供其他方法共享、调用
        """
        config = {}

        # 读取配置文件中的参数的类型是字符串，但以下参数值得类型不应该是字符串
        # 所以构建此列表，以供后续处理其中对应的值
        need_eval = ["proxy","connect_timeout","read_timeout","frequency"]
        config_file = os.path.abspath("config.txt")
        with open(config_file,"rt") as config_file:
            for item in config_file:
                item = self._tool.strip(item)
                key,value = item.split("=")
                if value == "":
                    msg = "'" + key + "'"
                    # 如果只获取到了 key 而没有获取到对应 value，则抛出解析错误异常
                    raise AnalysisError(msg)
                # 将字符串值转换为相应类型
                config[key] = eval(value) if key in need_eval else value
        self._tool.print_format("Loading config")

        # 设置各可配置项的默认值
        config.setdefault("proxy",False)
        config.setdefault("dir_name", "ips_lib/")
        config.setdefault("abs_dir", os.path.abspath(config["dir_name"]))

        #暂时只支持 html.parser，后续加入 lxml 等解析器
        config.setdefault("parser", "html.parser")
        config.setdefault("connect_timeout", 3)
        config.setdefault("read_timeout", 6)

        # frequency 指的是 每 {n} 秒请求一次 ip网站
        #
        config.setdefault("frequency", 6)

        # 用来测试 IP 是否可用的网站，可以设置成你自己以后要爬去的目标网站
        config.setdefault("test_domain", "https://book.douban.com/")
        self._tool.print_dict(config)
        return config

    def load_ips(self):
        """
        从缓存列表中获取爬到的代理IP
        :return: 存放代理IP的列表
        """
        return self.ip_ok_lib

    def get_html(self,url,encoding="utf8"):
        """
        :param url: 要访问的 url
        :param encoding: 默认字符集编码为 UTF-8
        :return: 返回请求的页面
        """
        response = self.manager.request("GET", url)
        html = BeautifulSoup(response.data.decode(encoding), self.config["parser"])
        return html

    def get_xici_ips(self):
        """
        获取 西刺网站 的 IP
        """
        base_url = ["http://www.xicidaili.com/nn/", # 国内高匿代理
                    "http://www.xicidaili.com/nt/", # 国内透明（普通）代理
                    "http://www.xicidaili.com/wn/", # 国内 HTTPS 代理
                    "http://www.xicidaili.com/wt/"] # 国内 HTTP 代理
        # 命名索引 协议，地址，端口号
        protocol,addr,port = 5,1,2
        for url in base_url:
            # 每个 url 访问 2 页，为了获取最近验证成功的IP，暂时写死，以后考虑可配置
            for n in range(0, 2):
                path = url if n == 0 else url + str(n)
                html = self.get_html(path)
                trs = html.select("#ip_list tr")[1::]
                for t in trs:
                    tds = t.select("td")
                    ip_path = tds[protocol].text.lower() + "://" + tds[addr].text + ":" + tds[port].text
                    print("xici.com : get ip {0}".format(ip_path))
                    self.ip_catch_lib.append(ip_path)
                time.sleep(self.config["frequency"])


    def get_66_ips(self):
        """
         获取 66网站 的 IP
        """
        base_url = ["http://www.66ip.cn/nmtq.php?proxytype=0", #http
                    "http://www.66ip.cn/nmtq.php?proxytype=1"] #https

        # 每次随机选取一个 url，一共进行 4 次
        for n in range(4):
            url = random.choice(base_url)
            html = self.get_html(url,"gbk")
            tag = list(islice(html,10,49))[0::2]
            pre = "http://" if url.endswith("0") else "https://"
            for t in tag:
                if t is None: continue
                ip_path = pre + self._tool.strip(t)
                print("66ip.com : Get ip {0}".format(ip_path))
                self.ip_catch_lib.append(ip_path)
            time.sleep(self.config["frequency"])


    def get_kuai_ips(self):
        """
        获取 快代理网站 的 IP
        """
        # 选取四个 url ，为了选取最近验证成功的 IP，暂时写死，以后考虑可配置
        base_url = ["http://www.kuaidaili.com/free/inha/",
                    "http://www.kuaidaili.com/free/inha/2/",
                    "http://www.kuaidaili.com/free/intr/",
                    "http://www.kuaidaili.com/free/intr/2/"]
        # 命名索引 协议，地址，端口号
        protocol, addr, port = 3, 0, 1
        for url in base_url:
            html = self.get_html(url)
            trs = html.select("#list tr")[1::]
            for tr in trs:
                tds = tr.select("td")
                ip_path = tds[protocol].text.lower()+"://"+tds[addr].text+":"+tds[port].text
                print("kuai.com : Get ip {0}".format(ip_path))
                self.ip_catch_lib.append(ip_path)
            time.sleep(self.config["frequency"])


    def test_ips(self):
        """
        测试爬取到的 IP 是否可用
        """
        timeout = urllib3.Timeout(connect=3,read=6)
        for ip in self.ip_catch_lib:
            # 将暂时可用的IP保存至 ips_ok.txt
            file = open(self.config["abs_dir"]+"/ips_ok.txt", "at")
            try:

                manager = urllib3.ProxyManager(ip,cert_reqs="CERT_REQUIRED", ca_certs=certifi.where(),
                                               timeout=timeout,)
                rep = manager.request("GET",self.config["test_domain"])
                # 如果 response headers 的状态码为 200，则说明此 IP 可用
                if rep.status == 200:
                    self.ip_ok_lib.append(ip)
                    file.write(ip+"\n")
                    print("Test success and saved ip: {0}".format(ip))
            # retry 次数过多则抛出此异常
            except urllib3.exceptions.MaxRetryError:
                print("{0} Test failed ".format(ip))
            # 处理其他未知异常
            except Exception as e:
                print("Problems :{0}".format(e))
            finally:
                file.close()
        self._tool.print_format("Test finished")
        self._tool.count_ip(self.config["abs_dir"])


    def connect_test(self):
        """
        测试要爬取的目标网站 此时 是否可用
        """
        manager = self.manager
        # 暂时支持以下三个网站，后续更新添加
        # key 为目标网站在IPReaper类中的方法名称，以供后续 eval()
        base_ip_com ={"get_xici_ips":"http://www.xicidaili.com/",
                      "get_66_ips": "http://www.66ip.cn/",
                      "get_kuai_ips":"http://www.kuaidaili.com/"}
        # 存储 此时 可爬去的 IP 网站
        self.ok_com = []
        self._tool.print_format("Connection test")
        for name,url in base_ip_com.items():
            # 对同一网站重复 3 次请求（实际上 urllib3 中的 request 已经有 retry 次数）
            # 以后会对此问题进行优化
            for n in range(3):
                print("{0}th url:{1}".format(n+1,url))
                try:
                    rep = manager.request("GET",url)
                    if rep.status == 200:
                        # 状态码为 200，则测试成功，此网站可用
                        self.ok_com.append((name,url))
                        print("success")
                        break
                except urllib3.exceptions.MaxRetryError:
                    print("fail")
        self._tool.print_format("Test finished")


    def run_reaper(self):
        """
        运行 reaper 爬虫
        """
        # 存储添加了可爬取网站对应方法的协程
        func_list = []
        for (func_name,domain_url) in self.ok_com:
            # 通过 eval() 将字符串的方法名 转换为 方法对象
            func = eval("self."+func_name)
            # 使用协程
            func_list.append(gevent.spawn(func))
            print("function {0} is ready: {1}".format(func_name,domain_url))
        self._tool.print_format("IPReaper running")
        # 将所有协程 join 并 运行
        gevent.joinall(func_list)

