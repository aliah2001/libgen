from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from os import makedirs, listdir, remove
from os.path import getsize

search_word = input('what is it you are searching? \t')
# to ignore search results for git
with open('.gitignore', 'w') as ignore:
    ignore.writelines('search_results/\n')

# to find the last tab if it's not the first time we are searching for this word
nums = []
try:
    files = listdir(f'search_results/{search_word}')
    for i in files:
        if 'txt' in i and i.find('_') > 0:
            nums.append(int(i[:i.find('_')]))
            nums.sort()
    if len(nums) != 0:
        last_tab = nums[-1]
    else:
        last_tab = 0
    print(f'last tab was {last_tab}')
except (FileNotFoundError, ValueError):
    last_tab = 0
urls = ['https://libgen.rs/', 'https://libgen.is/', 'https://libgen.st/']
search_url = 'search.php?req='
number_of_results = '&res=100'
tab_num = f'&page={last_tab+1}'
ch = webdriver.ChromeOptions()
op = ch.add_argument('start-minimized')
# service=Service(ChromeDriverManager().download_and_install()[0]),
browser = webdriver.Chrome(chrome_options=op)
browser.minimize_window()
browser.set_script_timeout(20000)
browser.set_page_load_timeout(20000)
for i in urls:
    try:
        browser.get(i+search_url+search_word+number_of_results+tab_num)
    except (TimeoutError, WebDriverException):
        continue
    break
# got into the site using the search word
page_source = browser.page_source
find_n = '<font color="grey" size="1">'
last_find_n = ' files found'
number_of_results = int(page_source[page_source.find(find_n) + len(find_n): page_source.find(last_find_n)])
number_of_tabs = number_of_results//100
if number_of_results % 100 > 0:
    number_of_tabs += 1
print(f'number of results: {number_of_results} \nnumber of tabs: {number_of_tabs}')

# now we know how many results are ready


def change_tab():
    current_url = browser.current_url
    tab_url = current_url[0:current_url.find('page')+5]
    current_tab = int(current_url[current_url.find('page')+5:])
    print(f'last tab was: {current_tab}')
    next_tab = current_tab + 1
    browser.get(tab_url + str(next_tab))
    print(f'tab changed to tab: {next_tab}')

# now we can use this function to change tabs


results = []
result_dic = [
        "ID",
        "Author",
        "Title",
        "Publisher",
        "Year",
        "Pages",
        "Language",
        "Size",
        "Extension",
        "link_page_to_download"
]
last_results = []
tab_number = int(tab_num[6:])
makedirs(f'search_results/{search_word}', exist_ok=True)

while tab_number <= number_of_tabs:
    tab_number = int(browser.current_url[browser.current_url.find('page')+5:])
    if tab_number > number_of_tabs:
        break
    results = []
    table_id = browser.find_element(By.CLASS_NAME, 'c')
    rows = table_id.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        if rows.index(row) == 0:
            continue
        result = dict()
        for i in range(9):
            col = row.find_elements(By.TAG_NAME, "td")[i]
            text = col.text
            if i == 2:
                title = row.find_element(By.ID, result['ID'])
                try:
                    colored = title.find_element(By.TAG_NAME, 'i').text
                    text = title.text[0:title.text.find(colored)-1]
                except NoSuchElementException:
                    text = title.text
            result[result_dic[i]] = text
        link = row.find_elements(By.TAG_NAME, "td")[9]
        link.find_element(By.TAG_NAME, 'a').click()
        ele = browser.find_element(By.XPATH, '//a[text()="Cloudflare"]')
        result[result_dic[9]] = ele.get_attribute('href')
        results.append(result)
        browser.back()
        print(result)
    with open(f'search_results/{search_word}/{tab_number}_{search_word}.txt', 'w', encoding='utf8') as txt:
        for i in results:
            last_results.append(i)
            txt.writelines(str(i) + '\n')
    change_tab()
try:
    if getsize(f'search_results/{search_word}/{search_word}.txt') == 0:
        remove(f'search_results/{search_word}')
        print(f'Please restart the program')
except FileNotFoundError:
    with open(f'search_results/{search_word}/{search_word}.txt', 'w+', encoding='utf8') as txt:
        for i in last_results:
            txt.writelines(str(i) + '\n')
browser.close()
print(f'results saved in search_results\\{search_word}\\')
# we have results now
