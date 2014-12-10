#!/bin/bash

# run this script via nohup then put it in the background
# jobs are submitted through the debug queue until all
# of the cases have been processed

nersc_user=$USER
n_realizations=10000
export cores_per_job=120

let n_jobs=($n_realizations/$cores_per_job)
let n_jobs1=($n_jobs-1)

if [ ! -e last_job ]
then
    echo -1 > last_job
fi
last_job=`cat last_job`
let last_job=$last_job+1

for i in `seq $last_job $n_jobs1`
do
    # stay under the 20 job limit
    j=`qs -u $nersc_user | grep debug | grep -v " C " | wc -l`
    while [ $j -gt 8 ]
    do
      sleep 1m
      j=`qs -u $nersc_user | grep debug | grep -v " C " | wc -l`
      echo -n "."
    done

    # set the base realiazation for the job. each rank processes
    # the realization given by base + rank
    let base_step=($i*$cores_per_job)
    export base_step

    # submit the job
    jid=`qsub -A planck -N im -q debug -l walltime=00:30:00 -l mppwidth=$cores_per_job mcplots.qsub`

    echo "$i $jid $base_step"

    # save where we are incase we need to restart
    echo $i > last_job
done

# run a job for the remainder of realizations
let rem=($n_realizations % $cores_per_job)
if [ ! $rem -eq 0 ]
then
    let base_step=($n_jobs*$cores_per_job)
    let cores_per_job=($n_realizations - $cores_per_job*$n_jobs)
    export cores_per_job base_step
    jid=`qsub -A planck -N im -q debug -l walltime=00:30:00 -l mppwidth=$cores_per_job mcplots.qsub`
    echo "$i $jid $base_step $cores_per_job"
fi
echo -1 > last_job
