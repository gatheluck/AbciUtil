import os
import argparse
import glob
import time
import subprocess


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-t", "--targetdir", type=str, required=True)
    parser.add_argument("--condition", type=str, default='*')
    opt = parser.parse_args()

    scripts = glob.glob(os.path.join(opt.targetdir, opt.condition))
    for script in scripts:
        if script.endswith('.sh'):
            cmd = 'qsub -g gca50149 {target_script}'.format(target_script=script)
            subprocess.call(cmd, shell=True)
            time.sleep(3)  # to prevent confliction of hydra save dirs.
