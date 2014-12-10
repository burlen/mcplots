#!/bin/bash
freqs=(30 44 70 100 143 217 353 545 857)
ress=(1080 720 480)
crfs=(18 22 26)
for freq in ${freqs[@]}
do
    for res in ${ress[@]}
    do
        for i in `seq 0 9999`
        do
            ii=`printf %05.f $i`
            if [ ! -e figures/ffp8_noise_${freq}_${res}_r_${ii}.png ]
            then
                echo figures/ffp8_noise_${freq}_${res}_r_${ii}.png
            fi
        done
    done
done
for res in ${ress[@]}
do
    for crf in ${crfs[@]}
    do
        for i in `seq 0 9999`
        do
            ii=`printf %05.f $i`
            if [ ! -e figures_3x3/ffp8_noise_${res}_r_${ii}.png ]
            then
                echo figures_3x3/ffp8_noise_${res}_r_${ii}.png
            fi
        done
    done
done
