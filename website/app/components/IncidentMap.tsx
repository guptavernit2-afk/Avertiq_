'use client';

import { useEffect, useRef, useState } from 'react';
import { MapPin, Layers3, LocateFixed, Mountain, Info, RefreshCw } from 'lucide-react';
import type { Map as MapLibreMap, GeoJSONSource, Marker } from 'maplibre-gl';
import { DEMO_LOCATION, FIXTURES, PLACES, type PresetId } from '@/lib/demo';

type Props = { revision: PresetId; current: boolean; selected: string; onSelect: (id: string) => void; captureRef: { current: (() => string | undefined) | null }; focused: boolean; onFocus: () => void };
export default function IncidentMap({ revision, current, selected, onSelect, captureRef, focused, onFocus }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<MapLibreMap | null>(null);
  const onSelectRef = useRef(onSelect);
  onSelectRef.current = onSelect;
  const [ready, setReady] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [terrain, setTerrain] = useState(true);
  const [tilted, setTilted] = useState(true);
  const [showArea, setShowArea] = useState(true);
  const [showPlaces, setShowPlaces] = useState(true);
  const [generation, setGeneration] = useState(0);
  const markers = useRef<Marker[]>([]);
  useEffect(() => {
    let cancelled = false;
    let timeout: ReturnType<typeof setTimeout>;
    let instance: MapLibreMap | null = null;
    const resizeObserver = new ResizeObserver(() => instance?.resize());
    setReady(false); setError(''); setLoading(true);
    import('maplibre-gl').then((ml) => {
      if (cancelled || !container.current) return;
      try {
        // Serve the pinned worker unchanged: Vinext's development overlay uses window,
        // which is unavailable when injected into a Vite-processed worker module.
        ml.setWorkerUrl('/vendor/maplibre/maplibre-gl-worker.mjs?v=6.17.0');
        instance = new ml.Map({ container: container.current, center: [DEMO_LOCATION.lng, DEMO_LOCATION.lat], zoom: 13.5, pitch: 57, bearing: -23, maxPitch: 75, canvasContextAttributes: { preserveDrawingBuffer: true }, attributionControl: { compact: true }, style: {
          version: 8,
          sources: {
            osm: { type: 'raster', tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'], tileSize: 256, maxzoom: 19, attribution: '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap contributors</a>' },
            terrain: { type: 'raster-dem', url: 'https://tiles.mapterhorn.com/tilejson.json' },
            hillshade: { type: 'raster-dem', url: 'https://tiles.mapterhorn.com/tilejson.json' },
          },
          layers: [{ id: 'background', type: 'background', paint: { 'background-color': '#dce7da' } }, { id: 'roads', type: 'raster', source: 'osm', paint: { 'raster-saturation': -0.48, 'raster-contrast': -0.10 } }, { id: 'hillshade', type: 'hillshade', source: 'hillshade', paint: { 'hillshade-exaggeration': 0.22, 'hillshade-shadow-color': '#46684d' } }],
          terrain: { source: 'terrain', exaggeration: 1 },
        } });
        map.current = instance;
        resizeObserver.observe(container.current);
        instance.addControl(new ml.NavigationControl({ visualizePitch: true }), 'bottom-right');
        instance.addControl(new ml.ScaleControl({ maxWidth: 100, unit: 'metric' }), 'bottom-left');
        timeout = setTimeout(() => { if (!cancelled) { setLoading(false); setError('Map layers are taking longer to load. Check your connection or retry; no assessment is being calculated.'); } }, 20000);
        instance.on('error', (e) => {
          if (!cancelled && e.error?.message?.includes('WebGL')) { setLoading(false); setError('3D rendering is unavailable in this browser. Try a browser with WebGL enabled.'); }
        });
        instance.on('load', () => {
          if (!instance || cancelled) return;
          instance.addSource('assessment', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
          instance.addLayer({ id: 'assessment-fill', type: 'fill', source: 'assessment', paint: { 'fill-color': '#e7a84a', 'fill-opacity': 0.30 } });
          instance.addLayer({ id: 'assessment-line', type: 'line', source: 'assessment', paint: { 'line-color': '#b97a1a', 'line-width': 2, 'line-dasharray': [3, 2] } });
          instance.addSource('source', { type: 'geojson', data: { type: 'Feature', properties: {}, geometry: { type: 'Point', coordinates: [DEMO_LOCATION.lng, DEMO_LOCATION.lat] } } });
          instance.addLayer({ id: 'source-point', type: 'circle', source: 'source', paint: { 'circle-radius': 8, 'circle-color': '#087e73', 'circle-stroke-color': '#ffffff', 'circle-stroke-width': 3 } });
          PLACES.forEach(place => {
            const element = document.createElement('button'); element.type = 'button'; element.className = 'place-marker'; element.textContent = place.name; element.dataset.place = place.id; element.setAttribute('aria-label', `${place.name}, fictional ${place.type} site`); element.addEventListener('click', () => onSelectRef.current(place.id));
            markers.current.push(new ml.Marker({ element, anchor: 'bottom' }).setLngLat(place.coordinates).addTo(instance!));
          });
          const tanker = document.createElement('div'); tanker.className = 'tanker-marker'; tanker.textContent = 'D-001 · DEMO TANKER';
          markers.current.push(new ml.Marker({ element: tanker, anchor: 'bottom', offset: [0, -15] }).setLngLat([DEMO_LOCATION.lng, DEMO_LOCATION.lat]).addTo(instance));
          captureRef.current = () => { try { return instance?.getCanvas().toDataURL('image/png'); } catch { return undefined; } };
          clearTimeout(timeout); setLoading(false); setReady(true); setError('');
        });
      } catch { setLoading(false); setError('The map could not start. WebGL and internet access are required for geographic layers.'); }
    }).catch(() => { setLoading(false); setError('The map library could not load. Please retry.'); });
    return () => { cancelled = true; clearTimeout(timeout); resizeObserver.disconnect(); markers.current.forEach(m => m.remove()); markers.current = []; instance?.remove(); map.current = null; captureRef.current = null; };
  }, [generation, captureRef]);
  useEffect(() => {
    const m = map.current;
    if (!ready || !m) return;
    const source = m.getSource('assessment') as GeoJSONSource | undefined;
    source?.setData({ type: 'FeatureCollection', features: current && showArea ? [{ type: 'Feature', properties: { evidence: 'illustrative', synthetic: true, revision }, geometry: { type: 'Polygon', coordinates: [FIXTURES[revision]] } }] : [] });
  }, [ready, revision, current, showArea]);
  useEffect(() => { if (ready) map.current?.easeTo({ pitch: tilted ? 57 : 0, duration: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 550 }); }, [ready, tilted]);
  useEffect(() => { if (ready) { map.current?.setTerrain(terrain ? { source: 'terrain', exaggeration: 1 } : null); map.current?.setLayoutProperty('hillshade', 'visibility', terrain ? 'visible' : 'none'); } }, [ready, terrain]);
  useEffect(() => { markers.current.forEach(marker => { const e = marker.getElement(); if (e.dataset.place) { e.hidden = !showPlaces; e.setAttribute('aria-pressed', String(e.dataset.place === selected)); } }); }, [ready, selected, showPlaces]);
  useEffect(() => { if (!map.current) return; const timer = setTimeout(() => map.current?.resize(), 100); return () => clearTimeout(timer); }, [focused]);
  function retry() { setGeneration(g => g + 1); setTerrain(true); setTilted(true); }
  return <section className={`map-panel ${focused ? 'map-expanded' : ''}`} aria-label="Incident geographic map">
    <div className="map-toolbar"><div><span className="section-kicker">GEOGRAPHIC CONTEXT</span><h2>Incident map <span className="map-status">{ready ? 'Map connected' : 'Loading map'}</span></h2></div><div className="map-actions"><div className="segmented"><button aria-pressed={!tilted} onClick={() => setTilted(false)}>2D</button><button aria-pressed={tilted} onClick={() => setTilted(true)}><Layers3 size={13}/>3D</button></div><button className="icon-button expand-button" onClick={onFocus} aria-label={focused ? 'Restore dashboard layout' : 'Expand map'}><MapPin size={16}/></button></div></div>
    <div className="map-viewport"><div ref={container} className="map-canvas"/>
      <div className="map-location"><MapPin size={14}/><span>Adoshi corridor <small>Approximate demo pin</small></span></div>
      <div className="wind-badge"><span className={`wind-arrow ${revision === 'B' ? 'southwest' : ''}`}>↑</span><div>2 m/s <small>From {revision === 'A' ? 'west' : 'southwest'} · preset {revision}</small></div></div>
      {loading && <div className="map-loading"><Mountain size={28}/><strong>Loading the corridor</strong><span>Geographic layers require internet access.</span></div>}
      {error && <div className="map-error" role="status"><Info size={20}/><p>{error}</p><button onClick={retry}><RefreshCw size={14}/>Retry map</button></div>}
      <button className="recenter" onClick={() => map.current?.easeTo({ center: [DEMO_LOCATION.lng, DEMO_LOCATION.lat], zoom: 13.5, bearing: -23 })}><LocateFixed size={15}/>Recenter</button>
      <div className={`map-legend ${!current ? 'outdated' : ''}`}><span className="legend-mark"/><div><strong>{current ? `Illustrative assessment ${revision}` : 'Assessment outdated · area hidden'}</strong><small>{current ? 'Prepared demo area · no calculated hazard distance' : 'Restore a documented preset to view its illustration'}</small></div><span className="label-tag">SIMULATED</span></div>
    </div>
    <div className="map-bottom"><div className="map-toggles"><label><input type="checkbox" checked={showArea} onChange={e => setShowArea(e.target.checked)} disabled={!current}/>Demo area</label><label><input type="checkbox" checked={terrain} onChange={e => setTerrain(e.target.checked)}/>Terrain</label><label><input type="checkbox" checked={showPlaces} onChange={e => setShowPlaces(e.target.checked)}/>Demo places</label></div><span><Info size={12}/>Terrain does not affect the assessment.</span></div>
  </section>;
}
