#!/bin/bash

# 0 - 9999

nersc_user=$USER
n_realizations=10000
export cores_per_job=120
let n_jobs=($n_realizations/$cores_per_job)
let n_jobs1=($n_jobs-1)
last_job=`cat last_job_3x3`
let last_job=$last_job+1
for i in `seq $last_job $n_jobs1`
do
    j=`qs -u $nersc_user | grep debug | grep -v " C " | wc -l`
    while [ $j -gt 8 ]
    do
      sleep 1m
      j=`qs -u $nersc_user | grep debug | grep -v " C " | wc -l`
      echo -n "."
    done
    let base_step=($i*$cores_per_job)
    export base_step
    jid=`qsub -A planck -N im_3x3 -q debug -l walltime=00:30:00 -l mppwidth=$cores_per_job mcplots_3x3.qsub`
    echo "$i $jid $base_step"
    echo $i > last_job_3x3
done
let base_step=($n_jobs*$cores_per_job)
let cores_per_job=( $n_realizations - $cores_per_job*$n_jobs )
export cores_per_job base_step
jid=`qsub -A planck -N im_3x3 -q debug -l walltime=00:30:00 -l mppwidth=$cores_per_job mcplots_3x3.qsub`
echo "$i $jid $base_step $cores_per_job"
