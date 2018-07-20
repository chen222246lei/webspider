# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from PIL import Image
from io import BytesIO
import time

URL = 'https://passport.weibo.cn/signin/login';
USERNAME = 'htywork_3@sina.com';
PASSWORD = 'htywork_3';

class weibogg():
    def __init__(self):
        chrome_options = webdriver.ChromeOptions();
        chrome_options.add_argument('start-maximized');
        self.browser = webdriver.Chrome(chrome_options=chrome_options);
        self.wait = WebDriverWait(self.browser, 20);
    
    def initpage(self):
        self.browser.get(URL);
        input_user = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#loginName')));
        input_pass = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#loginPassword')));
        login_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#loginAction')));
        time.sleep(1);
        input_user.clear();
        input_user.send_keys(USERNAME);
        time.sleep(1);
        input_pass.clear();
        input_pass.send_keys(PASSWORD);
        time.sleep(1);
        login_btn.click();
        time.sleep(3); 
    
    def get_direction_zb1(self, circles, index1, index2):
        x1 = circles[index1].location['x'] + circles[index1].size['width']/2;
        y1 = circles[index1].location['y'] + circles[index1].size['height']/2;
        x2 = circles[index2].location['x'] + circles[index2].size['width']/2;
        y2 = circles[index2].location['y'] + circles[index2].size['height']/2;
        cx = x1 + (x2-x1)/2;
        cy = y1 + (y2-y1)/2;
        return(cx, cy);
    
    def get_direction_zb2(self, circles, index1, index2):
        x1 = circles[index1].location['x'] + circles[index1].size['width']/2;
        y1 = circles[index1].location['y'] + circles[index1].size['height']/2;
        x2 = circles[index2].location['x'] + circles[index2].size['width']/2;
        y2 = circles[index2].location['y'] + circles[index2].size['height']/2;
        if x2 > x1 and y2 > y1:   
            cx1 = x1 + (x2-x1)*0.3;
            cy1 = y1 + (y2-y1)*0.3;
            cx2 = x1 + (x2-x1)*0.5;
            cy2 = y1 + (y2-y1)*0.5;
            cx3 = x1 + (x2-x1)*0.7;
            cy3 = y1 + (y2-y1)*0.7;
        else:
            cx1 = x1 + (x2-x1)*0.3;
            cy1 = y2 + (y1-y2)*0.7;
            cx2 = x1 + (x2-x1)*0.5;
            cy2 = y2 + (y1-y2)*0.5;
            cx3 = x1 + (x2-x1)*0.7;
            cy3 = y2 + (y1-y2)*0.3;
        return(cx1, cy1, cx2, cy2, cx3, cy3);
        
    def get_directions_zb(self):
        directions = [];
        circles = None;
        while not circles:
            circles = self.browser.find_elements_by_css_selector('.patt-wrap .patt-circ');
        cx, cy = self.get_direction_zb1(circles, 0, 1);
        directions.append((cx, cy));
        cx, cy = self.get_direction_zb1(circles, 1, 3);
        directions.append((cx, cy));
        cx, cy = self.get_direction_zb1(circles, 2, 3);
        directions.append((cx, cy));
        cx, cy = self.get_direction_zb1(circles, 0, 2);
        directions.append((cx, cy));
        cx1, cy1, cx2, cy2, cx3, cy3 = self.get_direction_zb2(circles, 0, 3);
        directions.append((cx1, cy1));
        directions.append((cx2, cy2));
        directions.append((cx3, cy3));
        cx1, cy1, cx2, cy2, cx3, cy3 = self.get_direction_zb2(circles, 2, 1);
        directions.append((cx1, cy1));
        directions.append((cx2, cy2));
        directions.append((cx3, cy3));
        return directions;
    
    def get_screenshot(self):
        screenshot = self.browser.get_screenshot_as_png();
        screenshot = Image.open(BytesIO(screenshot));
        return screenshot;
    
    def convert_greyimg(self, image):
        image = image.convert('L');
        return image;
    
    def convert_binaryimg(self, image):
        threshold = 250; 
        table = [];
        for i in range(256):
            if i < threshold:
                table.append(0);
            else:
                table.append(1);
        image =  image.point(table,'1');
        return image;
    
    def convert_img2pixel(self, image):
        datas = data = [];
        datas = []
        for y in range(image.height):
            for x in range(image.width):
                rgb = image.load()[x, y];
                if rgb < 253:
                    data.append(image.load()[x, y]);
                else:
                    data.append(0);
            havedata_inline = 0;
            for pixel in data:
                if pixel > 0:
                    havedata_inline = 1;
                    break;
            if havedata_inline > 0:
                datas.append(list(data));
            data = [];
        return datas;
    
    def determin_direction(self, datas, type):
        if len(datas) > 0:
            if type == 1:
                first_greater0_col = 0;
                second_greater0_col = 0;
                data1 = datas[0];
                data2 = datas[1];
                for n in range(len(data1)):
                    if data1[n] > 0:
                        first_greater0_col = n;
                        break;
                for n in range(len(data2)):
                    if data2[n] > 0:
                        second_greater0_col = n;
                        break;
                if first_greater0_col == second_greater0_col:
                    return 'l-r';
                else:
                    return 'r-l';
            elif type == 2:
                rows = len(datas);
                columns = len(datas[0]);
                first_greater0_row = 0;
                second_greater0_row = 0;
                for col in range(columns):
                    for row in range(rows):
                        if datas[row][col] > 0:
                            if first_greater0_row == 0:
                                first_greater0_row = row;
                                break;
                            else:
                                second_greater0_row = row;
                                break;
                    if first_greater0_row > 0 and second_greater0_row > 0:
                        break;
                if first_greater0_row == second_greater0_row:
                    return 't-b';
                else:
                    return 'b-t';
            elif type == 3:
                zerocnt = 0;
                for row in range(len(datas)):
                    for col in range(len(datas[0])):
                        if datas[row][col] == 0:
                            zerocnt += 1;
                if zerocnt <= 10:
                    return 'noline';
                rows = len(datas);
                columns = len(datas[0]);
                if datas[rows-1][0] == 0 or datas[rows-1][1] == 0:
                    return '';
                else:
                    max_zeros = 0;
                    temp_zeros = 0;
                    for col in range(columns):
                        for row in range(rows):
                            if datas[row][col] == 0:
                                temp_zeros += 1;
                        if temp_zeros > max_zeros:
                            max_zeros = temp_zeros;
                        temp_zeros = 0;
                    if max_zeros < 7:
                        return '';
                    else:
                        maxlen = 6;
                        print('31', datas);
                        zero_array = [];
                        times1 = 0;
                        length = len(datas);
                        for i in range(1,length+1):
                            times1 += 1;
                            zero_cnt = 0;
                            for j in range(i):
                                row = j;
                                col = i-j-1;
                                print('32', row, col, datas[row][col]);
                                if datas[row][col] == 0:
                                    zero_cnt += 1;
                            if zero_cnt > maxlen:
                                zero_cnt = maxlen;
                            zero_array.append((zero_cnt, times1));
                            print('-'*30, times1, 'end......');
                        times = times1;
                        times1 = 0;
                        for i in range(length-1,0,-1):
                            zero_cnt = 0;
                            for j in range(i):
                                row = j + times1+ 1;
                                col = (length-1) - j;
                                print('32', row, col, datas[row][col]);
                                if datas[row][col] == 0:
                                    zero_cnt += 1;
                            times1 += 1;
                            if zero_cnt > maxlen:
                                zero_cnt = maxlen;
                            zero_array.append((zero_cnt, times+times1));
                            print('-'*30, times+times1, 'end......');
                        print('33',zero_array );
                        max_of_firt_para = 0;
                        max_of_second_para = 0;
                        for i in range(len(zero_array)):
                            if zero_array[i][0] >= max_of_firt_para:
                                max_of_firt_para = zero_array[i][0];
                                max_of_second_para = zero_array[i][1]; 
                        after_zeronum = zero_array[max_of_second_para][0];
                        print('34', 'max_of_firt_para', max_of_firt_para, 'max_of_second_para', max_of_second_para, 'after_zeronum', after_zeronum);
                        print('35', 'max_of_firt_para - after_zeronum', max_of_firt_para - after_zeronum);
                        if max_of_firt_para - after_zeronum >= 3:
                            return 'rb-lt';
                        else:
                            return 'lt-rb';
            elif type == 4:
                zerocnt = 0;
                for row in range(len(datas)):
                    for col in range(len(datas[0])):
                        if datas[row][col] == 0:
                            zerocnt += 1;
                if zerocnt <= 10:
                    return 'notline';
                rows = len(datas);
                columns = len(datas[0]);
                if datas[0][0] == 0 or datas[1][0] == 0:
                    return '';
                else:
                    max_zeros = 0;
                    temp_zeros = 0;
                    for col in range(columns):
                        for row in range(rows):
                            if datas[row][col] == 0:
                                temp_zeros += 1;
                        if temp_zeros > max_zeros:
                            max_zeros = temp_zeros;
                        temp_zeros = 0;
                    if max_zeros < 7:
                        return '';
                    else:
                        maxlen = 6;
                        print('41', datas);
                        zero_array = [];
                        times1 = 0;
                        length = len(datas);
                        for i in range(1,length+1):
                            times1 += 1;
                            zero_cnt = 0;
                            for j in range(i):
                                row = j;
                                col = length-times1+j;
                                print('42', row, col, datas[col][row]);
                                if datas[col][row] == 0:
                                    zero_cnt += 1;
                            print('-'*30, times1, 'end......');
                            if zero_cnt > maxlen:
                                zero_cnt = maxlen;
                            zero_array.append((zero_cnt, times1));
                        times = times1;
                        times1 = 0;
                        for i in range(length-1,0,-1):
                            times1 += 1;
                            zero_cnt = 0;
                            for j in range(i):
                                row = times1 + j;
                                col = j;
                                print('42', row, col, datas[col][row]);
                                if datas[col][row] == 0:
                                    zero_cnt += 1;
                            print('-'*30, times+times1, 'end......');
                            if zero_cnt > maxlen:
                                zero_cnt = maxlen;
                            zero_array.append((zero_cnt, times+times1));
                        print('43', zero_array);

                        max_of_firt_para = 0;
                        max_of_second_para = 0;
                        for i in range(len(zero_array)):
                            if zero_array[i][0] > max_of_firt_para:
                                max_of_firt_para = zero_array[i][0];
                                max_of_second_para = zero_array[i][1];
                        pre_zeronum = zero_array[max_of_second_para-2][0];
                        print('44', 'max_of_firt_para', max_of_firt_para, 'max_of_second_para', max_of_second_para, 'pre_zeronum', pre_zeronum);
                        print('45', 'max_of_firt_para - pre_zeronum', max_of_firt_para - pre_zeronum);
                        if max_of_firt_para - pre_zeronum >= 3:
                            return 'lb-rt';
                        else:
                            return 'rt-lb';
            else:
                pass;
        else:
            return '';
    
    def detect_direction_relation(self, directions):
        lines_relation = [];
        screenshot = self.get_screenshot();

        img = screenshot.crop((directions[0][0]-8, directions[0][1]-8, directions[0][0]+8, directions[0][1]+8));
        img = self.convert_greyimg(img);
        datas = self.convert_img2pixel(img);
        direction_str = self.determin_direction(datas, 1);
        if direction_str == 'l-r':
            lines_relation.append((1, 2));
        if direction_str == 'r-l':
            lines_relation.append((2, 1));
        
        img = screenshot.crop((directions[1][0]-8, directions[1][1]-8, directions[1][0]+8, directions[1][1]+8));
        img = self.convert_greyimg(img);
        datas = self.convert_img2pixel(img);
        direction_str = self.determin_direction(datas, 2);
        if direction_str == 't-b':
            lines_relation.append((2, 4));
        if direction_str == 'b-t':
            lines_relation.append((4, 2));
            
        img = screenshot.crop((directions[2][0]-8, directions[2][1]-8, directions[2][0]+8, directions[2][1]+8));
        img = self.convert_greyimg(img);
        datas = self.convert_img2pixel(img);
        direction_str = self.determin_direction(datas, 1);
        if direction_str == 'l-r':
            lines_relation.append((3, 4));
        if direction_str == 'r-l':
            lines_relation.append((4, 3));
        
        img = screenshot.crop((directions[3][0]-8, directions[3][1]-8, directions[3][0]+8, directions[3][1]+8));
        img = self.convert_greyimg(img);
        datas = self.convert_img2pixel(img);
        direction_str = self.determin_direction(datas, 2);
        if direction_str == 't-b':
            lines_relation.append((1, 3));
        if direction_str == 'b-t':
            lines_relation.append((3, 1));
            
        ltrb = 0;
        img = screenshot.crop((directions[4][0]-8, directions[4][1]-8, directions[4][0]+8, directions[4][1]+8));
        img = self.convert_greyimg(img);
        img = self.convert_binaryimg(img);
        datas = self.convert_img2pixel(img);
        direction_str = self.determin_direction(datas, 3);
        if direction_str == 'noline':
            ltrb=1;
        elif direction_str == 'lt-rb':
            lines_relation.append((1, 4));
            ltrb=1;
        elif direction_str == 'rb-lt':
            lines_relation.append((4, 1));
            ltrb=1;
            
        if ltrb == 0:
            img = screenshot.crop((directions[5][0]-8, directions[5][1]-8, directions[5][0]+8, directions[5][1]+8));
            img = self.convert_greyimg(img);
            img = self.convert_binaryimg(img);
            datas = self.convert_img2pixel(img);
            direction_str = self.determin_direction(datas, 3);
            if direction_str == 'lt-rb':
                lines_relation.append((1, 4));
                ltrb=1;
            if direction_str == 'rb-lt':
                lines_relation.append((4, 1));
                ltrb=1;
                
        if ltrb == 0:
            img = screenshot.crop((directions[6][0]-8, directions[6][1]-8, directions[6][0]+8, directions[6][1]+8));
            img = self.convert_greyimg(img);
            img = self.convert_binaryimg(img);
            datas = self.convert_img2pixel(img);
            direction_str = self.determin_direction(datas, 3);
            if direction_str == 'lt-rb':
                lines_relation.append((1, 4));
                ltrb=1;
            if direction_str == 'rb-lt':
                lines_relation.append((4, 1));
                ltrb=1;
            
        lbrt = 0;
        img = screenshot.crop((directions[7][0]-8, directions[7][1]-8, directions[7][0]+8, directions[7][1]+8));
        img = self.convert_greyimg(img);
        img = self.convert_binaryimg(img);
        datas = self.convert_img2pixel(img);
        direction_str = self.determin_direction(datas, 4);
        if direction_str == 'noline':
            lbrt=1;
        elif direction_str == 'lb-rt':
            lines_relation.append((3, 2));
            lbrt=1;
        elif direction_str == 'rt-lb':
            lines_relation.append((2, 3));
            lbrt=1;
        
        if lbrt == 0:
            img = screenshot.crop((directions[8][0]-8, directions[8][1]-8, directions[8][0]+8, directions[8][1]+8));
            img = self.convert_greyimg(img);
            img = self.convert_binaryimg(img);
            datas = self.convert_img2pixel(img);
            direction_str = self.determin_direction(datas, 4);
            if direction_str == 'lb-rt':
                lines_relation.append((3, 2));
                lbrt=1;
            if direction_str == 'rt-lb':
                lines_relation.append((2, 3));
                lbrt=1;
                
        if lbrt == 0:
            img = screenshot.crop((directions[9][0]-8, directions[9][1]-8, directions[9][0]+8, directions[9][1]+8));
            img = self.convert_greyimg(img);
            img = self.convert_binaryimg(img);
            datas = self.convert_img2pixel(img);
            direction_str = self.determin_direction(datas, 4);
            if direction_str == 'lb-rt':
                lines_relation.append((3, 2));
                lbrt=1;
            if direction_str == 'rt-lb':
                lines_relation.append((2, 3));
                lbrt=1;
                
        return lines_relation;
    
    def get_lines_link(self, lines_relation):
        for item1 in lines_relation:
            for item2 in lines_relation:
                for item3 in lines_relation:
                    if item1[1] == item2[0] and item2[1] == item3[0]:
                        link_order = str(item1[0]) + str(item1[1]) + str(item2[1]) + str(item3[1]);
                        link_order = [int(num) for num in list(link_order)];
                        break;
        return link_order;
    
    def move(self, link_order):
        step = 30;
        dx = dy = 0;
        circles = self.browser.find_elements_by_css_selector('.patt-wrap .patt-circ');
        for index in range(4):
            circle = circles[link_order[index]-1];
            if index == 0:
                ActionChains(self.browser).move_to_element_with_offset(circle, circle.size['width']/2, circle.size['height']/2) \
                    .click_and_hold().perform();
            else:
                for i in range(step):
                    ActionChains(self.browser).move_by_offset(dx/step, dy/step).perform();
                    time.sleep(1/step);
            if index == 3:
                ActionChains(self.browser).release().perform();
            else:
                dx = circles[link_order[index+1]-1].location['x'] - circle.location['x'];
                dy = circles[link_order[index+1]-1].location['y'] - circle.location['y'];
        
def main():
    gg = weibogg();
    gg.initpage();
    directions = gg.get_directions_zb();
    lines_relation = gg.detect_direction_relation(directions);
    link_order = gg.get_lines_link(lines_relation);
    print(link_order);
    gg.move(link_order);

if __name__ == '__main__':
    main();
