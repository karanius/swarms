import SignalsmithStretch from 'signalsmith-stretch';
import {AudioData} from '@opendaw/lib-dsp';

const $=id=>document.getElementById(id);
const summary=data=>{let power=0,peak=0;const n=data.numberOfFrames*data.numberOfChannels;for(const frame of data.frames)for(const value of frame){power+=value*value;peak=Math.max(peak,Math.abs(value))}return {rms:Math.sqrt(power/n),peak}};
const settings=()=>({pitch:Number($('pitch').value),formant:Number($('formant').value)});
export async function createVoiceShaper(context,engine,decoded,renderBase,evidence){
 const channels=2;
 const stretch=await SignalsmithStretch(context,{numberOfInputs:1,numberOfOutputs:1,channelCount:channels,outputChannelCount:[channels]});
 await stretch.configure({preset:'default'});await stretch.start();
 engine.disconnect();engine.connect(stretch,0);
 const wetGain=context.createGain(),dryGain=context.createGain(),mix=context.createGain(),dryDelay=context.createDelay(1);
 const latency=await stretch.latency();dryDelay.delayTime.value=latency;
 stretch.connect(wetGain).connect(mix);dryDelay.connect(dryGain).connect(mix);
 mix.connect(context.destination);let drySource=null,mode='edited',version=0,timer=null,matched={dry:1,wet:1},ready=false,rendering=false;
 evidence.pitchProcessor={name:'Signalsmith Stretch Web',version:'1.3.2',latencySeconds:latency};
 const original={sampleRate:decoded.sampleRate,numberOfFrames:decoded.length,numberOfChannels:decoded.numberOfChannels,frames:Array.from({length:decoded.numberOfChannels},(_,i)=>decoded.getChannelData(i))};
 const originalMetrics=summary(original);const renderCache=new Map();
 function gains(){const now=context.currentTime;wetGain.gain.cancelScheduledValues(now);dryGain.gain.cancelScheduledValues(now);wetGain.gain.setTargetAtTime(mode==='edited'?matched.wet:0,now,.012);dryGain.gain.setTargetAtTime(mode==='original'?matched.dry:0,now,.012);$('compareOriginal').setAttribute('aria-pressed',String(mode==='original'));$('compareEdited').setAttribute('aria-pressed',String(mode==='edited'));}
 function invalidate(){version++;ready=false;$('compareOriginal').disabled=true;$('compareEdited').disabled=true;$('matchStatus').textContent='Measuring comparison levels…';clearTimeout(timer);timer=setTimeout(measure,350)}
 function update(){const s=settings();stretch.schedule({semitones:s.pitch,formantSemitones:s.formant,formantCompensation:true,formantBaseHz:0});$('pitchValue').textContent=(s.pitch>0?'+':'')+s.pitch.toFixed(1)+' st';$('formantValue').textContent=(s.formant>0?'+':'')+s.formant.toFixed(1)+' st';evidence.shaping={...s,formantCompensation:true,playing:engine.isPlaying.getValue()};invalidate()}
 async function render(s=settings()){
  const key=JSON.stringify({shape:s,eq:['body','air','frequency','gain','q'].map(id=>$(id).value),bypass:$('bypass').checked});if(renderCache.has(key))return renderCache.get(key);const pending=renderFresh(s);renderCache.set(key,pending);if(renderCache.size>4)renderCache.delete(renderCache.keys().next().value);try{return await pending}catch(error){renderCache.delete(key);throw error}
 }
 async function renderFresh(s){
  const base=await renderBase();
  if(s.pitch===0&&s.formant===0)return base;
  const offline=new OfflineAudioContext(channels,base.numberOfFrames,base.sampleRate);
  const node=await SignalsmithStretch(offline,{numberOfInputs:0,numberOfOutputs:1,channelCount:channels,outputChannelCount:[channels]});
  await node.configure({preset:'default'});
  await node.addBuffers(Array.from({length:channels},(_,i)=>new Float32Array(base.frames[Math.min(i,base.numberOfChannels-1)])));
  node.connect(offline.destination);
  await node.schedule({output:0,input:0,active:true,rate:1,semitones:s.pitch,formantSemitones:s.formant,formantCompensation:true,formantBaseHz:0});
  const result=await offline.startRendering();node.disconnect();node.port.close();
  const data=AudioData.create(result.sampleRate,result.length,result.numberOfChannels);data.frames.forEach((f,i)=>f.set(result.getChannelData(i)));return data;
 }
 async function measure(){if(rendering)return;const ticket=version;rendering=true;try{const result=await render(settings());if(ticket!==version)return;const metrics=summary(result);if(metrics.rms<1e-7||originalMetrics.rms<1e-7)throw Error('Audio is too quiet to match');
  // Attenuate the louder recording; never boost either one for comparison.
  const target=Math.min(metrics.rms,originalMetrics.rms);let wet=target/metrics.rms,dry=target/originalMetrics.rms;const ceiling=.891250938;const peak=Math.max(metrics.peak*wet,originalMetrics.peak*dry);const safety=peak>ceiling?ceiling/peak:1;matched={wet:wet*safety,dry:dry*safety};ready=true;$('compareOriginal').disabled=false;$('compareEdited').disabled=false;
  evidence.comparison={method:'Whole-recording RMS; attenuation only; shared -1 dBFS peak ceiling',original:originalMetrics,edited:metrics,gains:matched,version:ticket};$('matchStatus').textContent='RMS matched · comparison only';gains();
 }catch(error){ready=false;matched={wet:1,dry:1};gains();$('matchStatus').textContent='Level match unavailable: '+error.message}finally{rendering=false;if(ticket!==version)timer=setTimeout(measure,150)}}
 $('pitch').oninput=update;$('formant').oninput=update;
 $('resetShaping').onclick=()=>{$('pitch').value=0;$('formant').value=0;update()};
 $('compareOriginal').onclick=()=>{mode='original';gains()};$('compareEdited').onclick=()=>{mode='edited';gains()};
 for(const id of ['pitch','formant','resetShaping','compareOriginal','compareEdited'])$(id).disabled=false;
 gains();update();
 return {mix,stretch,render,invalidate,get ready(){return ready},get mode(){return mode},get matched(){return matched},
  start(){if(drySource){try{drySource.stop()}catch{}}drySource=context.createBufferSource();drySource.buffer=decoded;drySource.loop=$('repeat').checked;drySource.connect(dryDelay);drySource.start()},
  stop(){if(drySource){try{drySource.stop()}catch{}drySource.disconnect();drySource=null}},
  repeat(){if(drySource)drySource.loop=$('repeat').checked},
  close(){clearTimeout(timer);version++;stretch.disconnect();stretch.port.close();mix.disconnect()}
 };
}
