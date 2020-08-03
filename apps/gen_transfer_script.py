import os
import yaml
import uuid
from context import abci_util

targetdir = '/home/acb10767ym/scratch/Stronghold/logs/train'
script_save_dir = '/home/acb10767ym/scratch/Stronghold/logs/abci/transfer_script'
run_path = '/home/acb10767ym/scratch/Stronghold/apps'
log_dir = '/home/acb10767ym/scratch/Stronghold/logs/abci/abcilog/transfer'
# targetdir = '/home/gatheluck/Desktop/FBDB/train'
# script_save_dir = '/home/gatheluck/Desktop/test'
# run_path = '/run/path'
# log_path = '/home/gatheluck/Desktop/test/log'


def generate_transfer_script(targetdir, unfreeze_levels=[2, 3], augmentations=['standard', 'patch_gaussian'], datasets=['cifar10', 'imagenet100']):
    success, _ = abci_util.pick_targets(targetdir)

    # loop for success
    for k, v in success.items():

        # open config
        with open(v['config']) as f:
            conf = yaml.safe_load(f.read())

            for unfreeze_level in unfreeze_levels:
                for augmentation in augmentations:

                    cmds = list()
                    cmd = list()
                    cmd.append('python transfer.py')
                    cmd.append('gpus=4')
                    cmd.append('epochs=50')
                    cmd.append('optimizer.lr=0.01')
                    cmd.append('scheduler=steplr')
                    cmd.append('project_name=fbdb_transfer')
                    cmd.append('source={source}_{source_aug}'.format(source=conf['dataset']['name'], source_aug=conf['augmentation']['name']))

                    # undefined params
                    # arch
                    # dataset
                    # batch_size
                    # augmentation
                    # unfreeze_level
                    # weight
                    # source_num_classes

                    cmd.append('arch={}'.format(conf['arch']))

                    if conf['dataset']['input_size'] == 32:
                        target_dataset = 'cifar10'
                        cmd.append('dataset=cifar10')
                        cmd.append('batch_size=32')
                        batch_size = 1024  # set batch_size for test. Without this, ABCI causes out of memory.
                    elif conf['dataset']['input_size'] == 224:
                        target_dataset = 'imagenet100'
                        cmd.append('dataset=imagenet100')
                        cmd.append('batch_size=256')
                        batch_size = 256  # set batch_size for test. Without this, ABCI causes out of memory.
                    else:
                        raise NotImplementedError

                    # if target_dataset is not interested one, continue.
                    if target_dataset not in datasets:
                        continue

                    cmd.append('source_num_classes={}'.format(conf['dataset']['num_classes']))

                    cmd.append('weight={}'.format(v['weight']))

                    cmd.append('unfreeze_level={}'.format(unfreeze_level))
                    cmd.append('augmentation={}'.format(augmentation))

                    joined_cmd = ' '.join(cmd)
                    ex_name = 'transfer_{source}_{source_aug}_2_{target}_{target_aug}_unfreeze-{unfreeze}'.format(source=conf['dataset']['name'], source_aug=conf['augmentation']['name'], target=target_dataset, target_aug=augmentation, unfreeze=unfreeze_level)
                    script_save_path = os.path.join(script_save_dir, ex_name + ('.sh'))
                    log_path = os.path.join(log_dir, ex_name + '.o')

                    optional_cmds = ['export ONLINE_LOGGER_API_KEY=NmyQglPnLn5hXygaFurgEHG5M',
                                     'export EXP_ID={exp_id}'.format(exp_id=uuid.uuid4())]

                    # append to cmds
                    cmds.append(joined_cmd)

                    # cmd for test
                    cmds.append('python test.py tester=acc arch={arch} dataset={dataset} batch_size={batch_size}'.format(arch=conf['arch'], dataset=target_dataset, batch_size=batch_size))
                    if target_dataset == 'cifar10':
                        cmds.append('python test.py tester=corruption arch={arch} dataset={dataset} batch_size={batch_size}'.format(arch=conf['arch'], dataset=target_dataset + 'c', batch_size=batch_size))
                    cmds.append('python test.py tester=spacial arch={arch} dataset={dataset} batch_size={batch_size}'.format(arch=conf['arch'], dataset=target_dataset, batch_size=batch_size))
                    cmds.append('python test.py tester=sensitivity arch={arch} dataset={dataset} batch_size={batch_size}'.format(arch=conf['arch'], dataset=target_dataset, batch_size=batch_size))
                    cmds.append('python test.py tester=layer arch={arch} dataset={dataset} batch_size={batch_size}'.format(arch=conf['arch'], dataset=target_dataset, batch_size=batch_size))
                    cmds.append('python test.py tester=fourier arch={arch} dataset={dataset} batch_size={batch_size}'.format(arch=conf['arch'], dataset=target_dataset, batch_size=batch_size))

                    abci_util.generate_job_script(cmds, script_save_path, run_path, log_path, ex_name, conda_path='/home/acb10767ym/miniconda3', conda_env='nao', optional_cmds=optional_cmds)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-a", "--augmentations", type=str, nargs="+", default=['standard', 'patch_gaussian'])
    parser.add_argument("-u", "--unfreeze_levels", type=str, nargs="+", default=[2, 3])
    parser.add_argument("-d", "--datasets", type=str, nargs="+", default=['cifar10', 'imagenet100'])
    opt = parser.parse_args()

    generate_transfer_script(targetdir, augmentations=opt.augmentations, unfreeze_levels=opt.unfreeze_levels, datasets=opt.datasets)
