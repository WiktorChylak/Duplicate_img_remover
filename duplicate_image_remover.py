import os
import cv2 as cv
from concurrent.futures import ThreadPoolExecutor
import threading
import numpy as np


class DuplicateImageRemover:
    def __init__(self, directory):
        self.directory = directory
        self.lock = threading.Lock()
        self.progress_lock = threading.Lock()  # Dodatkowa blokada dla paska postępu
        self.progress = 0  # Zmienna śledząca postęp

    def set_directory(self, new_directory):
        if isinstance(new_directory, bytes):
            self.directory = new_directory.decode('utf-8')
        else:
            self.directory = new_directory

    def are_images_identical(self, img1=None, img2=None, threshold=0.95):
        if img1 is None or img2 is None:
            return False

        if img1.shape != (img1.shape[0], img1.shape[1], 3):
            print(f"Obraz img1 ma nieoczekiwaną liczbę kanałów: {img1.shape}")
            return False
        
        if img2.shape != (img2.shape[0], img2.shape[1], 3):
            print(f"Obraz img2 ma nieoczekiwaną liczbę kanałów: {img2.shape}")
            return False

        # min_dimension = min(img1.shape[0], img1.shape[1], img2.shape[0], img2.shape[1])
        # win_size = 7 if min_dimension >= 7 else min_dimension

        # similarity, _ = ssim(img1, img2, multichannel=True, full=True, win_size=win_size, channel_axis=2)
        similarity = self.are_images_similar(img1, img2)
        return similarity >= threshold

    def process_files_in_chunk(self, files_chunk, images, total_chunks, progress_callback):
        for filename in files_chunk:
            img_path = os.path.join(self.directory, filename)
            img = cv.imread(img_path)
            if img is None:
                continue

            with self.lock:
                for stored_img_path, stored_img in list(images.items()):
                    if self.are_images_identical(stored_img, img):
                        print(f"Znaleziono duplikat: {img_path} i {stored_img_path}. Usuwanie {img_path}")
                        os.remove(img_path)
                        break
                else:
                    images[img_path] = img

        # Aktualizacja postępu
        with self.progress_lock:
            self.progress += 1
            if progress_callback:
                progress_callback(self.progress, total_chunks)

    def remove_duplicate_images(self, progress_callback=None):
        images = {}
        file_list = [f for f in os.listdir(self.directory) if f.endswith((".png", ".jpg", ".jpeg"))]
        
        # Podziel pliki na mniejsze fragmenty do równoczesnego przetwarzania
        chunk_size = len(file_list) // os.cpu_count()  # Liczba fragmentów zależy od liczby dostępnych rdzeni procesora
        chunks = [file_list[i:i + chunk_size] for i in range(0, len(file_list), chunk_size)]
        total_chunks = len(chunks)  # Łączna liczba fragmentów

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.process_files_in_chunk, chunk, images, total_chunks, progress_callback)
                for chunk in chunks
            ]

            for future in futures:
                future.result()  # Poczekaj na zakończenie wszystkich wątków
    
    def are_images_similar(self, img1, img2, similarity_threshold=0.9):
        """
        Sprawdza, czy dwa obrazy są podobne w stopniu określonym przez próg podobieństwa.

        :param img1: Pierwszy obraz.
        :param img2: Drugi obraz.
        :param similarity_threshold: Próg podobieństwa (domyślnie 0.9).
        :return: True, jeśli obrazy są podobne w stopniu >= similarity_threshold, False w przeciwnym razie.
        """
        if img1.shape != img2.shape:
            return False
        return np.sum(img1 != img2) / img1.size <= 1 - similarity_threshold

if __name__ == '__main__':
    def progress_callback(progress, total):
        print(f"Postęp: {progress}/{total}")

    remover = DuplicateImageRemover(r"D:\BOTy\Broken Ranks\Data\SS\Spiders - kopia")
    remover.remove_duplicate_images(progress_callback=progress_callback)
    print(remover.directory)
