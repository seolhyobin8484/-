# LoL 내전 관리 디스코드 봇


## 주요 기능
- **전적 / 승률 순위 조회**: 시트 데이터를 기반으로 상위 순위 및 개인 전적 출력
- **유저 등록 UI**: Discord Dropdown 및 Model을 통한 회원 정보 입력 및 시트 자동 추가
- **메모리 캐싱**: Google Sheets API Rate Limit 방지 및 응답 속도 최적화를 위한 시트 데이터 캐싱



<img width="1427" height="608" alt="Image" src="https://github.com/user-attachments/assets/e87c8047-7964-43a2-8d00-96375c37d617" />
<img width="1427" height="780" alt="Image" src="https://github.com/user-attachments/assets/1b26890d-f472-44fe-b299-02a7a87fc504" />
Google Sheet로 게임 인원들의 정보와 라인 별 점수판을 만듭니다.

<img width="614" height="674" alt="Image" src="https://github.com/user-attachments/assets/d3c2f329-4554-4742-bdea-026c46eb9243" />
<img width="1069" height="511" alt="Image" src="https://github.com/user-attachments/assets/b373118e-06d1-4ab7-864c-2b2934e964a8" />
디스코드 계정으로 접속해서 연동된 봇에게 명령어를 입력하면 Google Sheet와 연동되어 디스코드에서도 엑셀 내의 정보를 확인할 수 있습니다.


---

- **Language:** Python 3.10+
- **Library:** `discord.py` (v2.0+), `gspread`, `google-auth`
- **Database / Storage:** Google Sheets API v4

---
