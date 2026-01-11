# main/parsers/stepik_parser.py
import aiohttp
import asyncio
from fake_useragent import UserAgent
from typing import List, Dict

CATEGORIES_NUMS_URL = "https://cdn.stepik.net/media/files/rubricator_prod_20251224.json"
COURSE_LISTS_API = "https://stepik.org/api/course-lists"
COURSES_API = "https://stepik.org/api/courses"


class StepikParser:
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.session = None
        self.semaphore = None

    def _generate_headers(self) -> Dict[str, str]:
        ua = UserAgent()
        return {"User-Agent": ua.random}

    async def _fetch_json(self, url: str) -> Dict:
        async with self.semaphore:
            headers = self._generate_headers()
            async with self.session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()

    async def get_categories(self) -> tuple[List[int], List[Dict]]:
        async with self.session.get(CATEGORIES_NUMS_URL) as response:
            categories_all = await response.json()

        for subject in categories_all["subjects"]:
            if subject["title"] == "Информационные технологии":
                categories_it_nums = subject["meta_categories"]
                categories_it = [
                    cat
                    for cat in categories_all["meta_categories"]
                    if cat["id"] in categories_it_nums
                ]

                all_course_lists = []
                for category in categories_it:
                    all_course_lists.extend(category.get("course_lists", []))

                return list(set(all_course_lists)), categories_it

        return [], []

    async def get_course_lists(self, course_list_ids: List[int]) -> Dict:
        params = "&".join([f"ids[]={cid}" for cid in course_list_ids])
        url = f"{COURSE_LISTS_API}?{params}"

        try:
            data = await self._fetch_json(url)
            course_lists = data.get("course-lists", [])

            result = {}
            for cl in course_lists:
                title = cl.get("title", "Unknown")
                result[title] = {
                    "id": cl.get("id"),
                    "title": title,
                    "description": cl.get("description", ""),
                    "course_count": len(cl.get("courses", [])),
                    "course_ids": cl.get("courses", []),
                }

            return result
        except Exception as e:
            print(f"Ошибка получения списков курсов: {e}")
            return {}

    async def get_course_details(self, course_ids: List[int], batch_size: int = 50) -> List[Dict]:
        batches = [
            course_ids[i: i + batch_size]
            for i in range(0, len(course_ids), batch_size)
        ]
        all_courses = []

        for i, batch in enumerate(batches, 1):
            params = "&".join([f"ids[]={cid}" for cid in batch])
            url = f"{COURSES_API}?{params}"

            try:
                data = await self._fetch_json(url)
                courses = data.get("courses", [])
                all_courses.extend(courses)
                print(f"Загружено {len(all_courses)}/{len(course_ids)} курсов")
            except Exception as e:
                print(f"Ошибка загрузки курсов: {e}")
                continue

        return all_courses

    async def parse(self):
        """Основной метод парсинга - возвращает словарь с данными"""
        connector = aiohttp.TCPConnector(limit=50)
        timeout = aiohttp.ClientTimeout(total=60)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            self.session = session
            self.semaphore = asyncio.Semaphore(self.max_concurrent)

            course_list_ids, categories = await self.get_categories()
            if not course_list_ids:
                print("Не найдены категории IT")
                return {}, set()

            print(f"Найдено {len(categories)} категорий IT")
            print(f"Список ID для парсинга: {len(course_list_ids)}")

            courses_by_lists = await self.get_course_lists(course_list_ids)
            if not courses_by_lists:
                print("Не удалось получить списки курсов")
                return {}, set()

            print(f"Получено {len(courses_by_lists)} списков курсов")

            all_unique_course_ids = set()
            for info in courses_by_lists.values():
                all_unique_course_ids.update(info["course_ids"])

            print(f"Уникальных курсов: {len(all_unique_course_ids)}")

            course_details = await self.get_course_details(list(all_unique_course_ids))
            print(f"Получено деталей: {len(course_details)} курсов")

            # Распределяем курсы по спискам
            course_by_id = {c["id"]: c for c in course_details}

            result = {}
            for list_name, info in courses_by_lists.items():
                list_courses = []
                for course_id in info["course_ids"]:
                    if course_id in course_by_id:
                        list_courses.append(course_by_id[course_id])

                if list_courses:
                    result[list_name] = {
                        **info,
                        "courses": list_courses
                    }

            print(f"\n{'=' * 60}")
            print(f"Всего обработано уникальных курсов: {len(course_details)}")

            return result, all_unique_course_ids

    def parse_raw(self, data):
        """
        Парсит данные в формате Stepik
        data: словарь с адаптированными данными
        """
        if not data or 'raw_data' not in data:
            raise ValueError("Invalid data format for StepikParser")

        raw_data = data['raw_data']

        # Реальная логика парсинга Stepik
        courses = []

        # Пример логики (замените на реальную)
        if isinstance(raw_data, list):
            for item in raw_data:
                course = {
                    'title': item.get('title', 'No title'),
                    'description': item.get('description', ''),
                    'source': 'stepik',
                    'url': item.get('url', ''),
                    'price': item.get('price', 0),
                }
                courses.append(course)

        return courses
    pass