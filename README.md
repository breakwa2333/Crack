# Crack 裂缝
A light proxy based on TLS to avoid network censorship.
一个轻量级代理，基于TLS帮助躲避审查。
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
  * Support proxy for TCP data only.
  * Lower CPU usage than before.
  * 目前仅支持TCP数据代理
  * 相比之前更少的CPU占用
* 2019/12/31
  * Support switching servers.
  * 支持切换服务器
* 2020/01/02
  * Support built-in auto mode, avoid DNS leaks caused by PAC.
  * 支持内建自动模式，避免因PAC模式造成的DNS泄露。
  * Speed up server verification speed.
  * 加速服务器认证速度。
