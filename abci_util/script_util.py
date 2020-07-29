import os
import sys

base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
sys.path.append(base)


def generate_job_script(cmd, script_save_path, run_path, log_path, ex_name, resource='rt_F=1', max_time='72:00:00', conda_path='', conda_env='', optional_cmds=[], cuda_version='10.0/10.0.130', cudnn_version='7.6/7.6.2', **kwargs):
    """
    This is helper function to generate abci job script. (About job script please check https://docs.abci.ai/ja/03/#submit-a-batch-job)

    Args
    - cmd (str or list): main command which is executed by ABCI.
    - scrtipt_save_path (str): generated scripts are saved under this path.
    - run_path (str): [cmd] is executed from this path.
    - log_path (str): log file of abci is saved under this path.
    - ex_name (str): name for experiment.
    - resource (str): computational resource type and number. (eg. rt_F=1)
    - max_time (str): maximum execution time for an experiment. when execution time of job exceed max_time, job is rejected.
    - conda_path (str): path to conda. if you want to use virtual env in batch job, you have to activate it in a job script.
    - conda_env (str): vitrual environment name which is used by conda.
    - optional_cmds (list): list of optional commands executed before [cmd]. example usage is declare api key of online logger.
    """
    SUPPORTED_RESOURCE_TYPE = 'rt_F rt_G.large rt_G.small rt_C.large rt_C.small'.split()

    assert resource.split('=')[0] in SUPPORTED_RESOURCE_TYPE

    script_save_dir = os.path.dirname(script_save_path)
    log_dir = os.path.dirname(log_path)

    if script_save_dir:
        os.makedirs(script_save_dir, exist_ok=True)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    with open(script_save_path, mode='w') as f:
        f.write('#!/bin/bash\n\n')
        f.write('#$ -l {resource}\n'.format(resource=resource))
        f.write('#$ -l h_rt={max_time}\n'.format(max_time=max_time))
        f.write('#$ -j y\n')  # standard error stream is merged into standard output stream
        f.write('#$ -N {ex_name}\n'.format(ex_name=ex_name))
        f.write('#$ -o {log_path}\n\n'.format(log_path=log_path))

        if conda_path and conda_env:
            f.write('export PATH={conda_path}/bin:${PATH}\n'.format(conda_path=conda_path, PATH='{PATH}'))
            f.write('source activate {conda_env}\n\n'.format(conda_env=conda_env))

        f.write('export PATH=/apps/gcc/7.3.0/bin:${PATH}\n'.format(PATH='{PATH}'))
        f.write('export LD_LIBRARY_PATH=/apps/gcc/7.3.0/lib64:${LD_LIBRARY_PATH}\n\n'.format(LD_LIBRARY_PATH='{LD_LIBRARY_PATH}'))

        # load modules
        f.write('source /etc/profile.d/modules.sh\n')
        f.write('module load cuda/{cuda_version}\n'.format(cuda_version=cuda_version))
        f.write('module load cudnn/{cudnn_version}\n\n'.format(cudnn_version=cudnn_version))

        # optional
        if optional_cmds:
            for optional_cmd in optional_cmds:
                f.write('{optional_cmd}\n'.format(optional_cmd=optional_cmd))
            f.write('\n')

        # execute command
        f.write('cd {run_path}\n'.format(run_path=run_path))
        if type(cmd) != list:
            cmd = [cmd]
        for cmd_i in cmd:
            f.write(cmd_i + '\n')


if __name__ == '__main__':
    generate_job_script('python hoge.py', '../logs/test_generate_script', '/run/path', '../logs/log_path/log.o', 'test_generate_script', optional_cmds=['export ONLINE_LOGGER_API_KEY=xxxxxxxx'])
