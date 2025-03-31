#!/bin/bash
#SBATCH --account=mia351
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=4
#SBATCH --mem=249208M 
#SBATCH --time=24:00:00
#SBATCH --error=%x-%j.err
#SBATCH --output=%x-%j.out
#SBATCH --mail-user=oohiro@umich.edu
#SBATCH --mail-type=ALL
#SBATCH --export=ALL

#SBATCH --comment=24:00:00
#SBATCH --time-min=24:00:00
#SBATCH --signal=B:USR1@300
#SBATCH --requeue
#SBATCH --open-mode=append
#SBATCH --job-name=A1_1TSvib

# Load necessary modules
# module purge
module load shared
module load sdsc/1.0
module load DefaultModules

#module use ~/privatemodules
#module load vasp-tpc/5.4.4

module load cpu/0.15.4
module load gcc/9.2.0
module load openmpi/3.1.6
module load fftw/3.3.8
module load vasp/5.4.4-vtst-openblas

# Remove STOPCAR file so job isn't blocked
if [ -f "STOPCAR" ]; then
    rm STOPCAR
fi


#srun must execute in background and catch signal on wait command
export MV2_ENABLE_AFFINITY=0
export SRUN_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK}
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_PROC_BIND='true'

srun  --cpu_bind=cores vasp_std &

#srun --mpi=pmi2 vasp_std 

# put any commands that need to run to continue the next job (fragment) here
ckpt_vasp() {
    set -x
    restarts=`squeue -h -O restartcnt -j $SLURM_JOB_ID`
    echo checkpointing the ${restarts}-th job

    # Trim space from restarts variable for inclusion into filenames
    restarts_num=`echo $restarts | sed -e 's/^[ \t]*//'`
    echo "Restart number: ==${restarts_num}=="

    #to terminate VASP at the next electronic step
    echo LABORT = .TRUE. > STOPCAR

    #wait until VASP to complete the current step, write out WAVECAR file and quit
    srun_pid=`ps -fle|grep srun|head -1|awk '{print $4}'`
    echo srun pid is $srun_pid
    wait $srun_pid

    # copy CONTCAR to POSCAR and back up data from current run, for each folder
    for folder in $(ls -d */); do
        cd "$folder"
        echo "In directory $folder"

        cp -p CONTCAR POSCAR
        echo "CONTCAR copied."

        cp -p OUTCAR "OUTCAR-${restarts_num}"
        echo "OUTCAR copied."

        cp -p OSZICAR "OSZICAR-${restarts_num}"
        echo "OSZICAR copied."

        cd ..
    done

    # Back up the vasprun.xml file in the parent folder
    cp -p vasprun.xml "vasprun-${restarts_num}.xml"
    echo "vasprun.xml copied."

    set +x
}

ckpt_command=ckpt_vasp
max_timelimit=24:00:00
ckpt_overhead=300

# requeueing the job if remaining time >0
#source ~/temp/vartime-setup.sh
#requeue_job func_trap USR1
wait
echo "run complete on `hostname`: `date` `pwd`" >> ~/job.log
