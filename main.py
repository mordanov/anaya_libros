from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import time
import os
import argparse

# ================= CONFIG =================

LINKS = {
    "doc_1": "https://example.com/first",
    "doc_2": "https://example.com/second",
}

BASE_DIR = "output"
IMAGES_DIR = os.path.join(BASE_DIR, "images")

# These will be set by command-line arguments
PROFILE_PATH = None
PROFILE_NAME = None
PDF_FILENAME = "result.pdf"

WAIT = 10

# ==========================================


def create_driver():
    options = Options()
    options.add_argument(f"--user-data-dir={PROFILE_PATH}")
    options.add_argument(f"--profile-directory={PROFILE_NAME}")

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


def collect_images(driver):
    os.makedirs(IMAGES_DIR, exist_ok=True)

    all_images = []
    global_step = 1
    wait = WebDriverWait(driver, WAIT)

    for name, url in LINKS.items():
        print(f"\n=== Processing {name} ===")
        driver.get(url)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.content")))
        time.sleep(1)

        while True:
            content = driver.find_element(By.CSS_SELECTOR, "div.content")

            # Find all pageSection elements inside content
            sections = content.find_elements(By.CSS_SELECTOR, '[id^="pageSection"]')

            if not sections:
                print("No pageSection elements found")
                break

            for section in sections:
                img_path = os.path.join(IMAGES_DIR, f"{global_step:04}.png")
                section.screenshot(img_path)
                all_images.append(img_path)

                section_id = section.get_attribute("id")
                print(f"Screenshot {global_step} ({section_id})")
                global_step += 1

            # Check the Next button state
            next_btn = driver.find_element(By.ID, "page_next")
            classes = next_btn.get_attribute("class")

            if "disabled" in classes:
                print("Next button is disabled — end of document")
                break

            next_btn.click()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.content")))
            time.sleep(1)

    return all_images


def images_to_pdf(images, pdf_path):
    pil_images = [Image.open(img).convert("RGB") for img in images]
    pil_images[0].save(
        pdf_path,
        save_all=True,
        append_images=pil_images[1:]
    )


def parse_arguments():
    parser = argparse.ArgumentParser(description="Collect images from web pages and convert to PDF")
    parser.add_argument("--username", required=True, help="Username for Chrome profile path")
    parser.add_argument("--profile-name", required=True, help="Chrome profile name (e.g., Default)")
    parser.add_argument("--pdf-filename", default="result.pdf", help="Output PDF filename (default: result.pdf)")
    return parser.parse_args()


def main():
    global PROFILE_PATH, PROFILE_NAME, PDF_FILENAME

    args = parse_arguments()
    PROFILE_PATH = f"/Users/{args.username}/Library/Application Support/Google/Chrome"
    PROFILE_NAME = args.profile_name
    PDF_FILENAME = args.pdf_filename

    os.makedirs(BASE_DIR, exist_ok=True)

    driver = create_driver()
    driver.maximize_window()

    try:
        images = collect_images(driver)
        pdf_path = os.path.join(BASE_DIR, PDF_FILENAME)
        images_to_pdf(images, pdf_path)
        print(f"\nPDF successfully created: {pdf_path}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
