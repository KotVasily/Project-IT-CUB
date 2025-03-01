import streamlit as st
import pandas as pd
import plotly.express as px
import time
import config as config_app
import warnings

from full_parser import get_data
from google import genai
from google.genai import types

warnings.filterwarnings(action='ignore')

st.set_page_config(layout="wide")

# Создания переменных 
if 'gemini_response' not in st.session_state:
    st.session_state.gemini_response = None
if 'image_uploaded' not in st.session_state:
    st.session_state.image_uploaded = False
if 'image_data' not in st.session_state:
    st.session_state.image_data = None
if 'ai_mem' not in st.session_state:
    st.session_state.ai_mem = None
if 'ai_mem_question' not in st.session_state:
    st.session_state.ai_mem_question = None
if 'ai_mem_new' not in st.session_state: 
    st.session_state.ai_mem_new = None

def load_data(year):
    """Загрузка/Парсинг данных"""
    try:
        df_mem = pd.read_csv(f"mem_csv/data_{year}.csv")
        df = pd.read_csv(f"mem_csv/wordstat_{year}.csv")
        return df, df_mem
    except:
        with st.spinner("Парсинг данных..."):
            get_data(year)

        df_mem = pd.read_csv(f"mem_csv/data_{year}.csv")
        df = pd.read_csv(f"mem_csv/wordstat_{year}.csv")
        return df, df_mem

def analyze_image():
    """Анализ изоображений"""
    with st.spinner("Gemini анализирует изображение..."):
        try:
            client = genai.Client(api_key=config_app.API_KEY)
            
            image_part = types.Part.from_bytes(
                data=st.session_state.image_data, 
                mime_type=f"image/jpeg" 
            )

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=["Опиши изоображения и скажи что на нем написанно", image_part],
                config=types.GenerateContentConfig(
                    max_output_tokens=500,
                    temperature=1,
                    top_p=0.95,
                    top_k=40))
            text = response.text
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[f"Класифицируй мем по описанию картинки(Формат ответа только названия мема и его описания не более 20 слов): {text} \n Возможные варианты с описанияем: {content}. Подумай шаг за шагом. Это очень важно"],
                config=types.GenerateContentConfig(
                    max_output_tokens=500,
                    temperature=1,
                    top_p=0.95,
                    top_k=40))
            
            st.session_state.gemini_response = response.text
        
        except Exception as e:
            st.error(f"Произошла ошибка: {str(e)}")
            st.session_state.gemini_response = f"Ошибка: {str(e)}"

def get_responce(content):
    """Функция для мемного мастера"""
    with st.spinner("Мемный мастер генерирует ответ..."):
        client = genai.Client(api_key=config_app.API_KEY)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[st.session_state.ai_mem_question + f"\n Ты эксперт по мемам, твои знанения: {content}"],
            config=types.GenerateContentConfig(
                max_output_tokens=500,
                temperature=1,
                top_p=0.95,
                top_k=40))
        
        st.session_state.ai_mem = response.text 

# Фильтрация данных       
year = st.number_input("Введите год:", value=2024, step=1, max_value=2025, min_value=2023)
filter_num = st.number_input("Введите порог views:", value=0, step=1)
type_plot = st.selectbox("Тип диаграммы:", options=['Гистограмма', 'Линейная'], key='lineplot')

df, df_mem = load_data(year)

for mem in df.mem.unique():
    df_mem_filter = df_mem.loc[df_mem.title==mem]
    df_filter = df.loc[df.mem==mem]

    df_filter['views'] = (df_filter['views']*df_filter['sum_views'].mean())/1_000_000
    df.loc[df.mem==mem, 'views'] = df_filter['views'].values.tolist()

df_sum = df.groupby('mem').views.max().reset_index()
df_sum = df_sum.loc[df_sum.views > filter_num]

df = df.loc[df.mem.isin(df_sum.mem.values)]
df_mem = df_mem.loc[df_mem.title.isin(df_sum.mem.values)]

mem_dict = {}
for x in df.mem.unique().tolist():
    mem_dict[x] = x

content = "\n".join(df_mem['content'].values.tolist()) 

# Ввывод графиков
if type_plot == 'Линейная':
    fig = px.line(
        df,
        x="date",
        y="views",
        color="mem",
        markers=True,
        title=f"Просмотры по месяцам для каждого 'mem' в {year}",
        labels={"date": "Дата", "views": "Коффецент популярности ", "mem": "Мем"},
        height=500
    )
else:
    fig = px.bar(
        df,
        x="mem",
        y="views",
        title=f"Просмотры по месяцам для каждого 'mem' в {year}",
        labels={"date": "Дата", "views": "Коффецент популярности ", "mem": "Мем"},
        height=500)
st.plotly_chart(fig, use_container_width=True)

# Получения информации о меме
with st.empty():
    selected_mem = st.selectbox("Выберите мем:", options=list(mem_dict.keys()), key='selected_mem')
    time.sleep(1)

with st.empty():
    print(selected_mem)
    context = df_mem.loc[df_mem.title==selected_mem]['content'].values.tolist()[0]
    mem_url = df_mem.loc[df_mem.title==selected_mem]['url'].values.tolist()[0]
    print(context)
    st.markdown(f'''#### {context} <br> <a href="{mem_url}" target="_blank" style="color: #ffff00; text-decoration: none;">Посетите полное описание мема</a>''', unsafe_allow_html=True)

st.markdown('---')
# Вопросы AI эксперту 
text_input = st.text_input("", placeholder='Задать вопросу AI эксперту по мемам')

if text_input is not None: 
    st.session_state.ai_mem_new = True 
    st.session_state.ai_mem_question = text_input
else: 
    st.session_state.ai_mem_new = False 

if st.session_state.ai_mem_new:
    if st.button("Отправить"):
        get_responce(content + df.to_string())

if st.session_state.ai_mem:
    st.markdown(f"#### Ответ: {st.session_state.ai_mem}")

st.markdown('---')
# Анализ изоображений
uploaded_file = st.file_uploader("Загрузите изображение", type=["jpg", "jpeg", "png"])
client = genai.Client(api_key=config_app.API_KEY,)

if uploaded_file is not None:
    uploaded_file.seek(0)
    image_bytes = uploaded_file.read()
    
    st.session_state.image_data = image_bytes
    st.session_state.image_uploaded = True
    
    st.image(st.session_state.image_data)
else:
    st.session_state.image_uploaded = False

if st.session_state.image_uploaded:
    if st.button("Что за мем?"):
        analyze_image()

if st.session_state.gemini_response:
    st.markdown(f"#### Ответ: {st.session_state.gemini_response}")