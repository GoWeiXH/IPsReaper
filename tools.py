# -*- coding: utf-8 -*-
class Tools():

    """
    此类包含了一些处理工具（方法）
    """

    def print_dict(self,dict_data):
        """
        将传入的字典对象进行格式化打印
        :param dict_data: 字典数据
        """
        for key,value in dict_data.items():
            print("{0}: {1}".format(key,value))

    def print_format(self,str_data):
        """
        将传入的字符串进行格式化打印
        :param str_data: 字符串数据
        """
        print("-"*20 + str_data +"-"*20)

    def strip(self,str):
        """
        删除 str中的 ['\n','\r' ,'\t',' ']
        :param str:旧字符串
        :return:删除后的字符串
        """
        #todo update in re
        str = str.replace("\n","").replace(" ","").replace("\r","").replace("\t","")
        return str

    def count_ip(self,abs_path):
        """
        统计此次任务最终保存的ip数量，并打印
        :param path: 存储 ips_ok.txt 的绝对路径
        """
        ok_txt = len(open(abs_path+"\\"+"ips_ok.txt","rt").readlines())
        print("The number of available ip is {0}".format(ok_txt))