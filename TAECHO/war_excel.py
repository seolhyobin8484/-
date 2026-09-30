import gspread
import unicodedata
import io
import requests
from PIL import Image, ImageDraw, ImageFont

from google.oauth2.service_account import Credentials

# 1. 구글 시트 연동 설정
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    r"D:\vs_workspace\TAECHO\teacho-bot-3535cc9506ef.json",
    scopes=scopes
)

gc = gspread.authorize(creds)
spreadsheet = gc.open_by_key("1WkLsskfIjLqdS18tnqmFKy4Xk9svVrUum-DnEacwviQ")

# 시트 객체 정의
member_sheet = spreadsheet.worksheet("명단")
win_rate_sheet = spreadsheet.worksheet("내전승률")
board_10p = spreadsheet.worksheet("10인 내전")
line_sheet = spreadsheet.worksheet("라인별 승률")

# 캐시 변수 초기화
_member_cache = None
_win_cache = None
_board_10p_cache = None
_line_sheet_cache = None

medal_map = {1: "🥇", 2: "🥈", 3: "🥉", 4: "4️⃣", 5: "5️⃣"}

# 2. 캐시 새로고침 함수들
def member_refresh_cache():
    global _member_cache
    _member_cache = member_sheet.get_values("B31:CC1000") 

def win_rate_refresh_cache():
    global _win_cache
    _win_cache = win_rate_sheet.get_values("B3:Z1000")

def board_10p_refresh_cache():
    global _board_10p_cache
    _board_10p_cache = board_10p.get_values("B4:AC100")

def line_sheet_cache():
    global _line_sheet_cache
    _line_sheet_cache = line_sheet.get_values("A1:O9999")

# 3. [내부 헬퍼 함수] 명단 시트에서 디스코드 ID로 유저 행 찾기 (중복 제거용)
def _find_member_row(discord_id):
    global _member_cache
    if _member_cache is None: 
        member_refresh_cache()
        
    target_id = str(discord_id).strip().lower()
    for row in _member_cache:
        if row and any(str(cell).strip().lower() == target_id for cell in row):
            return row
    return None


# 4. 메인 기능 함수들
def exists_user(discord_id):
    return _find_member_row(discord_id) is not None

class user_profile:
            
    def get_nickname(discord_id):
        row = _find_member_row(discord_id)
        if row:
            return row[0].strip() if len(row) > 0 and row[0] else "이름없음"
        return "등록 안됨"

    def get_lol_id(discord_id):
        row = _find_member_row(discord_id)
        if row:
            return row[1].strip() if len(row) > 1 else "이름없음"
        return "등록 안됨"

    def get_toprate(discord_id):
        row = _find_member_row(discord_id)
        if row:
            return (row[5].strip() + row[6].strip()) if len(row) > 6 else "이름없음"
        return "등록 안됨"

    def get_totalscore(discord_id):
        row = _find_member_row(discord_id)
        if row:
            return row[39].strip() if len(row) > 39 else "총점없음"
        return "등록 안됨"

    def get_win_rate(discord_id):
        global _win_cache
        if _win_cache is None: 
            win_rate_refresh_cache()
        
        nickname = user_profile.get_nickname(discord_id)

        for row in _win_cache:
            if row and len(row) > 2 and row[2].strip() == nickname.strip():
                
                if len(row) > 13:
                    return f"{row[13]} ({row[3]}전 {row[5]}승 {row[7]}패)"
                return "오류"
                
        return "기록 없음"
    
    def get_lane_win_rates(discord_id):

        # 1. 디스코드 ID로 시트용 실제 한글 닉네임 조회
        target_nickname = user_profile.get_nickname(discord_id)
        
        if not target_nickname or target_nickname == "등록 안됨":
            return "```text\n등록된 닉네임이 없습니다.\n```"
            
        global _line_sheet_cache
        
        # 💡 [핵심 수정] 캐시가 None이면 파일 상단 46번째 줄의 line_sheet_cache() 함수를 실행합니다.
        if _line_sheet_cache is None:
            try:
                line_sheet_cache()  # 상단에 선언된 캐시 로드 함수 실행
            except Exception as e:
                print(f"[오류] 캐시 함수 실행 중 예외 발생: {e}")
                
        # 만약 함수를 실행했음에도 구글 토큰 만료 등의 이유로 None인 경우 예외 처리
        if _line_sheet_cache is None:
            try:
                _line_sheet_cache = line_sheet.get_values("A1:O9999")
            except Exception as e:
                return "```text\n시트 데이터를 불러오지 못했습니다. (구글 연동 실패)\n```"
                
        all_rows = _line_sheet_cache
            
        lines = []
        lines.append("포지션   전적 (승/패)    라인 별 승률")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        lanes = ["TOP", "JUG", "MID", "ADC", "SUP"]
        current_nickname = None
        player_found = False
        match_count = 0
        
        for idx, row in enumerate(all_rows):
            if len(row) < 10:
                continue
                
            cell_a = str(row[0]).strip()
            cell_b = str(row[1]).strip()
            
            if "NICKNAME" in cell_a:
                continue
                
            if cell_a != "":
                current_nickname = cell_a
                
            if current_nickname == target_nickname and cell_b in lanes:
                player_found = True
                match_count += 1
                try:
                    lane_name = cell_b.ljust(6)
                    games = str(row[2]).strip()
                    wins = str(row[3]).strip()
                    losses = str(row[4]).strip()
                    record_str = f"{games}전 ({wins}승/{losses}패)".ljust(14)
                    win_rate = str(row[9]).strip()
                    
                    lines.append(f"{lane_name}   {record_str}   {win_rate}")
                except Exception as e:
                    continue
        if not player_found:
            return "```text\n내전 참여 기록이 없는 유저입니다.\n```"
            
        return "```text\n" + "\n".join(lines) + "\n```"

def get_most_wins_top5_table():
    global _board_10p_cache

    if _board_10p_cache is None:
        board_10p_refresh_cache()

    if not _board_10p_cache or len(_board_10p_cache) < 36:
        return "```데이터 없음```"

    # H35 셀이 포함된 5개의 행을 똑같이 잘라옵니다.
    top5_rows = _board_10p_cache[31:36]

    # 1. 시각적 너비 계산 함수 (한글=2, 영어/숫자=1)
    def get_visual_width(text):
        width = 0
        for char in str(text):
            if unicodedata.east_asian_width(char) in ('W', 'F'):
                width += 2
            else:
                width += 1
        return width

    # 2. 닉네임 길이를 시각적 너비 기준으로 제한 및 정렬
    def fit_name(name, width=8):
        name = str(name).strip()
        while get_visual_width(name) > width:
            name = name[:-1]
            if get_visual_width(name) <= width - 1: # "…" 자리를 위해 여유 확보
                name += "…"
                break
        return name + " " * (width - get_visual_width(name))

    lines = []
    # 최다 승리 표에 맞는 헤더 타이틀 정렬 (순위, 닉네임, 승리 수)
    lines.append("순위   닉네임     승리 수")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for row in top5_rows:
        try:
            # ⚠️ B열(0) 기준 -> H열(6)=순위, I열(7)=닉네임, J열(8)=승리수
            # 1. H열(row[6])에서 스프레드시트의 진짜 등수를 가져옵니다.
            try:
                real_rank = int(float(str(row[6]).strip()))
            except ValueError:
                real_rank = 1
            
            # 2. 진짜 등수(1, 2, 2, 4...)에 맞게 메달을 매칭합니다.
            grade = medal_map.get(real_rank, f"{real_rank}️⃣")

            name = fit_name(row[7])     # 너비 8 고정 (I열)
            wins = str(row[8]).strip()  # 승리 수 (J열)
            
            lines.append(f"{grade}   {name}   {wins}")
        except Exception:
            continue

    return "```text\n" + "\n".join(lines) + "\n```"

def get_most_plays_top5_table():
    global _board_10p_cache

    if _board_10p_cache is None:
        board_10p_refresh_cache()

    if not _board_10p_cache or len(_board_10p_cache) < 36:
        return "```데이터 없음```"

    # H35 셀이 포함된 5개의 행을 똑같이 잘라옵니다.
    top5_rows = _board_10p_cache[31:36]

    # 1. 시각적 너비 계산 함수 (한글=2, 영어/숫자=1)
    def get_visual_width(text):
        width = 0
        for char in str(text):
            if unicodedata.east_asian_width(char) in ('W', 'F'):
                width += 2
            else:
                width += 1
        return width

    # 2. 닉네임 길이를 시각적 너비 기준으로 제한 및 정렬
    def fit_name(name, width=8):
        name = str(name).strip()
        while get_visual_width(name) > width:
            name = name[:-1]
            if get_visual_width(name) <= width - 1: # "…" 자리를 위해 여유 확보
                name += "…"
                break
        return name + " " * (width - get_visual_width(name))

    lines = []
    lines.append("순위   닉네임     참여 수")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for row in top5_rows:
        try:
            try:
                real_rank = int(float(str(row[11]).strip()))
            except ValueError:
                real_rank = 1
            
            # 2. 진짜 등수(1, 2, 2, 4...)에 맞게 메달을 매칭합니다.
            grade = medal_map.get(real_rank, f"{real_rank}️⃣")

            name = fit_name(row[12])    
            plays = str(row[13]).strip()  # 내전 횟수 
            
            lines.append(f"{grade}   {name}   {plays}")
        except Exception:
            continue

    return "```text\n" + "\n".join(lines) + "\n```"

def get_win_rating_top5_table():
    global _board_10p_cache

    if _board_10p_cache is None:
        board_10p_refresh_cache()

    if not _board_10p_cache or len(_board_10p_cache) < 36:
        return "```데이터 없음```"

    top5_rows = _board_10p_cache[31:36]

    # 1. 시각적 너비 계산 함수 (한글=2, 영어/숫자=1)
    def get_visual_width(text):
        width = 0
        for char in str(text):
            if unicodedata.east_asian_width(char) in ('W', 'F'):
                width += 2
            else:
                width += 1
        return width

    # 2. 닉네임 길이를 시각적 너비 기준으로 제한 및 정렬
    def fit_name(name, width=8):
        name = str(name).strip()
        while get_visual_width(name) > width:
            name = name[:-1]
            if get_visual_width(name) <= width - 1: # "…" 자리를 위해 여유 확보
                name += "…"
                break
        return name + " " * (width - get_visual_width(name))

    lines = []
    # 헤더 정렬 맞춤 (순위: 3, 닉네임: 10, 전적: 12, 승률: 6)
    lines.append("순위   닉네임       전적        승률")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for row in top5_rows:
        try:
            # 1. 엑셀의 첫 번째 칸(row[0])에서 진짜 등수를 가져옵니다.
            try:
                real_rank = int(float(str(row[0]).strip()))
            except (ValueError):
                real_rank = 1 # 에러 발생 시 기본값 1등 처리
            
            # 2. 진짜 등수(1, 2, 2, 4...)에 맞는 메달을 딕셔너리에서 쏙 꺼내옵니다.
            # 만약 공동 8등처럼 1~5등을 벗어난 숫자가 오면 숫자 이모지(8️⃣)로 안전하게 보여줍니다.
            grade = medal_map.get(real_rank, f"{real_rank}️⃣")

            name = fit_name(row[1])       # 너비 8 고정
            record = str(row[2]).strip()  # 전적
            rate = str(row[4]).strip()    # 승률
            
            # 전적 열의 공백을 시각적 너비 기준으로 계산하여 채움
            record_width = get_visual_width(record)
            record_padding = " " * (12 - record_width)
            
            # \t(탭) 대신 기존처럼 공백으로 띄워야 디스코드나 텍스트창에서 정렬이 깨지지 않습니다.
            lines.append(f"{grade}   {name}  {record}{record_padding}  {rate}")
        except Exception:
            continue

    return "```text\n" + "\n".join(lines) + "\n```"
