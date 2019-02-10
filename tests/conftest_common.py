import os
import copy
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

import fuckit

import d6tpipe

# ************************************
# config
# ************************************

cfg_profile = 'utest-dev'
cfg_usr = cfg_profile
cfg_usrpwd = cfg_profile+'pwd'
cfg_remote = cfg_profile+'-remote'
cfg_pipe = cfg_profile+'-pipe'
cfg_pipe_encrypt = cfg_profile+'-pipe-encrypt'
cfg_cfgfname = '~/d6tpipe/cfg-'+cfg_profile+'.json'
cfg_cfgfname2 = os.path.expanduser(cfg_cfgfname)
p_cfgfname = Path(cfg_cfgfname2)
# cfg_server = 'http://localhost:5000'
cfg_server = 'http://192.168.1.44:5000'
cfg_settings_remote = {
    "name": cfg_remote,
    "protocol": "s3",
    "location": "test-augvest-20180719",
    "readCredentials" : {
        "aws_access_key_id": os.getenv("KEYREAD"), "aws_secret_access_key": os.getenv("SECRETREAD")
    },
    "writeCredentials" : {
        "aws_access_key_id": os.getenv("KEYWRITE"), "aws_secret_access_key": os.getenv("SECRETWRITE")
    }
}

cfg_settings_pipe = {
    "name": cfg_pipe,
    "remote": cfg_remote,
    "settings": {
        "remotedir": "vendorX/",
        "include": "*.csv"
    }
}

cfgjson = d6tpipe.utils.loadjson('tests/.creds-test.json')
cfg_settings_remote_sftp = {
    "name": cfg_remote+'-sftp',
    "protocol": "sftp",
    "location": cfgjson['sftp']['host'],
    "readCredentials" : {
        "username": cfgjson['sftp']['username'], "password": cfgjson['sftp']['password']
    },
    "writeCredentials" : {
        "username": cfgjson['sftp']['username'], "password": cfgjson['sftp']['password']
    }
}

cfg_settings_pipe_sftp = copy.deepcopy(cfg_settings_pipe)
cfg_settings_pipe_sftp['remote']=cfg_settings_remote_sftp['name']
cfg_settings_pipe_sftp['name']=cfg_settings_remote_sftp['name']
cfg_settings_pipe_sftp['settings']['remotedir']='/home/d6tdev/d6tpipe-files/vendorX'

def copy_encrypt(dict_):
    dict_ = copy.deepcopy(dict_)
    dict_['name'] = dict_['name'] + '-encrypt'
    return dict_

cfg_settings_remote_encrypt = copy_encrypt(cfg_settings_remote)
cfg_settings_pipe_encrypt = copy_encrypt(cfg_settings_pipe)

cfg_profile2 = cfg_profile+'2'
cfg_usr2 = cfg_usr+'2'

cfg_filenames_chk = ['machinedata-2018-0{}.csv'.format(i) for i in range(1,5)]

# ************************************
# helpers
# ************************************
def getapi(local=False):
    if local:
        return d6tpipe.api.APILocal(profile=cfg_profile, filecfg=cfg_cfgfname)
    else:
        return d6tpipe.api.APIClient(profile=cfg_profile, filecfg=cfg_cfgfname)
def getapi2(local=False):
    if local:
        return d6tpipe.api.APILocal(profile=cfg_profile2, filecfg=cfg_cfgfname2)
    else:
        return d6tpipe.api.APIClient(profile=cfg_profile2, filecfg=cfg_cfgfname2)

def getconfig(profile):
    return d6tpipe.api.ConfigManager(profile=profile, filecfg=cfg_cfgfname)

def getpipe(api, chk_empty=True, mode='default', name=None):
    name = cfg_pipe if name is None else name
    pipe = d6tpipe.pipe.Pipe(api, name, mode=mode)
    if chk_empty:
        assert pipe.filenames() == []
        assert pipe.scan_local()[0] == []
    return pipe

@fuckit
def wipeapi(apifun, **kwargs):
    api = apifun(**kwargs)
    api.wipe_all(confirm=False)

@fuckit
def unregister(apifun, usr):
    api = apifun()
    api._unregister(usr)

def cleaner(apifun, usr):
    wipeapi(apifun)
    unregister(apifun, usr)

def pytest_generate_tests(metafunc):
    idlist = []
    argvalues = []
    for scenario in metafunc.cls.scenarios:
        idlist.append(scenario[0])
        items = scenario[1].items()
        argnames = [x[0] for x in items]
        argvalues.append(([x[1] for x in items]))
    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")