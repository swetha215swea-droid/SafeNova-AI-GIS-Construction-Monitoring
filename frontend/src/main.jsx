import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw';
import 'leaflet-draw/dist/leaflet.draw.css';
import { Building2, Save, Trash2, MousePointer2, Pencil, Circle, Square, Pentagon, Info, Mountain, MapPinned, ShieldCheck, Layers, Crosshair, Download, Menu, X } from 'lucide-react';
import './style.css';

const initialCases = [
 {id:'B-032',lat:12.9277,lng:80.1038,priority:'High',status:'Needs review',note:'Image change requires field verification'},
 {id:'B-017',lat:12.9294,lng:80.1071,priority:'High',status:'Needs review',note:'Approval record not yet matched'},
 {id:'B-041',lat:12.9255,lng:80.0997,priority:'Medium',status:'Pending review',note:'Possible footprint change'},
 {id:'B-008',lat:12.9310,lng:80.1011,priority:'Low',status:'Queued',note:'No configured screening trigger'},
 {id:'B-021',lat:12.9242,lng:80.1063,priority:'Medium',status:'Pending review',note:'Verify against latest imagery'},
 {id:'B-015',lat:12.9288,lng:80.0969,priority:'Low',status:'Queued',note:'Routine monitoring'},
 {id:'B-024',lat:12.9301,lng:80.1044,priority:'High',status:'Needs review'},
 {id:'B-026',lat:12.9265,lng:80.1017,priority:'Medium',status:'Pending review'},
 {id:'B-029',lat:12.9281,lng:80.1001,priority:'Low',status:'Queued'},
 {id:'B-033',lat:12.9238,lng:80.1048,priority:'High',status:'Needs review'},
 {id:'B-036',lat:12.9259,lng:80.1081,priority:'Low',status:'Queued'},
 {id:'B-038',lat:12.9290,lng:80.0982,priority:'Medium',status:'Pending review'},
 {id:'B-044',lat:12.9248,lng:80.1024,priority:'High',status:'Needs review'},
 {id:'B-047',lat:12.9270,lng:80.1060,priority:'Low',status:'Queued'},
 {id:'B-051',lat:12.9312,lng:80.1054,priority:'Medium',status:'Pending review'},
 {id:'B-054',lat:12.9261,lng:80.0978,priority:'High',status:'Needs review'},
 {id:'B-057',lat:12.9239,lng:80.1009,priority:'Medium',status:'Pending review'},
 {id:'B-061',lat:12.9299,lng:80.1022,priority:'High',status:'Needs review'}
];
const priorityColor = {High:'#ef4444',Medium:'#f5b82e',Low:'#2f9145'};
const boundary = [[12.9315,80.1010],[12.9309,80.1067],[12.9274,80.1080],[12.9236,80.1044],[12.9240,80.1008],[12.9287,80.0990]];
function App(){
 const mapNode=useRef(null), mapRef=useRef(null), drawnRef=useRef(null), markersRef=useRef(null);
 const [cases,setCases]=useState(initialCases), [selected,setSelected]=useState(null), [areaName,setAreaName]=useState('Selected Area 1');
 const [areaSaved,setAreaSaved]=useState(false), [mapReady,setMapReady]=useState(false), [message,setMessage]=useState('');
 const [filter,setFilter]=useState('All'), [menuOpen,setMenuOpen]=useState(false);
 const [selectedCase,setSelectedCase]=useState(null);
 const counts=useMemo(()=>({High:cases.filter(c=>c.priority==='High').length,Medium:cases.filter(c=>c.priority==='Medium').length,Low:cases.filter(c=>c.priority==='Low').length}),[cases]);
 useEffect(()=>{
  if(!mapNode.current||mapRef.current)return;
  const map=L.map(mapNode.current,{zoomControl:false,preferCanvas:true}).setView([12.927,80.1035],16);
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',{attribution:'Tiles © Esri'}).addTo(map);
  L.control.zoom({position:'bottomright'}).addTo(map);
  const drawn=new L.FeatureGroup();map.addLayer(drawn);drawnRef.current=drawn;
  const area=L.polygon(boundary,{color:'#1674ff',weight:3,fillColor:'#2878ff',fillOpacity:.25,opacity:1}).addTo(drawn);
  setSelected(area.toGeoJSON());
  const drawControl=new L.Control.Draw({position:'topleft',draw:{polygon:{allowIntersection:false,showArea:true},rectangle:true,circle:true,polyline:false,marker:false,circlemarker:false},edit:{featureGroup:drawn,edit:true,remove:true}});
  map.addControl(drawControl);
  map.on(L.Draw.Event.CREATED,e=>{drawn.clearLayers();drawn.addLayer(e.layer);setSelected(e.layer.toGeoJSON());setAreaSaved(false);setMessage('Area selected. Save it to keep this selection for the current session.')});
  map.on(L.Draw.Event.EDITED,e=>{e.layers.eachLayer(layer=>setSelected(layer.toGeoJSON()));setAreaSaved(false)});
  map.on(L.Draw.Event.DELETED,()=>{setSelected(null);setAreaSaved(false)});
  markersRef.current=L.layerGroup().addTo(map);
  mapRef.current=map;setMapReady(true);
  return ()=>{map.remove();mapRef.current=null};
 },[]);
 useEffect(()=>{
  const layer=markersRef.current;if(!layer)return;layer.clearLayers();
  cases.filter(c=>filter==='All'||c.priority===filter).forEach(c=>{
   const color=priorityColor[c.priority]||priorityColor.Medium;
   const marker=L.rectangle([[c.lat-.00012,c.lng-.00018],[c.lat+.00012,c.lng+.00018]],{color,weight:2,fillColor:color,fillOpacity:.8}).addTo(layer);
   marker.bindTooltip('Building '+c.id+' · '+c.priority);
   marker.on('click',()=>{setSelectedCase(c.id);setMessage(c.id+': '+(c.note||'Illustrative alert; field verification required.'))});
  });
 },[cases,filter,mapReady]);
 function saveArea(){
  if(!selected){setMessage('Draw a polygon, rectangle, or circle on the map first.');return}
  const payload={name:areaName,geometry:selected,created_at:new Date().toISOString()};
  try{sessionStorage.setItem('safenova-selected-area',JSON.stringify(payload));setMessage('Area saved in this browser session.');}
  catch{setMessage('Area selected for this dashboard session.');}
  setAreaSaved(true);
 }
 function clearSelection(){drawnRef.current?.clearLayers();setSelected(null);setAreaSaved(false);setMessage('Selection cleared. Draw a new area to continue.')}
 const inspect=cases.slice().sort((a,b)=>({High:0,Medium:1,Low:2}[a.priority]-({High:0,Medium:1,Low:2}[b.priority])));
 return <div className="app-shell">
  <header className="topbar"><div className="brand"><div className="brand-icon"><Building2 size={31}/></div><div><h1>AI-Powered Online Monitoring System</h1><p>Unauthorized Construction Detection</p></div></div><div className="top-actions"><span className="connection demo">Demo mode · no backend</span><button className="btn btn-primary" onClick={saveArea}><Save size={17}/> Save Area</button><button className="btn btn-light" onClick={clearSelection}><Trash2 size={17}/> Clear Selection</button><button className="mobile-menu" onClick={()=>setMenuOpen(!menuOpen)}>{menuOpen?<X/>:<Menu/>}</button></div></header>
  <main className="workspace"><aside className={'left-panel '+(menuOpen?'open':'')}>
   <section className="panel-card"><div className="section-heading">SELECT AREA</div><p className="muted">Draw or select an area on the map</p><div className="draw-help"><span><Pentagon size={16}/> Polygon</span><span><Square size={16}/> Rectangle</span><span><Circle size={16}/> Circle</span></div><p className="tiny muted">Choose a drawing tool from the map toolbar to create or edit a boundary.</p><label className="field-label">Area name</label><input value={areaName} onChange={e=>setAreaName(e.target.value)} aria-label="Area name"/></section>
   <section className="panel-card"><div className="section-heading">PRIORITY FOR INSPECTION</div><div className="legend"><span><i style={{background:priorityColor.High}}/>High Priority</span><span><i style={{background:priorityColor.Medium}}/>Medium Priority</span><span><i style={{background:priorityColor.Low}}/>Low Priority</span></div><select value={filter} onChange={e=>setFilter(e.target.value)} aria-label="Filter priority"><option>All</option><option>High</option><option>Medium</option><option>Low</option></select></section>
   <section className="panel-card area-info"><div className="section-heading">AREA INFORMATION</div><div className="info-row"><span>Area Name</span><strong>{areaName||'Unnamed area'}</strong></div><div className="info-row"><span>Total Buildings</span><strong>{cases.length}</strong></div><div className="info-row high-text"><span>High Priority</span><strong>{counts.High}</strong></div><div className="info-row medium-text"><span>Medium Priority</span><strong>{counts.Medium}</strong></div><div className="info-row low-text"><span>Low Priority</span><strong>{counts.Low}</strong></div></section>
   <section className="panel-card"><div className="section-heading">SOIL & ELEVATION DATA</div><div className="data-line"><Mountain size={19}/><span>Soil Type</span><strong>Not available</strong></div><div className="data-line"><MapPinned size={19}/><span>Elevation</span><strong>Not available</strong></div><p className="tiny muted">Real soil and elevation values require verified external datasets.</p></section>
   <div className="notice"><Info size={18}/><span>{message||'Illustrative demo records only. Confirm all alerts against current imagery and official approval records.'}</span></div>
  </aside>
  <section className="map-column"><div className="map-wrap"><div ref={mapNode} className="map-canvas" aria-label="Satellite map with drawing tools"/><div className="map-filter"><Layers size={16}/><span>Satellite imagery</span><span className="live-dot"/></div><button className="locate-btn" title="Reset map view" onClick={()=>mapRef.current?.setView([12.927,80.1035],16)}><Crosshair size={18}/></button><div className="map-attribution-note">Imagery © Esri · Sample building markers are illustrative</div></div>
   <div className="bottom-panels"><section className="priority-guide"><div className="section-heading">PRIORITY INSPECTION GUIDE</div><div className="priority-cards"><div className="priority-card high"><div><i/> <b>High Priority ({counts.High})</b></div><p>Potential mismatch</p><strong>Inspect first</strong></div><div className="priority-card medium"><div><i/> <b>Medium Priority ({counts.Medium})</b></div><p>Under verification</p><strong>Inspect next</strong></div><div className="priority-card low"><div><i/> <b>Low Priority ({counts.Low})</b></div><p>No screening trigger</p><strong>Inspect later</strong></div></div></section>
    <section className="inspection-panel"><div className="section-heading">INSPECTION ORDER <span>(Suggested)</span></div><ol>{inspect.slice(0,5).map(c=><li key={c.id} className={selectedCase===c.id?'active':''} onClick={()=>{setSelectedCase(c.id);mapRef.current?.setView([c.lat,c.lng],18)}}><span>Building ID: {c.id}</span><i style={{background:priorityColor[c.priority]}}/><small>{c.priority}</small></li>)}</ol><button className="text-button" onClick={()=>{const blob=new Blob([JSON.stringify(inspect,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='safenova-inspection-order.json';a.click();URL.revokeObjectURL(url)}}><Download size={14}/> Export list</button></section>
   </div>
  </section></main>
  <footer><span><ShieldCheck size={14}/> SafeNova · AI + GIS construction screening prototype</span><span>Alerts are not legal findings. Authorized human verification is required.</span></footer>
 </div>
}
createRoot(document.getElementById('root')).render(<App/>);
