"""Тесты для рекомендательного сервиса"""
import logging
import unittest

import os
import requests
from dotenv import load_dotenv

load_dotenv()


headers = {"Content-type": "application/json", "Accept": "text/plain"}
main_app_url = os.getenv("BASE_URL") + ":" + str(os.getenv("MAIN_APP_PORT"))
events_url = os.getenv("BASE_URL") + ":" + str(os.getenv("EVENTS_SERVICE_PORT"))

# Конфигурация логгера
logger = logging.getLogger("logger")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("test_service.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def get_server_info(response):
    logger.info(
        f">>> Request: url='{response.request.url}', method='{response.request.method}'"
    )
    logger.info(
        f"<<< Response: status_code='{response.status_code}', data='{response.text}'"
    )


def send_test_request(params, url, endpoint, headers=headers):
    """Отправвить тестовый запрос на определенный эндпоинт"""
    resp = requests.post(url + endpoint, headers=headers, params=params)
    get_server_info(response=resp)
    if resp.status_code == 200:
        recs = resp.json()
    else:
        recs = []
        print(f"status code: {resp.status_code}")

    return recs


class TestRecommendationsService(unittest.TestCase):
    """Класс для тестирования рекомендательной системы"""

    def test_1_connection(self):
        """Проверка на то, что все сервисы доступны"""
        logger.info('Test 1: "Healthcheck status"')
        response = requests.get(main_app_url + "/healthy")
        get_server_info(response=response)
        response = response.json()
        response = response["status"]

        self.assertEqual(response, "healthy")
        logger.info("Test 1 PASS")

    def test_2_default_users(self, user_id_1: int = 1, user_id_2: int = 2):
        """Тестовые рекомендации для юзеров без персональных и онлайн истории."""
        # Получим рекомендации для user_id=1
        logger.info("-" * 50)
        logger.info('Test 2: "Default users check"')
        params_user_1 = {"user_id": user_id_1, "k": 5}
        response_user_1 = send_test_request(
            params=params_user_1,
            url=main_app_url,
            endpoint="/recommendations",
        )
        # Получим рекомендации для user_id=2
        params_user_2 = {"user_id": user_id_2, "k": 5}
        response_user_2 = send_test_request(
            params=params_user_2,
            url=main_app_url,
            endpoint="/recommendations",
        )

        self.assertEqual(response_user_1["recs"], response_user_2["recs"])
        logger.info("Test 2 PASS")
    #
    def test_3_no_empty_recs_1(self, user_id: int = 93968):
        """Тест на не пустые рекомендации для юзера с персональными рекомендациями"""
        logger.info("-" * 50)
        logger.info('Test 3: "User with personal recs check"')
        params = {"user_id": user_id, "k": 5}
        response = send_test_request(
            params=params,
            url=main_app_url,
            endpoint="/recommendations",
        )

        self.assertIsInstance(response["recs"], list)
        self.assertNotEqual(response["recs"], [])
        logger.info("Test 3 PASS")

    def test_4_no_empty_recs_2(self, user_id: int = 1):
        """Тест на непустые рекомендации для юзера без персональными рекомендаций"""
        logger.info("-" * 50)
        logger.info('Test 4: "User without personal recs check"')
        params = {"user_id": user_id, "k": 5}
        response = send_test_request(
            params=params,
            url=main_app_url,
            endpoint="/recommendations",
        )

        self.assertIsInstance(response["recs"], list)
        self.assertNotEqual(response["recs"], [])
        logger.info("Test 4 PASS")

    def test_5_online_history(
        self,
        user_id: int = 93968,
        events: list = [2193921, 6089757, 21228047, 61705629],
    ):
        """Проверка на то, что добавляется онлайн история"""
        logger.info("-" * 50)
        logger.info('Test 5: "Online events test"')
        for track_id in events:
            _ = send_test_request(
                url=events_url,
                endpoint="/put",
                params={"user_id": user_id, "track_id": track_id},
            )
        online_history = send_test_request(
            params={"user_id": user_id, "k": 10},
            url=events_url,
            endpoint="/get",
        )

        self.assertIsInstance(online_history["events"], list)
        self.assertNotEqual(online_history["events"], [])
        self.assertEqual(sorted(list(set(online_history["events"]))), events)
        logger.info("Test 5 PASS")

    def test_6_online_recommendations(self, user_id: int = 93968):
        """Тест на то, что юзер с онлайн историей имеет не нулевые онлайн рекомендации"""
        logger.info("-" * 50)
        logger.info('Test 6: "User with online events check"')
        params = {"user_id": user_id}
        response = send_test_request(
            params=params,
            url=main_app_url,
            endpoint="/recommendations_online",
        )
        self.assertEqual(len(response["recs"]), 5)
        self.assertIsInstance(response["recs"], list)
        self.assertNotEqual(response["recs"], [])

        logger.info("Test 6 PASS")

    def test_7_offline_recommendations(self, user_id: int = 93968):
        """
        Тест на то что юзер с онлайн рекомендациями имеет корректные оффлайн рекомендации
        """
        logger.info("-" * 50)
        logger.info('Test 7: "Offline recs check"')
        params = {"user_id": user_id, "k": 5}
        response = send_test_request(
            params=params,
            url=main_app_url,
            endpoint="/recommendations_offline",
        )

        self.assertIsInstance(response["recs"], list)
        self.assertNotEqual(response["recs"], [])
        self.assertEqual(len(response["recs"]), 5)
        logger.info("Test 7 PASS")

    def test_8_blended_recommendations(self, user_id: int = 93968):
        """Тест на смешивание рекомендаций оффлайн/онлайн"""
        logger.info("-" * 50)
        logger.info('Test 8: "Blended recommendations check"')
        params = {"user_id": user_id, "k": 5}
        response = send_test_request(
            params=params,
            url=main_app_url,
            endpoint="/recommendations",
        )

        self.assertIsInstance(response["recs"], list)
        self.assertNotEqual(response["recs"], [])
        self.assertEqual(len(response["recs"]), 5)
        logger.info("Test 8 PASS")

    def test_9_service_stats(self):
        """Тест статистики по запросам к сервису"""
        logger.info("-" * 50)
        logger.info('Test 9: "Stats check"')
        response = requests.get(main_app_url + "/stats")
        get_server_info(response=response)
        response = response.json()
        response_default_stats = response["request_default_count"]
        response_personal_stats = response["request_personal_count"]

        self.assertGreater(response_default_stats, 0)
        self.assertGreater(response_personal_stats, 0)
        logger.info("Test 9 PASS")


if __name__ == "__main__":
    unittest.main()