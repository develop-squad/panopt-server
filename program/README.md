<div align="center">
  <img align="center" src="logo.png" alt="panopt-logo" width="240">
  <br/>
  <h1>서버 API 명세서</h1>
</div>

<h1 align="center">Basics</h1>

## SERVER INFO  
IP: 49.247.197.181  
PORT: 80  

## RESPONSE FORMAT (JSON)  
`{ code: RESPONSE_CODE }`  

데이터 응답 포함 시 해당 필드 포함  
메시지 응답 포함 시 `messages` 필드 포함  
에러 발생 시 `error` 필드 포함  

## RESPONSE_CODE (int)  
-1: unexpected error  
0: request failed  
1: request success  

## RESPONSE_MESSAGE (JSON)  
`{ type: MESSAGE_TYPE , title: ”제목”, message: ”메시지”, datetime: ”시각” }`  

프로세스 정보 포함 시 `process` 필드 포함  
패킷 정보 포함 시 `packet` 필드 포함  

## MESSAGE_TYPE (int)  
0: 분류 없음  
1: 일반 메시지  
2: 알림 메시지  
3: 경고 메시지  
4: 위험 메시지  

<h1 align="center">서버 연결<h4 align="center">서버에 연결하고자 할때 초기 1회 호출합니다</h4></h1>

## PATH
`/connect`  

## REQUEST METHOD  
POST(,GET)  

## ARGUMENT  
(string) `device`: device unique id  

## OUTPUT  
RESPONSE FORMAT  

### OUTPUT EXAMPLE  
`{ code: 1 }`  

<h1 align="center">새로운 패킷 이벤트<h4 align="center">클라이언트에 새로운 패킷 이벤트 발생 시 호출합니다</h4></h1>

## PATH  
`/users/{device}/packet`  

## REQUEST METHOD  
POST  

## ARGUMENT  
(string) `data`: csv formed packet  

## OUTPUT  
RESPONSE FORMAT  

### OUTPUT EXAMPLE  
`{ code: 1 }`  

<h1 align="center">새로운 프로세스 통신 이벤트<h4 align="center">클라이언트에 새로운 프로세스 통신 이벤트 발생시 호출합니다 </h4></h1>

## PATH  
`/users/{device}/process`  

## REQUEST METHOD  
POST  

## ARGUMENT  
(string) `data`: csv formed process network activity  

## OUTPUT  
RESPONSE FORMAT  

### OUTPUT SAMPLE  
`{ code: 1 }`  

<h1 align="center">알림 이벤트 풀링<h4 align="center">클라이언트로의 이벤트 알림이 있는지 확인합니다</h4></h1>

## PATH  
`/users/{device}/event`  

## REQUEST METHOD  
POST(,GET)  

## ARGUMENT  
X  

## OUTPUT  
RESPONSE FORMAT  

메시지 존재 시, `messages` 필드 포함  

### OUTPUT SAMPLE  
`{ code: 1, messages: [{{ type: 1 , title: ”일반 메시지 제목”, message: ”일반 메시지 내용”, datetime: ”시각” }}, {{ type: 4 , title: ”위험 메시지 제목”, message: ”위험 메시지 내용”, datetime: ”시각”, process: “Bandizip.exe” }}] }`
