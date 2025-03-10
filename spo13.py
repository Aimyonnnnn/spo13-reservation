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
import os
import shutil

# Selenium Manager 비활성화
os.environ["SELENIUM_MANAGER"] = "0"

# 실제 운영용 설정
reservation_settings = [
    {
        "username": "jihae0716",
        "password": "Wlgofkd3369!",
        "place": "23",
        "time_no": "739",
        "team_name": "박지해",
        "users": "4",
        "purpose": "테니스",
        "discount_reason": "다자녀가정"
    }
]

def setup_chrome_options(unique_id):
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-cache')
    chrome_options.add_argument('--disable-cookies')  # 추가
    chrome_options.add_argument('--incognito')  # 추가
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--no-first-run')
    return chrome_options

def get_time_range(time_no):
    time_mapping = {
        '686': '0600%3B0800', '687': '0800%3B1000', '688': '1000%3B1200', '689': '1200%3B1400',
        '690': '1400%3B1600', '691': '1600%3B1800', '692': '1800%3B2000', '693': '2000%3B2200',
        '701': '2000%3B2200', '719': '0800%3B1000', '720': '1000%3B1200', '721': '1200%3B1400',
        '722': '1400%3B1600', '723': '1600%3B1800', '724': '1800%3B2000', '725': '2000%3B2200',
        '734': '0600%3B0800', '735': '0800%3B1000', '736': '1000%3B1200', '737': '1200%3B1400',
        '738': '1400%3B1600', '739': '1600%3B1800', '740': '1800%3B2000', '741': '2000%3B2200',
        '758': '0600%3B0800', '759': '0800%3B1000', '760': '1000%3B1200', '761': '1200%3B1400',
        '762': '1400%3B1600', '763': '1600%3B1800', '764': '1800%3B2000', '765': '2000%3B2200',
        '782': '0600%3B0800', '783': '0800%3B1000', '784': '1000%3B1200', '785': '1200%3B1400',
        '786': '1400%3B1600', '787': '1600%3B1800', '788': '1800%3B2000', '789': '2000%3B2200',
    }
    return time_mapping.get(time_no, 'unknown_time')

def wait_for_target_time(target_hour, target_minute, target_second):
    target_time = datetime.time(target_hour, target_minute, target_second)
    while True:
        current_time = datetime.datetime.now().time()
        if current_time >= target_time:
            print(f"목표 시각 도달: {target_time}")
            break
        if current_time.second % 5 == 0:
            print(f"대기 중: 현재 시각 {current_time}, 목표 시각 {target_time}")
        time.sleep(0.1)

def reserve_court(username, password, place, time_no, team_name, users, purpose, discount_reason):
    print(f"예약 프로세스 시작 - {team_name}")
    # 고유한 ID 생성 (스레드 ID와 타임스탬프 조합)
    unique_id = f"{threading.get_ident()}-{int(time.time())}"
    chrome_options = setup_chrome_options(unique_id)
    
    driver = None
    try:
        chromedriver_path = '/usr/local/bin/chromedriver'
        print(f"ChromeDriver 경로 확인: {chromedriver_path}")
        if os.path.exists(chromedriver_path):
            print("ChromeDriver 파일 존재함")
        else:
            print("ChromeDriver 파일이 존재하지 않음!")
        
        # Chrome 기본 디렉토리 초기화
        default_chrome_dir = "/root/.config/google-chrome"
        if os.path.exists(default_chrome_dir):
            shutil.rmtree(default_chrome_dir)
            print(f"기본 Chrome 디렉토리 {default_chrome_dir} 삭제 완료")

        # ChromeDriver 로그 활성화
        service = Service(executable_path=chromedriver_path, log_path=f'/tmp/chromedriver-{unique_id}.log')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
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

        now = datetime.datetime.now()
        target_date = now + datetime.timedelta(days=7)
        target_date_str = target_date.strftime('%Y%m%d')
        time_range = get_time_range(time_no)
        dynamic_url = f"https://nrsv.spo1.or.kr/fmcs/42?facilities_type=T¢er=SPOONE&part=11&base_date={target_date_str}&action=write&place={place}&comcd=SPOONE&part_cd=11&place_cd={place}&time_no={time_no}%3B2%ED%9A%8C%EC%B0%A8%3B{time_range}%3B1&rent_type=1001&rent_date={target_date_str}"

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
                if refresh_count % 5 == 0:
                    print(f"예약 페이지 새로고침 중... (시도 횟수: {refresh_count})")
                continue

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

        print("최종 예약 버튼 클릭")
        facility_reserve = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="writeForm"]/fieldset/p[2]/button/span'))
        )
        facility_reserve.click()
        print(f"{team_name} 예약 완료!")

        print("예약 결과 확인을 위해 10초 대기...")
        time.sleep(10)

    except Exception as e:
        print(f"오류 발생: {str(e)}")
        import traceback
        print(traceback.format_exc())
    finally:
        print("브라우저 종료")
        if driver is not None:
            driver.quit()

def run_reservation():
    print(f"=== 예약 프로세스 시작 시각: {datetime.datetime.now()} ===")
    threads = []
    
    for setting in reservation_settings:
        thread = threading.Thread(
            target=reserve_court,
            kwargs={
                'username': setting['username'],
                'password': setting['password'],
                'place': setting['place'],
                'time_no': setting['time_no'],
                'team_name': setting['team_name'],
                'users': setting['users'],
                'purpose': setting['purpose'],
                'discount_reason': setting['discount_reason']
            }
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    
    print("=== 모든 예약 프로세스 완료 ===")

def main():
    print("즉시 예약 테스트 시작...")
    run_reservation()
    print("테스트 완료!")

if __name__ == "__main__":
    main()
