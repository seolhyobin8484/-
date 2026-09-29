# TAECHO - LoL 내전 관리 디스코드 봇

Google Sheets API 연동 기반 리그 오브 레전드 내전 전적 관리 및 승률 순위 조회 디스코드 봇입니다.

## 주요 기능

- **전적 / 승률 순위 조회**: 시트 데이터를 기반으로 상위 순위 및 개인 전적 출력
- **유저 등록 UI**: Discord Dropdown 및 Modal을 통한 회원 정보 입력 및 시트 자동 추가
- **메모리 캐싱**: Google Sheets API Rate Limit 방지 및 응답 속도 최적화를 위한 시트 데이터 캐싱

## 파일 구조

```text
├── war_main.py      # 디스코드 봇 명령어 및 UI 이벤트 처리
├── war_excel.py     # gspread 연동, 데이터 파싱 및 캐시 관리
└── README.md
