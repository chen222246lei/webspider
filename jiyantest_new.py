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
SLIDER_RIGHT_SIDE = 50;
SLIDER_HEIGHT = 40;

class CrackGeetest():
    def __init__(self):
        self.url = 'https://account.geetest.com/login';
        chrome_options = webdriver.ChromeOptions();
        chrome_options.add_argument('start-maximized');
        self.browser = webdriver.Chrome(chrome_options=chrome_options);
        self.wait = WebDriverWait(self.browser, 20);
        self.email = EMAIL;
        self.SLIDER_RIGHT_SIDE = SLIDER_RIGHT_SIDE;
        self.SLIDER_HEIGHT = SLIDER_HEIGHT;
        self.password = PASSWORD;
        self.left = 0;
        self.right = 0;
        self.top = 0;
        self.bottom = 0;
    
    def __delattr__(self):
        self.browser.close();
        
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
        top, bottom, left, right = location['y'], location['y'] + size['height']-30, location['x'], location['x'] + size['width'];
        self.top = top;
        self.bottom = bottom;
        self.left = left;
        self.right = right;
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
    
    def get_geetest_image2(self,  left, top, right, bottom, name='captcha.png'):
        screenshot = self.get_screenshot();
        captcha = screenshot.crop((left, top, right, bottom));
        return captcha;

    def is_pixel_equal(self, image1, image2, x, y):
        pixel1 = image1.load()[x, y];
        pixel2 = image2.load()[x, y];
        threshold = 60;
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(pixel1[2] - pixel2[2]) < threshold:
            return True;
        else:
            return False;

    def get_gap(self, image1, image2):
        left = 15;
        for i in range(left, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    top = j;
                    return top;
        return top;
        
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
        col_threshold = 20; 
        row_threshold = 23; 
        matchtime = [];
        
        def get_colzero_nums(datas, col):
            zeronum = 0;
            for row in range(len(datas)):
                if datas[row][col] == 0:
                    zeronum += 1;
            return zeronum;
        
        def get_rowzero_nums(datas, row):
            zeronum = 0;
            for col in range(len(datas[0])):
                if datas[row][col] == 0:
                    zeronum += 1;
            return zeronum;
        
        cols = len(datas[0]);
        rows = len(datas);
        leftmark = False;
        rightmark = False;
        for col1 in range(cols-1):
            col1_zeros = get_colzero_nums(datas, col1);
            col2_zeros = get_colzero_nums(datas, col1+1);
            if abs(col2_zeros - col1_zeros) >= col_threshold:
                if col1_zeros < col2_zeros and not leftmark:
                    matchtime.append(col1+1);
                    leftmark = True;
                if col1_zeros > col2_zeros and not rightmark:
                    matchtime.append(col1+1-40);
                    rightmark = True;
                if leftmark and rightmark:
                    break;
        
        rows_maxzero_lists = [];
        byond_row_threshold_rows=[];
        for row in range(rows-1):
            if get_rowzero_nums(datas, row) >= row_threshold:
                byond_row_threshold_rows.append(row);
        for i in byond_row_threshold_rows:
            row_maxzero = [0, 0];
            for j in range(cols-41):
                nozero_num = 0;
                for k in range(41):
                    if datas[i][j+k] == 0:
                        nozero_num += 1;
                if nozero_num > row_maxzero[1]:
                    row_maxzero[0] = j;
                    row_maxzero[1] = nozero_num;
            rows_maxzero_lists.append(row_maxzero);
        max_nozero_num = 0;
        col = 0;
        for row_maxzero in rows_maxzero_lists:
            if row_maxzero[1] > max_nozero_num:
                col = row_maxzero[0];
                max_nozero_num = row_maxzero[1];
        if col > 0:
            matchtime.append(col);
            
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
        time.sleep(3);
        html = self.browser.page_source;
        doc = pq(html);
        item = doc('.geetest_success_radar_tip_content');
        returninfo = item.text();
        return returninfo;

    def correct_matchtime(self, matchtime):
        matchtime.sort();
        oldval = 0;
        newmatchtime=[];
        if len(matchtime) > 1:
            for n in range(len(matchtime)):
                if matchtime[n] != oldval:
                    newmatchtime.append(matchtime[n]+jytest.SLIDER_RIGHT_SIDE);
                    oldval = matchtime[n];
        if len(matchtime) == 1:
            newmatchtime = matchtime;
            newmatchtime[0] = newmatchtime[0] + jytest.SLIDER_RIGHT_SIDE;
        return newmatchtime;
    
def main(jytest):
    jytest.initpage();
    button = jytest.get_geetest_button();
    button.click();
    textinfo = '';
    image1 = jytest.get_geetest_image();
    slider = jytest.get_slider();
    tracks = [30];
    jytest.move_to_gap(slider, tracks);
    time.sleep(0.5);
    image2 = jytest.get_geetest_image2(jytest.left, jytest.top, jytest.right, jytest.bottom);
    time.sleep(1);
    top = jytest.get_gap(image1, image2);
    print('top', top);
    jytest.get_position();
    image3 = jytest.get_geetest_image2(jytest.left+jytest.SLIDER_RIGHT_SIDE, jytest.top+top, jytest.right, jytest.top+top+jytest.SLIDER_HEIGHT); 
    image3 = jytest.convert_image_grey(image3);
    threshold = 50;
    distance = 0;
    while threshold < 180:
        threshold += 10;
        image4 = jytest.convert_image_binary(image3, threshold);
        datas = jytest.convert_img2pixel(image4);
        matchtime = jytest.find_start_position(datas);
        if len(matchtime) > 0:
            break;
    print('before correct:', matchtime);
    matchtime = jytest.correct_matchtime(matchtime);
    print('after correct:', matchtime);
    
    if len(matchtime) > 0:
        for distance in matchtime:
            distance -= 6;
            tracks = jytest.get_track(distance);
            jytest.move_to_gap(slider, tracks);
            textinfo = jytest.get_movegap_returninfo();
            if textinfo == '验证成功':
                break;
            elif '秒后重试' in textinfo:
                break;
            else:
                time.sleep(3);
    return textinfo;
    
if __name__ == '__main__':
    MAX_RETRY = 5;
    current_times = 0;
    jytest = CrackGeetest();
    textinfo = main(jytest);
    while textinfo != '验证成功':
            textinfo = main(jytest);
            if textinfo == '验证成功':
                break;
            current_times += 1;
            print('Retry Times:', current_times);
            if current_times >= 10:
                print('Retry Times reacherd 10, Verify Faild! Quting...');
                break;
