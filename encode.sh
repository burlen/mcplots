#!/bin/bash
freqs=(30 44 70 100 143 217 353 545 857)
ress=(1080 720 480)
crfs=(18 22 26)
for freq in ${freqs[@]}
do
    for res in ${ress[@]}
    do
        #pids=()
        for crf in ${crfs[@]}
        do
            echo "processing freq=$freq res=$res crf=$crf"
            if [ ! -e ffp8_noise_${freq}_${res}_${crf}.mp4 ]
            then
                ffmpeg -loglevel error -y \
                    -i figures/ffp8_noise_${freq}_${res}_r_%05d.png \
                    -c:v libx264 -preset slow -crf $crf \
                    -pix_fmt yuv420p -threads 16 \
                    ffp8_noise_${freq}_${res}_${crf}.mp4 \
                    > fferr_$crf 2>&1 #&
                #pids[${#pids[@]}]=$!
            fi
        done
        #echo -n "waiting for ${pids[@]} ..."
        #wait ${pids[@]}
        echo "ok!"

    done
done
for res in ${ress[@]}
do
    for crf in ${crfs[@]}
    do
        #pids=()
        echo "processing 3x3 res=$res crf=$crf"
        if [ ! -e ffp8_noise_3x3_${res}_${crf}.mp4 ]
        then
            ffmpeg -loglevel error -y -i \
                figures_3x3/ffp8_noise_${res}_r_%05d.png \
                -c:v libx264 -preset slow -crf $crf \
                -threads 16 -pix_fmt yuv420p \
                ffp8_noise_3x3_${res}_${crf}.mp4 \
                > fferr_$crf 2>&1 #&
            #pids[${#pids[@]}]=$!
        fi
        #echo -n "waiting for ${pids[@]} ..."
        #wait ${pids[@]}
        echo "ok!"
    done
done
