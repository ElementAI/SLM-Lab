# The retro analysis module
# Runs analysis post-hoc using existing data files
# example: yarn retro_analyze data/reinforce_cartpole_2018_01_22_211751/
from glob import glob
from pathlib import Path

from slm_lab.experiment import analysis
from slm_lab.lib import logger, util
import os
import pydash as ps

logger = logger.get_logger(__name__)


def retro_analyze_sessions(predir):
    '''Retro analyze all sessions'''
    logger.info('Running retro_analyze_sessions')
    session_spec_paths = glob(f'{predir}/*_s*_spec.json')
    for p in session_spec_paths:
        _retro_analyze_session(p)


def _retro_analyze_session(session_spec_path):
    '''Method to retro analyze a single session given only a path to its spec'''
    session_spec = util.read(session_spec_path)
    info_prepath = session_spec['meta']['info_prepath']
    for df_mode in ('eval', 'train'):
        file = f'{info_prepath}_session_df_{df_mode}.csv'
        if Path(file).exists():
            session_df = util.read(file)
            analysis.analyze_session(session_spec, session_df, df_mode)
        else:
            logger.warn(f"skipping missing file {file}")


def retro_analyze_trials(predir):
    '''Retro analyze all trials'''
    logger.info('Running retro_analyze_trials')
    session_spec_paths = glob(f'{predir}/*_s*_spec.json')
    # remove session spec paths
    trial_spec_paths = ps.difference(glob(f'{predir}/*_t*_spec.json'), session_spec_paths)
    for p in trial_spec_paths:
        _retro_analyze_trial(p)


def _retro_analyze_trial(trial_spec_path):
    '''Method to retro analyze a single trial given only a path to its spec'''
    if Path(trial_spec_path).exists():
        trial_spec = util.read(trial_spec_path)
        meta_spec = trial_spec['meta']
        info_prepath = meta_spec['info_prepath']
        session_metrics_list = []
        for s in range(meta_spec['max_session']):
            file = f'{info_prepath}_s{s}_session_metrics_eval.pkl'
            if Path(file).exists():
                session_metrics_list.append(util.read(file))
        if len(session_metrics_list) > 0:
            analysis.analyze_trial(trial_spec, session_metrics_list)
        else:
            logger.warn(f"skipping, no sessions found for: {trial_spec_path}")
    else:
        logger.warn(f"skipping missing file {trial_spec_path}")


def retro_analyze_experiment(predir):
    '''Retro analyze an experiment'''
    logger.info('Running retro_analyze_experiment')
    if ps.is_empty(glob(f'{predir}/info/*_trial_data_dict.json')):
        logger.info('Skipping retro_analyze_experiment since no experiment was ran.')
        return  # only run analysis if experiment had been ran
    trial_spec_paths = glob(f'{predir}/*_t*_spec.json')
    # remove trial and session spec paths
    experiment_spec_paths = ps.difference(glob(f'{predir}/*_spec.json'), trial_spec_paths)
    experiment_spec_path = experiment_spec_paths[0]
    if Path(experiment_spec_path).exists():
        spec = util.read(experiment_spec_path)
        info_prepath = spec['meta'].get('info_prepath')
        trial_data_dict = util.read(f'{info_prepath}_trial_data_dict.json')
        analysis.analyze_experiment(spec, trial_data_dict)
    else:
        logger.warn(f"skipping missing file {experiment_spec_path}")


def retro_analyze(predir):
    '''
    Method to analyze experiment/trial from files after it ran.
    @example

    yarn retro_analyze data/reinforce_cartpole_2018_01_22_211751/
    '''
    predir = predir.strip('/')  # sanitary
    os.environ['LOG_PREPATH'] = f'{predir}/log/retro_analyze'  # to prevent overwriting log file
    logger.info(f'Running retro-analysis on {predir}')
    retro_analyze_sessions(predir)
    retro_analyze_trials(predir)
    retro_analyze_experiment(predir)
    logger.info('Finished retro-analysis')
