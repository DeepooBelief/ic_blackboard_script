from selenium import  webdriver
import time
import os
import re
from key import HOST
from key import PASSWORD
from key import EMAIL
from key import ROOT_DIR
from key import edge_driver_path


def isloaded(driver):
    page_loaded = False
    while not page_loaded:
        page_loaded = driver.execute_script("return document.readyState == 'complete';")
        time.sleep(0.5)
    
def validateTitle(title):
    title = title.lstrip()
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)
    return new_title

def set_download_path(driver, path):
    path = path.rstrip(os.sep)
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior',
                'params': {'behavior': 'allow', 'downloadPath': path}}
    driver.execute("send_command", params)
    print(path)

def getDownLoadedFileName():
    driver.execute_script("window.open()")
    # switch to new tab
    driver.switch_to.window(driver.window_handles[-1])
    # navigate to chrome downloads
    driver.get('chrome://downloads')
    while True:
        try:
            file_name = driver.execute_script("return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('div#content  #file-link').text")
            driver.close()
            return file_name
        except:
            pass
        time.sleep(0.5)
        
def check_and_delete_folder(download_path):
    if os.path.exists(download_path) and os.path.isdir(download_path):
        if not os.listdir(download_path):
            os.rmdir(download_path)
            print(f"The folder {download_path} has been deleted.")
        else:
            pass
    else:
        print(f"The path {download_path} is not a valid folder.")


def recursive(driver, layer, download_path): #递归
    Course_Contents = driver.find_elements("class name", 'item_icon')
    set_download_path(driver, download_path)
    for i in range(len(Course_Contents)): #循环当前目录所有的Course_Contents
        # print(Course_Contents[i].accessible_name)
        Course_Contents = driver.find_elements("class name", 'item_icon')
        #print all the elements in this variable
        # element_html = [x.get_attribute('outerHTML') for x in Course_Contents]
        # print(element_html)
        img_alt = Course_Contents[i].get_attribute('alt')
        print(img_alt)
        if img_alt == 'File':
            #//*[@id="anonymous_element_4"]/a
            file_name = Course_Contents[i].find_element("xpath", './../*/h3/a')
            if 'animation' in file_name.text:
                continue
            elif'.png' in file_name.text:
                continue
            pre_url = driver.current_url
            driver.get(file_name.get_attribute('href'))
            if driver.current_url == pre_url:
                print('-' * layer + file_name.text)
                FileName = getDownLoadedFileName()
                # print(FileName)
                driver.switch_to.window(driver.window_handles[0])
                while not os.path.exists(os.path.join(download_path, FileName)):
                    pass
                suffix = os.path.splitext(FileName)[-1]
                os.rename(os.path.join(download_path, FileName), os.path.join(download_path, validateTitle(file_name.text) + suffix))
            else:
                driver.back()
                time.sleep(1)
        elif img_alt == 'Content Folder':
            Folder = Course_Contents[i].find_element("xpath", './../*/h3')
            print('-' * layer + Folder.text)
            download_path = os.path.join(download_path, validateTitle(Folder.text))
            if not os.path.exists(download_path):
                os.mkdir(download_path)
            Folder.click()
            time.sleep(1)
            recursive(driver, layer + 1, download_path)
            download_path = os.path.dirname(download_path)
            set_download_path(driver, download_path)
            driver.back()
            time.sleep(1)
        elif img_alt == 'Item':
            attachments = Course_Contents[i].find_elements("xpath", './../div[2]/div[1]/div[2]/ul/*/a[1]')
            tables = Course_Contents[i].find_elements("xpath", './../div[2]/div/table')
            Folder_name = Course_Contents[i].find_element("xpath", './../*/h3').text
            download_path = os.path.join(download_path, validateTitle(Folder_name))
            if not os.path.exists(download_path):
                os.mkdir(download_path)
            set_download_path(driver, download_path)
            print('-' * layer + Folder_name)
            for attachment in attachments:
                print('-' * (layer + 1) + attachment.text)
                if '.png' in attachment.text or '.jpg' in attachment.text:
                    continue
                driver.get(attachment.get_attribute('href'))
                File_Name = getDownLoadedFileName()
                # print(File_Name)
                driver.switch_to.window(driver.window_handles[0])
                while not os.path.exists(os.path.join(download_path, File_Name)):
                    pass
                suffix = os.path.splitext(File_Name)[-1]
                if not suffix in validateTitle(attachment.text):
                    os.rename(os.path.join(download_path, File_Name), os.path.join(download_path, validateTitle(attachment.text) + suffix))
                else:
                    os.rename(os.path.join(download_path, File_Name), os.path.join(download_path, validateTitle(attachment.text)))
            
            for table in tables:
                # /tbody/tr
                rows = table.find_elements("xpath", './tbody/tr')
                column = []
                for i in range(len(rows)):
                    tds = rows[i].find_elements("xpath", './td')
                    if i == 0:
                        for td in tds:
                            column.append(td.text)
                    else:
                        Folder_name = tds[0].text
                        download_path = os.path.join(download_path, validateTitle(Folder_name))
                        if not os.path.exists(download_path):
                            os.mkdir(download_path)
                        set_download_path(driver, download_path)
                        for j in range(1, len(tds)):
                            download_path = os.path.join(download_path, validateTitle(column[j]))
                            if not os.path.exists(download_path):
                                os.mkdir(download_path)
                            set_download_path(driver, download_path)
                            files = tds[j].find_elements("xpath", './*/a[1]')
                            for file in files:
                                if 'ant-x' in file.get_attribute('href'):
                                    continue
                                driver.get(file.get_attribute('href'))
                                FileName = getDownLoadedFileName()
                                driver.switch_to.window(driver.window_handles[0])
                                while not os.path.exists(os.path.join(download_path, FileName)):
                                    pass
                                suffix = os.path.splitext(FileName)[-1]
                                os.rename(os.path.join(download_path, FileName), os.path.join(download_path, validateTitle(file.text) + suffix))
                            files = tds[j].find_elements("xpath", './a[1]')
                            for file in files:
                                driver.get(file.get_attribute('href'))
                                FileName = getDownLoadedFileName()
                                driver.switch_to.window(driver.window_handles[0])
                                while not os.path.exists(os.path.join(download_path, FileName)):
                                    pass
                                suffix = os.path.splitext(FileName)[-1]
                                os.rename(os.path.join(download_path, FileName), os.path.join(download_path, validateTitle(file.text) + suffix))
                            check_and_delete_folder(download_path)
                            download_path = os.path.dirname(download_path)
                            set_download_path(driver, download_path)
                        download_path = os.path.dirname(download_path)
                        set_download_path(driver, download_path)
                        
            download_path = os.path.dirname(download_path)
            set_download_path(driver, download_path)       
        elif img_alt == 'linked item':
            pass
        else:
            print('-' * layer + Course_Contents[i].find_element("xpath", './../*/h3').text + "(" + img_alt + ")")

options = webdriver.ChromeOptions()
profile = {
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
}
options.add_experimental_option("prefs", profile)
driver = webdriver.Chrome(options=options, executable_path=edge_driver_path)
driver.implicitly_wait(2)
# driver = webdriver.Chrome()
driver.get(HOST)
isloaded(driver)
driver.find_element("xpath",'//*[@id="i0116"]').send_keys(EMAIL)
driver.find_element("xpath", '//*[@id="idSIButton9"]').click()
time.sleep(2)
driver.find_element("xpath",'//*[@id="i0118"]').send_keys(PASSWORD)
time.sleep(0.5)
driver.find_element("xpath", '//*[@id="idSIButton9"]').click()
time.sleep(0.5)
input("Press Enter to continue...")
driver.get(HOST)
isloaded(driver)
driver.get(HOST)
isloaded(driver)

def run(dir):
    courses = driver.find_elements("xpath", '//*[@id="_4_1termCourses_noterm"]/ul/*/a')
    No_of_courses = len(courses)
    for i in range(No_of_courses):
        courses = driver.find_elements("xpath", '//*[@id="_4_1termCourses_noterm"]/ul/*/a')
        print(courses[i].text)
        download_path = os.path.join(dir, validateTitle(courses[i].text))
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        courses[i].click()
        isloaded(driver)
        learning_materials = driver.find_elements("xpath", '//*[text()="Learning Materials"]')
        if len(learning_materials) == 0:
            learning_materials = driver.find_elements("xpath", '//*[text()="Learning materials"]')
        
        if len(learning_materials) == 0:
            learning_materials = driver.find_elements("xpath", '//*[text()="Course Content"]')
        
        if len(learning_materials) == 0:
            learning_materials = driver.find_elements("xpath", '//*[text()="Content"]')
            
        if len(learning_materials) == 0:
            print("No learning material")
            driver.back()
            continue

        # //*[@id="paletteItem:_587743_1"]/a
        learning_materials[0].click()
        isloaded(driver)
        recursive(driver, 1, download_path)
        driver.get(HOST)
        isloaded(driver)
        
run(ROOT_DIR)
