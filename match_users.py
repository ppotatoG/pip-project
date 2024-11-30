import json
import os
from datetime import datetime, timedelta

USERS_FILE = 'users.json'

def load_users(filename=USERS_FILE):
    if not os.path.exists(filename):
        print(f"유저 정보 파일 '{filename}'이 존재하지 않습니다. 먼저 유저 정보를 생성해주세요.")
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_time_available(user, day, time):
    # 유저의 가용 시간에 해당 시간이 포함되는지 확인
    return time in user['availability'].get(day, [])

def get_matching_users(users, user_name, day, time):
    # 입력된 유저가 존재하는지 확인
    user = next((u for u in users if u['name'] == user_name), None)
    if not user:
        print(f"유저 '{user_name}'을(를) 찾을 수 없습니다.")
        return []

    # 입력된 시간에 해당 유저가 가능한지 확인
    if not is_time_available(user, day, time):
        # 유저가 정확한 시간에 불가능하다면, 회의가 끝난 후 가능한지 확인
        # 예: 매치 시간이 11:00이고, 회의가 10:30에 끝난다면 가능
        # 또는 회의가 11:15에 끝난다면 불가능
        # 따라서 매치 시간과 유저의 회의 끝 시간을 비교

        # 해당 유저의 회의 리스트를 가져옴
        meetings = user['meetings'].get(day, [])
        match_time_dt = datetime.strptime(time, "%H:%M")
        possible = False

        for meeting in meetings:
            meeting_end_dt = datetime.strptime(meeting['end_at'], "%H:%M")
            buffer = timedelta(minutes=15)  # 회의 종료 후 15분 버퍼
            if meeting_end_dt <= match_time_dt:
                # 회의가 매치 시간 전에 끝난 경우, 사용 가능
                possible = True
                break
            elif match_time_dt < meeting_end_dt <= match_time_dt + buffer:
                # 회의가 매치 시간 근처에 끝나는 경우, 사용 가능 여부 물어봄
                # 여기서는 간단히 사용 가능하다고 가정하거나, 추가 로직을 구현할 수 있음
                possible = True
                break

        if possible:
            print(f"유저 '{user_name}'은(는) {day} {time}시에 직접적으로는 매칭할 수 없지만, 회의가 종료된 후 참여할 수 있습니다.")
        else:
            print(f"유저 '{user_name}'은(는) {day} {time}시에 매칭할 수 없습니다.")
        return []

    # 매칭 가능한 다른 유저 찾기
    matching_users = []
    for u in users:
        if u['name'] == user_name:
            continue  # 자신은 제외
        if is_time_available(u, day, time):
            matching_users.append(u['name'])

    return matching_users

def validate_time_format(time_str):
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

def main():
    users = load_users()
    if not users:
        return

    print("=== e-Sports 매칭 봇 ===")
    user_name = input("당신의 이름을 입력하세요: ").strip()

    # 원하는 매치 시간 입력 받기
    print("\n원하는 매치 시간을 입력하세요.")
    day = input("요일을 입력하세요 (화요일 또는 목요일): ").strip()
    if day not in ["화요일", "목요일"]:
        print("잘못된 요일입니다. '화요일' 또는 '목요일'을 입력하세요.")
        return

    time = input("시간을 입력하세요 (HH:MM 형식, 예: 10:15): ").strip()
    if not validate_time_format(time):
        print("시간 형식이 잘못되었습니다. 'HH:MM' 형식으로 입력하세요.")
        return

    matching_users = get_matching_users(users, user_name, day, time)

    if matching_users:
        print(f"\n{day} {time}시에 매칭 가능한 유저 목록 ({len(matching_users)}명):")
        for name in matching_users:
            print(f"- {name}")
    else:
        print(f"\n{day} {time}시에 매칭 가능한 유저가 없습니다.")

if __name__ == "__main__":
    main()
