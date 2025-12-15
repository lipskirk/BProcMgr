Autor: Radosław Lipski
Tytuł pracy: "Analiza Przydatności Renderowanych Scen 3D w Procesie Uczenia Głębokich Sieci Neuronowych do Przetwarzania Obrazów"

Opis skryptów:

•	generate_synth_data.py - generuje p*c obrazów syntetycznych (p przejść renderowania po c pozycji kamery) na podstawie sceny .blend !WYMAGA BLENDERPROC!

•	fix_coco_categories.py - poprawia listę kategorii w plikach JSON zbioru COCO na podstawie pliku 'coco_categories.txt'

•	create_yolo_subset.py - tworzy podzbiór o zadanym rozmiarze w zadanej lokalizacji na podstawie wskazanego zbioru YOLO

•	format_det_results.py - formatuje predykcje detekcji wyeksportowane z FiftyOne do formatu COCO na serwer test-dev (bbox)

•	format_segm_results.py - konwertuje polygony do RLE, formatuje predykcje segmentacji wyeksportowane z FiftyOne do formatu COCO na serwer test-dev (segm) !WYMAGA BLENDERPROC!

•	augm_synth_data.py - generuje zmodyfikowane obrazy na podstawie obrazu wejsciowego i maski binarnej za pomocą modelu Stable Diffusion 

•	annotate_augm_data.py - kopiuje pliki .txt z etykietami w formacie YOLO ze wskazanej lokalizacji do innej, na podstawie nazw obrazów

•	remove_files.py - usuwa z danej lokalizacji wszytskie pliki, które znajdują się w innej

•	replace_background.py - podmienia we wskazanym obrazie tło na wskazany obraz, na podstawie wskazanej maski 
