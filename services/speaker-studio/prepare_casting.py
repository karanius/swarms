"""Extend the casting catalog without changing any existing role defaults or takes."""
import copy,csv,json
from pathlib import Path
import prepare_libraries as prep

path=prep.S/'scene-libraries.json'
libs=json.loads(path.read_text())
demographics={r['ActorID']:r for r in csv.DictReader((prep.S/'crema-d-audit/VideoDemographics.csv').open())}
for lib in libs.values():
    lib['voices']={r['speaker_id']:copy.deepcopy(r) for r in lib['roles'].values()}
    for voice in lib['voices'].values():
        voice['source_sex']='Unverified'
        voice['presentation_review']='Not yet judged by listening'

for actor in ('1059','1064'):
    extra=prep.crema([actor])['roles']['A']
    libs['crema']['voices'][extra['speaker_id']]=extra
for ident,voice in libs['crema']['voices'].items():
    actor=ident.split(':')[1]
    voice.update(source_sex=demographics[actor]['Sex'],metadata_source='CREMA-D VideoDemographics.csv',presentation_review='Not yet judged by listening')
libs['crema']['name']='CREMA-D · selectable cast'
libs['crema']['casting_note']='Two source-listed male and two source-listed female actors. Audition the voice: source sex is not a guarantee of perceived presentation or generated speaker similarity.'

extra=prep.ravdess(('03','04'))
for voice in extra['roles'].values():
    libs['ravdess']['voices'][voice['speaker_id']]=voice
for ident,voice in libs['ravdess']['voices'].items():
    voice.update(source_sex='Male' if int(ident.split(':')[1])%2 else 'Female',metadata_source='https://zenodo.org/records/1188976#file-naming-convention',presentation_review='Not yet judged by listening')
libs['ravdess']['name']='RAVDESS · selectable cast'
libs['ravdess']['casting_note']='Actors 01/03 are source-listed male; 02/04 female. Listen to confirm the presentation you want.'
libs['esd']['casting_note']='Only the two existing baseline profiles are enabled here. Their sex/presentation has not been verified in this catalog; no masculine/feminine label is inferred.'
libs['emns']['casting_note']='This remains a one-role swap: EMNS for Robin, fixed ESD for Casey. It cannot supply arbitrary two-actor casting.'
for role,voice in libs['emns']['roles'].items():
    libs['emns']['voices'][voice['speaker_id']]['allowed_roles']=[role]
path.write_text(json.dumps(libs,indent=2))
print('Casting pools saved: '+', '.join(k+' '+str(len(v['voices'])) for k,v in libs.items()))
