# -*- coding:utf-8 -*-
from selenium import webdriver;
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from pyquery import PyQuery as pq
import math, time
from PIL import Image
from io import BytesIO

EMAIL = 'test@geetest.com';
PASSWORD = '123456';

class CrackGeetest():
    def __init__(self):
        self.url = 'https://account.geetest.com/login';
        chrome_options = webdriver.ChromeOptions();
        chrome_options.add_argument('start-maximized');
        self.browser = webdriver.Chrome(chrome_options=chrome_options);
        self.wait = WebDriverWait(self.browser, 20);
        self.email = EMAIL;
        self.password = PASSWORD;
        self.left = 0;

    def initpage(self):
        try:
            self.browser.get(self.url);
            input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.input-box #email')));
            password = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.input-box #password')));
            input.clear();
            input.send_keys(self.email);
            password.clear();
            password.send_keys(self.password);
        except TimeoutException as e:
            print('TimeOut Ocurrs, retrying....');
            self.initpage();
    
    def get_geetest_button(self):
        button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.geetest_radar_btn')));
        return button;

    def get_position(self):
        img = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.geetest_canvas_img')));
        time.sleep(2);
        location = img.location;
        size = img.size;
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size['width'];
        return (top, bottom, left, right);
    
    def get_screenshot(self):
        screenshot = self.browser.get_screenshot_as_png();
        screenshot = Image.open(BytesIO(screenshot));
        return screenshot;

    def get_geetest_image(self, name='captcha.png'):
        top, bottom, left, right = self.get_position();
        self.left = left;
        screenshot = self.get_screenshot();
        captcha = screenshot.crop((left, top, right, bottom));
        return captcha;

    def get_slider(self):
        slider = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.geetest_slider_button')));
        return slider;

    def convert_image_grey(self, image):
        image = image.convert('L');
        return image;

    def convert_image_binary(self, image, threshold):
        table = [];
        for i in range(256): 
            if i < threshold:
                table.append(0);
            else:
                table.append(1);
        image =  image.point(table,'1');
        return image;

    def convert_img2pixel(self, image):
        datas = [];
        data = [];
        for y in range(image.height):
            for x in range(image.width):
                rgb = image.load()[x, y];
                data.append(rgb);
            datas.append(list(data));
            data = [];
        return datas;

    def find_start_position(self, datas):
        cols = 41;
        rows = 39;
        threshold = 13;
        finded = 0;
        matchtime = [];
        endcol = len(datas[0])-cols;
        endrow = len(datas)-rows;
        
        for i in range(endrow):
            for j in range(61, endcol):
                ltrt = 0;
                lbrb = 0;
                ltlb = 0;
                rtrb = 0;       
                for k in range(cols):
                    if datas[i][j+k] == 0:
                        ltrt += 1;
                for k in range(rows):
                    if datas[i+k][j] == 0:
                        ltlb += 1;
                for k in range(cols):
                    if datas[i+rows-1][j+k] == 0:
                        lbrb += 1;
                for k in range(rows):
                    if datas[i+k][j+cols-1] == 0:
                        rtrb += 1;
                if (ltrt+lbrb+ltlb+rtrb)/((rows+cols)*2)> 0.5:
                    matchtime.append(j);
                    break;
        
        if len(matchtime) <= 0:
            for i in range(endrow):
                for j in range(61, endcol):
                    zerocnt = 0;
                    for m in range(rows):
                        for n in range(cols):
                            if datas[i+m][j+n] ==0:
                                zerocnt += 1;
                    if zerocnt/(rows*cols) > 0.5:
                        matchtime.append(j);
                        break;
                    
        return matchtime;

    def get_track(self, distance):
        track = [];
        current = 0; 
        mid = distance *4/5;
        t = 0.2;
        v = 0;
        while current < distance:
            if current < mid:
                a = 2;
            else:
                a = -3;
            v0 = v; 
            v = v0 + a * t;  
            move = v0 * t + 1/2*a*t*t; 
            current += move;
            track.append(round(move));
        return track;

    def move_to_gap(self, slider, tracks):
        ActionChains(self.browser).click_and_hold(slider).perform();
        for x in tracks:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform(); 
        time.sleep(0.5);
        ActionChains(self.browser).release().perform();

    def get_movegap_returninfo(self):
        print('begin getting infomation that after moveing.');
        time.sleep(3);
        html = self.browser.page_source;
        doc = pq(html);
        item = doc('.geetest_success_radar_tip_content');
        returninfo = item.text();
        print('returninfo:',returninfo, '.' );
        return returninfo;

    def correct_matchtime(self, matchtime):
        matchtime.sort();
        oldval = 0;
        newmatchtime=[];
        if len(matchtime) > 1:
            for n in range(len(matchtime)):
                if matchtime[n] != oldval:
                    newmatchtime.append(matchtime[n]);
                    oldval = matchtime[n];
        return newmatchtime;
    
def main():
    jytest.initpage(); 
    button = jytest.get_geetest_button();
    button.click();
    image = jytest.get_geetest_image();
    image = jytest.convert_image_grey(image);
    threshold = 50;
    distance = 0;
    while threshold < 180:
        threshold += 10;
        image1 = jytest.convert_image_binary(image, threshold);
        datas = jytest.convert_img2pixel(image1);
        matchtime = jytest.find_start_position(datas);
        if len(matchtime) > 0:
            break;
    matchtime = jytest.correct_matchtime(matchtime);
    slider = jytest.get_slider(); 
    textinfo = '';
    if len(matchtime) > 0:
        for distance in matchtime:
            distance -= 6; 
            tracks = jytest.get_track(distance); 
            jytest.move_to_gap(slider, tracks); 
            textinfo = jytest.get_movegap_returninfo();
            if textinfo == '验证成功':
                break;
            else:
                time.sleep(3);
                
    return textinfo;
    
if __name__ == '__main__':
    MAX_RETRY = 10;
    current_times = 0;
    jytest = CrackGeetest();
    textinfo = main();
    while textinfo != '验证成功':
            textinfo = main();
            if textinfo == '验证成功':
                break;
            current_times += 1;
            print('Retry Times:', current_times);
            if current_times >= 10:
                print('Retry Times reacherd 10, Verify Faild! Quting...');
                break;
