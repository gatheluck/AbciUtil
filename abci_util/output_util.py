import os

import glob
import shutil
import yaml
import click


def pick_targets(targetdir, faildir_name='looks_failed', targets={'weight': 'model_weight_final.pth', 'config': '.hydra/config.yaml'}, move_fail=True):
    """
    this function pick dirs which includes targets.
    """
    def _check_experiment(experimentdir, targets: dict):
        retdict = dict()

        for k, v in targets.items():
            pathlist = glob.glob(os.path.join(experimentdir, '**', v), recursive=True)

            if len(pathlist) == 1:
                retdict[k] = pathlist[0]
            else:
                return None

        return retdict

    # serch experiments
    experiments = glob.glob(os.path.join(targetdir, '*'))
    if os.path.join(targetdir, faildir_name) in experiments:
        experiments.remove(os.path.join(targetdir, faildir_name))
    else:
        os.makedirs(os.path.join(targetdir, faildir_name))

    success, fail = dict(), dict()

    # loop over experiments
    for experiment in experiments:
        retdict = _check_experiment(experiment, targets)

        if retdict:
            success[os.path.basename(experiment)] = retdict
        else:
            fail[os.path.basename(experiment)] = experiment

    # move fail
    if move_fail:
        for k, v in fail.items():
            shutil.move(v, os.path.join(targetdir, faildir_name, k))

    return success, fail


def parse_config(confpath):
    with open(confpath) as f:
        conf = yaml.safe_load(f.read())

        print(conf)



if __name__ == '__main__':
    targetdir = '/home/gatheluck/Desktop/FBDB/train'
    success, fail = pick_targets(targetdir)
    # print(success)
    # print(fail)
    # print(len(success))
    # print(len(fail))

    for k, v in success.items():
        parse_config(v['config'])
        break