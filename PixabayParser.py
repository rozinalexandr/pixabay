import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import csv
import time
from tqdm import tqdm
load_dotenv()


class PixabayParser:
    def __init__(self, settings: dict):
        self._settings = settings
        self._API_KEY = os.getenv("API_KEY")
        self._base_url = f"https://pixabay.com/api/?key={self._API_KEY}&"

    def _compose_query_url(self) -> str:
        query_settings = self._settings["Query Settings"]

        settings_list = []
        for k, v in query_settings.items():
            settings_list.append(f"{k}={v.lower().replace(' ', '+') if isinstance(v, str) else v}")

        return self._base_url + "&".join(settings_list)

    @staticmethod
    def _extract_value_from_dict(image_info_dict: dict, key: str) -> str | int | None:
        try:
            return image_info_dict[key]
        except KeyError:
            return None

    @staticmethod
    def _save_image(image_url: str, image_name: str, image_extension: str, image_save_directory_path: str) -> None:
        img_data = requests.get(image_url).content
        with open(f"{image_save_directory_path}/{image_name}.{image_extension}", 'wb') as handler:
            handler.write(img_data)

    @staticmethod
    def _save_raw_data(raw_data_directory_path: str, row: list) -> None:
        with open(f"{raw_data_directory_path}/output.csv", "a", encoding="UTF-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)
            f.close()

    def run(self):
        current_date = datetime.now().date().strftime("%Y-%m-%d")

        output_image_dir_path = f"{self._settings['Output Directory']}/{current_date}/images"
        output_raw_data_dir_path = f"{self._settings['Output Directory']}/{current_date}/raw_data"
        Path(output_image_dir_path).mkdir(parents=True, exist_ok=True)
        Path(output_raw_data_dir_path).mkdir(parents=True, exist_ok=True)

        if len(os.listdir(output_raw_data_dir_path)) == 0:
            output_file_headers_list = ["img_id", "img_extension", "img_name", "img_url", "img_type", "img_tags",
                                        "img_views", "img_likes", "img_downloads", "img_comments", "author_id",
                                        "author_name", "image_query"]
            self._save_raw_data(output_raw_data_dir_path, output_file_headers_list)

        query_url = self._compose_query_url()

        response_json = requests.get(query_url).json()
        total_images = response_json["total"]

        page_amount = total_images // self._settings["Query Settings"]["per_page"] + 1

        for page in range(1, page_amount + 1):
            current_page_url = query_url + f"&page={page}"
            try:
                current_page_response = requests.get(current_page_url).json()
            except requests.exceptions.JSONDecodeError:
                break

            for image_info in tqdm(current_page_response["hits"], desc="Collecting images info...", leave=True):
                image_id = self._extract_value_from_dict(image_info, "id")
                image_type = self._extract_value_from_dict(image_info, "type")
                image_url = self._extract_value_from_dict(image_info, "largeImageURL")
                image_extension = image_url.split(".")[-1]
                image_name = str(image_id) + "." + image_extension
                image_tags = self._extract_value_from_dict(image_info, "tags")
                image_views = self._extract_value_from_dict(image_info, "views")
                image_likes = self._extract_value_from_dict(image_info, "likes")
                image_downloads = self._extract_value_from_dict(image_info, "downloads")
                image_comments = self._extract_value_from_dict(image_info, "comments")
                image_author_id = self._extract_value_from_dict(image_info, "user_id")
                image_author_name = self._extract_value_from_dict(image_info, "user")
                image_query = self._settings["Query Settings"]["q"].lower()
                self._save_image(image_url=image_url,
                                 image_name=image_id,
                                 image_extension=image_extension,
                                 image_save_directory_path=output_image_dir_path)

                self._save_raw_data(output_raw_data_dir_path, [image_id, image_extension, image_name, image_url,
                                                               image_type, image_tags, image_views, image_likes,
                                                               image_downloads, image_comments, image_author_id,
                                                               image_author_name, image_query])
