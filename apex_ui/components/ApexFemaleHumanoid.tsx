"use client";

import React, { Component, useEffect, useMemo, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { useJarvisAudioLevel } from "./JarvisBridge";
import type { OrbState } from "./ApexHeroOrb";

// Original, analytic 3D sculpture. No portrait texture, external assets or image plane.
const gaussian = (x: number, y: number, sx: number, sy: number) => Math.exp(-(x*x/(sx*sx)+y*y/(sy*sy)));
function sculpture() {
  const positions: number[] = [], colors: number[] = [], regions: number[] = [];
  let seed = 721;
  const random = () => { seed = (Math.imul(seed,1664525)+1013904223)>>>0; return seed/4294967296; };
  const add = (x: number,y: number,z: number,kind: number,brightness=1) => {
    positions.push(x,y,z);
    const base = kind===2 ? [.32,.32,.85] : kind===4 ? [.68,.92,1] : kind===5 ? [.58,.40,.85] : [.20,.72,.86];
    const light = brightness*(.55+random()*.45);
    colors.push(...base.map(c=>c*light)); regions.push(kind);
  };
  // A sculpted oval cranium, cheekbones, brow, projecting nose, cupid's bow and chin.
  for(let i=0;i<16000;i++) {
    const t=random()*2-1, phi=random()*Math.PI*2;
    const s=Math.sqrt(1-t*t), y=.64+1.05*t;
    const taper=t<-.25 ? 1-(Math.abs(t)-.25)*.38 : 1;
    const x=.69*s*Math.sin(phi)*taper;
    let z=.59*s*Math.cos(phi);
    if(z>0) {
      const front=Math.pow(Math.max(0,Math.cos(phi)),6);
      z+=front*(.075*gaussian(Math.abs(x)-.32,y-.55,.20,.19)
        +.055*gaussian(Math.abs(x)-.27,y-.96,.21,.09)
        +.20*gaussian(x,y-.57,.08,.29)+.15*gaussian(x,y-.39,.12,.10)
        +.065*gaussian(x,y-.09,.23,.07));
      // Empty eye sockets are filled by dedicated eyelid/iris geometry below.
      if(Math.abs(Math.abs(x)-.285)<.145 && Math.abs(y-.80)<.060 && z>.42) continue;
    }
    add(x,y+.40,z,0,z>0 ? 1 : .4);
  }
  // Eyelids, iris, pupils and brows: real curves at the face's depth, not a decal.
  for(const side of [-1,1]) {
    for(let i=0;i<650;i++) {
      const a=random()*Math.PI*2, r=Math.sqrt(random());
      const x=side*.285+Math.cos(a)*.105*r, y=.80+Math.sin(a)*.037*r;
      const iris=Math.abs(x-side*.285)<.041 && Math.abs(y-.80)<.043;
      if(iris && Math.hypot((x-side*.285)/.035,(y-.80)/.04)<.45) continue;
      add(x,y+.4,.564+Math.sqrt(Math.max(0,1-r*r))*.032,4,iris?.65:.14);
    }
    for(let i=0;i<230;i++) {
      const a=i/229*Math.PI*2;
      add(side*.285+Math.cos(a)*.112,1.20+Math.sin(a)*.042,.574,4,.38);
      const u=i/229;
      add(side*(.14+u*.30),1.34+.05*Math.sin(u*Math.PI),.555,2,.7);
    }
  }
  // Defined lip surfaces, kept subtle: audio energy opens the lower lip slightly.
  for(let i=0;i<1000;i++) {
    const x=(random()*2-1)*.215, w=Math.sqrt(Math.max(0,1-(x/.215)**2));
    const upper=random()>.48;
    const y=.09+(upper ? .020+.028*Math.cos(x/.215*Math.PI*2) : -.045)*w;
    add(x,y+.4+(random()-.5)*.016,.575+.038*w,5,.85);
  }
  // Layered hair follows the skull in 3D, with long side/back strands.
  for(let strand=0;strand<280;strand++) {
    const phi=(strand/280)*Math.PI*2, back=Math.cos(phi)<.1;
    for(let j=0;j<65;j++) {
      const u=j/64, a=.14+u*(back?2.30:1.60);
      let x=.74*Math.sin(a)*Math.sin(phi), y=.68+1.12*Math.cos(a), z=.65*Math.sin(a)*Math.cos(phi);
      if(!back && Math.abs(x)<.47 && y<1.02) continue;
      if(u>.57) { const f=(u-.57)/.43; y-=f*(back?.8:1.1); x+=Math.sign(x)*.10*f; }
      x+=Math.sin(u*10+phi*3)*.018;
      add(x,y+.40,z,2,.65+random()*.5);
    }
  }
  // Neck and shoulder/clavicle volume are separate from the head rig.
  for(let i=0;i<2300;i++) {
    const a=random()*Math.PI*2, u=random();
    add(.215*Math.cos(a)*(1+.28*u),-u*.97,.23*Math.sin(a)-.055,3,.65);
  }
  for(let i=0;i<10500;i++) {
    const a=random()*Math.PI*2, t=random(), width=1.54*Math.sqrt(1-t*.40);
    const x=Math.cos(a)*width, y=-1.02-t*1.10+.21*(1-Math.abs(Math.cos(a))), z=Math.sin(a)*(.40+.11*t)-.10;
    add(x,y,z,3,(1-t*.85)*.78);
  }
  return {position:new Float32Array(positions),color:new Float32Array(colors),region:new Float32Array(regions)};
}

function faceVolume() {
  const g = new THREE.SphereGeometry(1, 96, 80);
  const p = g.getAttribute("position");
  for (let i=0;i<p.count;i++) {
    const ux=p.getX(i),t=p.getY(i),uz=p.getZ(i);
    const taper=t<-.25?1-(Math.abs(t)-.25)*.38:1;
    const x=.69*ux*taper, y=.64+1.05*t;
    let z=.59*uz;
    if(uz>0){const front=Math.pow(uz/Math.max(.001,Math.sqrt(1-t*t)),6);
      z+=front*(.075*gaussian(Math.abs(x)-.32,y-.55,.20,.19)
        +.055*gaussian(Math.abs(x)-.27,y-.96,.21,.09)
        -.035*gaussian(Math.abs(x)-.28,y-.80,.12,.075)
        +.20*gaussian(x,y-.57,.08,.29)+.15*gaussian(x,y-.39,.12,.10)
        +.065*gaussian(x,y-.09,.23,.07));}
    p.setXYZ(i,x,y+.4,z);
  }
  g.computeVertexNormals();return g;
}

const vertex = `
attribute vec3 color; attribute float region;
uniform float time, energy, assembly, still;
varying vec3 tint; varying float alpha;
void main(){
 vec3 p=position;
 float birth=fract(sin(dot(position,vec3(12.9898,78.233,37.719)))*43758.5453);
 float form=smoothstep(birth*.55,birth*.55+.45,assembly);
 p.xz*=1.+(1.-form)*1.8; p.y-=(1.-form)*2.;
 if(region>1.5&&region<2.5) p.x+=sin(time*.7+p.y*3.+p.z*2.)*.008*(1.-still);
 if(region>2.5&&region<3.5) p.z+=sin(time*1.3)*.012*(1.-still);
 if(region>4.5) p.y-=energy*.06*(1.-smoothstep(.46,.52,p.y));
 float phase=mod(time+2.8,6.5);
 float blink=smoothstep(0.,.07,phase)*(1.-smoothstep(.09,.18,phase))*(1.-still);
 if(region>3.5&&region<4.5) p.y=mix(p.y,1.20,blink);
 vec4 mv=modelViewMatrix*vec4(p,1.);
 gl_Position=projectionMatrix*mv;
 gl_PointSize=clamp((region>3.5?1.9:1.35)*8./-mv.z, .8, 3.4);
 tint=color*(1.+energy*.30); alpha=form;
}`;
const fragment = `precision mediump float; varying vec3 tint; varying float alpha;
void main(){float r=length(gl_PointCoord-.5)*2.;if(r>1.) discard;
float glow=exp(-r*r*3.5);gl_FragColor=vec4(tint,glow*alpha*.82);}`;

function Figure({state,reduced}:{state:OrbState;reduced:boolean}) {
  const geometry=useMemo(()=>{const d=sculpture(),g=new THREE.BufferGeometry();
    g.setAttribute("position",new THREE.BufferAttribute(d.position,3));
    g.setAttribute("color",new THREE.BufferAttribute(d.color,3));
    g.setAttribute("region",new THREE.BufferAttribute(d.region,1));return g;},[]);
  const surface=useMemo(faceVolume,[]);
  useEffect(()=>()=>surface.dispose(),[surface]);
  const material=useMemo(()=>new THREE.ShaderMaterial({vertexShader:vertex,fragmentShader:fragment,
    uniforms:{time:{value:0},energy:{value:0},assembly:{value:reduced?1:0},still:{value:reduced?1:0}},
    transparent:true,depthWrite:false,blending:THREE.AdditiveBlending}),[reduced]);
  const group=useRef<THREE.Group>(null), gaze=useRef({x:0,y:0}), elapsed=useRef(0);
  const audio=useJarvisAudioLevel();
  useEffect(()=>{const move=(e:PointerEvent)=>{gaze.current={x:THREE.MathUtils.clamp((e.clientX/innerWidth-.5)*2,-1,1),y:THREE.MathUtils.clamp((e.clientY/innerHeight-.43)*2,-1,1)};};
    const reset=()=>{gaze.current={x:0,y:0};};
    window.addEventListener("pointermove",move);window.addEventListener("blur",reset);
    return()=>{window.removeEventListener("pointermove",move);window.removeEventListener("blur",reset);};},[]);
  useEffect(()=>()=>geometry.dispose(),[geometry]);
  useEffect(()=>()=>material.dispose(),[material]);
  useFrame((_,delta)=>{
    const dt=Math.min(delta,.05);elapsed.current+=dt;
    material.uniforms.time.value=elapsed.current;
    material.uniforms.assembly.value=reduced?1:Math.min(1,elapsed.current/2.1);
    material.uniforms.energy.value=THREE.MathUtils.damp(material.uniforms.energy.value,state==="speaking"?audio:0,12,dt);
    if(group.current){
      group.current.rotation.y=THREE.MathUtils.damp(group.current.rotation.y,reduced?0:gaze.current.x*.26,5,dt);
      group.current.rotation.x=THREE.MathUtils.damp(group.current.rotation.x,reduced?0:gaze.current.y*.14,5,dt);
      group.current.position.y=reduced?0:Math.sin(elapsed.current*.8)*.012;
    }
  });
  return <group ref={group}>
    <mesh geometry={surface} renderOrder={0}>
      <meshPhongMaterial color="#18677a" specular="#85d9e8" shininess={32} transparent opacity={.48} depthWrite={false}/>
    </mesh>
    <points geometry={geometry} material={material} frustumCulled={false} renderOrder={1}/>
  </group>;
}

function Fallback(){return <svg viewBox="0 0 400 500" width="100%" height="100%" role="img" aria-label="Female holographic silhouette — reduced graphics">
  <defs><linearGradient id="female-line" x2="0" y2="1"><stop stopColor="#80eaff"/><stop offset="1" stopColor="#7b66c8" stopOpacity=".2"/></linearGradient></defs>
  <g fill="none" stroke="url(#female-line)" strokeWidth="1.5">
    <path d="M130 302Q100 190 129 110Q148 56 200 59Q255 56 275 118Q301 210 270 302M140 142Q133 210 158 248Q184 281 200 281Q223 276 245 244Q268 202 259 143Q230 127 213 92Q180 134 140 142ZM174 275L170 320Q108 329 67 367L44 449M228 275L233 320Q295 328 335 371L356 449M153 179Q167 168 184 179M216 179Q234 168 248 179M198 183L190 218L207 221M180 244Q202 251 220 242M129 110Q100 277 118 350M275 118Q308 261 284 352"/>
    <ellipse cx="170" cy="181" rx="5" ry="4"/><ellipse cx="232" cy="181" rx="5" ry="4"/>
  </g></svg>;}
class GraphicsBoundary extends Component<{children:React.ReactNode},{failed:boolean}>{
  state={failed:false};static getDerivedStateFromError(){return {failed:true};}
  render(){return this.state.failed?<Fallback/>:this.props.children;}
}
export default function ApexFemaleHumanoid({state="idle"}:{state?:OrbState}) {
  const [reduced,setReduced]=useState(false),[supported,setSupported]=useState<boolean|null>(null);
  useEffect(()=>{const mq=matchMedia("(prefers-reduced-motion: reduce)");const apply=()=>setReduced(mq.matches);apply();mq.addEventListener("change",apply);
    setSupported(typeof window.WebGL2RenderingContext !== "undefined");
    return()=>mq.removeEventListener("change",apply);},[]);
  return <div role="img" aria-label={`Female particle humanoid, ${state}`} style={{width:"100%",height:"100%"}}>
    {supported ? <GraphicsBoundary><Canvas camera={{position:[0,.12,6.4],fov:40}} dpr={[1,1.5]} gl={{alpha:true,antialias:false,powerPreference:"low-power"}} frameloop={reduced?"demand":"always"}>
      <ambientLight intensity={.55}/>
      <directionalLight position={[-3,4,5]} intensity={1.5} color="#a4e9ff"/>
      <directionalLight position={[3,1,0]} intensity={.8} color="#a793e9"/>
      <Figure state={state} reduced={reduced}/>
    </Canvas></GraphicsBoundary> : <Fallback/>}
  </div>;
}
