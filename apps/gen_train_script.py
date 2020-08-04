import os
import yaml
import uuid
from context import abci_util

script_save_dir = '/home/acb10767ym/scratch/Stronghold/logs/abci/train_script'
run_path = '/home/acb10767ym/scratch/Stronghold/apps'
log_dir = '/home/acb10767ym/scratch/Stronghold/logs/abci/abcilog/train'
# targetdir = '/home/gatheluck/Desktop/FBDB/train'
# script_save_dir = '/home/gatheluck/Desktop/test'
# run_path = '/run/path'
# log_path = '/home/gatheluck/Desktop/test/log'


def generate_train_script(augmentations, datasets, project_name_postfix=''):

    for dataset in datasets:
        for augmentation in augmentations:

            cmds = list()
            cmd = list()
            cmd.append('python train.py')
            cmd.append('dataset={}'.format(dataset))
            cmd.append('augmentation={}'.format(augmentation))
            cmd.append('gpus=4')
            cmd.append('project_name=train{}'.format('_' + project_name_postfix if project_name_postfix else ''))

            # undefined params
            if dataset in ['cifar10',
                           'fbdb_metric-balance_norm-l2_basis-0031_size-0032_cls-0496',
                           'fbdb_metric-freq_norm-l2_basis-0031_size-0032_cls-0022',
                           'fbdb_metric-index_norm-l2_basis-0031_size-0032_cls-0496']:
                cmd.append('arch=resnet56')
                cmd.append('batch_size=128')
                cmd.append('epochs=200')
                cmd.append('scheduler.milestones=[100,150]')
            else:
                cmd.append('arch=resnet50')
                cmd.append('batch_size=256')
                cmd.append('epochs=90')
                cmd.append('scheduler.milestones=[30,60,80]')

            joined_cmd = ' '.join(cmd)
            ex_name = 'train_{dataset}_{aug}'.format(dataset=dataset, aug=augmentation)
            script_save_path = os.path.join(script_save_dir, ex_name + ('.sh'))
            log_path = os.path.join(log_dir, ex_name + '.o')

            optional_cmds = ['export ONLINE_LOGGER_API_KEY=NmyQglPnLn5hXygaFurgEHG5M']

            # append to cmds
            cmds.append(joined_cmd)
            abci_util.generate_job_script(cmds, script_save_path, run_path, log_path, ex_name, conda_path='/home/acb10767ym/miniconda3', conda_env='nao', optional_cmds=optional_cmds)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-a", "--augmentations", type=str, nargs="+", default=['standard', 'patch_gaussian'])
    parser.add_argument("-d", "--datasets", type=str, nargs="+", default=['cifar10',
                                                                          'fbdb_metric-balance_norm-l2_basis-0031_size-0032_cls-0496',
                                                                          'fbdb_metric-freq_norm-l2_basis-0031_size-0032_cls-0022',
                                                                          'fbdb_metric-index_norm-l2_basis-0031_size-0032_cls-0496'])
    parser.add_argument("--postfix", type=str, required=True)
    opt = parser.parse_args()

    generate_train_script(augmentations=opt.augmentations, datasets=opt.datasets, project_name_postfix=opt.postfix)
