# main/parsers/hexlet_parser.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class HexletParser:
    def __init__(self, base_url="https://hexlet.io"):
        self.base_url = base_url.rstrip('/')

    def parse(self):
        courses = []
        count_courses = ["courses_front_end_dev", "courses_backend_development"]

        for course in count_courses:
            url = f"https://ru.hexlet.io/{course}"
            try:
                response = requests.get(url)
                response.raise_for_status()
            except:
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            data = soup.find_all("div", tabindex="0")

            for i in data:
                try:
                    name = i.find("p", class_="mantine-focus-auto m_b6d8b162 mantine-Text-root").text
                    start_end = i.find("span", class_="mantine-focus-auto m_b6d8b162 mantine-Text-root").text
                    money = i.find("p", style="font-size:var(--mantine-font-size-xl)").text
                    image = i.find("img", class_="m_9e117634 mantine-Image-root mantine-visible-from-xs")["src"]

                    link_element = i.find("a",href=True)
                    if link_element:
                        href = link_element.get("href")
                        # Создаем полный URL
                        course_url = urljoin(self.base_url, href)
                    else:
                        # Если не нашли ссылку, создаем из названия
                        course_url = f"https://ru.hexlet.io/programs/{course}"

                    courses.append({
                        'title': name,
                        'description': start_end,
                        'source': 'hexlet',
                        'price': money,
                        'image_url': image,
                        'start_end': start_end,
                        'is_paid': 'бесплатно' not in money.lower(),
                        'learners_count': 0,
                        'language': 'ru',
                        'url': course_url,  # ДОБАВЛЕНО: ссылка на курс
                        'slug': course,  # ДОБАВЛЕНО: slug курса
                    })

                except:
                    continue

        return courses

    # ДОБАВЛЕН НОВЫЙ МЕТОД ДЛЯ ПОЛУЧЕНИЯ ТОЛЬКО ССЫЛОК
    def get_course_links(self, courses_list=None):
        """
        Возвращает список курсов с HTML ссылками
        courses_list: опционально, список курсов для обработки
                     если не указан, парсит заново
        """
        if courses_list is None:
            courses_list = self.parse()

        result = []
        for course in courses_list:
            # Создаем HTML ссылку
            html_link = f'<a href="{course["url"]}" target="_blank" class="course-link">{course["title"]}</a>'

            result.append({
                'title': course['title'],
                'url': course['url'],
                'html_link': html_link,
                'description': course['description'],
                'price': course['price'],
                'image_url': course['image_url'],
                'is_paid': course['is_paid'],
            })

        return result

    # ДОБАВЛЕН НОВЫЙ МЕТОД ДЛЯ ГЕНЕРАЦИИ HTML БЛОКА
    def generate_html_block(self, courses_list=None, css_class="hexlet-course"):
        """
        Генерирует HTML блок со всеми курсами
        """
        if courses_list is None:
            courses_list = self.parse()

        if not courses_list:
            return "<p>Курсы не найдены</p>"

        html_parts = ['<div class="hexlet-courses-container">']

        for course in courses_list:
            price_class = "course-paid" if course['is_paid'] else "course-free"

            html = f'''
                <div class="{css_class} {price_class}">
                    <div class="course-image">
                        <img src="{course['image_url']}" alt="{course['title']}" loading="lazy">
                    </div>
                    <div class="course-info">
                        <h3 class="course-title">
                            <a href="{course['url']}" target="_blank" rel="noopener noreferrer">
                                {course['title']}
                            </a>
                        </h3>
                        <p class="course-description">{course['description']}</p>
                        <div class="course-meta">
                            <span class="course-price">{course['price']}</span>
                            <span class="course-status">{'Платный' if course['is_paid'] else 'Бесплатный'}</span>
                        </div>
                    </div>
                </div>
                '''
            html_parts.append(html)

        html_parts.append('</div>')

        # Добавляем CSS стили
        css_styles = '''
            <style>
            .hexlet-courses-container {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                padding: 20px;
            }
            .hexlet-course {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                overflow: hidden;
                transition: transform 0.2s, box-shadow 0.2s;
                background: white;
            }
            .hexlet-course:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .course-image img {
                width: 100%;
                height: 180px;
                object-fit: cover;
            }
            .course-info {
                padding: 15px;
            }
            .course-title {
                margin: 0 0 10px 0;
                font-size: 18px;
            }
            .course-title a {
                color: #333;
                text-decoration: none;
            }
            .course-title a:hover {
                color: #0066cc;
                text-decoration: underline;
            }
            .course-description {
                color: #666;
                font-size: 14px;
                margin: 0 0 10px 0;
            }
            .course-meta {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .course-price {
                font-weight: bold;
                color: #2e7d32;
            }
            .course-free .course-price {
                color: #388e3c;
            }
            .course-paid .course-price {
                color: #d32f2f;
            }
            .course-status {
                font-size: 12px;
                padding: 3px 8px;
                border-radius: 12px;
                background: #f5f5f5;
                color: #666;
            }
            </style>
            '''

        return css_styles + '\n'.join(html_parts)
        pass