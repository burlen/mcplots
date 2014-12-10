#!/bin/bash
freqs=(30 44 70 100 143 217 353 545 857)
ress=(1080 720 480)
crfs=(18 22 26)

echo " fr res  img_mb    mov_mb   cr"
for res in ${ress[@]}
do
    echo "--------------------------------"
    for freq in ${freqs[@]}
    do
        im_size=0
        for sz in `ls -la figures/ffp8_noise_${freq}_${res}_r_*.png | tr -s ' ' | cut -d' ' -f5`
        do
            let im_size=$im_size+$sz
        done
        mv_size=`ls -la ffp8_noise_${freq}_${res}_26.mp4  | tr -s ' ' | cut -d' ' -f5`
        rat=`echo $im_size/$mv_size | bc -l`
        mv_size_mb=`echo "$mv_size/(2^20)" | bc -l`
        im_size_mb=`echo "$im_size/(2^20)" | bc -l`
        printf "%3.f %4.f %8.2f %8.2f %5.2f\n" $freq $res $im_size_mb $mv_size_mb $rat
    done
    im_size=0
    for sz in `ls -la figures_3x3/ffp8_noise_${res}_r_*.png | tr -s ' ' | cut -d' ' -f5`
    do
        let im_size=$im_size+$sz
    done
    mv_size=`ls -la ffp8_noise_3x3_${res}_26.mp4  | tr -s ' ' | cut -d' ' -f5`
    rat=`echo $im_size/$mv_size | bc -l`
    mv_size_mb=`echo "$mv_size/(2^20)" | bc -l`
    im_size_mb=`echo "$im_size/(2^20)" | bc -l`
    printf "3x3 %4.f %8.2f %8.2f %5.2f\n" $res $im_size_mb $mv_size_mb $rat
    echo "--------------------------------"
done
