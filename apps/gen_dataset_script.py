import os
import yaml
import uuid
from context import abci_util

script_save_dir = '/home/acb10767ym/scratch/FourierBasisDB/logs/abci/gen_dataset'
run_path = '/home/acb10767ym/scratch/FourierBasisDB/apps'
log_dir = '/home/acb10767ym/scratch/FourierBasisDB/logs/abci/abcilog/gen_dataset'
# targetdir = '/home/gatheluck/Desktop/FBDB/train'
# script_save_dir = '/home/gatheluck/Desktop/test'
# run_path = '/run/path'
# log_path = '/home/gatheluck/Desktop/test/log'


def generate_datset_script(metrics: list, norm_types: list, num_image_per_class: int, num_basies: list, image_sizes: list, val_ratio: float, log_dir: str):
    assert len(num_basies) == len(image_sizes)

    for metric in metrics:
        for norm_type in norm_types:
            for num_basis, image_size in zip(num_basies, image_sizes):
                cmd = list()
                cmd.append('python generate.py')
                cmd.append('metric={}'.format(metric))
                cmd.append('norm_type={}'.format(norm_type))
                cmd.append('num_image_per_class={}'.format(num_image_per_class))
                cmd.append('num_basis={}'.format(num_basis))
                cmd.append('image_size={}'.format(image_size))
                cmd.append('val_ratio={}'.format(val_ratio))
                cmd.append('log_dir={}'.format(log_dir))

                datasetname = '_'.join(['fbdb', metric, norm_type, str(num_image_per_class), str(num_basis), str(image_size)])
                script_save_path = os.path.join(script_save_dir, datasetname + '.sh')
                log_path = os.path.join(log_dir, datasetname + '.o')

                # append to cmd
                cmds = [' '.join(cmd)]
                abci_util.generate_job_script(cmds, script_save_path, run_path, log_path, datasetname, conda_path='/home/acb10767ym/miniconda3', conda_env='nao')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-l", "--log_dir", type=str, default='/groups1/gca50149/fukuhara/dataset')
    parser.add_argument("--metrics", type=str, nargs="+", default=['freq'])
    parser.add_argument("--norm_types", type=str, nargs="+", default=['l2'])
    parser.add_argument("--num_image_per_class_train", type=int, default=1000)
    parser.add_argument("--num_basies", type=list, default=[31])
    parser.add_argument("--image_sizes", type=list, default=[32])
    parser.add_argument("--val_ratio", type=float, default=0.1)
    opt = parser.parse_args()

    if opt.val_ratio > 0.0:
        num_image_per_class = int((1.0 + opt.val_ratio) * float(opt.num_image_per_class_train))
    else:
        num_image_per_class = opt.num_image_per_class_train

    generate_datset_script(metrics=opt.metrics, norm_types=opt.norm_types, num_image_per_class=num_image_per_class, num_basies=opt.num_basies, image_sizes=opt.image_sizes, val_ratio=opt.val_ratio, log_dir=opt.log_dir)
