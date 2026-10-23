"use strict";(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[664],{1004:(e,t,r)=>{r.d(t,{AH:()=>j,Mj:()=>w,SP:()=>ex,To:()=>eD,Vu:()=>eN,Xe:()=>eO,bv:()=>V,hH:()=>ec,i:()=>ea,oF:()=>a,s0:()=>p});var i=r(3264),s=(()=>{let e=new Float32Array([-1,-1,0,3,-1,0,-1,3,0]),t=new Float32Array([0,0,2,0,0,2]),r=new i.LoY;return r.setAttribute("position",new i.THS(e,3)),r.setAttribute("uv",new i.THS(t,2)),r})(),a=class e{static get fullscreenGeometry(){return s}constructor(e="Pass",t=new i.Z58,r=new i.qUd){this.name=e,this.renderer=null,this.scene=t,this.camera=r,this.screen=null,this.rtt=!0,this.needsSwap=!0,this.needsDepthBlit=!1,this.needsDepthTexture=!1,this.enabled=!0}get renderToScreen(){return!this.rtt}set renderToScreen(e){if(this.rtt===e){let t=this.fullscreenMaterial;null!==t&&(t.needsUpdate=!0),this.rtt=!e}}set mainScene(e){}set mainCamera(e){}setRenderer(e){this.renderer=e}isEnabled(){return this.enabled}setEnabled(e){this.enabled=e}get fullscreenMaterial(){return null!==this.screen?this.screen.material:null}set fullscreenMaterial(t){let r=this.screen;null!==r?r.material=t:((r=new i.eaF(e.fullscreenGeometry,t)).frustumCulled=!1,null===this.scene&&(this.scene=new i.Z58),this.scene.add(r),this.screen=r)}getFullscreenMaterial(){return this.fullscreenMaterial}setFullscreenMaterial(e){this.fullscreenMaterial=e}getDepthTexture(){return null}setDepthTexture(e,t=i.Rkk){}render(e,t,r,i,s){throw Error("Render method not implemented!")}setSize(e,t){}initialize(e,t,r){}dispose(){for(let t of Object.keys(this)){let r=this[t];(r instanceof i.nWS||r instanceof i.imn||r instanceof i.gPd||r instanceof e)&&this[t].dispose()}null!==this.fullscreenMaterial&&this.fullscreenMaterial.dispose()}},n=class extends a{constructor(){super("ClearMaskPass",null,null),this.needsSwap=!1}render(e,t,r,i,s){let a=e.state.buffers.stencil;a.setLocked(!1),a.setTest(!1)}},o=`#ifdef COLOR_WRITE
#include <common>
#include <dithering_pars_fragment>
#ifdef FRAMEBUFFER_PRECISION_HIGH
uniform mediump sampler2D inputBuffer;
#else
uniform lowp sampler2D inputBuffer;
#endif
#endif
#ifdef DEPTH_WRITE
#include <packing>
#ifdef GL_FRAGMENT_PRECISION_HIGH
uniform highp sampler2D depthBuffer;
#else
uniform mediump sampler2D depthBuffer;
#endif
float readDepth(const in vec2 uv){
#if DEPTH_PACKING == 3201
return unpackRGBAToDepth(texture2D(depthBuffer,uv));
#else
return texture2D(depthBuffer,uv).r;
#endif
}
#endif
#ifdef USE_WEIGHTS
uniform vec4 channelWeights;
#endif
uniform float opacity;varying vec2 vUv;void main(){
#ifdef COLOR_WRITE
vec4 texel=texture2D(inputBuffer,vUv);
#ifdef USE_WEIGHTS
texel*=channelWeights;
#endif
gl_FragColor=opacity*texel;
#ifdef COLOR_SPACE_CONVERSION
#include <colorspace_fragment>
#endif
#include <dithering_fragment>
#else
gl_FragColor=vec4(0.0);
#endif
#ifdef DEPTH_WRITE
gl_FragDepth=readDepth(vUv);
#endif
}`,l="varying vec2 vUv;void main(){vUv=position.xy*0.5+0.5;gl_Position=vec4(position.xy,1.0,1.0);}",c=class extends i.BKk{constructor(){super({name:"CopyMaterial",defines:{COLOR_SPACE_CONVERSION:"1",DEPTH_PACKING:"0",COLOR_WRITE:"1"},uniforms:{inputBuffer:new i.nc$(null),depthBuffer:new i.nc$(null),channelWeights:new i.nc$(null),opacity:new i.nc$(1)},blending:i.XIg,toneMapped:!1,depthWrite:!1,depthTest:!1,fragmentShader:o,vertexShader:l}),this.depthFunc=i.lGu}get inputBuffer(){return this.uniforms.inputBuffer.value}set inputBuffer(e){let t=null!==e;this.colorWrite!==t&&(t?this.defines.COLOR_WRITE=!0:delete this.defines.COLOR_WRITE,this.colorWrite=t,this.needsUpdate=!0),this.uniforms.inputBuffer.value=e}get depthBuffer(){return this.uniforms.depthBuffer.value}set depthBuffer(e){let t=null!==e;this.depthWrite!==t&&(t?this.defines.DEPTH_WRITE=!0:delete this.defines.DEPTH_WRITE,this.depthTest=t,this.depthWrite=t,this.needsUpdate=!0),this.uniforms.depthBuffer.value=e}set depthPacking(e){this.defines.DEPTH_PACKING=e.toFixed(0),this.needsUpdate=!0}get colorSpaceConversion(){return void 0!==this.defines.COLOR_SPACE_CONVERSION}set colorSpaceConversion(e){this.colorSpaceConversion!==e&&(e?this.defines.COLOR_SPACE_CONVERSION=!0:delete this.defines.COLOR_SPACE_CONVERSION,this.needsUpdate=!0)}get channelWeights(){return this.uniforms.channelWeights.value}set channelWeights(e){null!==e?(this.defines.USE_WEIGHTS="1",this.uniforms.channelWeights.value=e):delete this.defines.USE_WEIGHTS,this.needsUpdate=!0}setInputBuffer(e){this.uniforms.inputBuffer.value=e}getOpacity(e){return this.uniforms.opacity.value}setOpacity(e){this.uniforms.opacity.value=e}},u=class extends a{constructor(e,t=!0){super("CopyPass"),this.fullscreenMaterial=new c,this.needsSwap=!1,this.renderTarget=e,void 0===e&&(this.renderTarget=new i.nWS(1,1,{minFilter:i.k6q,magFilter:i.k6q,stencilBuffer:!1,depthBuffer:!1}),this.renderTarget.texture.name="CopyPass.Target"),this.autoResize=t}get resize(){return this.autoResize}set resize(e){this.autoResize=e}get texture(){return this.renderTarget.texture}getTexture(){return this.renderTarget.texture}setAutoResizeEnabled(e){this.autoResize=e}render(e,t,r,i,s){this.fullscreenMaterial.inputBuffer=t.texture,e.setRenderTarget(this.renderToScreen?null:this.renderTarget),e.render(this.scene,this.camera)}setSize(e,t){this.autoResize&&this.renderTarget.setSize(e,t)}initialize(e,t,r){void 0!==r&&(this.renderTarget.texture.type=r,r!==i.OUM?this.fullscreenMaterial.defines.FRAMEBUFFER_PRECISION_HIGH="1":null!==e&&e.outputColorSpace===i.er$&&(this.renderTarget.texture.colorSpace=i.er$))}},f=new i.Q1f,d=class extends a{constructor(e=!0,t=!0,r=!1){super("ClearPass",null,null),this.needsSwap=!1,this.color=e,this.depth=t,this.stencil=r,this.overrideClearColor=null,this.overrideClearAlpha=-1}setClearFlags(e,t,r){this.color=e,this.depth=t,this.stencil=r}getOverrideClearColor(){return this.overrideClearColor}setOverrideClearColor(e){this.overrideClearColor=e}getOverrideClearAlpha(){return this.overrideClearAlpha}setOverrideClearAlpha(e){this.overrideClearAlpha=e}render(e,t,r,i,s){let a=this.overrideClearColor,n=this.overrideClearAlpha,o=e.getClearAlpha(),l=null!==a,c=n>=0;l?(e.getClearColor(f),e.setClearColor(a,c?n:o)):c&&e.setClearAlpha(n),e.setRenderTarget(this.renderToScreen?null:t),e.clear(this.color,this.depth,this.stencil),l?e.setClearColor(f,o):c&&e.setClearAlpha(o)}},v=class extends a{constructor(e,t){super("MaskPass",e,t),this.needsSwap=!1,this.clearPass=new d(!1,!1,!0),this.inverse=!1}set mainScene(e){this.scene=e}set mainCamera(e){this.camera=e}get inverted(){return this.inverse}set inverted(e){this.inverse=e}get clear(){return this.clearPass.enabled}set clear(e){this.clearPass.enabled=e}getClearPass(){return this.clearPass}isInverted(){return this.inverted}setInverted(e){this.inverted=e}render(e,t,r,i,s){let a=e.getContext(),n=e.state.buffers,o=this.scene,l=this.camera,c=this.clearPass,u=+!this.inverted;n.color.setMask(!1),n.depth.setMask(!1),n.color.setLocked(!0),n.depth.setLocked(!0),n.stencil.setTest(!0),n.stencil.setOp(a.REPLACE,a.REPLACE,a.REPLACE),n.stencil.setFunc(a.ALWAYS,u,0xffffffff),n.stencil.setClear(1-u),n.stencil.setLocked(!0),this.clearPass.enabled&&(this.renderToScreen?c.render(e,null):(c.render(e,t),c.render(e,r))),this.renderToScreen?e.setRenderTarget(null):(e.setRenderTarget(t),e.render(o,l),e.setRenderTarget(r)),e.render(o,l),n.color.setLocked(!1),n.depth.setLocked(!1),n.stencil.setLocked(!1),n.stencil.setFunc(a.EQUAL,1,0xffffffff),n.stencil.setOp(a.KEEP,a.KEEP,a.KEEP),n.stencil.setLocked(!0)}},h=class{constructor(){this.startTime=performance.now(),this.previousTime=0,this.currentTime=0,this._delta=0,this._elapsed=0,this._fixedDelta=1e3/60,this.timescale=1,this.useFixedDelta=!1,this._autoReset=!1}get autoReset(){return this._autoReset}set autoReset(e){"undefined"!=typeof document&&void 0!==document.hidden&&(e?document.addEventListener("visibilitychange",this):document.removeEventListener("visibilitychange",this),this._autoReset=e)}get delta(){return .001*this._delta}get fixedDelta(){return .001*this._fixedDelta}set fixedDelta(e){this._fixedDelta=1e3*e}get elapsed(){return .001*this._elapsed}update(e){this.useFixedDelta?this._delta=this.fixedDelta:(this.previousTime=this.currentTime,this.currentTime=(void 0!==e?e:performance.now())-this.startTime,this._delta=this.currentTime-this.previousTime),this._delta*=this.timescale,this._elapsed+=this._delta}reset(){this._delta=0,this._elapsed=0,this.currentTime=performance.now()-this.startTime}getDelta(){return this.delta}getElapsed(){return this.elapsed}handleEvent(e){document.hidden||(this.currentTime=performance.now()-this.startTime)}dispose(){this.autoReset=!1}},p=class{constructor(e=null,{depthBuffer:t=!0,stencilBuffer:r=!1,multisampling:i=0,frameBufferType:s}={}){this.renderer=null,this.inputBuffer=this.createBuffer(t,r,s,i),this.outputBuffer=this.inputBuffer.clone(),this.copyPass=new u,this.depthRenderTarget=null,this.passes=[],this.timer=new h,this.autoRenderToScreen=!0,this.setRenderer(e)}get stableDepthTexture(){return null===this.depthRenderTarget?null:this.depthRenderTarget.depthTexture}get multisampling(){return this.inputBuffer.samples}set multisampling(e){this.multisampling!==e&&(this.inputBuffer.samples=e,this.outputBuffer.samples=e,this.inputBuffer.dispose(),this.outputBuffer.dispose())}getTimer(){return this.timer}getRenderer(){return this.renderer}setRenderer(e){if(this.renderer=e,null!==e){let t=e.getSize(new i.I9Y),r=e.getContext().getContextAttributes().alpha,s=this.inputBuffer.texture.type;for(let a of(s===i.OUM&&e.outputColorSpace===i.er$&&(this.inputBuffer.texture.colorSpace=i.er$,this.outputBuffer.texture.colorSpace=i.er$,this.inputBuffer.dispose(),this.outputBuffer.dispose()),e.autoClear=!1,this.setSize(t.width,t.height),this.passes))a.initialize(e,r,s)}}replaceRenderer(e,t=!0){let r=this.renderer,i=r.domElement.parentNode;return this.setRenderer(e),t&&null!==i&&(i.removeChild(r.domElement),i.appendChild(e.domElement)),r}createDepthTexture(){let e=new i.VCu;e.name="EffectComposer.InputDepth",this.inputBuffer.stencilBuffer?(e.format=i.dcC,e.type=i.V3x):e.type=i.RQf;let t=e.clone();t.name="EffectComposer.OutputDepth";let r=e.clone();r.name="EffectComposer.StableDepth",this.inputBuffer.depthTexture=e,this.outputBuffer.depthTexture=t,this.inputBuffer.dispose(),this.outputBuffer.dispose();let{width:s,height:a}=this.inputBuffer;this.depthRenderTarget=new i.nWS(s,a,{depthBuffer:!0,stencilBuffer:this.inputBuffer.stencilBuffer,depthTexture:r})}blitDepthBuffer(e){let t=this.renderer,r=this.depthRenderTarget,i=t.properties,s=t.getContext();t.setRenderTarget(r);let a=i.get(e).__webglFramebuffer,n=i.get(r).__webglFramebuffer,o=e.stencilBuffer?s.DEPTH_BUFFER_BIT|s.STENCIL_BUFFER_BIT:s.DEPTH_BUFFER_BIT;s.bindFramebuffer(s.READ_FRAMEBUFFER,a),s.bindFramebuffer(s.DRAW_FRAMEBUFFER,n),s.blitFramebuffer(0,0,e.width,e.height,0,0,r.width,r.height,o,s.NEAREST),s.bindFramebuffer(s.READ_FRAMEBUFFER,null),s.bindFramebuffer(s.DRAW_FRAMEBUFFER,null),t.setRenderTarget(null)}deleteDepthTexture(){let e=this.stableDepthTexture;for(let t of this.passes)t.getDepthTexture()===e&&t.setDepthTexture(null);null!==this.depthRenderTarget&&(this.depthRenderTarget.dispose(),this.depthRenderTarget=null),null!==this.inputBuffer.depthTexture&&(this.inputBuffer.depthTexture.dispose(),this.inputBuffer.depthTexture=null),null!==this.outputBuffer.depthTexture&&(this.outputBuffer.depthTexture.dispose(),this.outputBuffer.depthTexture=null)}createBuffer(e,t,r,s){let a=this.renderer,n=null===a?new i.I9Y:a.getDrawingBufferSize(new i.I9Y),o=new i.nWS(n.width,n.height,{minFilter:i.k6q,magFilter:i.k6q,samples:s,stencilBuffer:t,depthBuffer:e,type:r});return r===i.OUM&&null!==a&&a.outputColorSpace===i.er$&&(o.texture.colorSpace=i.er$),o.texture.name="EffectComposer.Buffer",o.texture.generateMipmaps=!1,o}setMainScene(e){for(let t of this.passes)t.mainScene=e}setMainCamera(e){for(let t of this.passes)t.mainCamera=e}addPass(e,t){let r=this.passes,s=this.renderer,a=s.getDrawingBufferSize(new i.I9Y),n=s.getContext().getContextAttributes().alpha,o=this.inputBuffer.texture.type;if(e.renderer=s,e.setSize(a.width,a.height),e.initialize(s,n,o),this.autoRenderToScreen&&(r.length>0&&(r[r.length-1].renderToScreen=!1),e.renderToScreen&&(this.autoRenderToScreen=!1)),void 0!==t?r.splice(t,0,e):r.push(e),this.autoRenderToScreen&&(r[r.length-1].renderToScreen=!0),e.needsDepthTexture||null!==this.depthRenderTarget)if(null===this.depthRenderTarget)for(let e of(this.createDepthTexture(),r))e.setDepthTexture(this.stableDepthTexture);else e.setDepthTexture(this.stableDepthTexture)}removePass(e){let t=this.passes,r=t.indexOf(e);if(-1!==r&&t.splice(r,1).length>0){let i=this.stableDepthTexture;null!==i&&(t.reduce((e,t)=>e||t.needsDepthTexture,!1)||(e.getDepthTexture()===i&&e.setDepthTexture(null),this.deleteDepthTexture())),this.autoRenderToScreen&&r===t.length&&(e.renderToScreen=!1,t.length>0&&(t[t.length-1].renderToScreen=!0))}}removeAllPasses(){let e=this.passes;this.deleteDepthTexture(),e.length>0&&(this.autoRenderToScreen&&(e[e.length-1].renderToScreen=!1),this.passes=[])}render(e){let t,r=this.renderer,i=this.copyPass,s=this.inputBuffer,a=this.outputBuffer,o=!1;for(let l of(void 0===e&&(this.timer.update(),e=this.timer.getDelta()),this.passes))if(l.enabled){if(l.render(r,s,a,e,o),l.needsDepthBlit&&null!==this.depthRenderTarget&&this.blitDepthBuffer(s),l.needsSwap){if(o){i.renderToScreen=l.renderToScreen;let t=r.getContext(),n=r.state.buffers.stencil;n.setFunc(t.NOTEQUAL,1,0xffffffff),i.render(r,s,a,e,o),n.setFunc(t.EQUAL,1,0xffffffff)}t=s,s=a,a=t}l instanceof v?o=!0:l instanceof n&&(o=!1)}}setSize(e,t,r){let s=this.renderer,a=s.getSize(new i.I9Y);(void 0===e||void 0===t)&&(e=a.width,t=a.height),(a.width!==e||a.height!==t)&&s.setSize(e,t,r);let n=s.getDrawingBufferSize(new i.I9Y);for(let e of(this.inputBuffer.setSize(n.width,n.height),this.outputBuffer.setSize(n.width,n.height),null!==this.depthRenderTarget&&this.depthRenderTarget.setSize(n.width,n.height),this.passes))e.setSize(n.width,n.height)}reset(){this.dispose(),this.autoRenderToScreen=!0}dispose(){for(let e of this.passes)e.dispose();this.deleteDepthTexture(),this.inputBuffer.dispose(),this.outputBuffer.dispose(),this.copyPass.dispose(),this.timer.dispose(),this.passes=[],a.fullscreenGeometry.dispose()}},m={NONE:0,DEPTH:1,CONVOLUTION:2},g={FRAGMENT_HEAD:"FRAGMENT_HEAD",FRAGMENT_MAIN_UV:"FRAGMENT_MAIN_UV",FRAGMENT_MAIN_IMAGE:"FRAGMENT_MAIN_IMAGE",VERTEX_HEAD:"VERTEX_HEAD",VERTEX_MAIN_SUPPORT:"VERTEX_MAIN_SUPPORT"},x=class{constructor(){this.shaderParts=new Map([[g.FRAGMENT_HEAD,null],[g.FRAGMENT_MAIN_UV,null],[g.FRAGMENT_MAIN_IMAGE,null],[g.VERTEX_HEAD,null],[g.VERTEX_MAIN_SUPPORT,null]]),this.defines=new Map,this.uniforms=new Map,this.blendModes=new Map,this.extensions=new Set,this.attributes=m.NONE,this.varyings=new Set,this.uvTransformation=!1,this.readDepth=!1,this.colorSpace=i.Zr2}};function E(e){let t;if(0===e)t=new Float64Array(0);else if(1===e)t=new Float64Array([1]);else if(e>1){let r=new Float64Array(e),i=new Float64Array(e);for(let s=1;s<=e;++s){for(let e=0;e<s;++e)i[e]=0===e||e===s-1?1:r[e-1]+r[e];t=i,i=r,r=t}}return t}var T=class{constructor(e,t=2){this.weights=null,this.offsets=null,this.linearWeights=null,this.linearOffsets=null,this.generate(e,t)}get steps(){return null===this.offsets?0:this.offsets.length}get linearSteps(){return null===this.linearOffsets?0:this.linearOffsets.length}generate(e,t){if(e<3||e>1020)throw Error("The kernel size must be in the range [3, 1020]");let r=e+2*t,i=t>0?E(r).slice(t,-t):E(r),s=Math.floor((i.length-1)/2),a=i.reduce((e,t)=>e+t,0),n=i.slice(s),o=[...Array(s+1).keys()],l=new Float64Array(Math.floor(o.length/2)),c=new Float64Array(l.length);l[0]=n[0]/a;for(let e=1,t=1,r=o.length-1;e<r;e+=2,++t){let r=o[e],i=o[e+1],s=n[e],u=n[e+1],f=s+u,d=(r*s+i*u)/f;l[t]=f/a,c[t]=d}for(let e=0,t=n.length,r=1/a;e<t;++e)n[e]*=r;let u=(l.reduce((e,t)=>e+t,0)-.5*l[0])*2;if(0!==u)for(let e=0,t=l.length,r=1/u;e<t;++e)l[e]*=r;this.offsets=o,this.weights=n,this.linearOffsets=c,this.linearWeights=l}},U=!1,S=class{constructor(e=null){this.originalMaterials=new Map,this.material=null,this.materials=null,this.materialsBackSide=null,this.materialsDoubleSide=null,this.materialsFlatShaded=null,this.materialsFlatShadedBackSide=null,this.materialsFlatShadedDoubleSide=null,this.setMaterial(e),this.meshCount=0,this.replaceMaterial=e=>{if(e.isMesh){let t;if(e.material.flatShading)switch(e.material.side){case i.$EB:t=this.materialsFlatShadedDoubleSide;break;case i.hsX:t=this.materialsFlatShadedBackSide;break;default:t=this.materialsFlatShaded}else switch(e.material.side){case i.$EB:t=this.materialsDoubleSide;break;case i.hsX:t=this.materialsBackSide;break;default:t=this.materials}this.originalMaterials.set(e,e.material),e.isSkinnedMesh?e.material=t[2]:e.isInstancedMesh?e.material=t[1]:e.material=t[0],++this.meshCount}}}cloneMaterial(e){if(!(e instanceof i.BKk))return e.clone();let t=e.uniforms,r=new Map;for(let e in t){let i=t[e].value;i.isRenderTargetTexture&&(t[e].value=null,r.set(e,i))}let s=e.clone();for(let e of r)t[e[0]].value=e[1],s.uniforms[e[0]].value=e[1];return s}setMaterial(e){if(this.disposeMaterials(),this.material=e,null!==e){let t=this.materials=[this.cloneMaterial(e),this.cloneMaterial(e),this.cloneMaterial(e)];for(let r of t)r.uniforms=Object.assign({},e.uniforms),r.side=i.hB5;t[2].skinning=!0,this.materialsBackSide=t.map(t=>{let r=this.cloneMaterial(t);return r.uniforms=Object.assign({},e.uniforms),r.side=i.hsX,r}),this.materialsDoubleSide=t.map(t=>{let r=this.cloneMaterial(t);return r.uniforms=Object.assign({},e.uniforms),r.side=i.$EB,r}),this.materialsFlatShaded=t.map(t=>{let r=this.cloneMaterial(t);return r.uniforms=Object.assign({},e.uniforms),r.flatShading=!0,r}),this.materialsFlatShadedBackSide=t.map(t=>{let r=this.cloneMaterial(t);return r.uniforms=Object.assign({},e.uniforms),r.flatShading=!0,r.side=i.hsX,r}),this.materialsFlatShadedDoubleSide=t.map(t=>{let r=this.cloneMaterial(t);return r.uniforms=Object.assign({},e.uniforms),r.flatShading=!0,r.side=i.$EB,r})}}render(e,t,r){let i=e.shadowMap.enabled;if(e.shadowMap.enabled=!1,U){let i=this.originalMaterials;for(let s of(this.meshCount=0,t.traverse(this.replaceMaterial),e.render(t,r),i))s[0].material=s[1];this.meshCount!==i.size&&i.clear()}else{let i=t.overrideMaterial;t.overrideMaterial=this.material,e.render(t,r),t.overrideMaterial=i}e.shadowMap.enabled=i}disposeMaterials(){if(null!==this.material)for(let e of this.materials.concat(this.materialsBackSide).concat(this.materialsDoubleSide).concat(this.materialsFlatShaded).concat(this.materialsFlatShadedBackSide).concat(this.materialsFlatShadedDoubleSide))e.dispose()}dispose(){this.originalMaterials.clear(),this.disposeMaterials()}static get workaroundEnabled(){return U}static set workaroundEnabled(e){U=e}},D=class extends i.Qev{constructor(e=null,t=-1,r=-1,s=1){super(),null!==e&&this.addEventListener("change",()=>e.setSize(this.baseSize.width,this.baseSize.height)),this.baseSize=new i.I9Y(1,1),this.preferredSize=new i.I9Y(t,r),this.target=this.preferredSize,this.s=s,this.effectiveSize=new i.I9Y,this.addEventListener("change",()=>this.updateEffectiveSize()),this.updateEffectiveSize()}updateEffectiveSize(){let e=this.baseSize,t=this.preferredSize,r=this.effectiveSize,i=this.scale;-1!==t.width?r.width=t.width:-1!==t.height?r.width=Math.round(t.height*(e.width/Math.max(e.height,1))):r.width=Math.round(e.width*i),-1!==t.height?r.height=t.height:-1!==t.width?r.height=Math.round(t.width/Math.max(e.width/Math.max(e.height,1),1)):r.height=Math.round(e.height*i)}get width(){return this.effectiveSize.width}set width(e){this.preferredWidth=e}get height(){return this.effectiveSize.height}set height(e){this.preferredHeight=e}getWidth(){return this.width}getHeight(){return this.height}get scale(){return this.s}set scale(e){this.s!==e&&(this.s=e,this.preferredSize.setScalar(-1),this.dispatchEvent({type:"change"}))}getScale(){return this.scale}setScale(e){this.scale=e}get baseWidth(){return this.baseSize.width}set baseWidth(e){this.baseSize.width!==e&&(this.baseSize.width=e,this.dispatchEvent({type:"change"}))}getBaseWidth(){return this.baseWidth}setBaseWidth(e){this.baseWidth=e}get baseHeight(){return this.baseSize.height}set baseHeight(e){this.baseSize.height!==e&&(this.baseSize.height=e,this.dispatchEvent({type:"change"}))}getBaseHeight(){return this.baseHeight}setBaseHeight(e){this.baseHeight=e}setBaseSize(e,t){(this.baseSize.width!==e||this.baseSize.height!==t)&&(this.baseSize.set(e,t),this.dispatchEvent({type:"change"}))}get preferredWidth(){return this.preferredSize.width}set preferredWidth(e){this.preferredSize.width!==e&&(this.preferredSize.width=e,this.dispatchEvent({type:"change"}))}getPreferredWidth(){return this.preferredWidth}setPreferredWidth(e){this.preferredWidth=e}get preferredHeight(){return this.preferredSize.height}set preferredHeight(e){this.preferredSize.height!==e&&(this.preferredSize.height=e,this.dispatchEvent({type:"change"}))}getPreferredHeight(){return this.preferredHeight}setPreferredHeight(e){this.preferredHeight=e}setPreferredSize(e,t){(this.preferredSize.width!==e||this.preferredSize.height!==t)&&(this.preferredSize.set(e,t),this.dispatchEvent({type:"change"}))}copy(e){this.s=e.scale,this.baseSize.set(e.baseWidth,e.baseHeight),this.preferredSize.set(e.preferredWidth,e.preferredHeight),this.dispatchEvent({type:"change"})}static get AUTO_SIZE(){return -1}},_=new class{constructor(e=0){this.nextId=e}getNextId(){return this.nextId++}reset(e=0){return this.nextId=e,this}}(2),y={ADD:0,ALPHA:1,AVERAGE:2,COLOR:3,COLOR_BURN:4,COLOR_DODGE:5,DARKEN:6,DIFFERENCE:7,DIVIDE:8,DST:9,EXCLUSION:10,HARD_LIGHT:11,HARD_MIX:12,HUE:13,INVERT:14,INVERT_RGB:15,LIGHTEN:16,LINEAR_BURN:17,LINEAR_DODGE:18,LINEAR_LIGHT:19,LUMINOSITY:20,MULTIPLY:21,NEGATION:22,NORMAL:23,OVERLAY:24,PIN_LIGHT:25,REFLECT:26,SATURATION:27,SCREEN:28,SOFT_LIGHT:29,SRC:30,SUBTRACT:31,VIVID_LIGHT:32},R=new Map([[y.ADD,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=dst.rgb+src.rgb;return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.ALPHA,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){return mix(dst,src,src.a*opacity);}"],[y.AVERAGE,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=(dst.rgb+src.rgb)*0.5;return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.COLOR,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 a=RGBToHSL(dst.rgb);vec3 b=RGBToHSL(src.rgb);vec3 c=HSLToRGB(vec3(b.xy,a.z));return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.COLOR_BURN,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 a=dst.rgb,b=src.rgb;vec3 c=mix(step(0.0,b)*(1.0-min(vec3(1.0),(1.0-a)/max(b,1e-9))),vec3(1.0),step(1.0,a));return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.COLOR_DODGE,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 a=dst.rgb,b=src.rgb;vec3 c=step(0.0,a)*mix(min(vec3(1.0),a/max(1.0-b,1e-9)),vec3(1.0),step(1.0,b));return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.DARKEN,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=min(dst.rgb,src.rgb);return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.DIFFERENCE,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=abs(dst.rgb-src.rgb);return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.DIVIDE,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=dst.rgb/max(src.rgb,1e-9);return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.DST,null],[y.EXCLUSION,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=dst.rgb+src.rgb-2.0*dst.rgb*src.rgb;return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.HARD_LIGHT,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 a=min(dst.rgb,1.0);vec3 b=min(src.rgb,1.0);vec3 c=mix(2.0*a*b,1.0-2.0*(1.0-a)*(1.0-b),step(0.5,b));return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.HARD_MIX,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=step(1.0,dst.rgb+src.rgb);return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.HUE,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 a=RGBToHSL(dst.rgb);vec3 b=RGBToHSL(src.rgb);vec3 c=HSLToRGB(vec3(b.x,a.yz));return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.INVERT,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=max(1.0-src.rgb,0.0);return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.INVERT_RGB,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=src.rgb*max(1.0-dst.rgb,0.0);return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.LIGHTEN,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=max(dst.rgb,src.rgb);return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.LINEAR_BURN,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=clamp(src.rgb+dst.rgb-1.0,0.0,1.0);return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.LINEAR_DODGE,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=min(dst.rgb+src.rgb,1.0);return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.LINEAR_LIGHT,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=clamp(2.0*src.rgb+dst.rgb-1.0,0.0,1.0);return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.LUMINOSITY,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 a=RGBToHSL(dst.rgb);vec3 b=RGBToHSL(src.rgb);vec3 c=HSLToRGB(vec3(a.xy,b.z));return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.MULTIPLY,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=dst.rgb*src.rgb;return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.NEGATION,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=max(1.0-abs(1.0-dst.rgb-src.rgb),0.0);return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.NORMAL,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){return mix(dst,src,opacity);}"],[y.OVERLAY,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 a=2.0*src.rgb*dst.rgb;vec3 b=1.0-2.0*(1.0-src.rgb)*(1.0-dst.rgb);vec3 c=mix(a,b,step(0.5,dst.rgb));return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.PIN_LIGHT,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 src2=2.0*src.rgb;vec3 c=mix(mix(src2,dst.rgb,step(0.5*dst.rgb,src.rgb)),max(src2-1.0,vec3(0.0)),step(dst.rgb,src2-1.0));return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.REFLECT,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 a=min(dst.rgb*dst.rgb/max(1.0-src.rgb,1e-9),1.0);vec3 c=mix(a,src.rgb,step(1.0,src.rgb));return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.SATURATION,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 a=RGBToHSL(dst.rgb);vec3 b=RGBToHSL(src.rgb);vec3 c=HSLToRGB(vec3(a.x,b.y,a.z));return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.SCREEN,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=dst.rgb+src.rgb-min(dst.rgb*src.rgb,1.0);return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.SOFT_LIGHT,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 src2=2.0*src.rgb;vec3 d=dst.rgb+(src2-1.0);vec3 w=step(0.5,src.rgb);vec3 a=dst.rgb-(1.0-src2)*dst.rgb*(1.0-dst.rgb);vec3 b=mix(d*(sqrt(dst.rgb)-dst.rgb),d*dst.rgb*((16.0*dst.rgb-12.0)*dst.rgb+3.0),w*(1.0-step(0.25,dst.rgb)));vec3 c=mix(a,b,w);return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.SRC,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){return src;}"],[y.SUBTRACT,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=max(dst.rgb-src.rgb,0.0);return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"],[y.VIVID_LIGHT,"vec4 blend(const in vec4 dst,const in vec4 src,const in float opacity){vec3 c=mix(max(1.0-min((1.0-dst.rgb)/(2.0*src.rgb),1.0),0.0),min(dst.rgb/(2.0*(1.0-src.rgb)),1.0),step(0.5,src.rgb));return mix(dst,vec4(c,max(dst.a,src.a)),opacity);}"]]),A=class extends i.Qev{constructor(e,t=1){super(),this._blendFunction=e,this.opacity=new i.nc$(t)}getOpacity(){return this.opacity.value}setOpacity(e){this.opacity.value=e}get blendFunction(){return this._blendFunction}set blendFunction(e){this._blendFunction=e,this.dispatchEvent({type:"change"})}getBlendFunction(){return this.blendFunction}setBlendFunction(e){this.blendFunction=e}getShaderCode(){return R.get(this.blendFunction)}},w=(i.GOR,class extends i.Qev{constructor(e,t,{attributes:r=m.NONE,blendFunction:s=y.NORMAL,defines:a=new Map,uniforms:n=new Map,extensions:o=null,vertexShader:l=null}={}){super(),this.name=e,this.renderer=null,this.attributes=r,this.fragmentShader=t,this.vertexShader=l,this.defines=a,this.uniforms=n,this.extensions=o,this.blendMode=new A(s),this.blendMode.addEventListener("change",e=>this.setChanged()),this._inputColorSpace=i.Zr2,this._outputColorSpace=i.jf0}get inputColorSpace(){return this._inputColorSpace}set inputColorSpace(e){this._inputColorSpace=e,this.setChanged()}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e,this.setChanged()}set mainScene(e){}set mainCamera(e){}getName(){return this.name}setRenderer(e){this.renderer=e}getDefines(){return this.defines}getUniforms(){return this.uniforms}getExtensions(){return this.extensions}getBlendMode(){return this.blendMode}getAttributes(){return this.attributes}setAttributes(e){this.attributes=e,this.setChanged()}getFragmentShader(){return this.fragmentShader}setFragmentShader(e){this.fragmentShader=e,this.setChanged()}getVertexShader(){return this.vertexShader}setVertexShader(e){this.vertexShader=e,this.setChanged()}setChanged(){this.dispatchEvent({type:"change"})}setDepthTexture(e,t=i.Rkk){}update(e,t,r){}setSize(e,t){}initialize(e,t,r){}dispose(){for(let e of Object.keys(this)){let t=this[e];(t instanceof i.nWS||t instanceof i.imn||t instanceof i.gPd||t instanceof a)&&this[e].dispose()}}}),B={MEDIUM:2,LARGE:3},I=`#ifdef FRAMEBUFFER_PRECISION_HIGH
uniform mediump sampler2D inputBuffer;
#else
uniform lowp sampler2D inputBuffer;
#endif
varying vec2 vUv0;varying vec2 vUv1;varying vec2 vUv2;varying vec2 vUv3;void main(){vec4 sum=texture2D(inputBuffer,vUv0);sum+=texture2D(inputBuffer,vUv1);sum+=texture2D(inputBuffer,vUv2);sum+=texture2D(inputBuffer,vUv3);gl_FragColor=sum*0.25;
#include <colorspace_fragment>
}`,b=[new Float32Array([0,0]),new Float32Array([0,1,1]),new Float32Array([0,1,1,2]),new Float32Array([0,1,2,2,3]),new Float32Array([0,1,2,3,4,4,5]),new Float32Array([0,1,2,3,4,5,7,8,9,10])],C=class extends i.BKk{constructor(e=new i.IUQ){super({name:"KawaseBlurMaterial",uniforms:{inputBuffer:new i.nc$(null),texelSize:new i.nc$(new i.IUQ),scale:new i.nc$(1),kernel:new i.nc$(0)},blending:i.XIg,toneMapped:!1,depthWrite:!1,depthTest:!1,fragmentShader:I,vertexShader:"uniform vec4 texelSize;uniform float kernel;uniform float scale;varying vec2 vUv0;varying vec2 vUv1;varying vec2 vUv2;varying vec2 vUv3;void main(){vec2 uv=position.xy*0.5+0.5;vec2 dUv=(texelSize.xy*vec2(kernel)+texelSize.zw)*scale;vUv0=vec2(uv.x-dUv.x,uv.y+dUv.y);vUv1=vec2(uv.x+dUv.x,uv.y+dUv.y);vUv2=vec2(uv.x+dUv.x,uv.y-dUv.y);vUv3=vec2(uv.x-dUv.x,uv.y-dUv.y);gl_Position=vec4(position.xy,1.0,1.0);}"}),this.setTexelSize(e.x,e.y),this.kernelSize=B.MEDIUM}set inputBuffer(e){this.uniforms.inputBuffer.value=e}setInputBuffer(e){this.inputBuffer=e}get kernelSequence(){return b[this.kernelSize]}get scale(){return this.uniforms.scale.value}set scale(e){this.uniforms.scale.value=e}getScale(){return this.uniforms.scale.value}setScale(e){this.uniforms.scale.value=e}getKernel(){return null}get kernel(){return this.uniforms.kernel.value}set kernel(e){this.uniforms.kernel.value=e}setKernel(e){this.kernel=e}setTexelSize(e,t){this.uniforms.texelSize.value.set(e,t,.5*e,.5*t)}setSize(e,t){let r=1/e,i=1/t;this.uniforms.texelSize.value.set(r,i,.5*r,.5*i)}},M=class extends a{constructor({kernelSize:e=B.MEDIUM,resolutionScale:t=.5,width:r=D.AUTO_SIZE,height:s=D.AUTO_SIZE,resolutionX:a=r,resolutionY:n=s}={}){super("KawaseBlurPass"),this.renderTargetA=new i.nWS(1,1,{depthBuffer:!1}),this.renderTargetA.texture.name="Blur.Target.A",this.renderTargetB=this.renderTargetA.clone(),this.renderTargetB.texture.name="Blur.Target.B";let o=this.resolution=new D(this,a,n,t);o.addEventListener("change",e=>this.setSize(o.baseWidth,o.baseHeight)),this._blurMaterial=new C,this._blurMaterial.kernelSize=e,this.copyMaterial=new c}getResolution(){return this.resolution}get blurMaterial(){return this._blurMaterial}set blurMaterial(e){this._blurMaterial=e}get dithering(){return this.copyMaterial.dithering}set dithering(e){this.copyMaterial.dithering=e}get kernelSize(){return this.blurMaterial.kernelSize}set kernelSize(e){this.blurMaterial.kernelSize=e}get width(){return this.resolution.width}set width(e){this.resolution.preferredWidth=e}get height(){return this.resolution.height}set height(e){this.resolution.preferredHeight=e}get scale(){return this.blurMaterial.scale}set scale(e){this.blurMaterial.scale=e}getScale(){return this.blurMaterial.scale}setScale(e){this.blurMaterial.scale=e}getKernelSize(){return this.kernelSize}setKernelSize(e){this.kernelSize=e}getResolutionScale(){return this.resolution.scale}setResolutionScale(e){this.resolution.scale=e}render(e,t,r,i,s){let a=this.scene,n=this.camera,o=this.renderTargetA,l=this.renderTargetB,c=this.blurMaterial,u=c.kernelSequence,f=t;this.fullscreenMaterial=c;for(let t=0,r=u.length;t<r;++t){let r=(1&t)==0?o:l;c.kernel=u[t],c.inputBuffer=f.texture,e.setRenderTarget(r),e.render(a,n),f=r}this.fullscreenMaterial=this.copyMaterial,this.copyMaterial.inputBuffer=f.texture,e.setRenderTarget(this.renderToScreen?null:r),e.render(a,n)}setSize(e,t){let r=this.resolution;r.setBaseSize(e,t);let i=r.width,s=r.height;this.renderTargetA.setSize(i,s),this.renderTargetB.setSize(i,s),this.blurMaterial.setSize(e,t)}initialize(e,t,r){void 0!==r&&(this.renderTargetA.texture.type=r,this.renderTargetB.texture.type=r,r!==i.OUM?(this.blurMaterial.defines.FRAMEBUFFER_PRECISION_HIGH="1",this.copyMaterial.defines.FRAMEBUFFER_PRECISION_HIGH="1"):null!==e&&e.outputColorSpace===i.er$&&(this.renderTargetA.texture.colorSpace=i.er$,this.renderTargetB.texture.colorSpace=i.er$))}static get AUTO_SIZE(){return D.AUTO_SIZE}},P=`#include <common>
#ifdef FRAMEBUFFER_PRECISION_HIGH
uniform mediump sampler2D inputBuffer;
#else
uniform lowp sampler2D inputBuffer;
#endif
#ifdef RANGE
uniform vec2 range;
#elif defined(THRESHOLD)
uniform float threshold;uniform float smoothing;
#endif
varying vec2 vUv;void main(){vec4 texel=texture2D(inputBuffer,vUv);float l=luminance(texel.rgb);float mask=1.0;
#ifdef RANGE
float low=step(range.x,l);float high=step(l,range.y);mask=low*high;
#elif defined(THRESHOLD)
mask=smoothstep(threshold,threshold+smoothing,l);
#endif
#ifdef COLOR
gl_FragColor=texel*mask;
#else
gl_FragColor=vec4(l*mask);
#endif
}`,F=class extends i.BKk{constructor(e=!1,t=null){super({name:"LuminanceMaterial",defines:{THREE_REVISION:i.sPf.replace(/\D+/g,"")},uniforms:{inputBuffer:new i.nc$(null),threshold:new i.nc$(0),smoothing:new i.nc$(1),range:new i.nc$(null)},blending:i.XIg,toneMapped:!1,depthWrite:!1,depthTest:!1,fragmentShader:P,vertexShader:l}),this.colorOutput=e,this.luminanceRange=t}set inputBuffer(e){this.uniforms.inputBuffer.value=e}setInputBuffer(e){this.uniforms.inputBuffer.value=e}get threshold(){return this.uniforms.threshold.value}set threshold(e){this.smoothing>0||e>0?this.defines.THRESHOLD="1":delete this.defines.THRESHOLD,this.uniforms.threshold.value=e}getThreshold(){return this.threshold}setThreshold(e){this.threshold=e}get smoothing(){return this.uniforms.smoothing.value}set smoothing(e){this.threshold>0||e>0?this.defines.THRESHOLD="1":delete this.defines.THRESHOLD,this.uniforms.smoothing.value=e}getSmoothingFactor(){return this.smoothing}setSmoothingFactor(e){this.smoothing=e}get useThreshold(){return this.threshold>0||this.smoothing>0}set useThreshold(e){}get colorOutput(){return void 0!==this.defines.COLOR}set colorOutput(e){e?this.defines.COLOR="1":delete this.defines.COLOR,this.needsUpdate=!0}isColorOutputEnabled(e){return this.colorOutput}setColorOutputEnabled(e){this.colorOutput=e}get useRange(){return null!==this.luminanceRange}set useRange(e){this.luminanceRange=null}get luminanceRange(){return this.uniforms.range.value}set luminanceRange(e){null!==e?this.defines.RANGE="1":delete this.defines.RANGE,this.uniforms.range.value=e,this.needsUpdate=!0}getLuminanceRange(){return this.luminanceRange}setLuminanceRange(e){this.luminanceRange=e}},N=class extends a{constructor({renderTarget:e,luminanceRange:t,colorOutput:r,resolutionScale:s=1,width:a=D.AUTO_SIZE,height:n=D.AUTO_SIZE,resolutionX:o=a,resolutionY:l=n}={}){super("LuminancePass"),this.fullscreenMaterial=new F(r,t),this.needsSwap=!1,this.renderTarget=e,void 0===this.renderTarget&&(this.renderTarget=new i.nWS(1,1,{depthBuffer:!1}),this.renderTarget.texture.name="LuminancePass.Target");let c=this.resolution=new D(this,o,l,s);c.addEventListener("change",e=>this.setSize(c.baseWidth,c.baseHeight))}get texture(){return this.renderTarget.texture}getTexture(){return this.renderTarget.texture}getResolution(){return this.resolution}render(e,t,r,i,s){this.fullscreenMaterial.inputBuffer=t.texture,e.setRenderTarget(this.renderToScreen?null:this.renderTarget),e.render(this.scene,this.camera)}setSize(e,t){let r=this.resolution;r.setBaseSize(e,t),this.renderTarget.setSize(r.width,r.height)}initialize(e,t,r){void 0!==r&&r!==i.OUM&&(this.renderTarget.texture.type=r,this.fullscreenMaterial.defines.FRAMEBUFFER_PRECISION_HIGH="1")}},O=`#ifdef FRAMEBUFFER_PRECISION_HIGH
uniform mediump sampler2D inputBuffer;
#else
uniform lowp sampler2D inputBuffer;
#endif
#define WEIGHT_INNER 0.125
#define WEIGHT_OUTER 0.05556
varying vec2 vUv;varying vec2 vUv00;varying vec2 vUv01;varying vec2 vUv02;varying vec2 vUv03;varying vec2 vUv04;varying vec2 vUv05;varying vec2 vUv06;varying vec2 vUv07;varying vec2 vUv08;varying vec2 vUv09;varying vec2 vUv10;varying vec2 vUv11;float clampToBorder(const in vec2 uv){return float(uv.s>=0.0&&uv.s<=1.0&&uv.t>=0.0&&uv.t<=1.0);}void main(){vec4 c=vec4(0.0);vec4 w=WEIGHT_INNER*vec4(clampToBorder(vUv00),clampToBorder(vUv01),clampToBorder(vUv02),clampToBorder(vUv03));c+=w.x*texture2D(inputBuffer,vUv00);c+=w.y*texture2D(inputBuffer,vUv01);c+=w.z*texture2D(inputBuffer,vUv02);c+=w.w*texture2D(inputBuffer,vUv03);w=WEIGHT_OUTER*vec4(clampToBorder(vUv04),clampToBorder(vUv05),clampToBorder(vUv06),clampToBorder(vUv07));c+=w.x*texture2D(inputBuffer,vUv04);c+=w.y*texture2D(inputBuffer,vUv05);c+=w.z*texture2D(inputBuffer,vUv06);c+=w.w*texture2D(inputBuffer,vUv07);w=WEIGHT_OUTER*vec4(clampToBorder(vUv08),clampToBorder(vUv09),clampToBorder(vUv10),clampToBorder(vUv11));c+=w.x*texture2D(inputBuffer,vUv08);c+=w.y*texture2D(inputBuffer,vUv09);c+=w.z*texture2D(inputBuffer,vUv10);c+=w.w*texture2D(inputBuffer,vUv11);c+=WEIGHT_OUTER*texture2D(inputBuffer,vUv);gl_FragColor=c;
#include <colorspace_fragment>
}`,L=class extends i.BKk{constructor(){super({name:"DownsamplingMaterial",uniforms:{inputBuffer:new i.nc$(null),texelSize:new i.nc$(new i.I9Y)},blending:i.XIg,toneMapped:!1,depthWrite:!1,depthTest:!1,fragmentShader:O,vertexShader:"uniform vec2 texelSize;varying vec2 vUv;varying vec2 vUv00;varying vec2 vUv01;varying vec2 vUv02;varying vec2 vUv03;varying vec2 vUv04;varying vec2 vUv05;varying vec2 vUv06;varying vec2 vUv07;varying vec2 vUv08;varying vec2 vUv09;varying vec2 vUv10;varying vec2 vUv11;void main(){vUv=position.xy*0.5+0.5;vUv00=vUv+texelSize*vec2(-1.0,1.0);vUv01=vUv+texelSize*vec2(1.0,1.0);vUv02=vUv+texelSize*vec2(-1.0,-1.0);vUv03=vUv+texelSize*vec2(1.0,-1.0);vUv04=vUv+texelSize*vec2(-2.0,2.0);vUv05=vUv+texelSize*vec2(0.0,2.0);vUv06=vUv+texelSize*vec2(2.0,2.0);vUv07=vUv+texelSize*vec2(-2.0,0.0);vUv08=vUv+texelSize*vec2(2.0,0.0);vUv09=vUv+texelSize*vec2(-2.0,-2.0);vUv10=vUv+texelSize*vec2(0.0,-2.0);vUv11=vUv+texelSize*vec2(2.0,-2.0);gl_Position=vec4(position.xy,1.0,1.0);}"})}set inputBuffer(e){this.uniforms.inputBuffer.value=e}setSize(e,t){this.uniforms.texelSize.value.set(1/e,1/t)}},H=`#ifdef FRAMEBUFFER_PRECISION_HIGH
uniform mediump sampler2D inputBuffer;uniform mediump sampler2D supportBuffer;
#else
uniform lowp sampler2D inputBuffer;uniform lowp sampler2D supportBuffer;
#endif
uniform float radius;varying vec2 vUv;varying vec2 vUv0;varying vec2 vUv1;varying vec2 vUv2;varying vec2 vUv3;varying vec2 vUv4;varying vec2 vUv5;varying vec2 vUv6;varying vec2 vUv7;void main(){vec4 c=vec4(0.0);c+=texture2D(inputBuffer,vUv0)*0.0625;c+=texture2D(inputBuffer,vUv1)*0.125;c+=texture2D(inputBuffer,vUv2)*0.0625;c+=texture2D(inputBuffer,vUv3)*0.125;c+=texture2D(inputBuffer,vUv)*0.25;c+=texture2D(inputBuffer,vUv4)*0.125;c+=texture2D(inputBuffer,vUv5)*0.0625;c+=texture2D(inputBuffer,vUv6)*0.125;c+=texture2D(inputBuffer,vUv7)*0.0625;vec4 baseColor=texture2D(supportBuffer,vUv);gl_FragColor=mix(baseColor,c,radius);
#include <colorspace_fragment>
}`,z=class extends i.BKk{constructor(){super({name:"UpsamplingMaterial",uniforms:{inputBuffer:new i.nc$(null),supportBuffer:new i.nc$(null),texelSize:new i.nc$(new i.I9Y),radius:new i.nc$(.85)},blending:i.XIg,toneMapped:!1,depthWrite:!1,depthTest:!1,fragmentShader:H,vertexShader:"uniform vec2 texelSize;varying vec2 vUv;varying vec2 vUv0;varying vec2 vUv1;varying vec2 vUv2;varying vec2 vUv3;varying vec2 vUv4;varying vec2 vUv5;varying vec2 vUv6;varying vec2 vUv7;void main(){vUv=position.xy*0.5+0.5;vUv0=vUv+texelSize*vec2(-1.0,1.0);vUv1=vUv+texelSize*vec2(0.0,1.0);vUv2=vUv+texelSize*vec2(1.0,1.0);vUv3=vUv+texelSize*vec2(-1.0,0.0);vUv4=vUv+texelSize*vec2(1.0,0.0);vUv5=vUv+texelSize*vec2(-1.0,-1.0);vUv6=vUv+texelSize*vec2(0.0,-1.0);vUv7=vUv+texelSize*vec2(1.0,-1.0);gl_Position=vec4(position.xy,1.0,1.0);}"})}set inputBuffer(e){this.uniforms.inputBuffer.value=e}set supportBuffer(e){this.uniforms.supportBuffer.value=e}get radius(){return this.uniforms.radius.value}set radius(e){this.uniforms.radius.value=e}setSize(e,t){this.uniforms.texelSize.value.set(1/e,1/t)}},G=class extends a{constructor(){super("MipmapBlurPass"),this.needsSwap=!1,this.renderTarget=new i.nWS(1,1,{depthBuffer:!1}),this.renderTarget.texture.name="Upsampling.Mipmap0",this.downsamplingMipmaps=[],this.upsamplingMipmaps=[],this.downsamplingMaterial=new L,this.upsamplingMaterial=new z,this.resolution=new i.I9Y}get texture(){return this.renderTarget.texture}get levels(){return this.downsamplingMipmaps.length}set levels(e){if(this.levels!==e){let t=this.renderTarget;this.dispose(),this.downsamplingMipmaps=[],this.upsamplingMipmaps=[];for(let r=0;r<e;++r){let e=t.clone();e.texture.name="Downsampling.Mipmap"+r,this.downsamplingMipmaps.push(e)}this.upsamplingMipmaps.push(t);for(let r=1,i=e-1;r<i;++r){let e=t.clone();e.texture.name="Upsampling.Mipmap"+r,this.upsamplingMipmaps.push(e)}this.setSize(this.resolution.x,this.resolution.y)}}get radius(){return this.upsamplingMaterial.radius}set radius(e){this.upsamplingMaterial.radius=e}render(e,t,r,i,s){let{scene:a,camera:n}=this,{downsamplingMaterial:o,upsamplingMaterial:l}=this,{downsamplingMipmaps:c,upsamplingMipmaps:u}=this,f=t;this.fullscreenMaterial=o;for(let t=0,r=c.length;t<r;++t){let r=c[t];o.setSize(f.width,f.height),o.inputBuffer=f.texture,e.setRenderTarget(r),e.render(a,n),f=r}this.fullscreenMaterial=l;for(let t=u.length-1;t>=0;--t){let r=u[t];l.setSize(f.width,f.height),l.inputBuffer=f.texture,l.supportBuffer=c[t].texture,e.setRenderTarget(r),e.render(a,n),f=r}}setSize(e,t){let r=this.resolution;r.set(e,t);let i=r.width,s=r.height;for(let e=0,t=this.downsamplingMipmaps.length;e<t;++e)i=Math.round(.5*i),s=Math.round(.5*s),this.downsamplingMipmaps[e].setSize(i,s),e<this.upsamplingMipmaps.length&&this.upsamplingMipmaps[e].setSize(i,s)}initialize(e,t,r){if(void 0!==r){let t=this.downsamplingMipmaps.concat(this.upsamplingMipmaps);for(let e of t)e.texture.type=r;if(r!==i.OUM)this.downsamplingMaterial.defines.FRAMEBUFFER_PRECISION_HIGH="1",this.upsamplingMaterial.defines.FRAMEBUFFER_PRECISION_HIGH="1";else if(null!==e&&e.outputColorSpace===i.er$)for(let e of t)e.texture.colorSpace=i.er$}}dispose(){for(let e of(super.dispose(),this.downsamplingMipmaps.concat(this.upsamplingMipmaps)))e.dispose()}},k=`#ifdef FRAMEBUFFER_PRECISION_HIGH
uniform mediump sampler2D map;
#else
uniform lowp sampler2D map;
#endif
uniform float intensity;void mainImage(const in vec4 inputColor,const in vec2 uv,out vec4 outputColor){outputColor=texture2D(map,uv)*intensity;}`,V=class extends w{constructor({blendFunction:e=y.SCREEN,luminanceThreshold:t=1,luminanceSmoothing:r=.03,mipmapBlur:s=!0,intensity:a=1,radius:n=.85,levels:o=8,kernelSize:l=B.LARGE,resolutionScale:c=.5,width:u=D.AUTO_SIZE,height:f=D.AUTO_SIZE,resolutionX:d=u,resolutionY:v=f}={}){super("BloomEffect",k,{blendFunction:e,uniforms:new Map([["map",new i.nc$(null)],["intensity",new i.nc$(a)]])}),this.renderTarget=new i.nWS(1,1,{depthBuffer:!1}),this.renderTarget.texture.name="Bloom.Target",this.blurPass=new M({kernelSize:l}),this.luminancePass=new N({colorOutput:!0}),this.luminanceMaterial.threshold=t,this.luminanceMaterial.smoothing=r,this.mipmapBlurPass=new G,this.mipmapBlurPass.enabled=s,this.mipmapBlurPass.radius=n,this.mipmapBlurPass.levels=o,this.uniforms.get("map").value=s?this.mipmapBlurPass.texture:this.renderTarget.texture;let h=this.resolution=new D(this,d,v,c);h.addEventListener("change",e=>this.setSize(h.baseWidth,h.baseHeight))}get texture(){return this.mipmapBlurPass.enabled?this.mipmapBlurPass.texture:this.renderTarget.texture}getTexture(){return this.texture}getResolution(){return this.resolution}getBlurPass(){return this.blurPass}getLuminancePass(){return this.luminancePass}get luminanceMaterial(){return this.luminancePass.fullscreenMaterial}getLuminanceMaterial(){return this.luminancePass.fullscreenMaterial}get width(){return this.resolution.width}set width(e){this.resolution.preferredWidth=e}get height(){return this.resolution.height}set height(e){this.resolution.preferredHeight=e}get dithering(){return this.blurPass.dithering}set dithering(e){this.blurPass.dithering=e}get kernelSize(){return this.blurPass.kernelSize}set kernelSize(e){this.blurPass.kernelSize=e}get distinction(){return console.warn(this.name,"distinction was removed"),1}set distinction(e){console.warn(this.name,"distinction was removed")}get intensity(){return this.uniforms.get("intensity").value}set intensity(e){this.uniforms.get("intensity").value=e}getIntensity(){return this.intensity}setIntensity(e){this.intensity=e}getResolutionScale(){return this.resolution.scale}setResolutionScale(e){this.resolution.scale=e}update(e,t,r){let i=this.renderTarget,s=this.luminancePass;s.enabled?(s.render(e,t),this.mipmapBlurPass.enabled?this.mipmapBlurPass.render(e,s.renderTarget):this.blurPass.render(e,s.renderTarget,i)):this.mipmapBlurPass.enabled?this.mipmapBlurPass.render(e,t):this.blurPass.render(e,t,i)}setSize(e,t){let r=this.resolution;r.setBaseSize(e,t),this.renderTarget.setSize(r.width,r.height),this.blurPass.resolution.copy(r),this.luminancePass.setSize(e,t),this.mipmapBlurPass.setSize(e,t)}initialize(e,t,r){this.blurPass.initialize(e,t,r),this.luminancePass.initialize(e,t,r),this.mipmapBlurPass.initialize(e,t,r),void 0!==r&&(this.renderTarget.texture.type=r,null!==e&&e.outputColorSpace===i.er$&&(this.renderTarget.texture.colorSpace=i.er$))}},Z={RED:0},K={DISCARD:0},W=`#ifdef FRAMEBUFFER_PRECISION_HIGH
uniform mediump sampler2D inputBuffer;
#else
uniform lowp sampler2D inputBuffer;
#endif
#if PASS == 1
uniform vec4 kernel64[32];
#else
uniform vec4 kernel16[8];
#endif
uniform lowp sampler2D cocBuffer;uniform vec2 texelSize;uniform float scale;varying vec2 vUv;void main(){
#ifdef FOREGROUND
vec2 cocNearFar=texture2D(cocBuffer,vUv).rg*scale;float coc=cocNearFar.x;
#else
float coc=texture2D(cocBuffer,vUv).g*scale;
#endif
if(coc==0.0){gl_FragColor=texture2D(inputBuffer,vUv);}else{
#ifdef FOREGROUND
vec2 step=texelSize*max(cocNearFar.x,cocNearFar.y);
#else
vec2 step=texelSize*coc;
#endif
#if PASS == 1
vec4 acc=vec4(0.0);for(int i=0;i<32;++i){vec4 kernel=kernel64[i];vec2 uv=step*kernel.xy+vUv;acc+=texture2D(inputBuffer,uv);uv=step*kernel.zw+vUv;acc+=texture2D(inputBuffer,uv);}gl_FragColor=acc/64.0;
#else
vec4 maxValue=texture2D(inputBuffer,vUv);for(int i=0;i<8;++i){vec4 kernel=kernel16[i];vec2 uv=step*kernel.xy+vUv;maxValue=max(texture2D(inputBuffer,uv),maxValue);uv=step*kernel.zw+vUv;maxValue=max(texture2D(inputBuffer,uv),maxValue);}gl_FragColor=maxValue;
#endif
}}`,X=(i.BKk,`#include <common>
#include <packing>
#ifdef GL_FRAGMENT_PRECISION_HIGH
uniform highp sampler2D depthBuffer;
#else
uniform mediump sampler2D depthBuffer;
#endif
uniform mat4 projectionMatrix;uniform mat4 projectionMatrixInverse;uniform float cameraNear;uniform float cameraFar;uniform float focusDistance;uniform float focusRange;varying vec2 vUv;float readDepth(const in vec2 uv){
#if DEPTH_PACKING == 3201
float depth=unpackRGBAToDepth(texture2D(depthBuffer,uv));
#else
float depth=texture2D(depthBuffer,uv).r;
#endif
#if defined(USE_LOGARITHMIC_DEPTH_BUFFER) || defined(LOG_DEPTH)
float d=pow(2.0,depth*log2(cameraFar+1.0))-1.0;float a=cameraFar/(cameraFar-cameraNear);float b=cameraFar*cameraNear/(cameraNear-cameraFar);depth=a+b/d;
#elif defined(USE_REVERSED_DEPTH_BUFFER)
depth=1.0-depth;
#endif
return depth;}
#ifdef PERSPECTIVE_CAMERA
#define getViewZ(depth) perspectiveDepthToViewZ(depth, cameraNear, cameraFar)
#else
#define getViewZ(depth) orthographicDepthToViewZ(depth, cameraNear, cameraFar)
#endif
vec3 getViewPosition(const in vec2 screenPosition,const in float depth,const in float viewZ){vec4 clipPosition=vec4(vec3(screenPosition,depth)*2.0-1.0,1.0);float clipW=projectionMatrix[2][3]*viewZ+projectionMatrix[3][3];clipPosition*=clipW;return(projectionMatrixInverse*clipPosition).xyz;}vec3 getViewPosition(const in vec2 screenPosition,const in float depth){return getViewPosition(screenPosition,depth,getViewZ(depth));}
#define getDistance(viewPosition) length(viewPosition)
void main(){float depth=readDepth(vUv);vec3 viewPosition=getViewPosition(vUv,depth);float distance=getDistance(viewPosition);float signedDistance=distance-focusDistance;float magnitude=smoothstep(0.0,focusRange,abs(signedDistance));gl_FragColor.rg=magnitude*vec2(step(signedDistance,0.0),step(0.0,signedDistance));}`),$=(i.BKk,`#ifdef FRAMEBUFFER_PRECISION_HIGH
uniform mediump sampler2D inputBuffer;
#else
uniform lowp sampler2D inputBuffer;
#endif
#ifdef MASK_PRECISION_HIGH
uniform mediump sampler2D maskTexture;
#else
uniform lowp sampler2D maskTexture;
#endif
#if MASK_FUNCTION != 0
uniform float strength;
#endif
varying vec2 vUv;void main(){
#if COLOR_CHANNEL == 0
float mask=texture2D(maskTexture,vUv).r;
#elif COLOR_CHANNEL == 1
float mask=texture2D(maskTexture,vUv).g;
#elif COLOR_CHANNEL == 2
float mask=texture2D(maskTexture,vUv).b;
#else
float mask=texture2D(maskTexture,vUv).a;
#endif
#if MASK_FUNCTION == 0
#ifdef INVERTED
mask=(mask>0.0)?0.0:1.0;
#else
mask=(mask>0.0)?1.0:0.0;
#endif
#else
mask=clamp(mask*strength,0.0,1.0);
#ifdef INVERTED
mask=1.0-mask;
#endif
#endif
#if MASK_FUNCTION == 3
vec4 texel=texture2D(inputBuffer,vUv);gl_FragColor=vec4(mask*texel.rgb,texel.a);
#elif MASK_FUNCTION == 2
gl_FragColor=vec4(mask*texture2D(inputBuffer,vUv).rgb,mask);
#else
gl_FragColor=mask*texture2D(inputBuffer,vUv);
#endif
}`);i.BKk,i.GYF;var Y=`#include <common>
#include <dithering_pars_fragment>
#ifdef FRAMEBUFFER_PRECISION_HIGH
uniform mediump sampler2D inputBuffer;
#else
uniform lowp sampler2D inputBuffer;
#endif
uniform vec2 lightPosition;uniform float exposure;uniform float decay;uniform float density;uniform float weight;uniform float clampMax;varying vec2 vUv;void main(){vec2 coord=vUv;vec2 delta=lightPosition-coord;delta*=1.0/SAMPLES_FLOAT*density;float illuminationDecay=1.0;vec4 color=vec4(0.0);for(int i=0;i<SAMPLES_INT;++i){coord+=delta;vec4 texel=texture2D(inputBuffer,coord);texel*=illuminationDecay*weight;color+=texel;illuminationDecay*=decay;}gl_FragColor=clamp(color*exposure,0.0,clampMax);
#include <dithering_fragment>
}`,j=(i.BKk,class extends a{constructor(e,t,r=null){super("RenderPass",e,t),this.needsSwap=!1,this.needsDepthBlit=!0,this.clearPass=new d,this.overrideMaterialManager=null===r?null:new S(r),this.ignoreBackground=!1,this.skipShadowMapUpdate=!1,this.selection=null}set mainScene(e){this.scene=e}set mainCamera(e){this.camera=e}get renderToScreen(){return super.renderToScreen}set renderToScreen(e){super.renderToScreen=e,this.clearPass.renderToScreen=e}get overrideMaterial(){let e=this.overrideMaterialManager;return null!==e?e.material:null}set overrideMaterial(e){let t=this.overrideMaterialManager;null!==e?null!==t?t.setMaterial(e):this.overrideMaterialManager=new S(e):null!==t&&(t.dispose(),this.overrideMaterialManager=null)}getOverrideMaterial(){return this.overrideMaterial}setOverrideMaterial(e){this.overrideMaterial=e}get clear(){return this.clearPass.enabled}set clear(e){this.clearPass.enabled=e}getSelection(){return this.selection}setSelection(e){this.selection=e}isBackgroundDisabled(){return this.ignoreBackground}setBackgroundDisabled(e){this.ignoreBackground=e}isShadowMapDisabled(){return this.skipShadowMapUpdate}setShadowMapDisabled(e){this.skipShadowMapUpdate=e}getClearPass(){return this.clearPass}render(e,t,r,i,s){let a=this.scene,n=this.camera,o=this.selection,l=n.layers.mask,c=a.background,u=e.shadowMap.autoUpdate,f=this.renderToScreen?null:t;null!==o&&n.layers.set(o.getLayer()),this.skipShadowMapUpdate&&(e.shadowMap.autoUpdate=!1),(this.ignoreBackground||null!==this.clearPass.overrideClearColor)&&(a.background=null),this.clearPass.enabled&&this.clearPass.render(e,t),e.setRenderTarget(f),null!==this.overrideMaterialManager?this.overrideMaterialManager.render(e,a,n):e.render(a,n),n.layers.mask=l,a.background=c,e.shadowMap.autoUpdate=u}}),Q={SCALE_UP:"lut.scaleup"};function q(e,t,r){let i=document.createElement("canvas"),s=i.getContext("2d");if(i.width=e,i.height=t,r instanceof Image)s.drawImage(r,0,0);else{let i=s.createImageData(e,t);i.data.set(r),s.putImageData(i,0,0)}return i}var J=class e{constructor(e=0,t=0,r=null){this.width=e,this.height=t,this.data=r}toCanvas(){return"undefined"==typeof document?null:q(this.width,this.height,this.data)}static from(t){let r,{width:i,height:s}=t;if(t instanceof Image){let e=q(i,s,t);null!==e&&(r=e.getContext("2d").getImageData(0,0,i,s).data)}else r=t.data;return new e(i,s,r)}},ee=new i.Q1f,et=(i.dYF,{FULL:0}),er={KEEP_MAX_DEPTH:1,DISCARD_MAX_DEPTH:2},ei={COLOR:2},es=`void mainImage(const in vec4 inputColor,const in vec2 uv,out vec4 outputColor){vec3 noise=vec3(rand(uv*(1.0+time)));
#ifdef PREMULTIPLY
outputColor=vec4(min(inputColor.rgb*noise,vec3(1.0)),inputColor.a);
#else
outputColor=vec4(noise,inputColor.a);
#endif
}`,ea=class extends w{constructor({blendFunction:e=y.SCREEN,premultiply:t=!1}={}){super("NoiseEffect",es,{blendFunction:e}),this.premultiply=t}get premultiply(){return this.defines.has("PREMULTIPLY")}set premultiply(e){this.premultiply!==e&&(e?this.defines.set("PREMULTIPLY","1"):this.defines.delete("PREMULTIPLY"),this.setChanged())}isPremultiplied(){return this.premultiply}setPremultiplied(e){this.premultiply=e}},en=`#include <packing>
#include <clipping_planes_pars_fragment>
#ifdef GL_FRAGMENT_PRECISION_HIGH
uniform highp sampler2D depthBuffer;
#else
uniform mediump sampler2D depthBuffer;
#endif
uniform float cameraNear;uniform float cameraFar;centroid varying float vViewZ;centroid varying vec4 vProjTexCoord;void main(){
#include <clipping_planes_fragment>
vec2 projTexCoord=(vProjTexCoord.xy/vProjTexCoord.w)*0.5+0.5;
#if DEPTH_PACKING == 3201
float depth=unpackRGBAToDepth(texture2D(depthBuffer,projTexCoord));
#else
float depth=texture2D(depthBuffer,projTexCoord).r;
#endif
#if defined(USE_LOGARITHMIC_DEPTH_BUFFER) || defined(LOG_DEPTH)
float d=pow(2.0,depth*log2(cameraFar+1.0))-1.0;float a=cameraFar/(cameraFar-cameraNear);float b=cameraFar*cameraNear/(cameraNear-cameraFar);depth=a+b/d;
#elif defined(USE_REVERSED_DEPTH_BUFFER)
depth=1.0-depth;
#endif
#ifdef PERSPECTIVE_CAMERA
float viewZ=perspectiveDepthToViewZ(depth,cameraNear,cameraFar);
#else
float viewZ=orthographicDepthToViewZ(depth,cameraNear,cameraFar);
#endif
float depthTest=(-vViewZ>-viewZ)?1.0:0.0;gl_FragColor.rg=vec2(0.0,depthTest);}`,eo=`#include <common>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <clipping_planes_pars_vertex>
varying float vViewZ;varying vec4 vProjTexCoord;void main(){
#include <skinbase_vertex>
#include <begin_vertex>
#include <morphtarget_vertex>
#include <skinning_vertex>
#include <project_vertex>
vViewZ=mvPosition.z;vProjTexCoord=gl_Position;
#include <clipping_planes_vertex>
}`,el=(i.BKk,i.BKk,`uniform float count;
#ifdef SCROLL
uniform float scrollSpeed;
#endif
void mainImage(const in vec4 inputColor,const in vec2 uv,out vec4 outputColor){float y=uv.y;
#ifdef SCROLL
y+=time*scrollSpeed;
#endif
vec2 sl=vec2(sin(y*count),cos(y*count));outputColor=vec4(sl.xyx,inputColor.a);}`),ec=class extends w{constructor({blendFunction:e=y.OVERLAY,density:t=1.25,scrollSpeed:r=0}={}){super("ScanlineEffect",el,{blendFunction:e,uniforms:new Map([["count",new i.nc$(0)],["scrollSpeed",new i.nc$(0)]])}),this.resolution=new i.I9Y,this.d=t,this.scrollSpeed=r}get density(){return this.d}set density(e){this.d=e,this.setSize(this.resolution.width,this.resolution.height)}getDensity(){return this.density}setDensity(e){this.density=e}get scrollSpeed(){return this.uniforms.get("scrollSpeed").value}set scrollSpeed(e){this.uniforms.get("scrollSpeed").value=e,0===e?this.defines.delete("SCROLL")&&this.setChanged():this.defines.has("SCROLL")||(this.defines.set("SCROLL","1"),this.setChanged())}setSize(e,t){this.resolution.set(e,t),this.uniforms.get("count").value=Math.round(t*this.density)}},eu=`#include <common>
#include <packing>
#ifdef GL_FRAGMENT_PRECISION_HIGH
uniform highp sampler2D depthBuffer0;uniform highp sampler2D depthBuffer1;
#else
uniform mediump sampler2D depthBuffer0;uniform mediump sampler2D depthBuffer1;
#endif
uniform sampler2D inputBuffer;uniform vec2 cameraNearFar;float getViewZ(const in float depth){
#ifdef PERSPECTIVE_CAMERA
return perspectiveDepthToViewZ(depth,cameraNearFar.x,cameraNearFar.y);
#else
return orthographicDepthToViewZ(depth,cameraNearFar.x,cameraNearFar.y);
#endif
}varying vec2 vUv;void main(){vec2 depth;
#if DEPTH_PACKING_0 == 3201
depth.x=unpackRGBAToDepth(texture2D(depthBuffer0,vUv));
#else
depth.x=texture2D(depthBuffer0,vUv).r;
#endif
#if DEPTH_PACKING_1 == 3201
depth.y=unpackRGBAToDepth(texture2D(depthBuffer1,vUv));
#else
depth.y=texture2D(depthBuffer1,vUv).r;
#endif
#if defined(USE_LOGARITHMIC_DEPTH_BUFFER) || defined(LOG_DEPTH)
float a=cameraNearFar.y/(cameraNearFar.y-cameraNearFar.x);float b=cameraNearFar.y*cameraNearFar.x/(cameraNearFar.x-cameraNearFar.y);float c=log2(cameraNearFar.y+1.0);float d=pow(2.0,depth.x*c)-1.0;depth.x=a+b/d;d=pow(2.0,depth.y*c)-1.0;depth.y=a+b/d;
#elif defined(USE_REVERSED_DEPTH_BUFFER)
depth.x=1.0-depth.x;depth.y=1.0-depth.y;
#endif
bool isMaxDepth=(depth.x==1.0);
#ifdef PERSPECTIVE_CAMERA
depth.x=viewZToOrthographicDepth(getViewZ(depth.x),cameraNearFar.x,cameraNearFar.y);depth.y=viewZToOrthographicDepth(getViewZ(depth.y),cameraNearFar.x,cameraNearFar.y);
#endif
#if DEPTH_TEST_STRATEGY == 0
bool keep=depthTest(depth.x,depth.y);
#elif DEPTH_TEST_STRATEGY == 1
bool keep=isMaxDepth||depthTest(depth.x,depth.y);
#else
bool keep=!isMaxDepth&&depthTest(depth.x,depth.y);
#endif
if(keep){gl_FragColor=texture2D(inputBuffer,vUv);}else{discard;}}`,ef=(i.BKk,`varying vec2 vUv;varying vec2 vUv0;varying vec2 vUv1;
#if EDGE_DETECTION_MODE != 0
varying vec2 vUv2;varying vec2 vUv3;varying vec2 vUv4;varying vec2 vUv5;
#endif
#if EDGE_DETECTION_MODE == 1
#include <common>
#endif
#if EDGE_DETECTION_MODE == 0 || PREDICATION_MODE == 1
#ifdef GL_FRAGMENT_PRECISION_HIGH
uniform highp sampler2D depthBuffer;
#else
uniform mediump sampler2D depthBuffer;
#endif
float readDepth(const in vec2 uv){
#if DEPTH_PACKING == 3201
return unpackRGBAToDepth(texture2D(depthBuffer,uv));
#else
return texture2D(depthBuffer,uv).r;
#endif
}vec3 gatherNeighbors(){float p=readDepth(vUv);float pLeft=readDepth(vUv0);float pTop=readDepth(vUv1);return vec3(p,pLeft,pTop);}
#elif PREDICATION_MODE == 2
uniform sampler2D predicationBuffer;vec3 gatherNeighbors(){float p=texture2D(predicationBuffer,vUv).r;float pLeft=texture2D(predicationBuffer,vUv0).r;float pTop=texture2D(predicationBuffer,vUv1).r;return vec3(p,pLeft,pTop);}
#endif
#if PREDICATION_MODE != 0
vec2 calculatePredicatedThreshold(){vec3 neighbours=gatherNeighbors();vec2 delta=abs(neighbours.xx-neighbours.yz);vec2 edges=step(PREDICATION_THRESHOLD,delta);return PREDICATION_SCALE*EDGE_THRESHOLD*(1.0-PREDICATION_STRENGTH*edges);}
#endif
#if EDGE_DETECTION_MODE != 0
uniform sampler2D inputBuffer;
#endif
void main(){
#if EDGE_DETECTION_MODE == 0
const vec2 threshold=vec2(DEPTH_THRESHOLD);
#elif PREDICATION_MODE != 0
vec2 threshold=calculatePredicatedThreshold();
#else
const vec2 threshold=vec2(EDGE_THRESHOLD);
#endif
#if EDGE_DETECTION_MODE == 0
vec3 neighbors=gatherNeighbors();vec2 delta=abs(neighbors.xx-vec2(neighbors.y,neighbors.z));vec2 edges=step(threshold,delta);if(dot(edges,vec2(1.0))==0.0){discard;}gl_FragColor=vec4(edges,0.0,1.0);
#elif EDGE_DETECTION_MODE == 1
float l=luminance(texture2D(inputBuffer,vUv).rgb);float lLeft=luminance(texture2D(inputBuffer,vUv0).rgb);float lTop=luminance(texture2D(inputBuffer,vUv1).rgb);vec4 delta;delta.xy=abs(l-vec2(lLeft,lTop));vec2 edges=step(threshold,delta.xy);if(dot(edges,vec2(1.0))==0.0){discard;}float lRight=luminance(texture2D(inputBuffer,vUv2).rgb);float lBottom=luminance(texture2D(inputBuffer,vUv3).rgb);delta.zw=abs(l-vec2(lRight,lBottom));vec2 maxDelta=max(delta.xy,delta.zw);float lLeftLeft=luminance(texture2D(inputBuffer,vUv4).rgb);float lTopTop=luminance(texture2D(inputBuffer,vUv5).rgb);delta.zw=abs(vec2(lLeft,lTop)-vec2(lLeftLeft,lTopTop));maxDelta=max(maxDelta.xy,delta.zw);float finalDelta=max(maxDelta.x,maxDelta.y);edges.xy*=step(finalDelta,LOCAL_CONTRAST_ADAPTATION_FACTOR*delta.xy);gl_FragColor=vec4(edges,0.0,1.0);
#elif EDGE_DETECTION_MODE == 2
vec4 delta;vec3 c=texture2D(inputBuffer,vUv).rgb;vec3 cLeft=texture2D(inputBuffer,vUv0).rgb;vec3 t=abs(c-cLeft);delta.x=max(max(t.r,t.g),t.b);vec3 cTop=texture2D(inputBuffer,vUv1).rgb;t=abs(c-cTop);delta.y=max(max(t.r,t.g),t.b);vec2 edges=step(threshold,delta.xy);if(dot(edges,vec2(1.0))==0.0){discard;}vec3 cRight=texture2D(inputBuffer,vUv2).rgb;t=abs(c-cRight);delta.z=max(max(t.r,t.g),t.b);vec3 cBottom=texture2D(inputBuffer,vUv3).rgb;t=abs(c-cBottom);delta.w=max(max(t.r,t.g),t.b);vec2 maxDelta=max(delta.xy,delta.zw);vec3 cLeftLeft=texture2D(inputBuffer,vUv4).rgb;t=abs(c-cLeftLeft);delta.z=max(max(t.r,t.g),t.b);vec3 cTopTop=texture2D(inputBuffer,vUv5).rgb;t=abs(c-cTopTop);delta.w=max(max(t.r,t.g),t.b);maxDelta=max(maxDelta.xy,delta.zw);float finalDelta=max(maxDelta.x,maxDelta.y);edges*=step(finalDelta,LOCAL_CONTRAST_ADAPTATION_FACTOR*delta.xy);gl_FragColor=vec4(edges,0.0,1.0);
#endif
}`),ed=`uniform vec2 texelSize;varying vec2 vUv;varying vec2 vUv0;varying vec2 vUv1;
#if EDGE_DETECTION_MODE != 0
varying vec2 vUv2;varying vec2 vUv3;varying vec2 vUv4;varying vec2 vUv5;
#endif
void main(){vUv=position.xy*0.5+0.5;vUv0=vUv+texelSize*vec2(-1.0,0.0);vUv1=vUv+texelSize*vec2(0.0,-1.0);
#if EDGE_DETECTION_MODE != 0
vUv2=vUv+texelSize*vec2(1.0,0.0);vUv3=vUv+texelSize*vec2(0.0,1.0);vUv4=vUv+texelSize*vec2(-2.0,0.0);vUv5=vUv+texelSize*vec2(0.0,-2.0);
#endif
gl_Position=vec4(position.xy,1.0,1.0);}`,ev=(i.BKk,`#define sampleLevelZeroOffset(t, coord, offset) texture2D(t, coord + offset * texelSize)
#if __VERSION__ < 300
#define round(v) floor(v + 0.5)
#endif
#ifdef FRAMEBUFFER_PRECISION_HIGH
uniform mediump sampler2D inputBuffer;
#else
uniform lowp sampler2D inputBuffer;
#endif
uniform lowp sampler2D areaTexture;uniform lowp sampler2D searchTexture;uniform vec2 texelSize;uniform vec2 resolution;varying vec2 vUv;varying vec4 vOffset[3];varying vec2 vPixCoord;void movec(const in bvec2 c,inout vec2 variable,const in vec2 value){if(c.x){variable.x=value.x;}if(c.y){variable.y=value.y;}}void movec(const in bvec4 c,inout vec4 variable,const in vec4 value){movec(c.xy,variable.xy,value.xy);movec(c.zw,variable.zw,value.zw);}vec2 decodeDiagBilinearAccess(in vec2 e){e.r=e.r*abs(5.0*e.r-5.0*0.75);return round(e);}vec4 decodeDiagBilinearAccess(in vec4 e){e.rb=e.rb*abs(5.0*e.rb-5.0*0.75);return round(e);}vec2 searchDiag1(const in vec2 texCoord,const in vec2 dir,out vec2 e){vec4 coord=vec4(texCoord,-1.0,1.0);vec3 t=vec3(texelSize,1.0);for(int i=0;i<MAX_SEARCH_STEPS_INT;++i){if(!(coord.z<float(MAX_SEARCH_STEPS_DIAG_INT-1)&&coord.w>0.9)){break;}coord.xyz=t*vec3(dir,1.0)+coord.xyz;e=texture2D(inputBuffer,coord.xy).rg;coord.w=dot(e,vec2(0.5));}return coord.zw;}vec2 searchDiag2(const in vec2 texCoord,const in vec2 dir,out vec2 e){vec4 coord=vec4(texCoord,-1.0,1.0);coord.x+=0.25*texelSize.x;vec3 t=vec3(texelSize,1.0);for(int i=0;i<MAX_SEARCH_STEPS_INT;++i){if(!(coord.z<float(MAX_SEARCH_STEPS_DIAG_INT-1)&&coord.w>0.9)){break;}coord.xyz=t*vec3(dir,1.0)+coord.xyz;e=texture2D(inputBuffer,coord.xy).rg;e=decodeDiagBilinearAccess(e);coord.w=dot(e,vec2(0.5));}return coord.zw;}vec2 areaDiag(const in vec2 dist,const in vec2 e,const in float offset){vec2 texCoord=vec2(AREATEX_MAX_DISTANCE_DIAG,AREATEX_MAX_DISTANCE_DIAG)*e+dist;texCoord=AREATEX_PIXEL_SIZE*texCoord+0.5*AREATEX_PIXEL_SIZE;texCoord.x+=0.5;texCoord.y+=AREATEX_SUBTEX_SIZE*offset;return texture2D(areaTexture,texCoord).rg;}vec2 calculateDiagWeights(const in vec2 texCoord,const in vec2 e,const in vec4 subsampleIndices){vec2 weights=vec2(0.0);vec4 d;vec2 end;if(e.r>0.0){d.xz=searchDiag1(texCoord,vec2(-1.0,1.0),end);d.x+=float(end.y>0.9);}else{d.xz=vec2(0.0);}d.yw=searchDiag1(texCoord,vec2(1.0,-1.0),end);if(d.x+d.y>2.0){vec4 coords=vec4(-d.x+0.25,d.x,d.y,-d.y-0.25)*texelSize.xyxy+texCoord.xyxy;vec4 c;c.xy=sampleLevelZeroOffset(inputBuffer,coords.xy,vec2(-1,0)).rg;c.zw=sampleLevelZeroOffset(inputBuffer,coords.zw,vec2(1,0)).rg;c.yxwz=decodeDiagBilinearAccess(c.xyzw);vec2 cc=vec2(2.0)*c.xz+c.yw;movec(bvec2(step(0.9,d.zw)),cc,vec2(0.0));weights+=areaDiag(d.xy,cc,subsampleIndices.z);}d.xz=searchDiag2(texCoord,vec2(-1.0,-1.0),end);if(sampleLevelZeroOffset(inputBuffer,texCoord,vec2(1,0)).r>0.0){d.yw=searchDiag2(texCoord,vec2(1.0),end);d.y+=float(end.y>0.9);}else{d.yw=vec2(0.0);}if(d.x+d.y>2.0){vec4 coords=vec4(-d.x,-d.x,d.y,d.y)*texelSize.xyxy+texCoord.xyxy;vec4 c;c.x=sampleLevelZeroOffset(inputBuffer,coords.xy,vec2(-1,0)).g;c.y=sampleLevelZeroOffset(inputBuffer,coords.xy,vec2(0,-1)).r;c.zw=sampleLevelZeroOffset(inputBuffer,coords.zw,vec2(1,0)).gr;vec2 cc=vec2(2.0)*c.xz+c.yw;movec(bvec2(step(0.9,d.zw)),cc,vec2(0.0));weights+=areaDiag(d.xy,cc,subsampleIndices.w).gr;}return weights;}float searchLength(const in vec2 e,const in float offset){vec2 scale=SEARCHTEX_SIZE*vec2(0.5,-1.0);vec2 bias=SEARCHTEX_SIZE*vec2(offset,1.0);scale+=vec2(-1.0,1.0);bias+=vec2(0.5,-0.5);scale*=1.0/SEARCHTEX_PACKED_SIZE;bias*=1.0/SEARCHTEX_PACKED_SIZE;return texture2D(searchTexture,scale*e+bias).r;}float searchXLeft(in vec2 texCoord,const in float end){vec2 e=vec2(0.0,1.0);for(int i=0;i<MAX_SEARCH_STEPS_INT;++i){if(!(texCoord.x>end&&e.g>0.8281&&e.r==0.0)){break;}e=texture2D(inputBuffer,texCoord).rg;texCoord=vec2(-2.0,0.0)*texelSize+texCoord;}float offset=-(255.0/127.0)*searchLength(e,0.0)+3.25;return texelSize.x*offset+texCoord.x;}float searchXRight(vec2 texCoord,const in float end){vec2 e=vec2(0.0,1.0);for(int i=0;i<MAX_SEARCH_STEPS_INT;++i){if(!(texCoord.x<end&&e.g>0.8281&&e.r==0.0)){break;}e=texture2D(inputBuffer,texCoord).rg;texCoord=vec2(2.0,0.0)*texelSize.xy+texCoord;}float offset=-(255.0/127.0)*searchLength(e,0.5)+3.25;return-texelSize.x*offset+texCoord.x;}float searchYUp(vec2 texCoord,const in float end){vec2 e=vec2(1.0,0.0);for(int i=0;i<MAX_SEARCH_STEPS_INT;++i){if(!(texCoord.y>end&&e.r>0.8281&&e.g==0.0)){break;}e=texture2D(inputBuffer,texCoord).rg;texCoord=-vec2(0.0,2.0)*texelSize.xy+texCoord;}float offset=-(255.0/127.0)*searchLength(e.gr,0.0)+3.25;return texelSize.y*offset+texCoord.y;}float searchYDown(vec2 texCoord,const in float end){vec2 e=vec2(1.0,0.0);for(int i=0;i<MAX_SEARCH_STEPS_INT;i++){if(!(texCoord.y<end&&e.r>0.8281&&e.g==0.0)){break;}e=texture2D(inputBuffer,texCoord).rg;texCoord=vec2(0.0,2.0)*texelSize.xy+texCoord;}float offset=-(255.0/127.0)*searchLength(e.gr,0.5)+3.25;return-texelSize.y*offset+texCoord.y;}vec2 area(const in vec2 dist,const in float e1,const in float e2,const in float offset){vec2 texCoord=vec2(AREATEX_MAX_DISTANCE)*round(4.0*vec2(e1,e2))+dist;texCoord=AREATEX_PIXEL_SIZE*texCoord+0.5*AREATEX_PIXEL_SIZE;texCoord.y=AREATEX_SUBTEX_SIZE*offset+texCoord.y;return texture2D(areaTexture,texCoord).rg;}void detectHorizontalCornerPattern(inout vec2 weights,const in vec4 texCoord,const in vec2 d){
#if !defined(DISABLE_CORNER_DETECTION)
vec2 leftRight=step(d.xy,d.yx);vec2 rounding=(1.0-CORNER_ROUNDING_NORM)*leftRight;rounding/=leftRight.x+leftRight.y;vec2 factor=vec2(1.0);factor.x-=rounding.x*sampleLevelZeroOffset(inputBuffer,texCoord.xy,vec2(0,1)).r;factor.x-=rounding.y*sampleLevelZeroOffset(inputBuffer,texCoord.zw,vec2(1,1)).r;factor.y-=rounding.x*sampleLevelZeroOffset(inputBuffer,texCoord.xy,vec2(0,-2)).r;factor.y-=rounding.y*sampleLevelZeroOffset(inputBuffer,texCoord.zw,vec2(1,-2)).r;weights*=clamp(factor,0.0,1.0);
#endif
}void detectVerticalCornerPattern(inout vec2 weights,const in vec4 texCoord,const in vec2 d){
#if !defined(DISABLE_CORNER_DETECTION)
vec2 leftRight=step(d.xy,d.yx);vec2 rounding=(1.0-CORNER_ROUNDING_NORM)*leftRight;rounding/=leftRight.x+leftRight.y;vec2 factor=vec2(1.0);factor.x-=rounding.x*sampleLevelZeroOffset(inputBuffer,texCoord.xy,vec2(1,0)).g;factor.x-=rounding.y*sampleLevelZeroOffset(inputBuffer,texCoord.zw,vec2(1,1)).g;factor.y-=rounding.x*sampleLevelZeroOffset(inputBuffer,texCoord.xy,vec2(-2,0)).g;factor.y-=rounding.y*sampleLevelZeroOffset(inputBuffer,texCoord.zw,vec2(-2,1)).g;weights*=clamp(factor,0.0,1.0);
#endif
}void main(){vec4 weights=vec4(0.0);vec4 subsampleIndices=vec4(0.0);vec2 e=texture2D(inputBuffer,vUv).rg;if(e.g>0.0){
#if !defined(DISABLE_DIAG_DETECTION)
weights.rg=calculateDiagWeights(vUv,e,subsampleIndices);if(weights.r==-weights.g){
#endif
vec2 d;vec3 coords;coords.x=searchXLeft(vOffset[0].xy,vOffset[2].x);coords.y=vOffset[1].y;d.x=coords.x;float e1=texture2D(inputBuffer,coords.xy).r;coords.z=searchXRight(vOffset[0].zw,vOffset[2].y);d.y=coords.z;d=round(resolution.xx*d+-vPixCoord.xx);vec2 sqrtD=sqrt(abs(d));float e2=sampleLevelZeroOffset(inputBuffer,coords.zy,vec2(1,0)).r;weights.rg=area(sqrtD,e1,e2,subsampleIndices.y);coords.y=vUv.y;detectHorizontalCornerPattern(weights.rg,coords.xyzy,d);
#if !defined(DISABLE_DIAG_DETECTION)
}else{e.r=0.0;}
#endif
}if(e.r>0.0){vec2 d;vec3 coords;coords.y=searchYUp(vOffset[1].xy,vOffset[2].z);coords.x=vOffset[0].x;d.x=coords.y;float e1=texture2D(inputBuffer,coords.xy).g;coords.z=searchYDown(vOffset[1].zw,vOffset[2].w);d.y=coords.z;d=round(resolution.yy*d-vPixCoord.yy);vec2 sqrtD=sqrt(abs(d));float e2=sampleLevelZeroOffset(inputBuffer,coords.xz,vec2(0,1)).g;weights.ba=area(sqrtD,e1,e2,subsampleIndices.x);coords.x=vUv.x;detectVerticalCornerPattern(weights.ba,coords.xyxz,d);}gl_FragColor=weights;}`);i.BKk;function eh(e,t,r){return Math.min(Math.max((e+t)/(t-r),0),1)}var ep=`#include <common>
#include <packing>
uniform vec2 cameraNearFar;
#define cameraNear cameraNearFar.x
#define cameraFar cameraNearFar.y
#ifdef NORMAL_DEPTH
#ifdef GL_FRAGMENT_PRECISION_HIGH
uniform highp sampler2D normalDepthBuffer;
#else
uniform mediump sampler2D normalDepthBuffer;
#endif
float readDepth(const in vec2 uv){float depth=texture2D(normalDepthBuffer,uv).a;
#if defined(USE_LOGARITHMIC_DEPTH_BUFFER) || defined(LOG_DEPTH)
float d=pow(2.0,depth*log2(cameraFar+1.0))-1.0;float a=cameraFar/(cameraFar-cameraNear);float b=cameraFar*cameraNear/(cameraNear-cameraFar);depth=a+b/d;
#endif
return depth;}
#else
uniform lowp sampler2D normalBuffer;
#if DEPTH_PACKING == 3201
uniform lowp sampler2D depthBuffer;
#elif defined(GL_FRAGMENT_PRECISION_HIGH)
uniform highp sampler2D depthBuffer;
#else
uniform mediump sampler2D depthBuffer;
#endif
float readDepth(const in vec2 uv){
#if DEPTH_PACKING == 3201
float depth=unpackRGBAToDepth(texture2D(depthBuffer,uv));
#else
float depth=texture2D(depthBuffer,uv).r;
#endif
#if defined(USE_LOGARITHMIC_DEPTH_BUFFER) || defined(LOG_DEPTH)
float d=pow(2.0,depth*log2(cameraFar+1.0))-1.0;float a=cameraFar/(cameraFar-cameraNear);float b=cameraFar*cameraNear/(cameraNear-cameraFar);depth=a+b/d;
#endif
return depth;}
#endif
uniform lowp sampler2D noiseTexture;uniform mat4 inverseProjectionMatrix;uniform mat4 projectionMatrix;uniform vec2 texelSize;uniform float intensity;uniform float minRadiusScale;uniform float fade;uniform float bias;uniform vec2 distanceCutoff;uniform vec2 proximityCutoff;varying vec2 vUv;varying vec2 vUv2;float getViewZ(const in float depth){
#ifdef PERSPECTIVE_CAMERA
return perspectiveDepthToViewZ(depth,cameraNear,cameraFar);
#else
return orthographicDepthToViewZ(depth,cameraNear,cameraFar);
#endif
}vec3 getViewPosition(const in vec2 screenPosition,const in float depth,const in float viewZ){vec4 clipPosition=vec4(vec3(screenPosition,depth)*2.0-1.0,1.0);float clipW=projectionMatrix[2][3]*viewZ+projectionMatrix[3][3];clipPosition*=clipW;return(inverseProjectionMatrix*clipPosition).xyz;}float getAmbientOcclusion(const in vec3 p,const in vec3 n,const in float depth,const in vec2 uv){float radiusScale=1.0-smoothstep(0.0,distanceCutoff.y,depth);radiusScale=radiusScale*(1.0-minRadiusScale)+minRadiusScale;float radius=RADIUS*radiusScale;float noise=texture2D(noiseTexture,vUv2).r;float baseAngle=noise*PI2;float rings=SPIRAL_TURNS*PI2;float occlusion=0.0;int taps=0;for(int i=0;i<SAMPLES_INT;++i){float alpha=(float(i)+0.5)*INV_SAMPLES_FLOAT;float angle=alpha*rings+baseAngle;vec2 rotation=vec2(cos(angle),sin(angle));vec2 coords=alpha*radius*rotation*texelSize+uv;if(coords.s<0.0||coords.s>1.0||coords.t<0.0||coords.t>1.0){continue;}float sampleDepth=readDepth(coords);float viewZ=getViewZ(sampleDepth);
#ifdef PERSPECTIVE_CAMERA
float linearSampleDepth=viewZToOrthographicDepth(viewZ,cameraNear,cameraFar);
#else
float linearSampleDepth=sampleDepth;
#endif
float proximity=abs(depth-linearSampleDepth);if(proximity<proximityCutoff.y){float falloff=1.0-smoothstep(proximityCutoff.x,proximityCutoff.y,proximity);vec3 Q=getViewPosition(coords,sampleDepth,viewZ);vec3 v=Q-p;float vv=dot(v,v);float vn=dot(v,n)-bias;float f=max(RADIUS_SQ-vv,0.0)/RADIUS_SQ;occlusion+=(f*f*f*max(vn/(fade+vv),0.0))*falloff;}++taps;}return occlusion/(4.0*max(float(taps),1.0));}void main(){
#ifdef NORMAL_DEPTH
vec4 normalDepth=texture2D(normalDepthBuffer,vUv);
#if defined(USE_LOGARITHMIC_DEPTH_BUFFER) || defined(LOG_DEPTH)
float d=pow(2.0,normalDepth.a*log2(cameraFar+1.0))-1.0;float a=cameraFar/(cameraFar-cameraNear);float b=cameraFar*cameraNear/(cameraNear-cameraFar);normalDepth.a=a+b/d;
#endif
#else
vec4 normalDepth=vec4(texture2D(normalBuffer,vUv).xyz,readDepth(vUv));
#endif
float ao=0.0;float depth=normalDepth.a;float viewZ=getViewZ(depth);
#ifdef PERSPECTIVE_CAMERA
float linearDepth=viewZToOrthographicDepth(viewZ,cameraNear,cameraFar);
#else
float linearDepth=depth;
#endif
if(linearDepth<distanceCutoff.y){vec3 viewPosition=getViewPosition(vUv,depth,viewZ);vec3 viewNormal=unpackRGBToNormal(normalDepth.rgb);ao+=getAmbientOcclusion(viewPosition,viewNormal,linearDepth,vUv);float d=smoothstep(distanceCutoff.x,distanceCutoff.y,linearDepth);ao=mix(ao,0.0,d);
#ifdef LEGACY_INTENSITY
ao=clamp(1.0-pow(1.0-ao,abs(intensity)),0.0,1.0);
#endif
}gl_FragColor.r=ao;}`,em=(i.BKk,`#include <packing>
#ifdef GL_FRAGMENT_PRECISION_HIGH
uniform highp sampler2D depthBuffer;
#else
uniform mediump sampler2D depthBuffer;
#endif
#ifdef DOWNSAMPLE_NORMALS
uniform lowp sampler2D normalBuffer;
#endif
varying vec2 vUv0;varying vec2 vUv1;varying vec2 vUv2;varying vec2 vUv3;float readDepth(const in vec2 uv){
#if DEPTH_PACKING == 3201
return unpackRGBAToDepth(texture2D(depthBuffer,uv));
#else
return texture2D(depthBuffer,uv).r;
#endif
}int findBestDepth(const in float samples[4]){float c=(samples[0]+samples[1]+samples[2]+samples[3])*0.25;float distances[4];distances[0]=abs(c-samples[0]);distances[1]=abs(c-samples[1]);distances[2]=abs(c-samples[2]);distances[3]=abs(c-samples[3]);float maxDistance=max(max(distances[0],distances[1]),max(distances[2],distances[3]));int remaining[3];int rejected[3];int i,j,k;for(i=0,j=0,k=0;i<4;++i){if(distances[i]<maxDistance){remaining[j++]=i;}else{rejected[k++]=i;}}for(;j<3;++j){remaining[j]=rejected[--k];}vec3 s=vec3(samples[remaining[0]],samples[remaining[1]],samples[remaining[2]]);c=(s.x+s.y+s.z)/3.0;distances[0]=abs(c-s.x);distances[1]=abs(c-s.y);distances[2]=abs(c-s.z);float minDistance=min(distances[0],min(distances[1],distances[2]));for(i=0;i<3;++i){if(distances[i]==minDistance){break;}}return remaining[i];}void main(){float d[4];d[0]=readDepth(vUv0);d[1]=readDepth(vUv1);d[2]=readDepth(vUv2);d[3]=readDepth(vUv3);int index=findBestDepth(d);
#ifdef DOWNSAMPLE_NORMALS
vec3 n[4];n[0]=texture2D(normalBuffer,vUv0).rgb;n[1]=texture2D(normalBuffer,vUv1).rgb;n[2]=texture2D(normalBuffer,vUv2).rgb;n[3]=texture2D(normalBuffer,vUv3).rgb;
#else
vec3 n[4];n[0]=vec3(0.0);n[1]=vec3(0.0);n[2]=vec3(0.0);n[3]=vec3(0.0);
#endif
gl_FragColor=vec4(n[index],d[index]);}`),eg=class extends i.BKk{constructor(){super({name:"DepthDownsamplingMaterial",defines:{DEPTH_PACKING:"0"},uniforms:{depthBuffer:new i.nc$(null),normalBuffer:new i.nc$(null),texelSize:new i.nc$(new i.I9Y)},blending:i.XIg,toneMapped:!1,depthWrite:!1,depthTest:!1,fragmentShader:em,vertexShader:"uniform vec2 texelSize;varying vec2 vUv0;varying vec2 vUv1;varying vec2 vUv2;varying vec2 vUv3;void main(){vec2 uv=position.xy*0.5+0.5;vUv0=uv;vUv1=vec2(uv.x,uv.y+texelSize.y);vUv2=vec2(uv.x+texelSize.x,uv.y);vUv3=uv+texelSize;gl_Position=vec4(position.xy,1.0,1.0);}"})}set depthBuffer(e){this.uniforms.depthBuffer.value=e}set depthPacking(e){this.defines.DEPTH_PACKING=e.toFixed(0),this.needsUpdate=!0}setDepthBuffer(e,t=i.Rkk){this.depthBuffer=e,this.depthPacking=t}set normalBuffer(e){this.uniforms.normalBuffer.value=e,null!==e?this.defines.DOWNSAMPLE_NORMALS="1":delete this.defines.DOWNSAMPLE_NORMALS,this.needsUpdate=!0}setNormalBuffer(e){this.normalBuffer=e}setTexelSize(e,t){this.uniforms.texelSize.value.set(e,t)}setSize(e,t){this.uniforms.texelSize.value.set(1/e,1/t)}},ex=class extends a{constructor({normalBuffer:e=null,resolutionScale:t=.5,width:r=D.AUTO_SIZE,height:s=D.AUTO_SIZE,resolutionX:a=r,resolutionY:n=s}={}){super("DepthDownsamplingPass");let o=new eg;o.normalBuffer=e,this.fullscreenMaterial=o,this.needsDepthTexture=!0,this.needsSwap=!1,this.renderTarget=new i.nWS(1,1,{minFilter:i.hxR,magFilter:i.hxR,depthBuffer:!1,type:i.RQf}),this.renderTarget.texture.name="DepthDownsamplingPass.Target",this.renderTarget.texture.generateMipmaps=!1;let l=this.resolution=new D(this,a,n,t);l.addEventListener("change",e=>this.setSize(l.baseWidth,l.baseHeight))}get texture(){return this.renderTarget.texture}getTexture(){return this.renderTarget.texture}getResolution(){return this.resolution}setDepthTexture(e,t=i.Rkk){this.fullscreenMaterial.depthBuffer=e,this.fullscreenMaterial.depthPacking=t}render(e,t,r,i,s){e.setRenderTarget(this.renderToScreen?null:this.renderTarget),e.render(this.scene,this.camera)}setSize(e,t){let r=this.resolution;r.setBaseSize(e,t),this.renderTarget.setSize(r.width,r.height),this.fullscreenMaterial.setSize(e,t)}initialize(e,t,r){let i=e.getContext();if(!(i.getExtension("EXT_color_buffer_float")||i.getExtension("EXT_color_buffer_half_float")))throw Error("Rendering to float texture is not supported.")}},eE=`#ifdef FRAMEBUFFER_PRECISION_HIGH
uniform mediump sampler2D inputBuffer;
#else
uniform lowp sampler2D inputBuffer;
#endif
uniform vec4 maskParams;varying vec2 vUv;varying vec2 vUv2;varying vec2 vOffset;float linearGradientMask(const in float x){return smoothstep(maskParams.x,maskParams.y,x)-smoothstep(maskParams.w,maskParams.z,x);}void main(){vec2 dUv=vOffset*(1.0-linearGradientMask(vUv2.y));vec4 sum=texture2D(inputBuffer,vec2(vUv.x-dUv.x,vUv.y+dUv.y));sum+=texture2D(inputBuffer,vec2(vUv.x+dUv.x,vUv.y+dUv.y));sum+=texture2D(inputBuffer,vec2(vUv.x+dUv.x,vUv.y-dUv.y));sum+=texture2D(inputBuffer,vec2(vUv.x-dUv.x,vUv.y-dUv.y));gl_FragColor=sum*0.25;
#include <colorspace_fragment>
}`,eT=class extends C{constructor({kernelSize:e=B.MEDIUM,offset:t=0,rotation:r=0,focusArea:s=.4,feather:a=.3}={}){super(),this.fragmentShader=eE,this.vertexShader="uniform vec4 texelSize;uniform float kernel;uniform float scale;uniform float aspect;uniform vec2 rotation;varying vec2 vUv;varying vec2 vUv2;varying vec2 vOffset;void main(){vec2 uv=position.xy*0.5+0.5;vUv=uv;vUv2=(uv-0.5)*2.0*vec2(aspect,1.0);vUv2=vec2(dot(rotation,vUv2),dot(rotation,vec2(vUv2.y,-vUv2.x)));vOffset=(texelSize.xy*vec2(kernel)+texelSize.zw)*scale;gl_Position=vec4(position.xy,1.0,1.0);}",this.kernelSize=e,this.uniforms.aspect=new i.nc$(1),this.uniforms.rotation=new i.nc$(new i.I9Y),this.uniforms.maskParams=new i.nc$(new i.IUQ),this._offset=t,this._focusArea=s,this._feather=a,this.rotation=r,this.updateParams()}updateParams(){let e=this.uniforms.maskParams.value,t=Math.max(this.focusArea,0),r=Math.max(t-this.feather,0);e.set(this.offset-t,this.offset-r,this.offset+t,this.offset+r)}get rotation(){return Math.acos(this.uniforms.rotation.value.x)}set rotation(e){this.uniforms.rotation.value.set(Math.cos(e),Math.sin(e))}get offset(){return this._offset}set offset(e){this._offset=e,this.updateParams()}get focusArea(){return this._focusArea}set focusArea(e){this._focusArea=e,this.updateParams()}get feather(){return this._feather}set feather(e){this._feather=e,this.updateParams()}setSize(e,t){super.setSize(e,t),this.uniforms.aspect.value=e/t}},eU=class extends M{constructor({offset:e=0,rotation:t=0,focusArea:r=.4,feather:i=.3,kernelSize:s=B.MEDIUM,resolutionScale:a=.5,resolutionX:n=D.AUTO_SIZE,resolutionY:o=D.AUTO_SIZE}={}){super({kernelSize:s,resolutionScale:a,resolutionX:n,resolutionY:o}),this.blurMaterial=new eT({kernelSize:s,offset:e,rotation:t,focusArea:r,feather:i})}},eS=`#ifdef FRAMEBUFFER_PRECISION_HIGH
uniform mediump sampler2D map;
#else
uniform lowp sampler2D map;
#endif
uniform vec2 maskParams;varying vec2 vUv2;float linearGradientMask(const in float x){return step(maskParams.x,x)-step(maskParams.y,x);}void mainImage(const in vec4 inputColor,const in vec2 uv,out vec4 outputColor){float mask=linearGradientMask(vUv2.y);vec4 texel=texture2D(map,uv);outputColor=mix(texel,inputColor,mask);}`,eD=class extends w{constructor({blendFunction:e,offset:t=0,rotation:r=0,focusArea:s=.4,feather:a=.3,kernelSize:n=B.MEDIUM,resolutionScale:o=.5,resolutionX:l=D.AUTO_SIZE,resolutionY:c=D.AUTO_SIZE}={}){super("TiltShiftEffect",eS,{vertexShader:"uniform vec2 rotation;varying vec2 vUv2;void mainSupport(const in vec2 uv){vUv2=(uv-0.5)*2.0*vec2(aspect,1.0);vUv2=vec2(dot(rotation,vUv2),dot(rotation,vec2(vUv2.y,-vUv2.x)));}",blendFunction:e,uniforms:new Map([["rotation",new i.nc$(new i.I9Y)],["maskParams",new i.nc$(new i.I9Y)],["map",new i.nc$(null)]])}),this._offset=t,this._focusArea=s,this._feather=a,this.renderTarget=new i.nWS(1,1,{depthBuffer:!1}),this.renderTarget.texture.name="TiltShift.Target",this.uniforms.get("map").value=this.renderTarget.texture,this.blurPass=new eU({kernelSize:n,resolutionScale:o,resolutionX:l,resolutionY:c,offset:t,rotation:r,focusArea:s,feather:a});let u=this.resolution=new D(this,l,c,o);u.addEventListener("change",e=>this.setSize(u.baseWidth,u.baseHeight)),this.rotation=r,this.updateParams()}updateParams(){let e=this.uniforms.get("maskParams").value,t=Math.max(this.focusArea-this.feather,0);e.set(this.offset-t,this.offset+t)}get rotation(){return Math.acos(this.uniforms.get("rotation").value.x)}set rotation(e){this.uniforms.get("rotation").value.set(Math.cos(e),Math.sin(e)),this.blurPass.blurMaterial.rotation=e}get offset(){return this._offset}set offset(e){this._offset=e,this.blurPass.blurMaterial.offset=e,this.updateParams()}get focusArea(){return this._focusArea}set focusArea(e){this._focusArea=e,this.blurPass.blurMaterial.focusArea=e,this.updateParams()}get feather(){return this._feather}set feather(e){this._feather=e,this.blurPass.blurMaterial.feather=e,this.updateParams()}get bias(){return 0}set bias(e){}update(e,t,r){this.blurPass.render(e,t,this.renderTarget)}setSize(e,t){let r=this.resolution;r.setBaseSize(e,t),this.renderTarget.setSize(r.width,r.height),this.blurPass.resolution.copy(r)}initialize(e,t,r){this.blurPass.initialize(e,t,r),void 0!==r&&(this.renderTarget.texture.type=r,null!==e&&e.outputColorSpace===i.er$&&(this.renderTarget.texture.colorSpace=i.er$))}},e_=`#include <packing>
#define packFloatToRGBA(v) packDepthToRGBA(v)
#define unpackRGBAToFloat(v) unpackRGBAToDepth(v)
uniform lowp sampler2D luminanceBuffer0;uniform lowp sampler2D luminanceBuffer1;uniform float minLuminance;uniform float deltaTime;uniform float tau;varying vec2 vUv;void main(){float l0=unpackRGBAToFloat(texture2D(luminanceBuffer0,vUv));
#if __VERSION__ < 300
float l1=texture2DLodEXT(luminanceBuffer1,vUv,MIP_LEVEL_1X1).r;
#else
float l1=textureLod(luminanceBuffer1,vUv,MIP_LEVEL_1X1).r;
#endif
l0=max(minLuminance,l0);l1=max(minLuminance,l1);float adaptedLum=l0+(l1-l0)*(1.0-exp(-deltaTime*tau));gl_FragColor=(adaptedLum==1.0)?vec4(1.0):packFloatToRGBA(adaptedLum);}`,ey=class extends i.BKk{constructor(){super({name:"AdaptiveLuminanceMaterial",defines:{MIP_LEVEL_1X1:"0.0"},uniforms:{luminanceBuffer0:new i.nc$(null),luminanceBuffer1:new i.nc$(null),minLuminance:new i.nc$(.01),deltaTime:new i.nc$(0),tau:new i.nc$(1)},extensions:{shaderTextureLOD:!0},blending:i.XIg,toneMapped:!1,depthWrite:!1,depthTest:!1,fragmentShader:e_,vertexShader:l})}set luminanceBuffer0(e){this.uniforms.luminanceBuffer0.value=e}setLuminanceBuffer0(e){this.uniforms.luminanceBuffer0.value=e}set luminanceBuffer1(e){this.uniforms.luminanceBuffer1.value=e}setLuminanceBuffer1(e){this.uniforms.luminanceBuffer1.value=e}set mipLevel1x1(e){this.defines.MIP_LEVEL_1X1=e.toFixed(1),this.needsUpdate=!0}setMipLevel1x1(e){this.mipLevel1x1=e}set deltaTime(e){this.uniforms.deltaTime.value=e}setDeltaTime(e){this.uniforms.deltaTime.value=e}get minLuminance(){return this.uniforms.minLuminance.value}set minLuminance(e){this.uniforms.minLuminance.value=e}getMinLuminance(){return this.uniforms.minLuminance.value}setMinLuminance(e){this.uniforms.minLuminance.value=e}get adaptationRate(){return this.uniforms.tau.value}set adaptationRate(e){this.uniforms.tau.value=e}getAdaptationRate(){return this.uniforms.tau.value}setAdaptationRate(e){this.uniforms.tau.value=e}},eR=`#ifdef FRAMEBUFFER_PRECISION_HIGH
uniform mediump sampler2D inputBuffer;
#else
uniform lowp sampler2D inputBuffer;
#endif
#ifdef BILATERAL
#include <packing>
uniform vec2 cameraNearFar;
#define cameraNear cameraNearFar.x
#define cameraFar cameraNearFar.y
#ifdef NORMAL_DEPTH
#ifdef GL_FRAGMENT_PRECISION_HIGH
uniform highp sampler2D normalDepthBuffer;
#else
uniform mediump sampler2D normalDepthBuffer;
#endif
float readDepth(const in vec2 uv){float depth=texture2D(normalDepthBuffer,uv).a;
#if defined(USE_LOGARITHMIC_DEPTH_BUFFER) || defined(LOG_DEPTH)
float d=pow(2.0,depth*log2(cameraFar+1.0))-1.0;float a=cameraFar/(cameraFar-cameraNear);float b=cameraFar*cameraNear/(cameraNear-cameraFar);depth=a+b/d;
#elif defined(USE_REVERSED_DEPTH_BUFFER)
depth=1.0-depth;
#endif
return depth;}
#else
#if DEPTH_PACKING == 3201
uniform lowp sampler2D depthBuffer;
#elif defined(GL_FRAGMENT_PRECISION_HIGH)
uniform highp sampler2D depthBuffer;
#else
uniform mediump sampler2D depthBuffer;
#endif
float readDepth(const in vec2 uv){
#if DEPTH_PACKING == 3201
float depth=unpackRGBAToDepth(texture2D(depthBuffer,uv));
#else
float depth=texture2D(depthBuffer,uv).r;
#endif
#if defined(USE_LOGARITHMIC_DEPTH_BUFFER) || defined(LOG_DEPTH)
float d=pow(2.0,depth*log2(cameraFar+1.0))-1.0;float a=cameraFar/(cameraFar-cameraNear);float b=cameraFar*cameraNear/(cameraNear-cameraFar);depth=a+b/d;
#elif defined(USE_REVERSED_DEPTH_BUFFER)
depth=1.0-depth;
#endif
return depth;}
#endif
float getViewZ(const in float depth){
#ifdef PERSPECTIVE_CAMERA
return perspectiveDepthToViewZ(depth,cameraNearFar.x,cameraNearFar.y);
#else
return orthographicDepthToViewZ(depth,cameraNearFar.x,cameraNearFar.y);
#endif
}
#ifdef PERSPECTIVE_CAMERA
#define linearDepth(v) viewZToOrthographicDepth(getViewZ(readDepth(v)), cameraNearFar.x, cameraNearFar.y)
#else
#define linearDepth(v) readDepth(v)
#endif
#endif
#define getTexel(v) texture2D(inputBuffer, v)
#if KERNEL_SIZE == 3
varying vec2 vUv00,vUv01,vUv02;varying vec2 vUv03,vUv04,vUv05;varying vec2 vUv06,vUv07,vUv08;
#elif KERNEL_SIZE == 5 && MAX_VARYING_VECTORS >= 13
varying vec2 vUv00,vUv01,vUv02,vUv03,vUv04;varying vec2 vUv05,vUv06,vUv07,vUv08,vUv09;varying vec2 vUv10,vUv11,vUv12,vUv13,vUv14;varying vec2 vUv15,vUv16,vUv17,vUv18,vUv19;varying vec2 vUv20,vUv21,vUv22,vUv23,vUv24;
#else
uniform vec2 texelSize;uniform float scale;varying vec2 vUv;
#endif
void main(){
#if KERNEL_SIZE == 3
vec4 c[]=vec4[KERNEL_SIZE_SQ](getTexel(vUv00),getTexel(vUv01),getTexel(vUv02),getTexel(vUv03),getTexel(vUv04),getTexel(vUv05),getTexel(vUv06),getTexel(vUv07),getTexel(vUv08));
#ifdef BILATERAL
float z[]=float[KERNEL_SIZE_SQ](linearDepth(vUv00),linearDepth(vUv01),linearDepth(vUv02),linearDepth(vUv03),linearDepth(vUv04),linearDepth(vUv05),linearDepth(vUv06),linearDepth(vUv07),linearDepth(vUv08));
#endif
#elif KERNEL_SIZE == 5 && MAX_VARYING_VECTORS >= 13
vec4 c[]=vec4[KERNEL_SIZE_SQ](getTexel(vUv00),getTexel(vUv01),getTexel(vUv02),getTexel(vUv03),getTexel(vUv04),getTexel(vUv05),getTexel(vUv06),getTexel(vUv07),getTexel(vUv08),getTexel(vUv09),getTexel(vUv10),getTexel(vUv11),getTexel(vUv12),getTexel(vUv13),getTexel(vUv14),getTexel(vUv15),getTexel(vUv16),getTexel(vUv17),getTexel(vUv18),getTexel(vUv19),getTexel(vUv20),getTexel(vUv21),getTexel(vUv22),getTexel(vUv23),getTexel(vUv24));
#ifdef BILATERAL
float z[]=float[KERNEL_SIZE_SQ](linearDepth(vUv00),linearDepth(vUv01),linearDepth(vUv02),linearDepth(vUv03),linearDepth(vUv04),linearDepth(vUv05),linearDepth(vUv06),linearDepth(vUv07),linearDepth(vUv08),linearDepth(vUv09),linearDepth(vUv10),linearDepth(vUv11),linearDepth(vUv12),linearDepth(vUv13),linearDepth(vUv14),linearDepth(vUv15),linearDepth(vUv16),linearDepth(vUv17),linearDepth(vUv18),linearDepth(vUv19),linearDepth(vUv20),linearDepth(vUv21),linearDepth(vUv22),linearDepth(vUv23),linearDepth(vUv24));
#endif
#endif
vec4 result=vec4(0.0);
#ifdef BILATERAL
float w=0.0;
#if KERNEL_SIZE == 3 || (KERNEL_SIZE == 5 && MAX_VARYING_VECTORS >= 13)
float centerDepth=z[KERNEL_SIZE_SQ_HALF];for(int i=0;i<KERNEL_SIZE_SQ;++i){float d=step(abs(z[i]-centerDepth),DISTANCE_THRESHOLD);result+=c[i]*d;w+=d;}
#else
float centerDepth=linearDepth(vUv);vec2 s=texelSize*scale;for(int x=-KERNEL_SIZE_HALF;x<=KERNEL_SIZE_HALF;++x){for(int y=-KERNEL_SIZE_HALF;y<=KERNEL_SIZE_HALF;++y){vec2 coords=vUv+vec2(x,y)*s;vec4 c=getTexel(coords);float z=(x==0&&y==0)?centerDepth:linearDepth(coords);float d=step(abs(z-centerDepth),DISTANCE_THRESHOLD);result+=c*d;w+=d;}}
#endif
gl_FragColor=result/max(w,1.0);
#else
#if KERNEL_SIZE == 3 || (KERNEL_SIZE == 5 && MAX_VARYING_VECTORS >= 13)
for(int i=0;i<KERNEL_SIZE_SQ;++i){result+=c[i];}
#else
vec2 s=texelSize*scale;for(int x=-KERNEL_SIZE_HALF;x<=KERNEL_SIZE_HALF;++x){for(int y=-KERNEL_SIZE_HALF;y<=KERNEL_SIZE_HALF;++y){result+=getTexel(uv+vec2(x,y)*s);}}
#endif
gl_FragColor=result*INV_KERNEL_SIZE_SQ;
#endif
}`,eA=`uniform vec2 texelSize;uniform float scale;
#if KERNEL_SIZE == 3
varying vec2 vUv00,vUv01,vUv02;varying vec2 vUv03,vUv04,vUv05;varying vec2 vUv06,vUv07,vUv08;
#elif KERNEL_SIZE == 5 && MAX_VARYING_VECTORS >= 13
varying vec2 vUv00,vUv01,vUv02,vUv03,vUv04;varying vec2 vUv05,vUv06,vUv07,vUv08,vUv09;varying vec2 vUv10,vUv11,vUv12,vUv13,vUv14;varying vec2 vUv15,vUv16,vUv17,vUv18,vUv19;varying vec2 vUv20,vUv21,vUv22,vUv23,vUv24;
#else
varying vec2 vUv;
#endif
void main(){vec2 uv=position.xy*0.5+0.5;
#if KERNEL_SIZE == 3
vec2 s=texelSize*scale;vUv00=uv+s*vec2(-1.0,-1.0);vUv01=uv+s*vec2(0.0,-1.0);vUv02=uv+s*vec2(1.0,-1.0);vUv03=uv+s*vec2(-1.0,0.0);vUv04=uv;vUv05=uv+s*vec2(1.0,0.0);vUv06=uv+s*vec2(-1.0,1.0);vUv07=uv+s*vec2(0.0,1.0);vUv08=uv+s*vec2(1.0,1.0);
#elif KERNEL_SIZE == 5
vec2 s=texelSize*scale;vUv00=uv+s*vec2(-2.0,-2.0);vUv01=uv+s*vec2(-1.0,-2.0);vUv02=uv+s*vec2(0.0,-2.0);vUv03=uv+s*vec2(1.0,-2.0);vUv04=uv+s*vec2(2.0,-2.0);vUv05=uv+s*vec2(-2.0,-1.0);vUv06=uv+s*vec2(-1.0,-1.0);vUv07=uv+s*vec2(0.0,-1.0);vUv08=uv+s*vec2(1.0,-1.0);vUv09=uv+s*vec2(2.0,-1.0);vUv10=uv+s*vec2(-2.0,0.0);vUv11=uv+s*vec2(-1.0,0.0);vUv12=uv;vUv13=uv+s*vec2(1.0,0.0);vUv14=uv+s*vec2(2.0,0.0);vUv15=uv+s*vec2(-2.0,1.0);vUv16=uv+s*vec2(-1.0,1.0);vUv17=uv+s*vec2(0.0,1.0);vUv18=uv+s*vec2(1.0,1.0);vUv19=uv+s*vec2(2.0,1.0);vUv20=uv+s*vec2(-2.0,2.0);vUv21=uv+s*vec2(-1.0,2.0);vUv22=uv+s*vec2(0.0,2.0);vUv23=uv+s*vec2(1.0,2.0);vUv24=uv+s*vec2(2.0,2.0);
#else
vUv=uv;
#endif
gl_Position=vec4(position.xy,1.0,1.0);}`,ew=(i.BKk,`#include <packing>
varying vec2 vUv;
#ifdef NORMAL_DEPTH
#ifdef GL_FRAGMENT_PRECISION_HIGH
uniform highp sampler2D normalDepthBuffer;
#else
uniform mediump sampler2D normalDepthBuffer;
#endif
float readDepth(const in vec2 uv){return texture2D(normalDepthBuffer,uv).a;}
#else
#if INPUT_DEPTH_PACKING == 3201
uniform lowp sampler2D depthBuffer;
#elif defined(GL_FRAGMENT_PRECISION_HIGH)
uniform highp sampler2D depthBuffer;
#else
uniform mediump sampler2D depthBuffer;
#endif
float readDepth(const in vec2 uv){
#if INPUT_DEPTH_PACKING == 3201
return unpackRGBAToDepth(texture2D(depthBuffer,uv));
#else
return texture2D(depthBuffer,uv).r;
#endif
}
#endif
void main(){
#if INPUT_DEPTH_PACKING == OUTPUT_DEPTH_PACKING
gl_FragColor=texture2D(depthBuffer,vUv);
#else
float depth=readDepth(vUv);
#if OUTPUT_DEPTH_PACKING == 3201
gl_FragColor=(depth==1.0)?vec4(1.0):packDepthToRGBA(depth);
#else
gl_FragColor=vec4(vec3(depth),1.0);
#endif
#endif
}`),eB=`varying vec2 vUv;
#if DEPTH_COPY_MODE == 1
uniform vec2 texelPosition;
#endif
void main(){
#if DEPTH_COPY_MODE == 1
vUv=texelPosition;
#else
vUv=position.xy*0.5+0.5;
#endif
gl_Position=vec4(position.xy,1.0,1.0);}`,eI=class extends i.BKk{constructor(){super({name:"DepthCopyMaterial",defines:{INPUT_DEPTH_PACKING:"0",OUTPUT_DEPTH_PACKING:"0",DEPTH_COPY_MODE:"0"},uniforms:{depthBuffer:new i.nc$(null),texelPosition:new i.nc$(new i.I9Y)},blending:i.XIg,toneMapped:!1,depthWrite:!1,depthTest:!1,fragmentShader:ew,vertexShader:eB}),this.depthCopyMode=et.FULL}get depthBuffer(){return this.uniforms.depthBuffer.value}set depthBuffer(e){this.uniforms.depthBuffer.value=e}set inputDepthPacking(e){this.defines.INPUT_DEPTH_PACKING=e.toFixed(0),this.needsUpdate=!0}get outputDepthPacking(){return Number(this.defines.OUTPUT_DEPTH_PACKING)}set outputDepthPacking(e){this.defines.OUTPUT_DEPTH_PACKING=e.toFixed(0),this.needsUpdate=!0}setDepthBuffer(e,t=i.Rkk){this.depthBuffer=e,this.inputDepthPacking=t}getInputDepthPacking(){return Number(this.defines.INPUT_DEPTH_PACKING)}setInputDepthPacking(e){this.defines.INPUT_DEPTH_PACKING=e.toFixed(0),this.needsUpdate=!0}getOutputDepthPacking(){return Number(this.defines.OUTPUT_DEPTH_PACKING)}setOutputDepthPacking(e){this.defines.OUTPUT_DEPTH_PACKING=e.toFixed(0),this.needsUpdate=!0}get texelPosition(){return this.uniforms.texelPosition.value}getTexelPosition(){return this.uniforms.texelPosition.value}setTexelPosition(e){this.uniforms.texelPosition.value=e}get mode(){return this.depthCopyMode}set mode(e){this.depthCopyMode=e,this.defines.DEPTH_COPY_MODE=e.toFixed(0),this.needsUpdate=!0}getMode(){return this.mode}setMode(e){this.mode=e}},eb=`#include <common>
#include <packing>
#include <dithering_pars_fragment>
#define packFloatToRGBA(v) packDepthToRGBA(v)
#define unpackRGBAToFloat(v) unpackRGBAToDepth(v)
#ifdef FRAMEBUFFER_PRECISION_HIGH
uniform mediump sampler2D inputBuffer;
#else
uniform lowp sampler2D inputBuffer;
#endif
#if DEPTH_PACKING == 3201
uniform lowp sampler2D depthBuffer;
#elif defined(GL_FRAGMENT_PRECISION_HIGH)
uniform highp sampler2D depthBuffer;
#else
uniform mediump sampler2D depthBuffer;
#endif
uniform vec2 resolution;uniform vec2 texelSize;uniform float cameraNear;uniform float cameraFar;uniform float aspect;uniform float time;varying vec2 vUv;vec4 sRGBToLinear(const in vec4 value){return vec4(mix(pow(value.rgb*0.9478672986+vec3(0.0521327014),vec3(2.4)),value.rgb*0.0773993808,vec3(lessThanEqual(value.rgb,vec3(0.04045)))),value.a);}float readDepth(const in vec2 uv){
#if DEPTH_PACKING == 3201
float depth=unpackRGBAToDepth(texture2D(depthBuffer,uv));
#else
float depth=texture2D(depthBuffer,uv).r;
#endif
#if defined(USE_LOGARITHMIC_DEPTH_BUFFER) || defined(LOG_DEPTH)
float d=pow(2.0,depth*log2(cameraFar+1.0))-1.0;float a=cameraFar/(cameraFar-cameraNear);float b=cameraFar*cameraNear/(cameraNear-cameraFar);depth=a+b/d;
#elif defined(USE_REVERSED_DEPTH_BUFFER)
depth=1.0-depth;
#endif
return depth;}float getViewZ(const in float depth){
#ifdef PERSPECTIVE_CAMERA
return perspectiveDepthToViewZ(depth,cameraNear,cameraFar);
#else
return orthographicDepthToViewZ(depth,cameraNear,cameraFar);
#endif
}vec3 RGBToHCV(const in vec3 RGB){vec4 P=mix(vec4(RGB.bg,-1.0,2.0/3.0),vec4(RGB.gb,0.0,-1.0/3.0),step(RGB.b,RGB.g));vec4 Q=mix(vec4(P.xyw,RGB.r),vec4(RGB.r,P.yzx),step(P.x,RGB.r));float C=Q.x-min(Q.w,Q.y);float H=abs((Q.w-Q.y)/(6.0*C+EPSILON)+Q.z);return vec3(H,C,Q.x);}vec3 RGBToHSL(const in vec3 RGB){vec3 HCV=RGBToHCV(RGB);float L=HCV.z-HCV.y*0.5;float S=HCV.y/(1.0-abs(L*2.0-1.0)+EPSILON);return vec3(HCV.x,S,L);}vec3 HueToRGB(const in float H){float R=abs(H*6.0-3.0)-1.0;float G=2.0-abs(H*6.0-2.0);float B=2.0-abs(H*6.0-4.0);return clamp(vec3(R,G,B),0.0,1.0);}vec3 HSLToRGB(const in vec3 HSL){vec3 RGB=HueToRGB(HSL.x);float C=(1.0-abs(2.0*HSL.z-1.0))*HSL.y;return(RGB-0.5)*C+HSL.z;}FRAGMENT_HEAD void main(){FRAGMENT_MAIN_UV vec4 color0=texture2D(inputBuffer,UV);vec4 color1=vec4(0.0);FRAGMENT_MAIN_IMAGE color0.a=clamp(color0.a,0.0,1.0);gl_FragColor=color0;
#ifdef ENCODE_OUTPUT
#include <colorspace_fragment>
#endif
#include <dithering_fragment>
}`,eC=class extends i.BKk{constructor(e,t,r,s,a=!1){super({name:"EffectMaterial",defines:{THREE_REVISION:i.sPf.replace(/\D+/g,""),DEPTH_PACKING:"0",ENCODE_OUTPUT:"1"},uniforms:{inputBuffer:new i.nc$(null),depthBuffer:new i.nc$(null),resolution:new i.nc$(new i.I9Y),texelSize:new i.nc$(new i.I9Y),cameraNear:new i.nc$(.3),cameraFar:new i.nc$(1e3),aspect:new i.nc$(1),time:new i.nc$(0)},blending:i.XIg,toneMapped:!1,depthWrite:!1,depthTest:!1,dithering:a}),e&&this.setShaderParts(e),t&&this.setDefines(t),r&&this.setUniforms(r),this.copyCameraSettings(s)}set inputBuffer(e){this.uniforms.inputBuffer.value=e}setInputBuffer(e){this.uniforms.inputBuffer.value=e}get depthBuffer(){return this.uniforms.depthBuffer.value}set depthBuffer(e){this.uniforms.depthBuffer.value=e}get depthPacking(){return Number(this.defines.DEPTH_PACKING)}set depthPacking(e){this.defines.DEPTH_PACKING=e.toFixed(0),this.needsUpdate=!0}setDepthBuffer(e,t=i.Rkk){this.depthBuffer=e,this.depthPacking=t}setShaderData(e){this.setShaderParts(e.shaderParts),this.setDefines(e.defines),this.setUniforms(e.uniforms),this.setExtensions(e.extensions)}setShaderParts(e){return this.fragmentShader=eb.replace(g.FRAGMENT_HEAD,e.get(g.FRAGMENT_HEAD)||"").replace(g.FRAGMENT_MAIN_UV,e.get(g.FRAGMENT_MAIN_UV)||"").replace(g.FRAGMENT_MAIN_IMAGE,e.get(g.FRAGMENT_MAIN_IMAGE)||""),this.vertexShader="uniform vec2 resolution;uniform vec2 texelSize;uniform float cameraNear;uniform float cameraFar;uniform float aspect;uniform float time;varying vec2 vUv;VERTEX_HEAD void main(){vUv=position.xy*0.5+0.5;VERTEX_MAIN_SUPPORT gl_Position=vec4(position.xy,1.0,1.0);}".replace(g.VERTEX_HEAD,e.get(g.VERTEX_HEAD)||"").replace(g.VERTEX_MAIN_SUPPORT,e.get(g.VERTEX_MAIN_SUPPORT)||""),this.needsUpdate=!0,this}setDefines(e){for(let t of e.entries())this.defines[t[0]]=t[1];return this.needsUpdate=!0,this}setUniforms(e){for(let t of e.entries())this.uniforms[t[0]]=t[1];return this}setExtensions(e){for(let t of(this.extensions={},e))this.extensions[t]=!0;return this}get encodeOutput(){return void 0!==this.defines.ENCODE_OUTPUT}set encodeOutput(e){this.encodeOutput!==e&&(e?this.defines.ENCODE_OUTPUT="1":delete this.defines.ENCODE_OUTPUT,this.needsUpdate=!0)}isOutputEncodingEnabled(e){return this.encodeOutput}setOutputEncodingEnabled(e){this.encodeOutput=e}get time(){return this.uniforms.time.value}set time(e){this.uniforms.time.value=e}setDeltaTime(e){this.uniforms.time.value+=e}adoptCameraSettings(e){this.copyCameraSettings(e)}copyCameraSettings(e){e&&(this.uniforms.cameraNear.value=e.near,this.uniforms.cameraFar.value=e.far,e instanceof i.ubm?this.defines.PERSPECTIVE_CAMERA="1":delete this.defines.PERSPECTIVE_CAMERA,this.needsUpdate=!0)}setSize(e,t){let r=this.uniforms;r.resolution.value.set(e,t),r.texelSize.value.set(1/e,1/t),r.aspect.value=e/t}static get Section(){return g}},eM=`#ifdef FRAMEBUFFER_PRECISION_HIGH
uniform mediump sampler2D inputBuffer;
#else
uniform lowp sampler2D inputBuffer;
#endif
uniform vec2 kernel[STEPS];varying vec2 vOffset;varying vec2 vUv;void main(){vec4 result=texture2D(inputBuffer,vUv)*kernel[0].y;for(int i=1;i<STEPS;++i){vec2 offset=kernel[i].x*vOffset;vec4 c0=texture2D(inputBuffer,vUv+offset);vec4 c1=texture2D(inputBuffer,vUv-offset);result+=(c0+c1)*kernel[i].y;}gl_FragColor=result;
#include <colorspace_fragment>
}`,eP=(i.BKk,i.sPf.replace(/\D+/g,""),255/256);function eF(e,t,r){for(let i of t){let t="$1"+e+i.charAt(0).toUpperCase()+i.slice(1),s=RegExp("([^\\.])(\\b"+i+"\\b)","g");for(let e of r.entries())null!==e[1]&&r.set(e[0],e[1].replace(s,t))}}new Float32Array([255/256/0x1000000,255/256/65536,255/256/256,255/256]),new Float32Array([eP,eP/256,eP/65536,1/0x1000000]);var eN=class extends a{constructor(e,...t){super("EffectPass"),this.fullscreenMaterial=new eC(null,null,null,e),this.listener=e=>this.handleEvent(e),this.effects=[],this.setEffects(t),this.skipRendering=!1,this.minTime=1,this.maxTime=Number.POSITIVE_INFINITY,this.timeScale=1}set mainScene(e){for(let t of this.effects)t.mainScene=e}set mainCamera(e){for(let t of(this.fullscreenMaterial.copyCameraSettings(e),this.effects))t.mainCamera=e}get encodeOutput(){return this.fullscreenMaterial.encodeOutput}set encodeOutput(e){this.fullscreenMaterial.encodeOutput=e}get dithering(){return this.fullscreenMaterial.dithering}set dithering(e){let t=this.fullscreenMaterial;t.dithering=e,t.needsUpdate=!0}setEffects(e){for(let e of this.effects)e.removeEventListener("change",this.listener);for(let t of(this.effects=e.sort((e,t)=>t.attributes-e.attributes),this.effects))t.addEventListener("change",this.listener)}updateMaterial(){let e=new x,t=0;for(let r of this.effects)if(r.blendMode.blendFunction===y.DST)e.attributes|=r.getAttributes()&m.DEPTH;else if((e.attributes&r.getAttributes()&m.CONVOLUTION)!=0)throw Error(`Convolution effects cannot be merged (${r.name})`);else!function(e,t,r){let s=t.getFragmentShader(),a=t.getVertexShader(),n=void 0!==s&&/mainImage/.test(s),o=void 0!==s&&/mainUv/.test(s);if(r.attributes|=t.getAttributes(),void 0===s)throw Error(`Missing fragment shader (${t.name})`);if(o&&(r.attributes&m.CONVOLUTION)!=0)throw Error(`Effects that transform UVs are incompatible with convolution effects (${t.name})`);if(n||o){let l=/\w+\s+(\w+)\([\w\s,]*\)\s*{/g,c=r.shaderParts,u=c.get(g.FRAGMENT_HEAD)||"",f=c.get(g.FRAGMENT_MAIN_UV)||"",d=c.get(g.FRAGMENT_MAIN_IMAGE)||"",v=c.get(g.VERTEX_HEAD)||"",h=c.get(g.VERTEX_MAIN_SUPPORT)||"",p=new Set,x=new Set;if(o&&(f+=`	${e}MainUv(UV);
`,r.uvTransformation=!0),null!==a&&/mainSupport/.test(a)){let t=/mainSupport *\([\w\s]*?uv\s*?\)/.test(a);for(let i of(h+=`	${e}MainSupport(`,h+=t?"vUv);\n":");\n",a.matchAll(/(?:varying\s+\w+\s+([\S\s]*?);)/g)))for(let e of i[1].split(/\s*,\s*/))r.varyings.add(e),p.add(e),x.add(e);for(let e of a.matchAll(l))x.add(e[1])}for(let e of s.matchAll(l))x.add(e[1]);for(let e of t.defines.keys())x.add(e.replace(/\([\w\s,]*\)/g,""));for(let e of t.uniforms.keys())x.add(e);x.delete("while"),x.delete("for"),x.delete("if"),t.uniforms.forEach((t,i)=>r.uniforms.set(e+i.charAt(0).toUpperCase()+i.slice(1),t)),t.defines.forEach((t,i)=>r.defines.set(e+i.charAt(0).toUpperCase()+i.slice(1),t));let E=new Map([["fragment",s],["vertex",a]]);eF(e,x,r.defines),eF(e,x,E),s=E.get("fragment"),a=E.get("vertex");let T=t.blendMode;if(r.blendModes.set(T.blendFunction,T),n){null!==t.inputColorSpace&&t.inputColorSpace!==r.colorSpace&&(d+=t.inputColorSpace===i.er$?"color0 = sRGBTransferOETF(color0);\n	":"color0 = sRGBToLinear(color0);\n	"),t.outputColorSpace!==i.jf0?r.colorSpace=t.outputColorSpace:null!==t.inputColorSpace&&(r.colorSpace=t.inputColorSpace),d+=`${e}MainImage(color0, UV, `,(r.attributes&m.DEPTH)!=0&&/MainImage *\([\w\s,]*?depth[\w\s,]*?\)/.test(s)&&(d+="depth, ",r.readDepth=!0),d+="color1);\n	";let a=e+"BlendOpacity";r.uniforms.set(a,T.opacity),d+=`color0 = blend${T.blendFunction}(color0, color1, ${a});

	`,u+=`uniform float ${a};

`}if(u+=s+"\n",null!==a&&(v+=a+"\n"),c.set(g.FRAGMENT_HEAD,u),c.set(g.FRAGMENT_MAIN_UV,f),c.set(g.FRAGMENT_MAIN_IMAGE,d),c.set(g.VERTEX_HEAD,v),c.set(g.VERTEX_MAIN_SUPPORT,h),null!==t.extensions)for(let e of t.extensions)r.extensions.add(e)}else throw Error(`Could not find mainImage or mainUv function (${t.name})`)}("e"+t++,r,e);let r=e.shaderParts.get(g.FRAGMENT_HEAD),s=e.shaderParts.get(g.FRAGMENT_MAIN_IMAGE),a=e.shaderParts.get(g.FRAGMENT_MAIN_UV),n=/\bblend\b/g;for(let t of e.blendModes.values())r+=t.getShaderCode().replace(n,`blend${t.blendFunction}`)+"\n";for(let[t,n]of((e.attributes&m.DEPTH)!=0?(e.readDepth&&(s="float depth = readDepth(UV);\n\n	"+s),this.needsDepthTexture=null===this.getDepthTexture()):this.needsDepthTexture=!1,e.colorSpace===i.er$&&(s+="color0 = sRGBToLinear(color0);\n	"),e.uvTransformation?(a="vec2 transformedUv = vUv;\n"+a,e.defines.set("UV","transformedUv")):e.defines.set("UV","vUv"),e.shaderParts.set(g.FRAGMENT_HEAD,r),e.shaderParts.set(g.FRAGMENT_MAIN_IMAGE,s),e.shaderParts.set(g.FRAGMENT_MAIN_UV,a),e.shaderParts))null!==n&&e.shaderParts.set(t,n.trim().replace(/^#/,"\n#"));this.skipRendering=0===t,this.needsSwap=!this.skipRendering,this.fullscreenMaterial.setShaderData(e)}recompile(){this.updateMaterial()}getDepthTexture(){return this.fullscreenMaterial.depthBuffer}setDepthTexture(e,t=i.Rkk){for(let r of(this.fullscreenMaterial.depthBuffer=e,this.fullscreenMaterial.depthPacking=t,this.effects))r.setDepthTexture(e,t)}render(e,t,r,i,s){for(let r of this.effects)r.update(e,t,i);if(!this.skipRendering||this.renderToScreen){let s=this.fullscreenMaterial;s.inputBuffer=t.texture,s.time+=i*this.timeScale,e.setRenderTarget(this.renderToScreen?null:r),e.render(this.scene,this.camera)}}setSize(e,t){for(let r of(this.fullscreenMaterial.setSize(e,t),this.effects))r.setSize(e,t)}initialize(e,t,r){for(let i of(this.renderer=e,this.effects))i.initialize(e,t,r);this.updateMaterial(),void 0!==r&&r!==i.OUM&&(this.fullscreenMaterial.defines.FRAMEBUFFER_PRECISION_HIGH="1")}dispose(){for(let e of(super.dispose(),this.effects))e.removeEventListener("change",this.listener),e.dispose()}handleEvent(e){"change"===e.type&&this.recompile()}},eO=class extends a{constructor(e,t,{renderTarget:r,resolutionScale:s=1,width:a=D.AUTO_SIZE,height:n=D.AUTO_SIZE,resolutionX:o=a,resolutionY:l=n}={}){super("NormalPass"),this.needsSwap=!1,this.renderPass=new j(e,t,new i.qBx);let c=this.renderPass;c.ignoreBackground=!0,c.skipShadowMapUpdate=!0;let u=c.getClearPass();u.overrideClearColor=new i.Q1f(7829503),u.overrideClearAlpha=1,this.renderTarget=r,void 0===this.renderTarget&&(this.renderTarget=new i.nWS(1,1,{minFilter:i.hxR,magFilter:i.hxR}),this.renderTarget.texture.name="NormalPass.Target");let f=this.resolution=new D(this,o,l,s);f.addEventListener("change",e=>this.setSize(f.baseWidth,f.baseHeight))}set mainScene(e){this.renderPass.mainScene=e}set mainCamera(e){this.renderPass.mainCamera=e}get texture(){return this.renderTarget.texture}getTexture(){return this.renderTarget.texture}getResolution(){return this.resolution}getResolutionScale(){return this.resolution.scale}setResolutionScale(e){this.resolution.scale=e}render(e,t,r,i,s){let a=this.renderToScreen?null:this.renderTarget;this.renderPass.render(e,a,a)}setSize(e,t){let r=this.resolution;r.setBaseSize(e,t),this.renderTarget.setSize(r.width,r.height)}};new Float32Array(3),new Float32Array(3),new Float32Array(3),new Float32Array(3),new Float32Array(3),new Float32Array(3),new Float32Array([0,0,0]),new Float32Array([1,0,0]),new Float32Array([1,1,0]),new Float32Array([1,1,1]),new Float32Array([0,0,0]),new Float32Array([1,0,0]),new Float32Array([1,0,1]),new Float32Array([1,1,1]),new Float32Array([0,0,0]),new Float32Array([0,0,1]),new Float32Array([1,0,1]),new Float32Array([1,1,1]),new Float32Array([0,0,0]),new Float32Array([0,1,0]),new Float32Array([1,1,0]),new Float32Array([1,1,1]),new Float32Array([0,0,0]),new Float32Array([0,1,0]),new Float32Array([0,1,1]),new Float32Array([1,1,1]),new Float32Array([0,0,0]),new Float32Array([0,0,1]),new Float32Array([0,1,1]),new Float32Array([1,1,1]);var eL=[new Float32Array(2),new Float32Array(2)],eH=(new Float32Array([0,-.25,.25,-.125,.125,-.375,.375]),new Float32Array([0,0]),new Float32Array([.25,-.25]),new Float32Array([-.25,.25]),new Float32Array([.125,-.125]),new Float32Array([-.125,.125]),new Uint8Array([0,0]),new Uint8Array([3,0]),new Uint8Array([0,3]),new Uint8Array([3,3]),new Uint8Array([1,0]),new Uint8Array([4,0]),new Uint8Array([1,3]),new Uint8Array([4,3]),new Uint8Array([0,1]),new Uint8Array([3,1]),new Uint8Array([0,4]),new Uint8Array([3,4]),new Uint8Array([1,1]),new Uint8Array([4,1]),new Uint8Array([1,4]),new Uint8Array([4,4]),[new Uint8Array([0,0]),new Uint8Array([1,0]),new Uint8Array([0,2]),new Uint8Array([1,2]),new Uint8Array([2,0]),new Uint8Array([3,0]),new Uint8Array([2,2]),new Uint8Array([3,2]),new Uint8Array([0,1]),new Uint8Array([1,1]),new Uint8Array([0,3]),new Uint8Array([1,3]),new Uint8Array([2,1]),new Uint8Array([3,1]),new Uint8Array([2,3]),new Uint8Array([3,3])]);function ez(e){let t=eL[0],r=eL[1],i=.5*Math.sqrt(2*t[0]),s=.5*Math.sqrt(2*t[1]),a=.5*Math.sqrt(2*r[0]),n=.5*Math.sqrt(2*r[1]),o=Math.min(Math.max(e/32,0),1);t[0]=i+(t[0]-i)*o,t[1]=s+(t[1]-s)*o,r[0]=a+(r[0]-a)*o,r[1]=n+(r[1]-n)*o}function eG(e,t,r,i,s,a){let n=r-e,o=i-t,l=s+1,c=t+o*(s-e)/n,u=t+o*(l-e)/n;if(s>=e&&s<r||l>e&&l<=r)if(Math.sign(c)===Math.sign(u)||1e-4>Math.abs(c)||1e-4>Math.abs(u)){let e=(c+u)/2;e<0?(a[0]=Math.abs(e),a[1]=0):(a[0]=0,a[1]=Math.abs(e))}else{let i=-t*n/o+e,s=Math.trunc(i),l=i>e?c*(i-s)/2:0,f=i<r?u*(1-(i-s))/2:0;(Math.abs(l)>Math.abs(f)?l:-f)<0?(a[0]=Math.abs(l),a[1]=Math.abs(f)):(a[0]=Math.abs(f),a[1]=Math.abs(l))}else a[0]=0,a[1]=0;return a}function ek(e,t,r,i,s,a){let n=0;for(let o=0;o<30;++o)for(let l=0;l<30;++l)(function(e,t,r,i,s,a){let n=e===r&&t===i;return n||(n=(i-t)*(s-(e+r)/2)+(e-r)*(a-(t+i)/2)>0),n})(e,t,r,i,s+l/29,a+o/29)&&++n;return n/900}function eV(e,t,r,i,s,a,n,o){let l=eH[e],c=l[0],u=l[1];return c>0&&(t+=n[0],r+=n[1]),u>0&&(i+=n[0],s+=n[1]),o[0]=1-ek(t,r,i,s,1+a,0+a),o[1]=ek(t,r,i,s,1+a,1+a),o}eZ(0,0,0,0),new Float32Array([0,0,0,0]),eZ(0,0,0,1),new Float32Array([0,0,0,1]),eZ(0,0,1,0),new Float32Array([0,0,1,0]),eZ(0,0,1,1),new Float32Array([0,0,1,1]),eZ(0,1,0,0),new Float32Array([0,1,0,0]),eZ(0,1,0,1),new Float32Array([0,1,0,1]),eZ(0,1,1,0),new Float32Array([0,1,1,0]),eZ(0,1,1,1),new Float32Array([0,1,1,1]),eZ(1,0,0,0),new Float32Array([1,0,0,0]),eZ(1,0,0,1),new Float32Array([1,0,0,1]),eZ(1,0,1,0),new Float32Array([1,0,1,0]),eZ(1,0,1,1),new Float32Array([1,0,1,1]),eZ(1,1,0,0),new Float32Array([1,1,0,0]),eZ(1,1,0,1),new Float32Array([1,1,0,1]),eZ(1,1,1,0),new Float32Array([1,1,1,0]),eZ(1,1,1,1),new Float32Array([1,1,1,1]);function eZ(e,t,r,i){var s;return(s=e+(t-e)*.75)+(r+(i-r)*.75-s)*.875}}}]);