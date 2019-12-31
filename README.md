# Crack 裂缝
A light proxy based on TLS to avoid network censorship.
一个轻量级代理，基于TLS帮助躲避审查。
## ABOUT THIS PROJECT 关于本项目
* In order to prove both HTTP/WS and camouflage website isn't a necessary factor to crack the wall, this project simply use TCP+TLS as the transport methord only.
* 证明 HTTP/WS 和网站伪装不是过墙的重要因素，本项目只使用TCP+TLS作为传输方式。
* Goal for this project is to balance the speed, security and stability that could someday replace Shadowsocks, ShadowsocksR even V2RAY.
* 本项的目标是平衡速度，安全以及稳定性，有朝一日可以取代Shadowsocks、ShadowsocksR甚至V2RAY。
## TO DO LIST 未来目标
* DNS Proxy
* DNS代理
* Proxy for UDP data
* UDP数据代理
* TLS Pre-Handshake (Reduce latency)
* TLS预握手（减少延迟）
* Link Aggregation (Increase single-thread bandwidth during peak hours)
* 链路聚合（高峰时段增加单线程带宽）
## PROJECT STATUS 项目状态
* 2019/12/30 First Release
  * Support proxy for TCP data only.
  * Lower CPU usage than before.
