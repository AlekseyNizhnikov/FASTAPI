"""Написать программу, которая скачивает изображения с заданных URL-адресов и сохраняет их на диск. Каждое изображение
должно сохраняться в отдельном файле, название которого соответствует названию изображения в URL-адресе.
Например, URL-адрес: https://example/images/image1.jpg -> файл на диске: image1.jpg
— Программа должна использовать многопоточный, многопроцессорный и асинхронный подходы.
— Программа должна иметь возможность задавать список URL-адресов через аргументы командной строки.
— Программа должна выводить в консоль информацию о времени скачивания каждого изображения и общем времени выполнения
программы."""


import threading
import multiprocessing
import asyncio
import requests
import time
import argparse, sys


def time_work(function):
    def wrapper(*args, **kwargs):
        start = time.time()
        file_name = function(*args, **kwargs) or "всех файлов сразу"
        print(f"Время скачивания {file_name}: {time.time() - start} c.")
    return wrapper


@time_work
def download_img(link):
    response = requests.get(link).content

    *_, file_name = link.split("/")
    with open(file_name, 'wb') as handler:
        handler.write(response)
    return file_name


@time_work
def start_threading(links):
    threads = []
    for link in links:
        t = threading.Thread(target=download_img, args=(link,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


@time_work
def start_multiprocessing(links):
    process = []
    for link in links:
        p = multiprocessing.Process(target=download_img, args=(link,))
        process.append(p)
        p.start()

    for p in process:
        p.join()


async def asynk_download_img(link):
    start = time.time()
    response = requests.get(link).content

    *_, file_name = link.split("/")
    with open(file_name, 'wb') as handler:
        handler.write(response)
    print(f"Время скачивания {file_name}: {time.time() - start}")


async def start_asynk(links):
    start = time.time()
    res = [asyncio.get_event_loop().create_task(asynk_download_img(link)) for link in links]
    await asyncio.gather(*res)
    print(f"Время скачивания всех файлов сразу: {time.time() - start}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', nargs='+')
    name_space = parser.parse_args(sys.argv[1:])
    links = name_space.l

    if not links:
        links = ["https://pic.rutubelist.ru/video/82/10/8210b7ee82f9973bb2ca7aebe59f4b01.jpg",
             "https://celes.club/uploads/posts/2021-12/1640827655_89-celes-club-p-zima-vecher-priroda-krasivo-foto-99.jpg",
             "https://damion.top/uploads/posts/2022-02/1645259482_36-damion-club-p-uyutnii-zimnii-vecher-priroda-39.jpg",
             "https://disgustingmen.com/wp-content/uploads/2017/12/richard-savoi-5.jpg",
             "https://adonius.club/uploads/posts/2022-07/thumbs/1657136474_59-adonius-club-p-zimnii-vecher-v-derevne-priroda-krasivo-fo-66.jpg"]

    # start_threading(links)
    # start_multiprocessing(links)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_asynk(links))
