// @ts-nocheck — needs `npm i leaflet react-leaflet @types/leaflet`
import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export interface RegionPoint {
  name: string;
  lat: number;
  lng: number;
  value: number;
  /** Optional override radius (px). */
  radius?: number;
}

interface Props {
  data: RegionPoint[];
  metricLabel?: string;
  height?: number;
}

/**
 * Leaflet map centered on Uzbekistan with bubble overlays
 * proportional to a chosen metric (e.g. universities, students, avg GPA).
 */
export default function UzbekistanMap({ data, metricLabel = "Qiymat", height = 500 }: Props) {
  const center: [number, number] = [41.3, 64.6];
  const max = Math.max(...data.map((d) => d.value), 1);

  return (
    <div style={{ height, width: '100%', borderRadius: 8, overflow: 'hidden' }}>
      <MapContainer center={center} zoom={6} style={{ height: '100%', width: '100%' }} scrollWheelZoom={false}>
        <TileLayer
          attribution='&copy; OpenStreetMap'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {data.map((p) => (
          <CircleMarker
            key={p.name}
            center={[p.lat, p.lng]}
            radius={p.radius ?? 6 + (p.value / max) * 24}
            pathOptions={{ color: '#1677ff', fillColor: '#1677ff', fillOpacity: 0.55 }}
          >
            <Tooltip direction="top">
              <b>{p.name}</b><br />
              {metricLabel}: {p.value}
            </Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}

/** Default 14-region coordinates for Uzbekistan (centroid-ish) */
export const UZ_REGIONS: Omit<RegionPoint, 'value'>[] = [
  { name: 'Toshkent sh.', lat: 41.2995, lng: 69.2401 },
  { name: 'Toshkent v.', lat: 41.3, lng: 69.6 },
  { name: 'Andijon', lat: 40.7821, lng: 72.3442 },
  { name: 'Buxoro', lat: 39.7681, lng: 64.4556 },
  { name: 'Farg\'ona', lat: 40.3894, lng: 71.7836 },
  { name: 'Jizzax', lat: 40.1158, lng: 67.842 },
  { name: 'Namangan', lat: 40.9983, lng: 71.6726 },
  { name: 'Navoiy', lat: 40.0844, lng: 65.3792 },
  { name: 'Qashqadaryo', lat: 38.85, lng: 65.79 },
  { name: 'Qoraqalpog\'iston', lat: 42.46, lng: 59.6 },
  { name: 'Samarqand', lat: 39.6542, lng: 66.9597 },
  { name: 'Sirdaryo', lat: 40.38, lng: 68.78 },
  { name: 'Surxondaryo', lat: 37.94, lng: 67.57 },
  { name: 'Xorazm', lat: 41.55, lng: 60.63 },
];
