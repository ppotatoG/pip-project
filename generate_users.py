import json
import random
from datetime import datetime, timedelta

# 유저 수
NUM_USERS = 100

# 유저 이름 생성용 리스트
FIRST_NAMES = [
    "김", "이", "박", "최", "정", "강", "조", "윤", "장", "임",
    "오", "한", "신", "서", "권", "황", "안", "송", "류", "홍"
]

LAST_NAMES = [
    "민준", "서연", "도윤", "지우", "하준", "서연", "지민", "지후",
    "준우", "예준", "서현", "지안", "도현", "은우", "지유", "유준",
    "시우", "하은", "민서", "지호"
]

# 화요일과 목요일을 나타내는 리스트
DAYS = ["화요일", "목요일"]

# 가능한 시간대 (24시간 형식)
WORK_START = 6  # 6시
WORK_END = 20   # 20시
CORE_START = 11 # 11시
CORE_END = 15   # 15시

# 회의 시작 시 분 단위 (0, 15, 30, 45)
MINUTES_OPTIONS = [0, 15, 30, 45]

# 회의 소요 시간 (분 단위, 최소 30분, 최대 120분, 15분 단위)
DURATION_OPTIONS = [30, 45, 60, 75, 90, 105, 120]

def generate_user_name(existing_names):
    while True:
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first}{last}"
        if name not in existing_names:
            return name

def generate_meetings():
    meetings = {}
    for day in DAYS:
        num_meetings = random.randint(1, 6)  # 하루에 1~6개의 회의
        meeting_list = []
        attempts = 0
        max_attempts = 100  # 무한 루프 방지
        while len(meeting_list) < num_meetings and attempts < max_attempts:
            attempts += 1
            start_hour = random.randint(WORK_START, WORK_END - 1)
            start_minute = random.choice(MINUTES_OPTIONS)
            start_time = f"{start_hour:02d}:{start_minute:02d}"
            # 회의 소요 시간 결정
            if start_hour == 12 and start_minute == 0:
                duration = 120  # 점심시간 회의는 2시간
            else:
                duration = random.choice(DURATION_OPTIONS)
            # 종료 시간 계산
            start_dt = datetime.strptime(start_time, "%H:%M")
            end_dt = start_dt + timedelta(minutes=duration)
            end_time = end_dt.strftime("%H:%M")
            # 워크 시간 내인지 확인
            if end_dt.hour > WORK_END or (end_dt.hour == WORK_END and end_dt.minute > 0):
                continue
            # 회의 시간 겹치는지 확인
            overlap = False
            for m in meeting_list:
                existing_start = datetime.strptime(m['start_at'], "%H:%M")
                existing_end = datetime.strptime(m['end_at'], "%H:%M")
                if (start_dt < existing_end and end_dt > existing_start):
                    overlap = True
                    break
            if not overlap:
                meeting_list.append({"start_at": start_time, "end_at": end_time})
        meetings[day] = meeting_list
    return meetings

def calculate_availability(meetings):
    availability = {}
    for day in DAYS:
        available_slots = []
        # 전체 근무 시간: 6:00 ~ 20:00
        current_time = datetime.strptime(f"{WORK_START:02d}:00", "%H:%M")
        end_of_day = datetime.strptime(f"{WORK_END:02d}:00", "%H:%M")
        # 회의 리스트를 시간 순으로 정렬
        day_meetings = sorted(meetings[day], key=lambda x: x['start_at'])
        for meeting in day_meetings:
            meeting_start = datetime.strptime(meeting['start_at'], "%H:%M")
            meeting_end = datetime.strptime(meeting['end_at'], "%H:%M")
            # 회의 전 가용 시간 추가
            while current_time < meeting_start:
                available_slots.append(current_time.strftime("%H:%M"))
                current_time += timedelta(minutes=15)
            # 회의 후 시간으로 이동
            current_time = meeting_end
        # 회의 후 남은 가용 시간 추가
        while current_time < end_of_day:
            available_slots.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=15)
        availability[day] = available_slots
    return availability

def generate_users():
    users = []
    existing_names = set()

    for i in range(NUM_USERS):
        name = generate_user_name(existing_names)
        existing_names.add(name)
        meetings = generate_meetings()
        availability = calculate_availability(meetings)
        user = {
            "name": name,
            "meetings": meetings,  # 각 요일별 회의 리스트
            "availability": availability  # 각 요일별 가용 시간 리스트 (HH:MM 형식)
        }
        users.append(user)
    return users

def save_users_to_file(users, filename='users.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)
    print(f"{len(users)}명의 유저 정보가 '{filename}' 파일로 저장되었습니다.")

if __name__ == "__main__":
    users = generate_users()
    save_users_to_file(users)
