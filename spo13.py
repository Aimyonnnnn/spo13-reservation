import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
import easyocr
import re
import schedule
from webdriver_manager.chrome import ChromeDriverManager

# 실제 운영용 설정
reservation_settings = [
    {   
        "username": "hg8501081",
        "password": "nigimi36!!",
        "place": "22",
        "time_no": "723",
        "team_name": "김형",
        "users": "4",
        "purpose": "테니스",
        "discount_reason": "다자녀가정"
    }
]

def setup_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    return chrome_options

def get_time_range(time_no):
    # 기존 time_mapping 코드 유지...
    time_mapping = {
        '686': '0600%3B0800', #1번
        '687': '0800%3B1000',
        '688': '1000%3B1200',
        '689': '1200%3B1400',
        '690': '1400%3B1600',
        '691': '1600%3B1800',
        '692': '1800%3B2000',
        '693': '2000%3B2200',
        '701': '2000%3B2200',
        '719': '0800%3B1000', #2번
        '720': '1000%3B1200',
        '721': '1200%3B1400',
        '722': '1400%3B1600',
        '723': '1600%3B1800',
        '724': '1800%3B2000',
        '725': '2000%3B2200',
        '734': '0600%3B0800', #3번
        '735': '0800%3B1000',
        '736': '1000%3B1200',
        '737': '1200%3B1400',
        '738': '1400%3B1600',
        '739': '1600%3B1800',
        '740': '1800%3B2000',
        '741': '2000%3B2200',
        '758': '0600%3B0800', #4번
        '759': '0800%3B1000',
        '760': '1000%3B1200',
        '761': '1200%3B1400',
        '762': '1400%3B1600',
        '763': '1600%3B1800',
        '764': '1800%3B2000',
        '765': '2000%3B2200',
        '782': '0600%3B0800', #5번
        '783': '0800%3B1000',
        '784': '1000%3B1200',
        '785': '1200%3B1400',
        '786': '1400%3B1600',
        '787': '1600%3B1800',
        '788': '1800%3B2000',
        '789': '2000%3B2200',
    }
    return time_mapping.get(time_no, 'unknown_time')

def wait_for_target_time(target_hour, target_minute, target_second):
    """지정된 시간까지 대기"""
    target_time = datetime.time(target_hour, target_minute, target_second)
    
    while True:
        current_time = datetime.datetime.now().time()
        if current_time >= target_time:
            print(f"목표 시각 도달: {target_time}")
            break
        if current_time.second % 5 == 0:  # 5초마다 한 번씩만 출력
            print(f"대기 중: 현재 시각 {current_time}, 목표 시각 {target_time}")
        time.sleep(0.1)  # 0.1초마다 체크

def reserve_court(username, password, place, time_no, team_name, users, purpose, discount_reason):
    print(f"예약 프로세스 시작 - {team_name}")
    chrome_options = setup_chrome_options()
    
    driver_path = ChromeDriverManager().install()
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # 로그인
        print("웹사이트 접속 중...")
        driver.get('https://nrsv.spo1.or.kr/fmcs/42?center=SPOONE&part=11&place=24')
        
        print("로그인 시도 중...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="process_login"]/span'))
        )
        login_button.click()

        main_window = driver.current_window_handle
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        new_window = [window for window in driver.window_handles if window != main_window][0]
        driver.switch_to.window(new_window)

        id_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="textfield01"]'))
        )
        id_field.send_keys(username)
        password_field = driver.find_element(By.XPATH, '//*[@id="textfield02"]')
        password_field.send_keys(password)
        login_submit_button = driver.find_element(By.XPATH, '//*[@id="buttom01"]')
        login_submit_button.click()

        try:
            alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
            print(f"로그인 알림: {alert.text}")
            alert.accept()
        except:
            print("로그인 알림 없음")

        driver.switch_to.window(main_window)
        print("로그인 완료")

        # 예약 페이지 URL 준비
        now = datetime.datetime.now()
        target_date = now + datetime.timedelta(days=7)
        target_date_str = target_date.strftime('%Y%m%d')
        time_range = get_time_range(time_no)
        dynamic_url = f"https://nrsv.spo1.or.kr/fmcs/42?facilities_type=T&center=SPOONE&part=11&base_date={target_date_str}&action=write&place={place}&comcd=SPOONE&part_cd=11&place_cd={place}&time_no={time_no}%3B2%ED%9A%8C%EC%B0%A8%3B{time_range}%3B1&rent_type=1001&rent_date={target_date_str}"

        
        # 예약 페이지 열릴 때까지 새로고침
        print("예약 페이지 새로고침 시작...")
        refresh_count = 0
        while True:
            try:
                driver.get(dynamic_url)
                team_name_field = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="team_nm"]'))
                )
                print("예약 페이지 접속 성공!")
                break
            except:
                refresh_count += 1
                if refresh_count % 5 == 0:  # 5회 새로고침마다 한 번씩만 출력
                    print(f"예약 페이지 새로고침 중... (시도 횟수: {refresh_count})")
                continue

        # 예약 정보 입력
        print("예약 정보 입력 중...")
        team_name_field.send_keys(team_name)
        users_field = driver.find_element(By.XPATH, '//*[@id="users"]')
        users_field.send_keys(users)
        purpose_field = driver.find_element(By.XPATH, '//*[@id="purpose"]')
        purpose_field.send_keys(purpose)
        discount_reason_field = driver.find_element(By.XPATH, '//*[@id="place_item_1_dc"]')
        discount_reason_field.send_keys(discount_reason)
        agree_check = driver.find_element(By.XPATH, '//*[@id="agree_use1"]')
        agree_check.click()

        # CAPTCHA 처리
        print("CAPTCHA 처리 시작...")
        reader = easyocr.Reader(['ko', 'en'])
        captcha_attempts = 0
        max_captcha_attempts = 10
        captcha_success = False

        while captcha_attempts < max_captcha_attempts and not captcha_success:
            captchaPng = driver.find_element(By.XPATH, '//*[@id="captcha_string_image"]')
            result = reader.readtext(captchaPng.screenshot_as_png, detail=0)
            captchaValue = ''.join(re.findall(r'\d+', result[0]))
            print(f"CAPTCHA 시도 중: {captchaValue}")

            captchaText = driver.find_element(By.XPATH, '//*[@id="captcha"]')
            captchaText.send_keys(captchaValue)

            captcha_submit = driver.find_element(By.XPATH, '//*[@id="writeForm"]/fieldset/div[4]/div/div[4]/button')
            captcha_submit.click()

            try:
                alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
                alert_text = alert.text
                print(f"CAPTCHA 결과: {alert_text}")

                if "입력문자가 맞지않습니다." in alert_text:
                    alert.accept()
                    driver.find_element(By.XPATH, '//*[@id="writeForm"]/fieldset/div[4]/div/div[2]/button[1]/span').click()
                    captchaText.clear()
                    captcha_attempts += 1
                elif "입력문자가 맞습니다." in alert_text:
                    alert.accept()
                    captcha_success = True
                    print("CAPTCHA 통과!")
                    break
            except:
                print("CAPTCHA 알림 없음, 통과로 간주")
                captcha_success = True
                break

        if not captcha_success:
            print("CAPTCHA 실패")
            return

        # 예약 시간까지 대기
        print("CAPTCHA 완료, 예약 시간 대기 중...")
        # wait_for_target_time(9, 0, 7)  # 반드시 09:00:06까지 대기

        # 최종 예약 버튼 클릭
        print("최종 예약 버튼 클릭")
        facility_reserve = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="writeForm"]/fieldset/p[2]/button/span'))
        )
        facility_reserve.click()
        print(f"{team_name} 예약 완료!")

        # 결과 확인을 위해 10초 대기
        print("예약 결과 확인을 위해 10초 대기...")
        time.sleep(10)

    except Exception as e:
        print(f"오류 발생: {str(e)}")
        import traceback
        print(traceback.format_exc())
    finally:
        print("브라우저 종료")
        driver.quit()

def run_reservation():
    """모든 예약을 동시에 실행하는 함수"""
    print(f"=== 예약 프로세스 시작 시각: {datetime.datetime.now()} ===")
    threads = []
    
    # 각 예약을 별도의 스레드로 실행
    for setting in reservation_settings:
        thread = threading.Thread(target=reserve_court, kwargs=setting)
        threads.append(thread)
        thread.start()

    # 모든 스레드가 완료될 때까지 대기
    for thread in threads:
        thread.join()
    
    print("=== 모든 예약 프로세스 완료 ===")

def main():
    print("예약 즉시 실행 중...")
    run_reservation()

if __name__ == "__main__":
    main()
