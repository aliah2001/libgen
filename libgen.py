from selenium import webdriver
from selenium.webdriver.common.by import By
from os import makedirs, listdir
from selenium.common.exceptions import NoSuchElementException
makedirs('search_results', exist_ok=True)
with open('.gitignore', 'w') as ignore:
    ignore.writelines('search_results/\n')
nums = []
files = listdir('search_results')
for i in files:
    if 'txt' in i:
        nums.append(int(i[:i.find('_')]))
        nums.sort()
if len(nums) != 0:
    last_tab = nums[-1]
else:
    last_tab = 0
print(f'last tab was {last_tab}')
urls = ['https://libgen.rs/', 'https://libgen.is/', 'https://libgen.st/']
search_url = 'search.php?req='
search_word = 'aviation'
tab_num = f'&page={last_tab+1}'
ch = webdriver.ChromeOptions()
op = ch.add_argument('--headless')
browser = webdriver.Chrome(options=op)
browser.set_script_timeout(20000)
browser.set_page_load_timeout(20000)
for i in urls:
    try:
        browser.get(i+search_url+search_word+tab_num)
        break
    except TimeoutError:
        pass

# got into the site using the search word
page_source = browser.page_source
find_n = '<font color="grey" size="1">'
last_find_n = ' files found | showing results from '
number_of_results = int(page_source[page_source.find(find_n) + len(find_n): page_source.find(last_find_n)])
number_of_tabs = number_of_results//25+1
print(f'number of results: {number_of_results} \nnumber of tabs: {number_of_tabs}')
if last_tab == number_of_tabs:
    print('It\'s over.')
    browser.close()
    exit()
# now we know how many results are ready


def change_tab():
    current_url = browser.current_url
    tab_url = current_url[0:current_url.find('page')+5]
    current_tab = int(current_url[current_url.find('page')+5:])
    print(f'current tab: {current_tab}')
    next_tab = current_tab + 1
    browser.get(tab_url + str(next_tab))
    print(f'tab changed to tab number {next_tab}')

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
while True:
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
    tab_number = int(browser.current_url[browser.current_url.find('page')+5:])
    with open(f'search_results\\{tab_number}_{search_word}.txt', 'w', encoding='utf8') as txt:
        for i in results:
            txt.writelines(str(i) + '\n')
    if tab_number == number_of_tabs:
        break
    change_tab()

with open(f'\\search_results\\{search_word}.txt', 'w') as txt:
    for i in results:
        txt.writelines(str(i) + '\n')
# we have results now
