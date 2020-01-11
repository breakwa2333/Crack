# Crack 裂缝
A light anonymous proxy based on TLS to avoid network censorship.
一个轻量级匿名代理，基于TLS帮助躲避审查。
## ABOUT THIS PROJECT 关于本项目
* In order to prove both HTTP/WS and camouflage website isn't a necessary factor to crack the wall, this project simply use TCP+TLS as the transport methord only.
* Goal for this project is to balance the speed, security and stability that could someday replace Shadowsocks, ShadowsocksR even V2RAY.
* 证明 HTTP/WS 和网站伪装不是过墙的重要因素，本项目只使用TCP+TLS作为传输方式。
* 本项的目标是平衡速度，安全以及稳定性，有朝一日可以取代Shadowsocks、ShadowsocksR甚至V2RAY。
## TO DO LIST 未来目标
* ~~Auto mode (Crack built-in automatic mode to avoid DNS leaks caused by PAC)~~ (Finished)
* Proxy for UDP data
* TLS Pre-Handshake (Reduce latency)
* Link Aggregation (Increase single-thread bandwidth during peak hours)
* ~~自动模式（Crack内建自动模式，避免因PAC造成的DNS泄露）~~ (已完成)
* UDP数据代理
* TLS预握手（减少延迟）
* 链路聚合（高峰时段增加单线程带宽）
## PROJECT STATUS 项目状态
* 2019/12/30
  * Support HTTP proxy for TCP data only.
  * Lower CPU usage than before.
  * 目前仅支持TCP数据HTTP代理。
  * 相比之前更少的CPU占用。
* 2019/12/31
  * Support switching servers.
  * 支持切换服务器。
* 2020/01/02
  * Support built-in auto mode, avoid DNS leaks caused by PAC.
  * Speed up server verification speed.
  * 支持内建自动模式，避免因PAC模式造成的DNS泄露。
  * 加速服务器认证速度。
* 2020/01/05
  * Support Certificate Authority Root Certificate.
  * Fix path escape characters under Windows environment.
  * 支持证书颁发机构根证书。
  * 修复Windows下路径转义符问题。
* 2020/01/08
  * Reduce 1-RTT latency.
  * 减少1-RTT延迟。
* 2020/01/11
  * Support SOCKS5 proxy for TCP data.
  * 支持TCP数据SOCKS5代理。
## PROFILE KEYWORDS 配置文件关键字
* LocalServer 本地服务器
  * 'mode' 内置路由模式，现有3种模式：'global','auto','none'
    * 'global' 全局模式，此关键字将导致所有流经本地代理的流量全部转发至代理服务器。
    * 'auto' 自动模式，此关键字将导致所有流经本地代理的流量根据chinalist排除国内流量，剩余流量将全部转发至代理服务器。
    * 'none' 直连模式，此关键字将导致所有流经本地代理的流量全部直接转发到对应服务器。
  * 'active' 当前所选择使用的服务器
  * 'uuid' 发送至服务器的认证ID(一个服务器仅限一个)
  * 'ca' CA根证书，现有2种模式：'default',自签CA根证书路径
    * 'default' 默认模式，此关键字将导致加载系统已安装的所有受信任CA机构根证书
    * 自签CA根证书路径 自定义模式，此关键字将仅加载路径所指定的自签CA根证书
  * 'server_host' 服务器主机名
  * 'server_port' 服务器监听的端口
  * 'local_port' 指定本地服务器监听的端口
  * 'china_list_path' china_list文件路径
* Server 服务器
  * 'uuids' 合法认证ID列表
  * 'crt' 服务器证书路径
  * 'key' 服务器私钥路径
  * 'port' 指定服务器监听端口
