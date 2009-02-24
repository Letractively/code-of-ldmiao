python D:\Program\pyinstaller-1.3\Configure.py
python D:\Program\pyinstaller-1.3\Makespec.py -F -c -n PicasaDownloader getcontent.py picasa.py
python D:\Program\pyinstaller-1.3\Build.py PicasaDownloader.spec

python D:\Program\pyinstaller-1.3\Makespec.py -F -c -n removeNonsenseImages removeNonsenseImages.py
python D:\Program\pyinstaller-1.3\Build.py removeNonsenseImages.spec
