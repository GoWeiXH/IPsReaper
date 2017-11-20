# IPsReaper

__Version__ ：1.0.0  
__Author__ : Jacky Wei  
__Last Update Time__ : 2017.11.17  
__Encoding__ : UTF-8</br>


1. ### 综述
    * 这是一个爬取代理IP的项目。  
    * 但本人技术不足，尚有很多功能没有实现，还有很多地方可以优化，希望各位前辈、大神指导！  
    * 本项目会持续更新。  
    * 目前支持爬取代理网站：西刺、66、快代理。

2. ### 使用方法
    * 在自己的项目中输入：  
    <pre><code>
    from reaper import IPReaper
    rp = IPReaper(proxy=None)
    rp.run_reaper()
    rp.test_ips()
    </code></pre>

3. ### 数据
    * 最终爬取到的 IP，存储在 ips_ok.txt 文件中。若使用，可以读取该文件。
    * 若要使用爬取到的IP，可在程序中使用
                <pre><code>
                
                # 1.从缓存中获取
                rp.get_ips_from_cache()
                
                # 2.从文件中获取
                rp.get_ips_from_file()
                
                # 3.从文件中读取，以生成器的方式返回
                rp.generate_ips()
                
                </code></pre>

4. ### 配置文件  **config.txt，可配置选项**

    * proxy ：（布尔，默认 False) 决定是否使用代理。  
                若使用代理，则在初始化时应传入参数 proxy。  
                例：  
                <pre><code>
                proxy = "https://115.200.37.94:80"  
                rp = IPReaper(proxy=proxy)  
                </code></pre>
    * dir_name ：（字符串，默认 ips_lib/）存放最终 IP 的相对路径。  
    * abs_dir ：（字符串，可配可不配）存放最终 IP 的绝对路径。配置后，则 dir_name 失效。  
    * connect_timeout ：（数字，默认 3）连接超时的时间，若对应时间内无响应则放弃访问。urllib3 中每个 request 请求默认 retry 3次，若3次都无响应，则总共耗费时间为 9 秒。
    * read_timeout ：（数字，默认 6）读取相应超时的时间。
    * frequency ：（数字，默认 6）访问网站的频率，默认每 6 秒访问一次。很多网站设置阈值为每 5 秒 1 次，注意频率。  
    * test_domain ：测试 IP 是否可用的域名，可以设置成使用代理IP要爬取的网站。