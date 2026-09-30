# TAECHO - LoL 내전 관리 디스코드 봇
<img width="1427" height="608" alt="Image" src="https://github.com/user-attachments/assets/e87c8047-7964-43a2-8d00-96375c37d617" />

<img width="614" height="674" alt="Image" src="https://github.com/user-attachments/assets/d3c2f329-4554-4742-bdea-026c46eb9243" />

<img width="1069" height="511" alt="Image" src="https://github.com/user-attachments/assets/b373118e-06d1-4ab7-864c-2b2934e964a8" />

<img width="1427" height="780" alt="Image" src="https://github.com/user-attachments/assets/1b26890d-f472-44fe-b299-02a7a87fc504" />
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
