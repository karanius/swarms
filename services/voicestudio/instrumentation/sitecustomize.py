"""Observe only the selected VoxCPM sidecar, without changing upstream code."""
import sys, os

if os.environ.get('OMNIVOICE_STUDY_VOXCPM_TRACE') == '1' and '/engines/voxcpm2/' in sys.executable:
    import atexit, json, os, time, resource
    from pathlib import Path
    import torch

    target = Path(os.environ['OMNIVOICE_DATA_DIR']).parent/'voxcpm-device-evidence.json'
    evidence = dict(pid=os.getpid(), started_unix=time.time(), forward_calls=0,
                    observed_parameter_devices=[], observed_tensor_devices=[])
    def save():
        evidence['observed_unix'] = time.time()
        evidence['process_maxrss_bytes'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if torch.backends.mps.is_available():
            evidence['mps_allocated_bytes'] = torch.mps.current_allocated_memory()
            evidence['mps_driver_bytes'] = torch.mps.driver_allocated_memory()
        partial=target.with_suffix('.tmp')
        partial.write_text(json.dumps(evidence,indent=2)); partial.replace(target)
    def observe(module, args):
        evidence['forward_calls'] += 1
        parameters={str(p.device) for p in module.parameters(recurse=False)}
        tensors={str(x.device) for x in args if isinstance(x,torch.Tensor)}
        old=(evidence['observed_parameter_devices'],evidence['observed_tensor_devices'])
        evidence['observed_parameter_devices']=sorted(set(old[0])|parameters)
        evidence['observed_tensor_devices']=sorted(set(old[1])|tensors)
        if evidence['forward_calls']==1 or evidence['forward_calls']%1000==0 or old!=(evidence['observed_parameter_devices'],evidence['observed_tensor_devices']):
            save()
    torch.nn.modules.module.register_module_forward_pre_hook(observe)
    atexit.register(save)
    save()
