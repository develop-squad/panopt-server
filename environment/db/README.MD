<div align="center">
  <img align="center" src="logo.png" alt="panopt-logo" width="240">
  <br/>
  <h1>서버 DB 명세서</h1>
</div>

<h1 align="center">기본 명세서</h1>

## MESSAGE TYPE  
0 : 분류 없음  
1 : 일반 메시지  
2 : 알림 메시지  
3 : 경고 메시지  
4 : 위험 메시지  

## PROCESS TYPE  
TODO  

## PROCESS LEVEL  
TODO  

## PACKET TYPE  
TODO  

## NETWORK STATUS  
TODO  

## NETWORK TYPE  
TODO  

## PROTOCOL TYPE  
TODO  

<h1 align="center">DEVICES<h4 align="center">디바이스 테이블입니다</h4></h1>

## device_index
`int(11)`  
device index  

## device_id  
`varchar(45)`  
device id  

## device_created  
`timestamp`
device created datetime  

<h1 align="center">MESSAGES<h4 align="center">클라이언트에 전달하는 메시지 테이블입니다</h4></h1>

## message_index  
`int(11)`  
message index  

## message_device  
`int(11)`  
message target device  
related by **device_index**  
if _0_, it is global message  

## message_sent  
`int(11)`  
message sent to target devices  
if _0_, it is not sent  
if _1_, it is sent to target device  

## message_type  
`int(11)`  
message type  
check **MESSAGE_TYPE**  

## message_title  
`varchar(45)`  
message title  

## message_content  
`varchar(45)`  
message content  

## message_data  
`varchar(45)`  
message data  

<h1 align="center">PROCESSES<h4 align="center">프로세스 테이블입니다</h4></h1>

## process_index  
`int(11)`  
process index  

## process_name  
`varchar(45)`  
process name  

## process_type  
`int(11)`  
process type  
check **PROCESS_TYPE**  

## process_level  
`int(11)`  
process warning level  

<h1 align="center">PACKETS<h4 align="center">패킷 테이블입니다</h4></h1>

## packet_index  
`int(11)`  
packet index  

## packet_device  
`int(11)`  
packet owner device  
related by **device_index**  

## packet_process  
`int(11)`  
packet owner process  
related by **process_index**  

## packet_network  
`int(11)`  
packet releated network index  
related by **network_index**  

## packet_type  
`int(11)`  
packet type  
check **PACKET_TYPE**  

## packet_srcip  
`varchar(45)`  
packet source ip  

## packet_dstip  
`varchar(45)`  
packet destination ip  

## packet_srcdevice  
`varchar(45)`  
packet source device  

## packet_dstdevice  
`varchar(45)`  
packet destination device  

## packet_protocol  
`int(11)`  
packet protocol  
check **PROTOCOL_TYPE**  

## packet_srcport  
`int(11)`  
packet source port  

## packet_dstport  
`int(11)`  
packet destination port  

## packet_length  
`int(11)`  
packet length  

<h1 align="center">NETWORKS<h4 align="center">패킷 그룹인, 네트워크 테이블입니다</h4></h1>

## network_index  
`int(11)`  
network index  

## network_device  
`int(11)`  
network owner device  
related by **device_index**  

## network_process  
`int(11)`  
network owner process  
related by **process_index**  

## network_status  
`int(11)`  
network status  
check **NETWORK STATUS**  

## network_start  
`timestamp`  
network start time  

## network_end  
`timestamp`  
network end time  

## network_type  
`int(11)`  
network type  
check **NETWORK_TYPE**  

## network_srcip  
`varchar(45)`  
network source ip  

## network_dstip  
`varchar(45)`  
network destination ip  

## network_srcdevice  
`varchar(45)`  
network source device  

## network_dstdevice  
`varchar(45)`  
network destination device  

## network_protocol  
`int(11)`  
network protocol  
check **PROTOCOL_TYPE**  

## network_srcport  
`int(11)`  
network source port  

## network_dstport  
`int(11)`  
network destination port  

## network_srcpackets  
`int(11)`  
network packets sent by source device  

## network_dstpackets  
`int(11)`  
network packets sent by destination device  

## network_srcbytes  
`int(11)`  
network bytes sent by source device  

## network_dstbytes  
`int(11)`  
network bytes sent by destination device  
