import os
import sys

base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
sys.path.append(base)

import hydra
import omegaconf
import logging

from abci_util.script_util import generate_job_script


@hydra.main(config_path='../conf/generate_script.yaml')
def main(cfg: omegaconf.DictConfig) -> None:
    assert cfg.run_path is not None, 'please specify [run_path] option'
    assert cfg.ex_name is not None, 'please specify [ex_name] option'
    assert cfg.cmd is not None, 'please specify [cmd] option'

    # if some option is not defined, automatically fill them.
    cfg.script_save_path = os.path.join(cfg.ex_name + '_run.sh') if cfg.script_save_path is None else cfg.script_save_path
    cfg.log_path = os.path.join(cfg.ex_name + '_log.o') if cfg.log_path is None else cfg.log_path

    hydra_logger = logging.getLogger(__name__)
    hydra_logger.info(' '.join(sys.argv))
    hydra_logger.info(cfg.pretty())

    # fix relative path specification because hydra automatically change current working directory.
    for k, v in cfg.items():
        if k.endswith('path'):
            if k in 'script_save_path log_path'.split():
                continue

            if not (v.startswith('/') or v.startswith('~')):
                cfg[k] = os.path.join(hydra.utils.get_original_cwd(), v)

    generate_job_script(**cfg)


if __name__ == '__main__':
    main()
