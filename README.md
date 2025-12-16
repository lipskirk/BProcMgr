Autor: Radosław Lipski

Tytuł pracy: "Analiza Przydatności Renderowanych Scen 3D w Procesie Uczenia Głębokich Sieci Neuronowych do Przetwarzania Obrazów"



•	generate_synth_data.py - generuje p*c obrazów syntetycznych (p przejść renderowania po c pozycji kamery) na podstawie wskazanej sceny .blend !WYMAGA BLENDERPROC!

•	fix_coco_categories.py - poprawia listę kategorii w plikach JSON zbioru COCO na podstawie pliku 'coco_categories.txt'

•	create_yolo_subset.py - tworzy podzbiór o zadanym rozmiarze w zadanej lokalizacji na podstawie wskazanego zbioru YOLO

•	format_det_results.py - formatuje predykcje detekcji wyeksportowane z FiftyOne do formatu COCO, wymaganego przez serwer test-dev (bbox)

•	format_segm_results.py - formatuje predykcje segmentacji wyeksportowane z FiftyOne do formatu COCO, wymaganego przez serwer test-dev (segm); konwertuje polygony do formatu RLE  !WYMAGA BLENDERPROC!

•	augm_synth_data.py - generuje zmodyfikowane obrazy na podstawie obrazu wejściowego i maski binarnej za pomocą modelu Stable Diffusion 

•	annotate_augm_data.py - kopiuje oryginalne pliki .txt z etykietami w formacie YOLO do wskazanej lokalizacji i dostosowuje ich nazwy na podstawie wskazanych obrazów

•	remove_files.py - usuwa z danej lokalizacji wszystkie pliki, które znajdują się w drugiej wskazanej lokalizacji

•	replace_background.py - podmienia we wskazanym obrazie tło na drugi wskazany obraz, na podstawie wskazanej maski 

•	coco_categories.txt - lista kategorii i superkategorii COCO dostosowana do serwera ewaluacyjnego test-dev
