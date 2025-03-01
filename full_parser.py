from parser.parser_mem import load_mem
from parser.wordstat_parser import create_driver, load_cookie, load_wordstat

def check_short_words(word_list):
    """Проверяем короткие слова"""
    if len(word_list) != 2:  
        return False
    return any(len(word) <= 2 for word in word_list)  

def get_data(year):
    """Парсим данные."""
    data_mem = load_mem(year=year)
    data_mem = data_mem[
        (data_mem['title'].str.strip().str.split().str.len() > 1) & 
        ~(data_mem['title'].str.strip().str.split().apply(check_short_words))
    ]
    data_mem.to_csv(f"mem_csv/data_{year}.csv", index=False)

    mem_list = data_mem.title.values.tolist()
    driver = create_driver()
    load_cookie(driver)
    load_wordstat(mem_list, driver, year)
