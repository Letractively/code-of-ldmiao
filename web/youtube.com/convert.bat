ffmpeg -i "QreYBpXQh2o.flv" -vcodec libx264 -s 320x240 -r 20 -g 250 -keyint_min 25 -coder ac -me_range 16 -subq 5 -sc_threshold 40 -acodec libfaac -ab 96000 -ar 22500 -cmp +chroma -partitions +parti4x4+partp8x8+partb8x8 -i_qfactor 0.71 -b_strategy 1 -crf 30 -y "converted_video_file.mp4" 2>"converted_video_file.txt"