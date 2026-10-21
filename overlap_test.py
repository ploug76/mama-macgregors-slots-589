# Overlap test: HUD pills, Mama's speech-bubble slot, reel frame, win ticker, every button, DOM buttons and modals,
# sampled over many frames of real play (all 3 machines, free spins, pick bonus, big wins) at 4 phone sizes.
import sys,asyncio,json
from playwright.async_api import async_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8800/mama-macgregors-slots/'
VIEWS=[(390,844,None),(375,667,None),(430,932,None),(390,844,{'t':47,'b':34})]
JS=r'''async (mid)=>{const T=__T;T.setMachine(mid);T.setSave({lvl:10,coins:1e6});T.setTurbo(Math.random()<.5);const ov=(a,b)=>a.x<b.x+b.w-.01&&b.x<a.x+a.w-.01&&a.y<b.y+b.h-.01&&b.y<a.y+a.h-.01;
 const btns=()=>{const L=T.layout();return[...document.querySelectorAll('.tb')].filter(e=>getComputedStyle(e).display!='none').map(e=>{const b=e.getBoundingClientRect();return{k:'dom-'+e.id,x:(b.left-L.OXs)/L.SC,y:(b.top-L.OYs)/L.SC,w:b.width/L.SC,h:b.height/L.SC}})};
 let frames=0;const bad=[];const check=()=>{frames++;const L=T.layout(),E=L.els.concat(btns());const vis={x0:Math.max(0,(L.SAFE.l-L.OXs)/L.SC),y0:Math.max(0,(L.SAFE.t-L.OYs)/L.SC),x1:Math.min(400,(L.VW-L.SAFE.r-L.OXs)/L.SC),y1:Math.min(720,(L.VH-L.SAFE.b-L.OYs)/L.SC)};
  for(let i=0;i<E.length;i++){for(let j=i+1;j<E.length;j++)if(ov(E[i],E[j]))bad.push([E[i].k,E[j].k]);const e=E[i];if(!e.k.startsWith('dom')&&(e.x<vis.x0-.01||e.y<vis.y0-.01||e.x+e.w>vis.x1+.01||e.y+e.h>vis.y1+.01))bad.push(['edge',e.k])}
  if(L.modal){const m=L.modal;if(m.x<vis.x0||m.y<vis.y0||m.x+m.w>vis.x1||m.y+m.h>vis.y1)bad.push(['modal-edge']);for(const b of btns())if(ov(m,b))bad.push(['modal-dom',b.k])}};
 const step=(s)=>{for(let i=0;i<Math.round(s*30);i++){T.update(1/30);if(i%4==0)check()}};
 for(let n=0;n<40;n++){const r=Math.random();let s=null;if(r<.1)s=T.findStops(e=>e.fs>0);else if(r<.18)s=T.findStops(e=>e.bonus);else if(r<.3)s=T.findStops(e=>e.lineTot>=15*T.M().lines/ T.M().lines*10);if(s)T.force(s);T.startSpin();step(4);
  let k=0;while((T.get().modal||T.get().mq||T.get().bonus||(T.get().fs&&T.get().fs.left>0)||T.get().spinning)&&k<400){k++;const g=T.get();if(g.bonus){if(g.bonus.done)T.collect();else T.pickTile(Math.floor(Math.random()*12))}else if(g.modal&&Math.random()<.5)T.closeModal();step(.5)}}
 return{mid,frames,overlaps:bad.length,sample:bad.slice(0,4)}}'''
async def main():
  tot=0;fr=0
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for (w,h,safe) in VIEWS:
      pg=await b.new_page(viewport={'width':w,'height':h},is_mobile=True,has_touch=True);errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
      if safe:await pg.add_init_script('window.__SAFE='+json.dumps(safe))
      await pg.goto(URL+'?play');await pg.wait_for_timeout(600)
      for mid in ['pasture','derby','kirk']:
        r=await pg.evaluate(JS,mid);tot+=r['overlaps'];fr+=r['frames'];print(f"{w}x{h}{' safe' if safe else ''} {mid:8} frames {r['frames']} overlaps {r['overlaps']}",r['sample'] if r['overlaps'] else '')
      if errs:print('PAGE ERRORS',errs);tot+=len(errs)
      await pg.close()
    await b.close()
  print(f'TOTAL frames {fr} overlaps {tot}');sys.exit(1 if tot else 0)
asyncio.run(main())
