과제 중
1번 2번은 구현했습니다.
그런데 ssl 부분도 조금 해 보려다가 문제가 생긴게
ssl 통신이 중간에 들어오게 되면 프로그램이 멈추는 듯 합니다.
ssl 이외의 80 포트를 통한 통신은 제대로 proxying이 되는 듯 합니다.
그리고 internet explorer 기준으로 했기에 internet explorer로 테스트 해 주시면 될 듯 하고
ssl 통신이 중간에 이상하게 끼어드는 경우 빼고는
www.naver.com과 test.gilgil.net에서 정상적으로 로딩이 되는 것과
data change도 제대로 되는 것을 테스트해 보았습니다. 
한 가지 아쉬운 점은 시간 문제 때문에 content-length를 바꾸는 과정에서
content-length 필드 자체의 길이에 의한 변화를 고려해 주지 못했다는 것이었습니다.

socket programming이 처음이라 blocking, nonblocking 부분에서 되게 고생했네요
어쨌든 유익했고 socket programming에 대해서 따로 배워 봤으면 하는 생각입니다

==================================================
[1시쯤 새로 commit한 이유]
제가 세팅한 환경에서는 돌아갔는데 중간에 ssl 끼어드는 부분이 계속 걸려서 그 부분을 조금 수정해 봤습니다...
한 번 더 확인하고 제출했어야 하는데 죄송합니다