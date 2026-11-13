#!/bin/bash
# T=<thư mục phân tích> strip.sh <video_id> <t_start_s> <dur_s> [fps=12] [cols=6]  -> zoom/<id>_<t>_<fps>.jpg (dải khung hình dày, có nhãn thời gian)
# frame.sh-like full-res: strip.sh <id> <t> full  -> zoom/<id>_<t>_full.png
S=${T:?"đặt biến T = thư mục phân tích (có videos/, zoom/)"}
FF=/home/vmiz/.local/bin/ffmpeg; V=$S/videos/$1.mp4
if [ "$3" = "full" ]; then O=$S/zoom/${1}_${2}_full.png; $FF -v error -y -ss $2 -i $V -frames:v 1 $O; echo $O; exit; fi
FPS=${4:-12}; C=${5:-6}; N=$(python3 -c "import math;print(math.ceil($3*$FPS))"); R=$(( (N + C - 1) / C ))
O=$S/zoom/${1}_${2}_${FPS}.jpg
$FF -v error -y -ss $2 -t $3 -i $V -vf "fps=$FPS,scale=240:-2,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='%{pts\:hms}':x=4:y=4:fontsize=16:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=${C}x${R}" -frames:v 1 -q:v 3 $O; echo $O
